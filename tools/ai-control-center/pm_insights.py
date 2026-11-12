"""AI-PM 1.6: honest, source-aware readiness and schedule-risk interpretation.

Derived only from the 61-task inventory, evidence reviews, dependency planning,
and independent milestone history. No writes, no guessed acceptance or ETA.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from collections import Counter
from zoneinfo import ZoneInfo

STAGES = ("planned", "in_progress", "implementation_candidate", "review",
          "blocked", "technical_complete", "dev_accepted")
AGE_DAYS = 30


def assess(coverage, review, plan, readiness, history, *, as_of=None):
    if any(x.get("state") != "loaded" for x in (coverage, review, plan, readiness, history)):
        return {"state": "unavailable",
                "reason": "Verifizierte Aufgaben, Reviews, Abhängigkeiten, Excel-Readiness und Gate-Historie erforderlich.",
                "global_release": "NO_GO"}
    if (coverage.get("total") != 61 or
        coverage.get("reviewed") + coverage.get("needs_review") != 61 or
        coverage.get("source_sha256") != readiness.get("source_sha256") or
        coverage.get("source_sha256") != history.get("source_sha256") or
        plan.get("modeled_tasks") != coverage.get("dependency_modeled") or
        review.get("covered") != coverage.get("reviewed") or
        readiness.get("history_status") != "loaded"):
        return {"state": "unavailable", "reason": "Unvereinbare Quellversionen oder Review-Zählungen.",
                "global_release": "NO_GO"}
    rows=coverage.get("items",[])
    if len(rows) != 61 or len({r.get("task_key") for r in rows}) != 61:
        return {"state": "unavailable", "reason": "Fiverr-Aufgabenbestand unvollständig oder doppelt.",
                "global_release": "NO_GO"}
    if any(r.get("stage") not in STAGES for r in rows):
        return {"state": "unavailable", "reason": "Unbekannter Arbeitsstatus im Task-Register.",
                "global_release": "NO_GO"}
    current=as_of or dt.datetime.now(ZoneInfo("Europe/Berlin")).date()
    if isinstance(current, str):
        current=dt.date.fromisoformat(current)

    # Original manually-maintained stage is not proof of acceptance.
    raw=Counter(r["stage"] for r in rows)
    stage_counts={stage:raw[stage] for stage in STAGES}
    observed=sum(bool(r.get("observed_prs")) for r in rows)
    checked_tech=sum(bool(r.get("imported_technical")) for r in rows)
    checked_live=sum(bool(r.get("imported_go_live")) for r in rows)
    gates=history.get("counts",{})
    if (not all(isinstance(gates.get(g),int) and 0<=gates[g]<=61
                for g in ("technical","dev","go_live")) or
        checked_tech>gates["technical"] or checked_live>gates["go_live"]):
        return {"state": "unavailable", "reason": "Milestone-Zählungen inkonsistent.",
                "global_release": "NO_GO"}

    # Curated source age describes the review *document*, not exact PR/CI staleness.
    age=review.get("review_age_days")
    if age is None:
        try:
            age=(current-dt.date.fromisoformat(review["reviewed_at"])).days
        except (KeyError, ValueError, TypeError):
            age=None
    source_age=age if isinstance(age,int) and age>=0 else None
    stale=source_age is not None and source_age>AGE_DAYS
    unknown=coverage["needs_review"]
    known=coverage["reviewed"]
    with_observation_only=sum(
        r["review_coverage"]=="unreviewed" and bool(r.get("observed_prs")) for r in rows)
    without_any_evidence=sum(
        r["review_coverage"]=="unreviewed" and not r.get("observed_prs") for r in rows)

    # Graph coverage cannot safely imply global critical path, schedule certainty,
    # execution status or that undocumented dependencies do not exist.
    roots=plan.get("upstream_p0_reviews",[])
    if not roots or any(x.get("id") not in {r["id"] for r in plan.get("items",[])} for x in roots):
        return {"state": "unavailable", "reason": "P0-Startreviews fehlen.",
                "global_release": "NO_GO"}
    focus=sorted(roots,key=lambda x:(-x["downstream_count"],x["id"]))[0]
    other_roots=[x["id"] for x in roots if x["id"]!=focus["id"]]

    timeline=readiness.get("timeline",{})
    if timeline.get("state")=="loaded":
        # Linear baseline is a *scenario*, not the contract milestone schedule.
        schedule={"state":"provisional", "planning_gap_pp":timeline["gap_percentage_points"],
                  "baseline_date":timeline["baseline_date"],
                  "target_date":timeline["target_date"],
                  "actual_history_points":len(history.get("points",[])),
                  "attested_event_count":history.get("count_events",0),
                  "interpretation":("baseline_only" if history.get("count_events",0)==0
                                    else "attested_history_but_incomplete"),
                  "delay_days":None,
                  "forecast_reliability":"not_established",
                  "warning":"Rechnerischer linearer Soll-Ist-Abstand; keine belegbare Verspätung in Arbeitstagen. "
                            "Kein genehmigter Meilensteinplan oder belastbarer Critical Path."}
    else:
        schedule={"state":"unavailable","delay_days":None,
                  "reason":"Verifizierter historischer Planvergleich nicht verfügbar."}

    risks=[
        {"code":"COVERAGE_GAP","level":"unknown_scope",
         "label":"46 Aufgaben ohne kuratiertes Review",
         "affected_tasks":unknown,
         "reason":"Priorität und echte Abhängigkeiten bei unreviewten Aufgaben unbekannt."},
        {"code":"MODEL_LIMIT","level":"uncertain",
         "label":"Abhängigkeitsnetz nur teilweise modelliert",
         "affected_tasks":coverage["dependency_unknown"],
         "reason":"Vorhandene Planungskanten sind Hypothesen aus 15 Reviews, nicht Gesamtprojekt-Critical-Path."},
        {"code":"P0_OPEN","level":"blocking_review",
         "label":"P0-Abnahmebedingungen weiterhin offen",
         "affected_tasks":review["p0_candidates"],
         "reason":"Kein offenes Kriterium ohne formelle unabhängige Evidenzprüfung automatisch erfüllt."},
    ]
    if stale:
        risks.append({"code":"OLD_REVIEW_SOURCE","level":"recheck_needed",
                      "label":"Quellenreview älter als 30 Tage",
                      "affected_tasks":known,
                      "reason":"Alter des kuratierten Reviewdokuments, nicht bewiesenes Alter einzelner PR-Tests."})

    return {
        "state":"loaded","source_sha256":coverage["source_sha256"],
        "as_of_date":current.isoformat(),"global_release":"NO_GO",
        "work_status":{"total":61,"raw_stage_counts":stage_counts,
                       "observed_pr_tasks":observed,
                       "historical_excel_technical":checked_tech,
                       "historical_excel_go_live":checked_live,
                       "attested_and_baseline_technical":gates["technical"],
                       "independent_dev_attested":gates["dev"],
                       "attested_and_baseline_task_go_live":gates["go_live"],
                       "note":"Arbeitsstatus ist manuell; PR-Beobachtungen und historische Häkchen "
                              "sind keine neue technische/DEV-/Go-Live-Abnahme."},
        "evidence_quality":{"curated_review_tasks":known,
                            "unreviewed_tasks":unknown,
                            "unreviewed_with_pr_observations":with_observation_only,
                            "unreviewed_without_observed_pr":without_any_evidence,
                            "review_source_date":review.get("reviewed_at"),
                            "review_source_age_days":source_age,
                            "review_source_stale":stale,
                            "stale_after_days":AGE_DAYS,
                            "meaning":"Reviewabdeckung, nicht automatische PR-/CI-/BC27-Evidenzverifikation."},
        "risk_summary":{"p0_review_tasks":review["p0_candidates"],
                        "p0_open_criteria":sum(len(r["criteria"]) for r in review["items"]
                                               if r["priority"]=="P0"),
                        "curated_model_tasks":plan["modeled_tasks"],
                        "modeled_dependencies":plan["edge_count"],
                        "risks":risks,
                        "schedule_confidence":"insufficient_for_release_ETA"},
        "schedule":schedule,
        "next_action":{"task_id":focus["id"],"title":focus["title"],
                       "action":focus["next_check"],"known_downstream":focus["downstream_count"],
                       "parallel_review_threads":other_roots,
                       "basis":"Highest downstream reach among explicitly curated upstream P0 reviews; "
                               "heuristic for reviewing, not a guaranteed priority.",
                       "requires_human_review":True},
        "fiverr_go_live_fraction":readiness["gate_fraction"],
        "legacy_total_project_estimate":readiness["legacy_estimate_fraction"],
        "warning":"Bisher nur 15/61 Detailreviews; keine Status- oder Freigabeautomation. "
                  "Soll-Ist-Projektion ist Kapazitätsarithmetik, kein Liefertermin."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=("assess",))
    args=p.parse_args()
    import app
    data=app.snapshot()
    print(json.dumps(data.get("pm_insights",{}),ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
