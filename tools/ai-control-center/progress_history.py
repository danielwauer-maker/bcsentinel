"""Operator-attested milestone history. No GitHub observation can authorize a gate.

All mutations require explicit CLI confirmation and a reviewer distinct from actor.
Legacy Excel marks are immutable baseline, never newly granted approvals.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import project_store

GATES = ("implementation", "technical", "dev", "go_live")
ACCEPTED = ("technical", "dev", "go_live")
BASELINE_SCHEMA = """
CREATE TABLE IF NOT EXISTS progress_baseline (
    task_key TEXT PRIMARY KEY REFERENCES task(task_key),
    plan_hours REAL NOT NULL CHECK(plan_hours >= 0),
    imported_technical INTEGER NOT NULL,
    imported_go_live INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS progress_meta (
    id INTEGER PRIMARY KEY CHECK(id=1),
    source_sha256 TEXT NOT NULL,
    baseline_date TEXT NOT NULL,
    initial_fraction REAL NOT NULL,
    total_hours REAL NOT NULL,
    initialized_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS progress_event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_key TEXT NOT NULL REFERENCES task(task_key),
    gate TEXT NOT NULL CHECK(gate IN ('implementation','technical','dev','go_live')),
    actor TEXT NOT NULL,
    reviewer TEXT,
    evidence_uri TEXT NOT NULL,
    reason TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    UNIQUE(task_key,gate)
);
"""

def now():
    return dt.datetime.now(dt.timezone.utc)

def db_path(value=None):
    return Path(value or project_store.DB_PATH)

def init_baseline(source, path=None):
    """Initialize exactly once from SHA-verified workbook and previously imported tasks."""
    from readiness import planning_anchor
    if source.get("state") != "loaded" or not source.get("sha256"):
        raise ValueError("Expected verified live workbook, not snapshot")
    expected = [r for r in source["rows"] if r["area"] == "fiverr"]
    if len(expected) != 61:
        raise ValueError("Expected 61 Fiverr tasks")
    start = planning_anchor(source["planning_issue_date"])
    if start > now().astimezone(ZoneInfo("Europe/Berlin")).date():
        raise ValueError("Future baseline date")
    try:
        start_fraction = float(source["legacy_start_fraction"])
        hours = {("fiverr:"+str(r["id"])):float(r["plan_hours"]) for r in expected}
    except (KeyError,ValueError,TypeError) as exc:
        raise ValueError("Missing numeric plan input") from exc
    if (len(hours)!=61 or not 0<=start_fraction<=1 or
        any(not math.isfinite(v) or v<0 for v in hours.values()) or sum(hours)<=0):
        raise ValueError("Invalid baseline plan")
    path=db_path(path)
    if not path.is_file():
        raise ValueError("Task database not imported")
    con=project_store.connect(path)
    try:
        con.executescript(BASELINE_SCHEMA)
        with con:
            existing=con.execute("SELECT * FROM progress_meta WHERE id=1").fetchone()
            if existing:
                if (existing["source_sha256"]!=source["sha256"] or
                    existing["baseline_date"]!=start.isoformat()):
                    raise ValueError("Baseline changed. Explicit reconciliation required")
                return {"state":"already_initialized","tasks":61}
            imported=con.execute("SELECT sha256 FROM imports LIMIT 1").fetchone()
            if not imported or imported["sha256"]!=source["sha256"]:
                raise ValueError("Workbook SHA does not match the original imported master")
            rows={r["task_key"]:r for r in con.execute(
                "SELECT task_key,imported_technical,imported_acceptance FROM task WHERE area='fiverr'")}
            if rows.keys()!=hours.keys():
                raise ValueError("Imported Fiverr task IDs differ from workbook")
            # Capture historical checkmarks verbatim; do not insert approval events.
            for r in expected:
                key="fiverr:"+str(r["id"])
                t=rows[key]
                if int(bool(r["technical_checked"]))!=t["imported_technical"] or int(bool(r["live_checked"]))!=t["imported_acceptance"]:
                    raise ValueError("Historic checkbox mismatch")
                con.execute("INSERT INTO progress_baseline VALUES(?,?,?,?)",
                    (key,hours[key],t["imported_technical"],t["imported_acceptance"]))
            total=sum(hours.values())
            con.execute("INSERT INTO progress_meta VALUES(1,?,?,?,?,?)",
                (source["sha256"],start.isoformat(),start_fraction,total,now().isoformat(timespec="seconds")))
            con.execute("INSERT INTO audit_event(event_type,task_key,detail_json,created_at) VALUES(?,?,?,?)",
                ("progress.baseline_initialized",None,json.dumps({"sha256":source["sha256"],"tasks":61}),project_store.timestamp()))
        return {"state":"initialized","tasks":61,"total_hours":total,
                "baseline_date":start.isoformat()}
    finally:
        con.close()

def validate_evidence(uri):
    try:
        u=urlsplit(uri)
    except ValueError:
        raise ValueError("Invalid evidence link") from None
    if u.scheme!="https" or not u.netloc or u.username or u.password or u.fragment:
        raise ValueError("Evidence must be an HTTPS URL without credentials or fragment")
    if not re.fullmatch(r"[a-zA-Z0-9.-]+",u.hostname or ""):
        raise ValueError("Invalid evidence hostname")
    return uri

def record(task_key, gate, actor, reviewer, evidence_uri, reason, path=None,
           *, confirm=False, at=None):
    """Explicit human CLI only; never called by GitHub sync or API GET."""
    if not confirm:
        raise ValueError("Explicit --confirm required, nothing recorded")
    if gate not in GATES:
        raise ValueError("Unknown gate")
    if not actor.strip() or len(actor)>100 or (gate in ACCEPTED and
        (not reviewer.strip() or reviewer.strip().casefold()==actor.strip().casefold())):
        raise ValueError("Independent reviewer and actor required for acceptance")
    if len(reason.strip())<15 or len(reason)>2000:
        raise ValueError("Evidence rationale must be at least 15 characters")
    validate_evidence(evidence_uri)
    instant=at or now()
    if instant.tzinfo is None:
        raise ValueError("Timezone-aware event date required")
    if instant > now()+dt.timedelta(minutes=2):
        raise ValueError("Future approval forbidden")
    path=db_path(path)
    if not path.is_file():
        raise ValueError("No project database")
    con=project_store.connect(path)
    try:
        with con:
            meta=con.execute("SELECT * FROM progress_meta WHERE id=1").fetchone() if has_table(con,"progress_meta") else None
            if not meta:
                raise ValueError("Run explicit baseline init first")
            if instant.date() < dt.date.fromisoformat(meta["baseline_date"]):
                raise ValueError("Events before baseline cannot be backfilled")
            task=con.execute("SELECT t.area,b.imported_technical,b.imported_go_live FROM progress_baseline b JOIN task t USING(task_key) WHERE task_key=?",
                             (task_key,)).fetchone()
            if task is None or task["area"]!="fiverr":
                raise ValueError("Only imported Fiverr task keys supported")
            if (gate=="technical" and task["imported_technical"] or
                gate=="go_live" and task["imported_go_live"]):
                raise ValueError("Task already counted in immutable historic Excel baseline")
            if gate=="dev":
                technical=bool(task["imported_technical"]) or con.execute(
                    "SELECT 1 FROM progress_event WHERE task_key=? AND gate='technical'",(task_key,)).fetchone()
                if not technical: raise ValueError("Technical approval required before DEV approval")
            if gate=="go_live" and not con.execute(
                "SELECT 1 FROM progress_event WHERE task_key=? AND gate='dev'",(task_key,)).fetchone():
                raise ValueError("DEV approval required before go-live task gate")
            con.execute("""INSERT INTO progress_event(task_key,gate,actor,reviewer,evidence_uri,reason,recorded_at)
                           VALUES(?,?,?,?,?,?,?)""",
                        (task_key,gate,actor.strip(),reviewer.strip(),evidence_uri,reason.strip(),
                         instant.astimezone(dt.timezone.utc).isoformat(timespec="seconds")))
            if gate in ACCEPTED:
                con.execute("""INSERT INTO approval(task_key,gate,approved_by,evidence_uri,reason,approved_at)
                               VALUES(?,?,?,?,?,?)""",
                            (task_key,gate,reviewer.strip(),evidence_uri,reason.strip(),
                             instant.astimezone(dt.timezone.utc).isoformat(timespec="seconds")))
            # task stages remain separate; no global release authorization.
            con.execute("INSERT INTO audit_event(event_type,task_key,detail_json,created_at) VALUES(?,?,?,?)",
                        ("progress.gate_recorded",task_key,
                         json.dumps({"gate":gate,"actor":actor.strip(),"reviewer":reviewer.strip(),
                                     "evidence_uri":evidence_uri}),project_store.timestamp()))
        return {"state":"recorded","task_key":task_key,"gate":gate,"global_release":"NO_GO"}
    finally:
        con.close()

def has_table(con,name):
    return bool(con.execute("SELECT 1 FROM sqlite_master WHERE name=? AND type='table'",(name,)).fetchone())

def history(path=None):
    path=db_path(path)
    if not path.is_file():return {"state":"not_initialized"}
    con=project_store.connect(path)
    try:
        if not has_table(con,"progress_meta"):
            return {"state":"not_initialized"}
        meta=con.execute("SELECT * FROM progress_meta WHERE id=1").fetchone()
        if not meta:return {"state":"not_initialized"}
        tasks=[dict(r) for r in con.execute("SELECT * FROM progress_baseline ORDER BY task_key")]
        events=[dict(r) for r in con.execute("SELECT id,task_key,gate,recorded_at,evidence_uri,actor,reviewer FROM progress_event ORDER BY recorded_at,id")]
    finally:
        con.close()
    weights={t["task_key"]:t["plan_hours"] for t in tasks}
    imported_tech={t["task_key"] for t in tasks if t["imported_technical"]}
    imported_go={t["task_key"] for t in tasks if t["imported_go_live"] and t["imported_technical"]}
    approved={gate:set() for gate in GATES}
    for ev in events:approved[ev["gate"]].add(ev["task_key"])
    def weighted(keys):return sum(weights[x] for x in keys)
    total=meta["total_hours"]
    tech_hours=weighted(imported_tech|approved["technical"])
    dev_hours=weighted(approved["dev"])
    go_hours=weighted(imported_go|approved["go_live"])
    base=meta["initial_fraction"]
    overall=base+(1-base)*go_hours/total
    # Historical baseline is not fabricated as individual approval events.
    initial=base+(1-base)*weighted(imported_go)/total
    points=[{"date":meta["baseline_date"],"overall_fraction":round(initial,6),
             "technical_fraction":round(weighted(imported_tech)/total,6),
             "dev_fraction":0.0,"go_live_fraction":round(weighted(imported_go)/total,6),
             "source":"historic_excel_baseline"}]
    for ev in events:
        date=dt.datetime.fromisoformat(ev["recorded_at"]).astimezone(ZoneInfo("Europe/Berlin")).date().isoformat()
        if date < meta["baseline_date"]:date=meta["baseline_date"]
        cumulative={g:set() for g in GATES}
        instant=dt.datetime.fromisoformat(ev["recorded_at"])
        for r in events:
            if dt.datetime.fromisoformat(r["recorded_at"])<=instant:
                cumulative[r["gate"]].add(r["task_key"])
        go=weighted(imported_go|cumulative["go_live"])
        value={"date":date,
               "overall_fraction":round(base+(1-base)*go/total,6),
               "technical_fraction":round(weighted(imported_tech|cumulative["technical"])/total,6),
               "dev_fraction":round(weighted(cumulative["dev"])/total,6),
               "go_live_fraction":round(go/total,6),"source":"operator_attested"}
        if points[-1]["date"]==date:points[-1]=value
        else:points.append(value)
    return {"state":"loaded","source_sha256":meta["source_sha256"],
            "baseline_date":meta["baseline_date"],"initial_fraction":round(initial,6),
            "overall_fraction":round(overall,6),"technical_fraction":round(tech_hours/total,6),
            "dev_fraction":round(dev_hours/total,6),"go_live_fraction":round(go_hours/total,6),
            "count_events":len(events),"counts":{"technical":len(imported_tech|approved["technical"]),
                    "dev":len(approved["dev"]),"go_live":len(imported_go|approved["go_live"])},
            "points":points,"latest_events":events[-15:],
            "global_release":"NO_GO",
            "caution":"Operator-attestierte Nachweise; kein automatischer BC-E2E-Nachweis und keine globale Go-Live-Freigabe."}

def apply_to_readiness(readiness, hist, *, as_of=None):
    """Replace frozen actual with separately attested gate history; never overwrite source data."""
    import copy
    from readiness import estimate_work_date
    if (readiness.get("state")!="loaded" or hist.get("state")!="loaded" or
        hist["source_sha256"]!=readiness.get("source_sha256")):
        result=copy.deepcopy(readiness)
        result["history_status"]=("source_mismatch" if hist.get("state")=="loaded" else hist.get("state","unavailable"))
        return result
    result=copy.deepcopy(readiness)
    result["history_status"]="loaded"
    result["history_event_count"]=hist["count_events"]
    result["historical_excel_fraction"]=result["legacy_estimate_fraction"]
    result["legacy_estimate_fraction"]=hist["overall_fraction"]
    result["legacy_remaining_fraction"]=round(1-hist["overall_fraction"],6)
    result["technical_fraction"]=hist["technical_fraction"]
    result["gate_fraction"]=hist["go_live_fraction"]
    total=result["total_hours"]
    result["technical_hours"]=round(total*hist["technical_fraction"],2)
    result["accepted_hours"]=round(total*hist["go_live_fraction"],2)
    result["remaining_hours"]=round(total-result["accepted_hours"],2)
    result["remaining_weeks"]=round(result["remaining_hours"]/result["hours_per_week"],2)
    result["technical_count"]=hist["counts"]["technical"]
    result["gate_count"]=hist["counts"]["go_live"]
    current=as_of or dt.datetime.now(ZoneInfo("Europe/Berlin")).date()
    days=math.ceil(result["remaining_hours"]/(result["hours_per_week"]/5)) if result["remaining_hours"] else 0
    result["remaining_workdays"]=days
    result["capacity_scenario_date"]=estimate_work_date(current,days).isoformat()
    result["go_live"]="NO_GO"
    if result.get("timeline",{}).get("state")=="loaded":
        model=result["timeline"]
        model["actual_fraction"]=hist["overall_fraction"]
        model["gap_percentage_points"]=round((model["actual_fraction"]-model["planned_fraction"])*100,2)
        delta=model["gap_percentage_points"]
        model["schedule_status"]="ahead" if delta>0.15 else "behind" if delta<-.15 else "on_track"
        model["actual_series"]=[{"date":p["date"],"value":p["overall_fraction"],"source":p["source"]}
                                for p in hist["points"]]
        last=model["actual_series"][-1]
        model["actual_point"]=last
        model["actual_source"]="operator_attested_history" if hist["count_events"] else "historic_excel_baseline_only"
        model["assumptions"] += (" Nur ausdrücklich attestierte Gate-Ereignisse erhöhen die Ist-Kurve."
            " PRs, Code, CI und Dashboard-Refresh allein nicht.")
    result["warning"] = ("Ist-Readiness aus historischer Excel-Baseline plus ausdrücklich und unabhängig"
                          " operator-attestierten Aufgaben-Gates; globale Go-Live-Freigabe weiterhin NO-GO.")
    return result


def cli():
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=("init","history","record"))
    p.add_argument("--db")
    p.add_argument("--task")
    p.add_argument("--gate",choices=GATES)
    p.add_argument("--actor",default="")
    p.add_argument("--reviewer",default="")
    p.add_argument("--evidence",default="")
    p.add_argument("--reason",default="")
    p.add_argument("--confirm",action="store_true")
    args=p.parse_args()
    if args.action=="init":
        import app
        result=init_baseline(app.tracker(),args.db)
    elif args.action=="history":result=history(args.db)
    else:result=record(args.task or "",args.gate or "",args.actor,
                       args.reviewer,args.evidence,args.reason,args.db,confirm=args.confirm)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":cli()
