"""AI-PM 1.7: local, deterministic and review-only PM briefing.

No LLM/API integration, agents, GitHub writes, local writes, task approvals or releases.
This is an offline recommendation engine until optional model execution is approved.
Never treat untrusted PR text as an instruction.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from zoneinfo import ZoneInfo

MAX_CHANGES = 8
SYNC_AGE_MINUTES = 90
TRUSTED_REPOS = ("danielwauer-maker/bcsentinel",
                 "danielwauer-maker/bcsentinel-frontend")
ALLOWED_TASK_ID = re.compile(r"^\d{1,2}\.\d{2}$")


def _utc(value):
    try:
        moment = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return moment if moment.tzinfo else None
    except (TypeError, AttributeError, ValueError):
        return None


def _clean_ref(repo, number):
    if repo not in TRUSTED_REPOS or not isinstance(number, int) or isinstance(number, bool) or number <= 0:
        return None
    return f"https://github.com/{repo}/pull/{number}"


def _unavailable(reason):
    return {"state":"unavailable","reason":reason,"mode":"offline_rule_based",
            "human_review_required":True,"global_release":"NO_GO"}


def compose(insights, coverage, plan, gh_brief, *, as_of=None):
    """Generate a source-grounded daily brief. Observations cannot affect acceptance."""
    if insights.get("state")!="loaded" or coverage.get("state")!="loaded" or plan.get("state")!="loaded":
        return _unavailable("Verifizierte PM-1.6-Bewertung, Fiverr-Aufgabeninventar oder Blockerplan fehlt.")
    if insights.get("source_sha256")!=coverage.get("source_sha256"):
        return _unavailable("Unterschiedliche Quell-SHAs – keine Empfehlung.")
    action=insights.get("next_action",{})
    task_id=action.get("task_id")
    curated={x["id"]:x for x in coverage.get("items",[]) if x.get("review_coverage")=="curated"}
    roots={r["id"] for r in plan.get("upstream_p0_reviews",[])}
    if not isinstance(task_id,str) or not ALLOWED_TASK_ID.fullmatch(task_id) or task_id not in curated or task_id not in roots:
        return _unavailable("Empfohlener Sprint ist kein kuratierter P0-Startreview.")
    if (coverage.get("total")!=61 or len(coverage.get("items",[]))!=61 or
        insights.get("global_release")!="NO_GO" or plan.get("global_release")!="NO_GO"):
        return _unavailable("Projektmodell oder Release-Gate inkonsistent.")
    current=as_of or dt.datetime.now(ZoneInfo("Europe/Berlin"))
    if current.tzinfo is None:
        return _unavailable("Zeitstempel ohne Zeitzone")
    today=current.astimezone(ZoneInfo("Europe/Berlin")).date().isoformat()
    moment=current.astimezone(dt.timezone.utc)
    # Source freshness is about polling only, not PR CI, runtime or contractual truth.
    sync_state=gh_brief.get("state","not_synced")
    updated=_utc(gh_brief.get("last_sync"))
    age=int((moment-updated).total_seconds()//60) if updated else None
    github_fresh=(sync_state=="loaded" and age is not None and 0<=age<=SYNC_AGE_MINUTES)
    if sync_state=="partial":
        github_note="GitHub-Abgleich mit Quellenfehlern; Änderungen sind nur unvollständig beobachtet."
    elif age is None:
        github_note="Keine verwertbare GitHub-Synchronisierung vorhanden."
    elif age<0:
        github_note="Zeitstempel liegt in der Zukunft; GitHub-Sync als unbekannt behandeln."
    elif age>SYNC_AGE_MINUTES:
        github_note="GitHub-Abgleich älter als 90 Minuten; keine aktuellen PR-Aussagen."
    else:
        github_note="GitHub-Metadaten zuletzt beobachtet; keine Aussage zu CI, BC oder Laufzeit."

    changes=[]
    if github_fresh:
        for event in gh_brief.get("changes_24h",[]):
            detail=event.get("detail") or {}
            url=_clean_ref(detail.get("repo"),detail.get("number"))
            observed=_utc(event.get("created_at"))
            if not url or not observed or observed>moment or (moment-observed).total_seconds()>86400:
                continue
            changes.append({"url":url,"repo":detail["repo"],"number":detail["number"],
                            "state":str(detail.get("state") or "unknown")[:30],
                            "observed_at":observed.isoformat(),
                            "task_key":event.get("task_key") if event.get("task_key") in
                                {r["task_key"] for r in coverage["items"]} else None,
                            "interpretation":"Beobachtetes PR-Ereignis; kein Abnahmenachweis."})
            if len(changes)>=MAX_CHANGES:
                break

    unknown=insights["evidence_quality"]["unreviewed_tasks"]
    p0=insights["risk_summary"]["p0_open_criteria"]
    dev=insights["work_status"]["independent_dev_attested"]
    selected=curated[task_id]
    criteria=[c["text"] for c in selected.get("acceptance_criteria",[]) if c.get("state")=="open"]
    if not criteria:
        return _unavailable("Abnahmekriterien für Startreview sind nicht kuratiert.")
    # Strongly controlled bounded instruction, does not interpolate GitHub PR bodies/titles.
    # This is a copyable HUMAN review request, never an executable agent command.
    instruction=(
        f"BCSentinel DEV-first – Bitte Sprint {task_id} als unabhängigen technischen Review prüfen.\n"
        "Nur vorhandene versionierte Quellen/SHA und reale DEV-/BC27-Evidence prüfen. "
        "Keine PROD-/DEV-Deployments, GitHub-Merges, Änderungen an Berechtigungen, "
        "Freigaben, Zahlungen oder Kundendaten.\n"
        f"Prüffokus: {action['action']}\n"
        "Explizit offene Prüfbedingungen:\n"+
        "\n".join(f"- {c}" for c in criteria)+"\n"
        "Ergebnis strukturiert liefern: Quell-SHA und Zeitstempel, "
        "geprüfte Belege mit URLs, PASS/FAIL/UNKNOWN je Kriterium, verbleibende "
        "P0-Blocker, konkreter nächster manueller Schritt. "
        "Fehlende Evidence als UNKNOWN kennzeichnen. "
        "Weder technische noch DEV-/Go-Live-Freigabe ohne unabhängige Abnahme."
    )
    return {
        "state":"loaded","date":today,"mode":"offline_rule_based",
        "headline":f"Fiverr NO-GO · {p0} offene P0-Prüfkriterien · {unknown} Aufgaben ohne Detailreview",
        "summary":[
            f"Alle 61 Fiverr-Aufgaben inventarisiert, davon {coverage['reviewed']} quellenbasiert im Detail geprüft.",
            f"{dev} unabhängig attestierte DEV-Aufgabengates; die historische Excel-Ausgangsbasis ist separat.",
            "Die historische Gesamtprojektschätzung ist keine Fiverr-Release-Readiness.",
            github_note],
        "github":{"state":sync_state,"synced_at":gh_brief.get("last_sync"),"sync_age_minutes":age,
                  "fresh":github_fresh,"change_count_24h":len(changes),"changes_24h":changes},
        "risks":[{"code":r["code"],"label":r["label"],"affected_tasks":r["affected_tasks"]}
                 for r in insights["risk_summary"]["risks"]],
        "recommendation":{"task_id":task_id,"title":selected["title"],
                           "next_action":action["action"],"known_downstream":action["known_downstream"],
                           "parallel_threads":action["parallel_review_threads"],
                           "criteria_open":criteria,
                           "why":"Quellenbasierter vorgelagerter P0-Review mit der größten bekannten Folgewirkung; "
                                 "nicht als Projektgesamt-Ranking oder Releaseentscheidung verstehen.",
                           "human_review_required":True},
        "review_request":{"type":"manual_copy_only","text":instruction,
                          "execution":"disabled","requires_human_review":True},
        "source_limits":["Nur 15/61 Aufgaben mit kuratiertem Einzelreview und 22 modellierten Kanten.",
                         "GitHub-Sync-Stand ist kein CI-Status; ein PR-Link beweist keine BC27-Abnahme.",
                         "Keine validierte globale Critical-Path- oder Go-Live-Terminprognose."],
        "global_release":"NO_GO",
        "agent_execution":"disabled","llm_execution":"not_configured",
        "ai_api_cost":"none",
        "warning":"Regelbasiertes Offline-Briefing, keine angebundene generative KI. "
                  "Keine Hintergrundaufträge, GitHub-Schreibzugriffe oder automatische Freigaben."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=("brief",))
    args=p.parse_args()
    import app
    snapshot=app.snapshot()
    print(json.dumps(snapshot.get("ai_pm_brief",{}),ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
