"""AI-PM 2.0.1 team roster: visual representation, never invented agent runtime.

Roles are design-time definitions. There is NO LLM provider or runnable agent yet.
The human agent_job ledger lacks a role-assignment column, so jobs are deliberately
unassigned rather than guessed from their title/purpose.
"""
from __future__ import annotations
import datetime as dt
from zoneinfo import ZoneInfo

ROLES = (
    ("pm","AI Project Manager","Projektsteuerung","Leadership","workflow","Führt die Prioritäten zusammen und bereitet Prüfaufträge vor.",None),
    ("architect","Solution Architect","Architektur & Produktvertrag","Architecture","blueprint","Prüft Verträge, Architektur, Schnittstellen und Systemgrenzen.","pm"),
    ("bc","Business Central Specialist","Business Central","ERP","database","Prüft AL-Extension, BC27-Sandbox und Upgrade-Sicherheit.","architect"),
    ("backend","Backend Engineer","Backend & API","Engineering","code","Entwickelt Schnittstellen, Datenmodelle und Backend-Tests.","architect"),
    ("frontend","Frontend & UX Designer","Frontend & Erlebnis","Design","layout","Gestaltet nutzerfreundliche Oberflächen und Reports.","architect"),
    ("qa","QA & Evidence Analyst","Tests & Qualitätsnachweise","Quality","shield","Prüft reproduzierbare Tests, Regressionen und Abnahmen.","pm"),
    ("devops","DevOps & Security","CI/CD & Sicherheit","Operations","cloud","Prüft Build-, Laufzeit- und Bereitstellungs-Sicherheit.","pm"),
    ("data","Data & Reporting Analyst","Daten & Reporting","Analytics","chart","Prüft Datenqualität, Kennzahlen und Report-Konsistenz.","pm"),
)

def roster(agents, daily, *, as_of=None):
    moment=as_of or dt.datetime.now(ZoneInfo("Europe/Berlin"))
    now=moment.isoformat(timespec="seconds")
    state=agents.get("state","unavailable")
    if state not in ("loaded","not_initialized"):
        return {"state":"unavailable","reason":"Agent control store unavailable","members":[],
                "runtime_execution":"disabled","global_release":"NO_GO"}
    if agents.get("execution")!="disabled" or agents.get("global_release")!="NO_GO":
        return {"state":"unavailable","reason":"Unknown execution or release state","members":[],
                "runtime_execution":"disabled","global_release":"NO_GO"}
    current_jobs=agents.get("jobs",[]) if state=="loaded" else []
    if not isinstance(current_jobs,list):
        return {"state":"unavailable","reason":"Invalid job ledger","members":[],
                "runtime_execution":"disabled","global_release":"NO_GO"}
    pending=[j for j in current_jobs if j.get("status") in ("proposed","approved","claimed")]
    # The control ledger does not record a role/agent identity. Deliberately
    # expose unassigned jobs instead of attributing them by task type.
    unassigned=[{"id":j["id"],"task_id":j["task_id"],"status":j["status"],
                 "purpose":j["purpose"],"meaning":"manually tracked, not an agent run"}
                for j in pending]
    recommendation=None
    if daily.get("state")=="loaded":
        r=daily.get("recommendation",{})
        if isinstance(r.get("task_id"),str):
            recommendation={"task_id":r["task_id"],"title":r.get("title",""),
                            "kind":"recommendation_only","assigned":False}
    members=[]
    for rid,name,subtitle,category,art,description,parent in ROLES:
        members.append({"id":rid,"name":name,"subtitle":subtitle,
                        "category":category,"art":art,"description":description,"reports_to":parent,
                        "configured":True,"runtime_state":"disabled",
                        "assignment_state":"unassigned",
                        "current_sprint":None,"current_task":None,
                        "activity_state":"no_runtime_telemetry",
                        "last_activity_at":None,
                        "last_activity":"Keine echte Agentenlaufzeit konfiguriert.",
                        "suggested_review":recommendation if rid=="pm" else None,
                        "progress_percent":None})
    return {"state":"loaded","updated_at":now,"roster_type":"planned_roles",
            "runtime_execution":"disabled","global_release":"NO_GO",
            "agent_count":len(members),"active_agents":0,
            "waiting_for_operator":len(members),
            "assigned_agents":0,"role_assignments_supported":False,
            "pending_unassigned_jobs":unassigned,
            "members":members,
            "refresh_interval_seconds":30,
            "warning":"Konfigurierte Teamrollen, keine ausführbaren KI-Agenten. "
                      "Eine genehmigte oder reservierte CLI-Aufgabe ist kein Agentenlauf. "
                      "Keine Agentenzuweisung oder Echtzeit-Telemetrie verfügbar. "
                      "Aktuelle Sprint-Empfehlung des Projektmanagers ist NICHT zugeteilt."}
