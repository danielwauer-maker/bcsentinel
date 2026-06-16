# Task 3 Audit: Free Data Health Score, Free Insights, Premium Locking

Datum: 2026-06-16

## Gepruefte bestehende Flows

- Backend Scan Start: `POST /scan/start` in `backend/app/routers/scans.py`
  - Bisher war nur `scan_mode=deep` fuer BC-Start vorbereitet.
  - Deep Scan ohne Credit oder aktives Monitoring wurde mit HTTP 402 blockiert.
  - Credits wurden bei neuem Deep Scan direkt beim Start verbraucht.
- Backend Scan Sync: `POST /scan/sync` in `backend/app/routers/scans.py`
  - Scan-Ergebnisse werden in `Scan` gespeichert und fuer Analytics, Reports und Pricing genutzt.
  - Deep Sync ohne Credit oder Monitoring wurde blockiert.
  - Non-Deep Scan-Typen liefen bereits ohne Credit-Verbrauch.
- License Snapshot: `backend/app/services/product_license_service.py` und `backend/app/routers/license.py`
  - Bereits vorhanden: Free-Insight- und Premium-Flags (`can_view_free_insights`, `can_view_issues`, `can_view_actions`, `can_view_reports`, `can_view_record_details`, `can_use_monitoring`).
  - Fehlend fuer Task 3: explizite Free-Score-Flags.
- Analytics Dashboard: `backend/app/routers/analytics.py`, `backend/app/templates/analytics_embed.html`, `backend/app/static/js/analytics-dashboard.js`, `backend/app/static/css/dashboard.css`
  - Dashboard-Daten kamen ueber `GET /analytics/embed/data`.
  - Premium-Findings wurden fuer Free-Tenants bereits aus `top_findings` entfernt.
  - Separate serverseitige Section-Gates fuer Issues, Actions und Reports gab es noch nicht.
- Reports: `backend/app/routers/reports.py`
  - Executive Report ist bereits serverseitig ueber `can_view_executive_report` gesperrt.
- BC Extension:
  - `DHSetup.Page.al` startete bisher den Deep Scan aus der Scan-Aktion.
  - `DHApiClient.Codeunit.al` sendete `scan_mode=deep`.
  - `DHDeepScanRunner.Codeunit.al` synchronisierte Ergebnisse mit `scan_type=deep`.

## Umsetzung

- Free Data Health Score
  - `scan_mode`/`scan_type=data_health_score` wird nun normalisiert und akzeptiert.
  - `POST /scan/start` erlaubt `data_health_score` ohne Scan Credit und ohne Purchase.
  - `POST /scan/sync` akzeptiert `data_health_score` ohne Credit-Verbrauch.
  - Die bestehende Deep-Scan-Ergebnisstruktur wird weiterverwendet. Es war keine Migration noetig, weil `Scan.scan_type` und `ScanRunStatus.scan_mode` bereits String-Felder sind.
- Neue Flags
  - `can_run_data_health_score`
  - `has_completed_data_health_score`
  - Bestehende Scan-Ergebnisse zaehlen als abgeschlossener Data Health Score, damit Free Insights sofort aus vorhandenen Daten angezeigt werden koennen.
- Free Insights
  - Dashboard-Payload enthaelt nun einen `free_insights`-Block mit:
    - Top Findings
    - Business Impacts
    - Module Distribution
    - Records by Module
    - Active Issues Summary
  - Tenant Pricing wird weiter aus der aktuellen Record-Anzahl berechnet und im Dashboard mitgeliefert.
- Premium Locking
  - Free-Tenants erhalten keine Premium-Listen in `top_findings`.
  - Neue serverseitige Section-Endpunkte:
    - `GET /analytics/embed/issues`
    - `GET /analytics/embed/actions`
    - `GET /analytics/embed/reports`
  - Diese Endpunkte antworten fuer Free-Tenants mit HTTP 402 und geben Premium-Daten erst bei Full Analysis, Validation Check oder Monitoring frei.
- Dashboard-Grundlayout
  - Neues funktionales Layout mit dunkler linker Sidebar.
  - Navigation: Overview, Analytics, Issues, Actions, Reports, Subscription, Settings.
  - Footer: Support, Documentation, Logout.
  - Free-Lock-Overlays fuer gesperrte Premium-Bereiche.
  - Subscription-Bereich zeigt die produkt-/tierabhaengige Preisstruktur.
- BC Extension
  - Neue Aktion `Start Data Health Score` startet den kostenlosen Score.
  - Neue Aktion `Start Premium Deep Scan` nutzt weiter Credit/Premium-Pruefung.
  - API-Client kann `StartDataHealthScore` senden.
  - Runner synchronisiert Data-Health-Score-Laeufe mit `scan_type=data_health_score`.
  - Aktive AL-Quelltexte verwenden keine sichtbaren Assessment-Labels mehr fuer den neuen Startflow.

## Bewusst nicht geaendert

- Keine Daten wurden geloescht.
- Keine Docker-, Deployment- oder Produktivoperation wurde ausgefuehrt.
- Keine Stripe-Produkte oder Stripe-Preise wurden erstellt.
- Bestehende Legacy-Begriffe in alten Dokus, Legacy-Tests und generierten Translation-XLF-Dateien bleiben aus Kompatibilitaetsgruenden bestehen.

## Verifikation

- Python Syntax:
  - `python -m py_compile backend/app/routers/analytics.py backend/app/routers/scans.py backend/app/routers/license.py backend/app/services/product_license_service.py backend/tests/test_product_licensing_p0.py`
- JavaScript Syntax:
  - `node --check backend/app/static/js/analytics-dashboard.js`
- Backend Tests:
  - `pytest backend/tests/test_product_licensing_p0.py backend/tests/test_pricing.py backend/tests/test_billing.py backend/tests/test_admin.py`
  - Ergebnis: 81 passed, 46 warnings

## Hinweise / Follow-ups

- Die AL Extension wurde quellenbasiert angepasst; ein echter AL Compiler/Package-Build wurde in dieser Umgebung nicht ausgefuehrt.
- Die neuen Dashboard-Sections liefern jetzt serverseitige Daten und Locks. Detailseiten, Drilldowns und echte Report-Download-Links koennen darauf aufbauend weiter ausgebaut werden.
- Wenn produktseitig exakt ein kostenloser Score pro Tenant erzwungen werden soll, kann auf Basis der neuen Flags noch eine harte Wiederholungs-Sperre ergaenzt werden. Aktuell ist die zentrale Sicherheitsgrenze: kein Credit-Verbrauch fuer `data_health_score`, aber Premium-Daten bleiben serverseitig gesperrt.
