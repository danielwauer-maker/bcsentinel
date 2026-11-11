"""Read-only GitHub observation and task evidence matching, never gate approval."""
from __future__ import annotations
import argparse
import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import urlparse

import project_store
import pm_mapping

REPOS = ("danielwauer-maker/bcsentinel", "danielwauer-maker/bcsentinel-frontend")
# Require 'Sprint 7.03' or 'S7.03' with token boundaries, not arbitrary '7.03'.
SPRINT_RE = re.compile(r"(?<![\w])(?:sprint\s*|s\s*)(\d{1,2}\.\d{2})(?![\w.])",re.I)
MAX_PAGES = 5
PAGE_SIZE = 100

def match_tasks(pr, tasks):
    text = " ".join(str(pr.get(k) or "") for k in ("title", "body", "head_ref"))
    codes = set(SPRINT_RE.findall(text))
    if len(codes) != 1:
        return {"state": "ambiguous" if codes else "unmatched", "task_keys": [], "codes":sorted(codes)}
    code = next(iter(codes))
    candidates = sorted(t["task_key"] for t in tasks if t["source_id"] == code)
    return {"state":"matched" if len(candidates)==1 else ("ambiguous" if candidates else "unmatched"),
            "task_keys":candidates if len(candidates)==1 else [], "codes":[code]}

def collect(fetch):
    results, errors = [], []
    for repo in REPOS:
        items = []
        for page in range(1, MAX_PAGES + 1):
            path = f"repos/{repo}/pulls?state=all&sort=updated&direction=desc&per_page={PAGE_SIZE}&page={page}"
            response = fetch(path)
            if not isinstance(response,list):
                errors.append({"repo":repo,"state":response.get("state","error"),"reason":response.get("reason","")})
                break
            items.extend(response)
            if len(response)<PAGE_SIZE: break
        # All PRs in observed window. Repo failures never erase previously stored evidence.
        if not any(e["repo"]==repo for e in errors):
            results.extend({"repo":repo,"number":int(p["number"]),"title":p.get("title") or "",
                            "body":p.get("body") or "","head_ref":(p.get("head") or {}).get("ref",""),
                            "state":"draft" if p.get("draft") and p.get("state")=="open" else p.get("state","unknown"),
                            "merged_at":p.get("merged_at"),"updated_at":p.get("updated_at"),
                            "url":p.get("html_url") or ""} for p in items)
    return results, errors

def reconcile(pulls, errors, db_path=None):
    path = Path(db_path or project_store.DB_PATH)
    if not path.is_file():
        return {"state":"not_initialized","matched":0,"changes":0,"errors":errors}
    con = project_store.connect(path)
    now = project_store.timestamp()
    tasks = [dict(r) for r in con.execute("SELECT task_key,source_id FROM task")]
    matched, changes, ambiguous, links_total, reviewed_count = 0, 0, 0, 0, 0
    curated = pm_mapping.evidence_source()
    with con:
        con.execute("""CREATE TABLE IF NOT EXISTS pr_observation (
          repo TEXT NOT NULL, number INTEGER NOT NULL, url TEXT NOT NULL,
          title TEXT NOT NULL, pr_state TEXT NOT NULL, updated_at TEXT,
          task_key TEXT, match_state TEXT NOT NULL, observed_at TEXT NOT NULL,
          PRIMARY KEY(repo,number))""")
        con.execute("""CREATE TABLE IF NOT EXISTS sync_run (
          id INTEGER PRIMARY KEY AUTOINCREMENT, checked_at TEXT NOT NULL,
          received INTEGER NOT NULL, matched INTEGER NOT NULL,
          changed INTEGER NOT NULL, errors_json TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS pr_task_link (
          repo TEXT NOT NULL, number INTEGER NOT NULL,
          task_key TEXT NOT NULL REFERENCES task(task_key),
          source TEXT NOT NULL, reason TEXT NOT NULL,
          observed_at TEXT NOT NULL,
          PRIMARY KEY(repo,number,task_key))""")
        con.execute("""CREATE TABLE IF NOT EXISTS pr_match_review (
          repo TEXT NOT NULL, number INTEGER NOT NULL,
          reason TEXT NOT NULL, observed_at TEXT NOT NULL,
          PRIMARY KEY(repo,number))""")
        has_baseline = con.execute("SELECT 1 FROM sync_run LIMIT 1").fetchone() is not None
        for p in pulls:
            if p["repo"] not in REPOS or not re.fullmatch(r"https://github\.com/danielwauer-maker/[\w-]+/pull/\d+",p["url"]):
                continue
            result = pm_mapping.match_evidence(p,tasks,curated)
            links = result["links"]
            key = links[0]["task_key"] if len(links)==1 else None
            if links: matched += 1
            links_total += len(links)
            if result["state"]=="reviewed": reviewed_count += 1
            if result["state"]=="review": ambiguous += 1
            existing_links = {(r["task_key"],r["source"]) for r in con.execute(
                "SELECT task_key,source FROM pr_task_link WHERE repo=? AND number=?", (p["repo"],p["number"]))}
            new_links = {(r["task_key"],r["source"]) for r in links}
            if existing_links != new_links:
                con.execute("DELETE FROM pr_task_link WHERE repo=? AND number=?", (p["repo"],p["number"]))
                for link in links:
                    con.execute("INSERT INTO pr_task_link VALUES(?,?,?,?,?,?)",
                                (p["repo"],p["number"],link["task_key"],link["source"],link["reason"],now))
            if result["state"] in ("review","unmatched"):
                con.execute("""INSERT INTO pr_match_review VALUES(?,?,?,?)
                    ON CONFLICT(repo,number) DO UPDATE SET reason=excluded.reason,observed_at=excluded.observed_at""",
                    (p["repo"],p["number"],result["reason"],now))
            else:
                con.execute("DELETE FROM pr_match_review WHERE repo=? AND number=?", (p["repo"],p["number"]))
            previous=con.execute("SELECT title,pr_state,updated_at,task_key,match_state FROM pr_observation WHERE repo=? AND number=?",
                                  (p["repo"],p["number"])).fetchone()
            current=(p["title"],p["state"],p["updated_at"],key,result["state"])
            # New/revised mapping is metadata enrichment, not a PR content change.
            pr_changed = previous is None or tuple(previous)[:3] != current[:3]
            if has_baseline and pr_changed:
                changes+=1
                con.execute("INSERT INTO audit_event(event_type,task_key,detail_json,created_at) VALUES(?,?,?,?)",
                            ("github.pr_observed",key,json.dumps({"repo":p["repo"],"number":p["number"],
                             "title":p["title"][:240],"state":p["state"],"match":result["state"],
                             "previous_state":previous["pr_state"] if previous else None},ensure_ascii=False),now))
            con.execute("""INSERT INTO pr_observation
                (repo,number,url,title,pr_state,updated_at,task_key,match_state,observed_at)
                VALUES(?,?,?,?,?,?,?,?,?)
                ON CONFLICT(repo,number) DO UPDATE SET url=excluded.url,title=excluded.title,
                  pr_state=excluded.pr_state,updated_at=excluded.updated_at,task_key=excluded.task_key,
                  match_state=excluded.match_state,observed_at=excluded.observed_at""",
                (p["repo"],p["number"],p["url"],p["title"][:500],p["state"],p["updated_at"],key,result["state"],now))
        con.execute("INSERT INTO sync_run (checked_at,received,matched,changed,errors_json) VALUES(?,?,?,?,?)",
                    (now,len(pulls),matched,changes,json.dumps(errors)))
    con.close()
    return {"state":"partial" if errors else "loaded","matched":matched,"changed":changes,
            "links":links_total,"reviewed_references":reviewed_count,
            "ambiguous":ambiguous,"received":len(pulls),"errors":errors,"checked_at":now}

def briefing(db_path=None):
    path = Path(db_path or project_store.DB_PATH)
    if not path.exists(): return {"state":"not_initialized"}
    con=project_store.connect(path)
    if not con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sync_run'").fetchone():
        con.close()
        return {"state":"not_synced"}
    latest=con.execute("SELECT * FROM sync_run ORDER BY id DESC LIMIT 1").fetchone()
    since=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(hours=24)).isoformat(timespec="seconds")
    observations=[dict(x) for x in con.execute("""SELECT p.repo,p.number,p.url,p.title,p.pr_state,
       p.task_key,p.match_state,p.updated_at, r.reason
       FROM pr_observation p LEFT JOIN pr_match_review r
       ON p.repo=r.repo AND p.number=r.number ORDER BY p.updated_at DESC LIMIT 200""")]
    for item in observations:
        item["links"]=[dict(r) for r in con.execute(
            "SELECT task_key,source,reason FROM pr_task_link WHERE repo=? AND number=? ORDER BY task_key",
            (item["repo"], item["number"]))]
    unresolved = con.execute("SELECT count(*) FROM pr_match_review").fetchone()[0]
    reviewed = con.execute("SELECT count(DISTINCT repo||'#'||number) FROM pr_task_link WHERE source='reviewed_reference'").fetchone()[0]
    changes=[]
    for r in con.execute("""SELECT event_type,task_key,detail_json,created_at FROM audit_event
                            WHERE created_at>=? AND event_type='github.pr_observed' ORDER BY id DESC LIMIT 30""",(since,)):
        item=dict(r)
        item["detail"]=json.loads(item.pop("detail_json"))
        changes.append(item)
    con.close()
    errors=json.loads(latest["errors_json"])
    return {"state":"partial" if errors else "loaded","last_sync":latest["checked_at"],
            "received":latest["received"],"matched":latest["matched"],
            "changes_in_latest_sync":latest["changed"],"errors":errors,
            "changes_24h":changes,"observations":observations,
            "review_queue": pm_mapping.review_summary(observations),
            "unresolved_total": unresolved, "curated_count": reviewed,
            "interpretation":"GitHub observations only; task stage, acceptance and release gates remain unchanged."}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("action",choices=["sync","briefing"])
    ap.add_argument("--db",default=str(project_store.DB_PATH))
    args=ap.parse_args()
    if args.action=="briefing": result=briefing(args.db)
    else:
        import app
        pulls,errors=collect(app.github)
        result=reconcile(pulls,errors,args.db)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
