"""Current project fact layer. Distinguishes corroborated source, DEV and manual gates.

Immutable Excel task titles and historical narratives are not rewritten.
This view is curated by exact PR/sha operator evidence and fail-closed if
the corresponding source cannot be observed.
"""
from __future__ import annotations

BC_VERSION="1.0.2.60"
CURRENT_TITLE_OVERRIDES={
  "1.03":"BC27 · Extension 1.0.2.60 installieren und Upgrade/Datenerhalt abnehmen",
  "1.02":"DEV Backend · Release 403709ca / Migration 0041 nachweisen",
  "2.01":"3B · 199 Checks / 6 Duplikat-Routen gegen BC27 prüfen",
  "3.02":"Full-v6 Report / Viewer · echtes BC27-E2E durchführen",
}
CURRENT_ACTION_OVERRIDES={
 "1.03":"BC27 Sandbox: 1.0.2.60 Artefakt-SHA/Installation, Upgrade-Datenerhalt und Non-SUPER in 12 manuellen Fällen prüfen.",
 "1.02":"DEV-Backend 403709ca / Migration 0041 gegen Operator-Evidence und aktuelle Laufzeit prüfen; Restore nicht als erledigt markieren.",
 "2.01":"199-Check-Abdeckung und sechs Duplikat-Routen mit finaler CI und echten BC27-Scans nachweisen.",
 "3.02":"Free → Full-v6: Auth, Tenant-Isolation, Einmal-Token, bezahlte Reportdaten und Ablauf in BC27 E2E testen.",
 "3.03":"Validation: zwei real vergleichbare versiegelte BC27-Scans plus Report-Inhalt prüfen.",
 "3.04":"Monitoring: Zugriff, Subscription/History und Report mit echten BC27-Daten E2E abnehmen.",
 "4.01":"Product-System Draft #33, Preismatrix, 14-Tage-Vertrag und Monitoring/Renewal normativ entscheiden.",
 "6.02":"Finale Fiverr-Landingpage aus redaktionellem DE/EN-Material implementieren, testen und freigeben.",
 "7.03":"Buyer Kit gegen finalen Preis-/Access-Vertrag angleichen, Fiverr-Editor und echte Käuferreise abnehmen.",
}
REPOS={
 "core":"danielwauer-maker/bcsentinel",
 "frontend":"danielwauer-maker/bcsentinel-frontend"
}
def _pr(repo,number,obs):
    return (obs.get(f"{REPOS[repo]}#{number}") or {}).get("state")
def _merged(repo,number,obs):
    return _pr(repo,number,obs)=="merged"
def _source_stage(verified,other="Quelle nicht ausreichend zugeordnet"):
    return "merged" if verified else other

def current_view(source,radar):
    gates=source.get("observed_gates") or {}
    runtime=gates.get("dev_runtime_release_20261116") or {}
    backend=runtime.get("backend") or {}
    frontend=runtime.get("frontend") or {}
    bc=runtime.get("bc27") or {}
    obs=radar.get("github_observations") or {} # Not returned by radar; see _current_prs observation below.
    state=radar.get("github",{}).get("state")
    verified_backend=(backend.get("state")=="deployed_exact_staging_sha" and
                      backend.get("sha")=="403709ca2dfdcbcc2ceb2e9dda4461f261d04aae")
    version=bc.get("source_extension_version")
    bc_current=(version==BC_VERSION and bc.get("sandbox_runtime_acceptance")=="NOT_EXECUTED")
    # Reviewed cross-cutting evidence is allowed for specific facts, not generic task approval.
    specs=[
      ("BC27 Extension","code_candidate",
       f"Quellstand {BC_VERSION} dokumentiert; aktuelles APP-Artefakt und Installation nicht verifiziert",
       "12 reale Sandbox-Fälle: Upgrade, Datenerhalt, Non-SUPER und Scan/Report prüfen",
       ["https://github.com/danielwauer-maker/bcsentinel/pull/191"]),
      ("Datenqualität / 3B","source_partial",
       "199-Check-Matrix und Finding/Provenance-Entwicklung belegt; 6 Duplikat-Routen offen",
       "Finale CI/AL-Coverage und echte BC27-Findings für alle relevanten Checks nachweisen",
       ["https://github.com/danielwauer-maker/bcsentinel/pull/191"]),
      ("Backend / DEV","dev_verified" if verified_backend else "unverified",
       "DEV Backend 403709ca mit DB-Upgrade/Health operatorverifiziert" if verified_backend else "Aktuelle DEV Backend-SHA nicht nachgewiesen",
       "Vollständige Report-/Berechtigungs-E2E und unabhängiger Restore-Test offen",
       [f"https://github.com/danielwauer-maker/bcsentinel/actions/runs/{backend.get('github_run')}" ]
        if backend.get("github_run") else []),
      ("Frontend / Report Viewer","dev_verified_prior",
       "DEV Frontend 2af0ae55 / Viewer HTTP 200 zuletzt nachgewiesen; nach Backend-Release nicht separat revalidiert",
       "Realen Full/Validation/Monitoring-Report mit berechtigtem Nutzer testen",
       ["https://github.com/danielwauer-maker/bcsentinel-frontend/pull/14"]),
      ("Access-v2 / Commercial","source_partial",
       "Enrollment und Free-Schema-Schutz im Staging integriert; Product-System #33 Draft, keine kommerzielle Freigabe",
       "14-Tage-Vertrag, Operator Grant, Monitoring/Renewal, Preise und Pilot-E2E abnehmen",
       ["https://github.com/danielwauer-maker/bcsentinel/pull/182",
        "https://github.com/danielwauer-maker/bcsentinel-product-system/pull/33"]),
      ("Security / CI / Release","merged_source_controls",
       "Fail-closed CI/Release-Kontrollen in GitHub gemergt; konkrete PROD-Freigabe nicht erteilt",
       "Branch-Protection, Reviewer und echte Rollen-/Session-Sicherheit separat prüfen",
       ["https://github.com/danielwauer-maker/bcsentinel/pull/184",
        "https://github.com/danielwauer-maker/bcsentinel/pull/188"]),
      ("Landingpage / Inhalte","editorial_complete",
       "DE/EN-Inhalte vorbereitet; derzeitige DEV-Pilot-Landingpage nicht finale Fiverr-Seite",
       "Fiverr-Landingpage integrieren, Rechts- und Visuallayout abnehmen",
       ["https://github.com/danielwauer-maker/bcsentinel/pull/166"]),
      ("Fiverr / Buyer Journey","editorial_complete",
       "Buyer Kit redaktionell vorhanden, aber Vertrags-/Onboarding-Freeze und echte E2E fehlen",
       "Assessment, Validation und Monitoring als reale Käuferreise prüfen",
       ["https://github.com/danielwauer-maker/bcsentinel/pull/165"]),
      ("AI Control Center","dev_verified",
       "Dashboard 2.6 auf DEV 8092, 85 Aufgaben und Excel 287 h, manuelle Minutenpersistenz erfolgreich browsergeprüft",
       "Historische Aufgaben-Nachweise zuordnen; Überblick und Versionsbeschriftung laufend reconciliieren",
       ["https://github.com/danielwauer-maker/bcsentinel/pull/201"]),
      ("PROD Release","not_started",
       "Keine PROD-Freigabe und kein Go-Live; Sicherheitscontroller im Quellcode vorhanden",
       "Erst nach BC27, Paid-E2E, Produktverträgen, Recht und Operator-Freigabe starten",
       ["https://github.com/danielwauer-maker/bcsentinel/pull/184"]),
      ("SaaS / Stripe","unreconciled",
       "24 Excel-Tasks importiert; aktueller operativer Stand der Einzelaufgaben nicht unabhängig reconciliert",
       "Product-System, Commerce, Auth/Onboarding und Stripe nach Aufgaben/Runtime prüfen",
       ["https://github.com/danielwauer-maker/bcsentinel-product-system/pull/31"])
    ]
    # A source release state MUST be current before claiming a version title.
    titles={k:v for k,v in CURRENT_TITLE_OVERRIDES.items() if k!="1.03" or bc_current}
    actions={k:v for k,v in CURRENT_ACTION_OVERRIDES.items() if k!="1.03" or bc_current}
    return {
      "state":"curated_partial","reviewed_at":source.get("reviewed_at"),
      "source_state":{"github":state,"backend":backend.get("state"),"bc27":bc.get("sandbox_runtime_acceptance")},
      "bc27_version":version if bc_current else None,
      "current_titles":titles,"current_actions":actions,
      "areas":[{"name":name,"stage":stage,"evidence":evidence,"remaining":remaining,"refs":refs}
               for name,stage,evidence,remaining,refs in specs],
      "next":[{"id":"1.03","title":titles.get("1.03","BC27 Runtime-Abnahme"),"action":actions.get("1.03","BC27-Version nachprüfen"),"gate":"manual_not_executed"},
              {"id":"3.02","title":"Full-v6 / Report E2E","action":actions["3.02"],"gate":"e2e_not_accepted"},
              {"id":"4.01","title":"Access-v2 / Preise freigeben","action":actions["4.01"],"gate":"normative_draft"}],
      "coverage_note":"11 fachliche Bereiche aus überprüfter kuratierter Evidence; 85 Excel-Tasks vollständig importiert, nur 15 Fiverr-Tasks einzeln reviewt. Kein prozentualer Gesamtfortschritt aus unbekannten Aufgaben ableitbar.",
      "gate":"NO_GO"
    }
