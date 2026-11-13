"""AI-PM 1.5: complete 61-task Fiverr inventory with explicit evidence gaps.

Inventory completeness is NOT evidence-review completeness or go-live readiness.
This is read-only against the immutable imported DB, verified Excel and curated review.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import project_store


def catalog(tracker, acceptance, dependencies, db_path=None):
    if tracker.get("state") != "loaded" or not tracker.get("sha256"):
        return {"state": "unavailable", "reason": "Verified live Excel source is required", "items": []}
    if acceptance.get("state") != "loaded" or dependencies.get("state") != "loaded":
        return {"state": "unavailable", "reason": "Review or dependency model unavailable", "items": []}
    db = Path(db_path or project_store.DB_PATH)
    if not db.is_file():
        return {"state": "unavailable", "reason": "Imported SQLite task store missing", "items": []}

    source_rows = [r for r in tracker.get("rows", []) if r.get("area") == "fiverr"]
    if len(source_rows) != 61 or len({str(r.get("id")) for r in source_rows}) != 61:
        return {"state": "unavailable", "reason": "Fiverr Excel inventory is not exactly 61 unique tasks", "items": []}
    try:
        con = project_store.connect(db)
        try:
            imported = con.execute("SELECT sha256 FROM imports ORDER BY imported_at LIMIT 1").fetchone()
            rows = [dict(r) for r in con.execute("""SELECT task_key,source_id,title,sprint,
                stage,source_note,imported_technical,imported_acceptance
                FROM task WHERE area='fiverr' ORDER BY source_id""")]
            links = []
            if con.execute("SELECT 1 FROM sqlite_master WHERE name='pr_task_link' AND type='table'").fetchone():
                links = [dict(r) for r in con.execute("""SELECT l.task_key,l.repo,l.number,l.source,
                    p.pr_state,p.url,p.updated_at FROM pr_task_link l
                    INNER JOIN pr_observation p ON l.repo=p.repo AND l.number=p.number
                    WHERE l.task_key LIKE 'fiverr:%' ORDER BY p.updated_at DESC""")]
            approvals = [dict(r) for r in con.execute("""SELECT task_key,gate,evidence_uri
                FROM approval WHERE task_key LIKE 'fiverr:%'""")]
        finally:
            con.close()
    except Exception as exc:
        return {"state": "unavailable", "reason": "Cannot inspect imported task store: " + type(exc).__name__, "items": []}

    source_ids = {str(x["id"]) for x in source_rows}
    imported_ids = {str(x["source_id"]) for x in rows}
    if (not imported or imported["sha256"] != tracker["sha256"] or
        len(rows) != 61 or source_ids != imported_ids):
        return {"state": "unavailable", "reason": "Excel/SQLite SHA or identifiers differ; reconciliation required", "items": []}
    by_review = {r["id"]:r for r in acceptance["items"]}
    by_dependency = {r["id"]:r for r in dependencies["items"]}
    if (set(by_review) != set(by_dependency) or len(by_review) != acceptance["covered"]
        or acceptance["covered"] + acceptance["unreviewed"] != 61):
        return {"state": "unavailable", "reason": "Curated review/dependency coverage inconsistent", "items": []}
    by_link = {}
    for l in links:
        by_link.setdefault(l["task_key"], []).append(l)
    by_approval = {}
    for a in approvals:
        by_approval.setdefault(a["task_key"], set()).add(a["gate"])
    excel = {str(r["id"]):r for r in source_rows}
    result = []
    for row in rows:
        identifier = row["source_id"]
        x = excel[identifier]
        key = row["task_key"]
        # The import is immutable. Never silently substitute a new title/status for that import.
        if (key != "fiverr:"+identifier or str(x.get("title") or "") != row["title"]
            or bool(x.get("technical_checked")) != bool(row["imported_technical"])
            or bool(x.get("live_checked")) != bool(row["imported_acceptance"])):
            return {"state": "unavailable", "reason": "Workbook/task metadata drift; explicit reconciliation required", "items": []}
        review = by_review.get(identifier)
        graph = by_dependency.get(identifier)
        item_links = []
        for l in by_link.get(key, []):
            if l["repo"] not in ("danielwauer-maker/bcsentinel","danielwauer-maker/bcsentinel-frontend"):
                continue
            if l["url"] != f"https://github.com/{l['repo']}/pull/{l['number']}":
                continue
            item_links.append({"url":l["url"],"repo":l["repo"],"number":l["number"],
                               "state":l["pr_state"],"mapping_source":l["source"]})
        result.append({
            "id": identifier, "task_key": key, "title":row["title"],"sprint":row["sprint"],
            "stage":row["stage"],"imported_technical":bool(row["imported_technical"]),
            "imported_go_live":bool(row["imported_acceptance"]),
            "review_coverage":"curated" if review else "unreviewed",
            "review_state":review["review_state"] if review else "unknown",
            "priority":review["priority"] if review else None,
            "next_review":(graph["next_check"] if graph else
                           "Aufgabenbeschreibung/Abnahmekriterien und Evidenz unabhängig erheben"),
            "direct_prerequisites":graph["prerequisites"] if graph else [],
            "dependency_coverage":"curated" if graph else "unmodeled",
            "affected_downstream_count":graph["downstream_count"] if graph else None,
            "acceptance_criteria":review["criteria"] if review else [],
            "references":review["refs"] if review else [],
            "observed_prs":item_links,
            "attested_gates":sorted(by_approval.get(key,set())),
            "note":("Review- und Dependency-Modell vorhanden; alle Prüfkriterien bleiben bis Einzelabnahme offen"
                    if review else
                    "Noch keine unabhängige Einzelprüfung: Priorität, Voraussetzungen und reale Evidence unbekannt"),
        })
    result.sort(key=lambda x:x["id"])
    reviewed = sum(x["review_coverage"] == "curated" for x in result)
    unknown = len(result)-reviewed
    return {"state":"loaded", "source":"sha_verified_excel_and_imported_sqlite",
            "source_sha256":tracker["sha256"], "total":len(result),
            "reviewed":reviewed, "needs_review":unknown,
            "dependency_modeled":sum(x["dependency_coverage"]=="curated" for x in result),
            "dependency_unknown":sum(x["dependency_coverage"]=="unmodeled" for x in result),
            "tasks_with_observed_prs":sum(bool(x["observed_prs"]) for x in result),
            "unassigned_priority":sum(x["priority"] is None for x in result),
            "global_release":"NO_GO", "items":result,
            "warning":"61/61 bedeutet ausschließlich Inventarabdeckung. Für 46 Aufgaben fehlen "
                      "unabhängige Einzelreviews und geprüfte Abhängigkeiten. Nicht zugeordnete PRs "
                      "sind kein Beweis fehlender Implementierung. Automatische Freigaben ausgeschlossen."}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=("inventory",))
    p.add_argument("--db")
    args=p.parse_args()
    import app
    import acceptance_review
    import blocker_plan
    source=app.evidence()
    reviewed=acceptance_review.review(source,args.db)
    model=blocker_plan.analyze(reviewed)
    print(json.dumps(catalog(app.tracker(),reviewed,model,args.db),ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()
