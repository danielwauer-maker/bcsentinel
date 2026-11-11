"""Read-only DEV-first acceptance review for Fiverr tracker tasks.

A PR and the curated source review may justify a candidate review, NEVER an approval.
The checklists are review requirements; no check is silently marked satisfied.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import project_store

# Fixed review criteria based on documented acceptance findings.
# Public descriptions are intentionally actionable but never claim BC acceptance.
PLAYBOOK = {
 "1.01": ("P0", "Releasekandidat / SHA / CI",
     ["Immutable BC-App/Backend/Frontend-SHAs gegen Release-Matrix abgleichen",
      "CI-Ergebnisse auf exakt diesen SHAs dokumentieren",
      "DEV-Runtime- und Artefakthashes unabhängig bestätigen"]),
 "1.02": ("P0", "DEV-Image, Migration, Backup",
     ["Laufendes DEV-Backend-Image und DB-Migration 0040 read-only nachweisen",
      "Backup und Restore-Probe für denselben Datenstand bestätigen",
      "DEV-Release-Entscheid gegen Hash und Readiness-Gates protokollieren"]),
 "1.03": ("P0", "BC27-In-place-Upgrade",
     ["Upgrade 1.0.2.52 auf 1.0.2.58 in BC27 Sandbox real durchführen",
      "Daten, Registrierungen und Scanhistorie nach Upgrade erhalten",
      "Berechtigungen ohne SUPER und BC-Compiler-/Runtime-Evidence belegen"]),
 "2.01": ("P0", "199-Check-Ausführung",
     ["Für alle 199 Checks terminale PASS/FINDINGS/FAILED/SKIPPED-Evidence nachweisen",
      "Gruppierte Checks und Unterbrechungs-/Fehlerfälle abdecken",
      "CI am finalen SHA, AL-Compile und echten BC27-Lauf belegen"]),
 "2.02": ("P0", "Unveränderliche Source-Provenance",
     ["Record-Identitäten und Scope unveränderlich vom BC-Scan nachweisen",
      "Vergleich gleicher/anderer Tenant- und Company-Kontexte testen",
      "Positive und fail-closed BC27-Scanpaar-Evidence archivieren"]),
 "3.02": ("P0", "Full-Report E2E",
     ["Free-Baseline → Full-Freischaltung an demselben Scan prüfen",
      "Viewer, HTML/PDF, Access-Expiry und Archiv real in DEV testen",
      "Kein Free-Leak und korrekter Company-Scope bestätigen"]),
 "3.03": ("P0", "Validation-Vergleich E2E",
     ["Verifizierte vergleichbare Quell-Identitäten für zwei BC27-Scans nachweisen",
      "Resolved/New/Unchanged nur bei vollständiger Provenance anzeigen",
      "Nicht vergleichbare Fälle blockiert und reportseitig korrekt ausgeben"]),
 "3.04": ("P0", "Monitoring E2E",
     ["Nachweisbarer wiederkehrender Scan- und Subscription-Zyklus",
      "Abbruch, Verlängerung, Kündigung, Historie und Berechtigung testen",
      "Alerts/Monitoring-Reports nur nach verifizierter Datenprovenance freigeben"]),
 "4.01": ("P0", "Access-v2 Vertragsfreigabe",
     ["Produkt-Systemvertrag versioniert normativ entscheiden",
      "Free/Full14/Renewal/Validation/Monitoring mit altem Quick/7d abgleichen",
      "Preismatrix, Bestandsrechte und E2E-Kompatibilität freigeben"]),
 "4.02": ("P0", "Free → Full14",
     ["Full14 statt Legacy7 vertraglich freigeben und in DEV prüfen",
      "Nur bestehenden Free-Baselinescan entsperren, kein zweiter Scan",
      "Scope/TTL/Replay/Refund-Guards testen"]),
 "4.03": ("P0", "Renewal +14d",
     ["Versionierten Renewal-Vertrag, Stapelregeln und Preis freigeben",
      "Keinen neuen Scan oder Credit bei Renewal vergeben",
      "Token/Ablauf und unveränderte Legacy-Rechte E2E prüfen"]),
 "4.04": ("P0", "Renewal + Validation",
     ["Bestehende bezahlte Baseline und exakt einen neuen Scan nachweisen",
      "Nicht vergleichbare Findings fail-closed behandeln",
      "Credit/Refund/Access-Ablauf und BC27-Vergleich prüfen"]),
 "4.06": ("P0", "Operator Grants / Refund",
     ["V2-Operator-Grants gegen zugelassenen Produktvertrag prüfen",
      "Idempotenz und Refund-Widerruf ungenutzter Credits testen",
      "Audit/Permissions ohne privilegierte Bypass-Pfade prüfen"]),
 "6.02": ("P1", "Website DE/EN & Report-Beispiele",
     ["DE/EN-Copy gemäß freigegebenem Produktvertrag in Frontend umsetzen",
      "Mobile/Desktop, Barrierefreiheit und Routen visuell in DEV abnehmen",
      "DSGVO-/Trust-Claims, fiktive Euro-Beispiele und Legal-Seiten prüfen"]),
 "7.03": ("P1", "Fiverr Buyer Kit DE/EN",
     ["Finale Fiverr-Kategorien, Texte, Bilder und USD-Preise im echten Editor prüfen",
      "Recht/Privacy und vollständige BC-Kundenreise mit Full/Validation/Monitoring abnehmen",
      "Monitoring nur mit bestätigtem Abo-/Cancellation-/Report-E2E veröffentlichen"]),
}

STATUS = {
 "tracker_checked": ("historical_checked", "Historische Excel-Häkchen; Runtime neu bestätigen"),
 "manual_gate": ("blocked", "Manuelle Runtime-Abnahme offen"),
 "code_candidate": ("candidate", "Codekandidat; technische Evidence zu prüfen"),
 "partial": ("blocked", "Integration/Runtime-Evidence unvollständig"),
 "audit_draft": ("blocked", "Auditentwurf; Produktentscheidung offen"),
 "implementation_draft": ("candidate", "Implementierungsentwurf; Vertrag/BC-E2E offen"),
 "editorial_complete": ("editorial", "Redaktioneller Entwurf fertig; Live-Abnahme offen"),
}

def _safe_ref(url):
    return (isinstance(url,str) and url.startswith(
        ("https://github.com/danielwauer-maker/bcsentinel/",
         "https://github.com/danielwauer-maker/bcsentinel-frontend/")))

def review(source, db_path=None, *, as_of=None):
    """Inventory source-evidenced acceptance candidates; never write SQLite."""
    try:
        items=source.get("work_items")
        if not isinstance(items,list):
            raise ValueError("Missing reviewed source items")
        if source.get("schema_version") != 1:
            raise ValueError("Unexpected evidence schema")
        seen=set()
        for item in items:
            key=str(item["id"])
            if key in seen: raise ValueError("Duplicate review task")
            seen.add(key)
    except (KeyError,TypeError,ValueError) as exc:
        return {"state":"unavailable","reason":str(exc),"items":[]}
    db=Path(db_path or project_store.DB_PATH)
    if not db.is_file():
        return {"state":"not_initialized","items":[],"reason":"Task database unavailable"}
    con=project_store.connect(db)
    try:
        tasks={r["source_id"]:dict(r) for r in con.execute(
            "SELECT task_key,source_id,title,stage,imported_technical,imported_acceptance FROM task WHERE area='fiverr'")}
        if len(tasks)!=61: return {"state":"unavailable","items":[],"reason":"Fiverr register not complete"}
        links=[]
        if con.execute("SELECT 1 FROM sqlite_master WHERE name='pr_task_link'").fetchone():
            links=[dict(r) for r in con.execute(
                """SELECT l.task_key,l.repo,l.number,l.source,l.reason,p.pr_state,p.title,p.updated_at,p.url
                FROM pr_task_link l LEFT JOIN pr_observation p
                ON l.repo=p.repo AND l.number=p.number
                ORDER BY l.repo,l.number""")]
        approvals=[dict(r) for r in con.execute("SELECT task_key,gate,evidence_uri FROM approval")]
        by_task={}
        for link in links:by_task.setdefault(link["task_key"],[]).append(link)
        by_approval={}
        for a in approvals:by_approval.setdefault(a["task_key"],set()).add(a["gate"])
    finally:con.close()
    today=as_of or dt.datetime.now(dt.timezone.utc).date()
    source_date=str(source.get("reviewed_at") or "")
    try:
        age=(today-dt.date.fromisoformat(source_date)).days
    except ValueError:
        age=None
    result=[]
    for item in items:
        identifier=str(item["id"])
        if identifier not in tasks or identifier not in PLAYBOOK:
            continue
        key=tasks[identifier]["task_key"]
        rank,title,criteria=PLAYBOOK[identifier]
        category,message=STATUS.get(item.get("status"),("unknown","Evidence-Status unbekannt"))
        references=[r for r in item.get("refs",[]) if _safe_ref(r)]
        pr_links=by_task.get(key,[])
        observations=[{"url":l["url"],"number":l["number"],"repo":l["repo"],
                       "state":l["pr_state"] or "unknown","source":l["source"]}
                      for l in pr_links if _safe_ref(l.get("url"))]
        gate_set=by_approval.get(key,set())
        # Manual acceptance remains distinct from historic unchecked/checked raw flags.
        if category=="historical_checked":
            state="revalidation"
        elif "go_live" in gate_set:
            state="review_again"
        elif "technical" in gate_set or "dev" in gate_set:
            state="gate_review"
        else:
            state=category
        priority=(0 if rank=="P0" else 1,
                  0 if state in ("blocked","revalidation") else 1,
                  identifier)
        result.append({"id":identifier,"task_key":key,"title":title,
             "priority":rank,"review_state":state,"evidence_state":category,
             "assessment":message,"finding":item.get("detail",""),
             "criteria":[{"text":v,"state":"open"} for v in criteria],
             "refs":references,"pr_links":observations,"reviewed_at":source_date,
             "review_age_days":age,
             "technical_checked_historic":bool(tasks[identifier]["imported_technical"]),
             "go_live_checked_historic":bool(tasks[identifier]["imported_acceptance"]),
             "attested_gates":sorted(gate_set),
             "_order":priority})
    result.sort(key=lambda i:i["_order"])
    for item in result:item.pop("_order",None)
    missing=sorted(set(PLAYBOOK)-{x["id"] for x in result})
    return {"state":"loaded","reviewed_at":source_date,"review_age_days":age,
      "total_fiverr":len(tasks),"covered":len(result),"unreviewed":61-len(result),
      "p0_candidates":sum(x["priority"]=="P0" for x in result),
      "unresolved_criteria":sum(len(x["criteria"]) for x in result),
      "missing_playbooks":missing,"items":result,
      "warning":"Prüfliste, keine automatisch bestandenen Abnahmen. Kriterien sind offen, bis echte, unabhängig geprüfte Evidenz vorliegt. Alte Reviews können überholt sein; PR-Metadaten belegen keine BC27-E2E-Abnahme.",
      "global_release":"NO_GO"}

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=["review"])
    p.add_argument("--db")
    args=p.parse_args()
    from pathlib import Path
    root=Path(__file__).resolve().parent
    source=json.loads((root/"data"/"evidence-status.json").read_text(encoding="utf-8"))
    print(json.dumps(review(source,args.db),ensure_ascii=False,indent=2))

if __name__=="__main__":main()
