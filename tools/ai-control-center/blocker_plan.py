"""DEV-first dependency hypothesis planner for curated Fiverr acceptance reviews.

Read-only; never a release gate, time forecast, or approval engine.
Dependencies are engineering planning assumptions, requiring human verification.
"""
from __future__ import annotations

import argparse
import json

# (prerequisite, dependent, rationale). Only tasks with curated review evidence.
# These edges describe what must be *verified* before downstream approval,
# NOT which engineering tasks are forbidden to start in parallel.
EDGES = (
    ("1.01", "1.03", "Release SHAs / build evidence before BC27 upgrade acceptance"),
    ("1.02", "1.03", "DEV image, migration and restore baseline before real BC27 E2E"),
    ("1.03", "2.01", "BC27 execution acceptance requires verified extension runtime"),
    ("1.03", "2.02", "BC27 must persist trustworthy source evidence"),
    ("2.01", "2.02", "Completed check lifecycle before persisted comparability can be trusted"),
    ("2.02", "3.03", "Validation must fail closed without comparable provenance"),
    ("2.02", "3.04", "Monitoring comparison/history needs source evidence"),
    ("2.02", "4.04", "Renewal+Validation must consume a comparable scan pair"),
    ("4.01", "4.02", "Free/Full access is subject to approved v2 terms"),
    ("4.01", "4.03", "Renewal terms, price and stacking require normative contract"),
    ("4.01", "4.04", "Renewal+Validation offer requires normative contract"),
    ("4.01", "4.06", "Operator grants and refunds must match approved entitlements"),
    ("4.01", "6.02", "Public product and pricing claims require approved contract"),
    ("4.01", "7.03", "Fiverr offers require approved contract and prices"),
    ("4.02", "3.02", "Full report must be unlocked only by verified Full access"),
    ("4.02", "4.04", "Paid Full baseline is prerequisite to Validation access"),
    ("3.02", "3.03", "Validation journey requires accessible paid Full baseline"),
    ("3.03", "3.04", "Monitoring comparisons require validated report semantics"),
    ("3.02", "7.03", "Buyer journey needs working Full report"),
    ("3.03", "7.03", "Buyer journey needs working Validation comparison"),
    ("3.04", "7.03", "Monitoring Gig requires validated subscription E2E"),
    ("4.06", "7.03", "Sales delivery requires verified operator entitlement and refunds"),
)

# Suggested manual review focus, not automated certification or assumptions of completed tests.
NEXT_CHECK = {
    "1.01": "Release-Matrix und Commit-SHAs gegen die tatsächlich installierten DEV-Images nachprüfen",
    "1.02": "Laufende DEV-Migration/Backup-Restore-Evidence aus der Sandbox verifizieren",
    "4.01": "Versionierte Access-v2-Vertragsentscheidung und Preismatrix zur Freigabe vorbereiten",
    "1.03": "BC27 In-place-Upgrade in Sandbox und Datenerhalt protokollieren",
    "2.01": "199-Check-Lifecycle an finalem SHA sowie BC27-Runtime prüfen",
    "2.02": "Persistierte Provenance auf zwei realen BC27-Scans verifizieren",
    "4.02": "Free-Baseline → Full14 mit gleichem Scan und sicherer Laufzeit testen",
    "4.03": "Renewal ohne zusätzlichen Scan/Credit und vertragliche Regeln testen",
    "4.04": "Renewal+Validation mit genau einem Scan und Vergleichs-Gates prüfen",
    "4.06": "Operator-Grants, Refund-Idempotenz und Rollen ohne SUPER testen",
    "3.02": "Full-Viewer/PDF mit realer Freischaltung und Archiv prüfen",
    "3.03": "Validation-Positive/Negative-E2E und fail-closed Ergebnis prüfen",
    "3.04": "Monitoring-Abonnement, Historie und Kündigung in DEV testen",
    "6.02": "Website DE/EN nach vertraglicher Freigabe implementieren und visuell testen",
    "7.03": "Fiverr Editor, Recht/Preise und gesamte Buyer Journey erst nach E2E prüfen",
}

def _validated_graph(items):
    ids = {str(x["id"]) for x in items}
    if len(ids) != len(items):
        raise ValueError("Duplicate reviewed task identifiers")
    if ids != set(NEXT_CHECK):
        raise ValueError("Curated acceptance inventory changed; revalidate dependency model")
    prereqs = {k:set() for k in ids}
    dependents = {k:set() for k in ids}
    for source,target,_ in EDGES:
        if source not in ids or target not in ids or source == target:
            raise ValueError("Dependency references missing/self task")
        if source in prereqs[target]:
            raise ValueError("Duplicate dependency")
        prereqs[target].add(source)
        dependents[source].add(target)
    visited=set()
    active=set()
    def visit(node):
        if node in active:
            raise ValueError("Circular dependencies")
        if node in visited:
            return
        active.add(node)
        for child in dependents[node]:
            visit(child)
        active.remove(node)
        visited.add(node)
    for key in ids:
        visit(key)
    return prereqs,dependents

def analyze(acceptance):
    if acceptance.get("state") != "loaded":
        return {"state":"unavailable","reason":"Acceptance review unavailable", "items":[]}
    items = acceptance.get("items",[])
    try:
        prerequisites,dependents = _validated_graph(items)
    except (ValueError,TypeError,KeyError) as exc:
        return {"state":"unavailable","reason":str(exc),"items":[]}
    by_id={x["id"]:x for x in items}
    # An independently recorded technical+DEV approval is a *review signal* only.
    # Contract approval and release-critical gates are never inferred here.
    def evidence_signal(key):
        gates=set(by_id[key].get("attested_gates",[]))
        return ("technical" in gates and "dev" in gates)
    def descendants(root):
        result=set()
        todo=list(dependents[root])
        while todo:
            child=todo.pop()
            if child not in result:
                result.add(child)
                todo.extend(dependents[child])
        return result
    output=[]
    for task_id in sorted(by_id):
        task=by_id[task_id]
        parents=sorted(prerequisites[task_id])
        not_verified=[p for p in parents if not evidence_signal(p)]
        downstream=sorted(descendants(task_id))
        priority=task["priority"]
        review_type=task["review_state"]
        verified=evidence_signal(task_id)
        # This is a review scheduling recommendation, NOT approval eligibility.
        phase=("review_first" if not parents else
               "review_with_prerequisites" if not_verified else "review_prerequisites_attested")
        impact=len(downstream)
        tier=(0 if priority=="P0" else 1,
              0 if phase=="review_first" else 1,
              -impact,task_id)
        output.append({
            "id":task_id,"task_key":task["task_key"],"title":task["title"],
            "priority":priority,"review_state":review_type,
            "review_phase":phase,"next_check":NEXT_CHECK[task_id],
            "prerequisites":parents,"unverified_prerequisites":not_verified,
            "direct_dependents":sorted(dependents[task_id]),
            "downstream_tasks":downstream,"downstream_count":impact,
            "independent_tech_dev_attested":verified,
            "evidence_refs":task.get("refs",[]),
            "gate_caution":"Freigaben nur nach gesonderter sachlicher Prüfung; Modell signalisiert keine Vertrags-/BC27-/Go-Live-Abnahme.",
            "_sort":tier
        })
    output.sort(key=lambda t:t["_sort"])
    for item in output:
        item.pop("_sort")
    first=[t for t in output if t["review_phase"]=="review_first" and t["priority"]=="P0"]
    return {
        "state":"loaded",
        "scope":"15_curated_fiverr_tasks_only",
        "mode":"planning_hypothesis_read_only",
        "modeled_tasks":len(output),"unmodeled_fiverr_tasks":acceptance["unreviewed"],
        "edge_count":len(EDGES),
        "upstream_p0_reviews":[{"id":x["id"],"title":x["title"],
                                "downstream_count":x["downstream_count"],
                                "next_check":x["next_check"]} for x in first],
        "items":output,"global_release":"NO_GO",
        "warning":"Abhängigkeiten sind geprüfte Planungsannahmen, keine verifizierte Critical-Path-/ETA-Rechnung. "
                  "46 Fiverr-Aufgaben ohne Detailreview sind NICHT modelliert. "
                  "PRs, CI und historische Excel-Häkchen entsperren keine Abnahmen. "
                  "Ein unabhängiger Reviewer muss jede technische/DEV-/Vertragsentscheidung bestätigen."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=("plan",))
    p.add_argument("--db")
    args=p.parse_args()
    import acceptance_review
    source=json.loads((__import__("pathlib").Path(__file__).resolve().parent/
                       "data"/"evidence-status.json").read_text(encoding="utf-8"))
    result=analyze(acceptance_review.review(source,args.db))
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
