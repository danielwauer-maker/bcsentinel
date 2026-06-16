# Task 3.1 Audit: Data Health Score Completion & Sync Fix

Datum: 2026-06-16

## Root Cause

Der kostenlose Data Health Score startete korrekt mit:

- `POST /scan/start`
- `scan_mode=data_health_score`
- Backend-Run/Scan wurde als queued Platzhalter mit 0-Werten angelegt.

Der finale Ergebnis-Sync wurde aber im BC-Client blockiert, bevor das Backend erreicht wurde:

- `DHDeepScanRunner.Codeunit.al` rief nach Abschluss `ApiClient.SyncScanToBackendAndGetResponse(Setup, RequestText)` auf.
- `DHApiClient.Codeunit.al` fuehrte in `SyncScanToBackendAndGetResponse()` immer `EnsureReadyForScan(Setup)` aus.
- `EnsureReadyForScan()` fuehrt `RefreshLicenseStatus(Setup)` aus und prueft `Setup."Can Run Deep Scan"` bzw. Premium-Status.
- Bei Free-Tenants ohne Credit/Monitoring konnte dadurch nach lokal berechnetem Score die Fehlermeldung erscheinen:
  - `No scan credit or active monitoring available. Please buy Full Analysis, Validation Check or start Monitoring.`
- Weil der finale `POST /scan/sync` nicht gesendet wurde, blieb der Backend-Platzhalter bei Score/Checks/Issues/Records/Loss = 0.

## Gefundene Fehler / Befunde

1. Finaler Sync wurde fuer Data Health Score durch Premium-Gate blockiert.
   - Ursache: `EnsureReadyForScan()` in `SyncScanToBackendAndGetResponse()`.
   - Fix: Bei Sync-Payload `scan_type=data_health_score` wird nur noch `EnsureTenantAccessConfigured(Setup)` ausgefuehrt.

2. Der Data-Health-Score-Runner verwendete bereits denselben vollstaendigen Ergebnis-Payload wie Deep Scan.
   - Gesendet werden:
     - `scan_type`
     - `data_score`
     - `checks_count`
     - `issues_count`
     - `module_scores`
     - `enabled_modules`
     - `data_profile` inklusive `total_records`
     - `issues`
   - `estimated_loss_eur` und `potential_saving_eur` werden im Backend aus Issues/Data Profile berechnet und als Sync-Antwort in BC zurueckgeschrieben.

3. Der queued Backend-Datensatz war nicht falsch, sondern unvollstaendig.
   - `/scan/start` legt bewusst einen queued Scan mit 0-Werten an.
   - `/scan/sync` aktualisiert denselben Scan ueber dieselbe `scan_id`/`run_id`.
   - Wenn Sync blockiert wird, sieht Analytics den queued Platzhalter.

4. Backend `/scan/sync` war bereits korrekt fuer `data_health_score`.
   - Keine Credit-Pruefung fuer `data_health_score`.
   - Vorhandene queued Scans werden aktualisiert.
   - Scanwerte, Modulwerte, Datenprofil und Issues werden gespeichert.

5. Analytics nullt `data_health_score` nicht absichtlich.
   - Analytics liest `active_scan.data_score`, `checks_count`, `issues_count`, `total_records`, `estimated_loss_eur`, `potential_saving_eur` und Modulfelder.
   - Die 0-Werte kamen vom nicht aktualisierten Backend-Platzhalter.

6. TryFunction-Befund.
   - Progress-Updates laufen ueber `TryUpdateBackendProgress()` und koennen Fehler schlucken.
   - Der finale Ergebnis-Sync selbst ist keine TryFunction und wurde nicht verschluckt; er wurde durch `EnsureReadyForScan()` aktiv mit Fehler beendet.

## Geaenderte Dateien

- `bc-extension/app/src/codeunits/DHApiClient.Codeunit.al`
  - `SyncScanToBackendAndGetResponse()` prueft jetzt den Sync-Payload.
  - Bei `scan_type=data_health_score` wird keine Credit-, Monitoring- oder Premium-Pruefung ausgefuehrt.
  - Neue Hilfsfunktion `IsDataHealthScoreSyncPayload(RequestText: Text): Boolean`.

- `backend/tests/test_product_licensing_p0.py`
  - Neuer Regressionstest:
    - Startet `data_health_score`.
    - Erzeugt queued Backend-Platzhalter.
    - Synchronisiert echte Werte auf derselben `run_id`.
    - Prueft Analytics auf echte KPIs.
    - Prueft, dass Issues/Actions/Reports weiter gesperrt bleiben.

## Vorher / Nachher

Vorher:

1. BC startet Free Score.
2. Backend legt queued Scan mit 0-Werten an.
3. BC berechnet lokal Score/Checks/Issues.
4. Finaler Sync ruft `EnsureReadyForScan()` auf.
5. Free-Tenant ohne Credit/Monitoring erhaelt Premium-Fehler.
6. Backend bleibt bei 0-Werten.
7. Dashboard zeigt 0.

Nachher:

1. BC startet Free Score.
2. Backend legt queued Scan mit 0-Werten an.
3. BC berechnet lokal Score/Checks/Issues.
4. Finaler Sync erkennt `scan_type=data_health_score`.
5. Es wird nur Tenant/API-Konfiguration geprueft.
6. `POST /scan/sync` aktualisiert denselben Scan.
7. Dashboard liest echte Werte.
8. Issues, Actions und Reports bleiben Premium-gelockt.

## Ablauf `scan_mode=data_health_score`

Start:

- `DHSetup.Page.al`
  - Aktion `Start Data Health Score`
  - Ruft `DeepScanMgt.QueueDataHealthScore(Setup)` auf.

Backend-Start:

- `DHDeepScanMgt.Codeunit.al`
  - Setzt `DeepScanRun."Scan Mode" := 'data_health_score'`.
  - Ruft `ApiClient.StartDataHealthScore(...)` auf.
- `DHApiClient.Codeunit.al`
  - `StartDataHealthScore()` ruft `StartBackendScan(..., 'data_health_score')`.
  - Backend erhaelt `scan_mode=data_health_score`.

Runner:

- `DHDeepScanRunner.Codeunit.al`
  - Verwendet `"Scan Mode"` fuer Running-Headline, Progress und Sync.
  - `BuildSyncPayload()` setzt `scan_type=data_health_score`.
  - `premium_available` ist fuer Data Health Score `false`.

Sync:

- `DHApiClient.Codeunit.al`
  - `SyncScanToBackendAndGetResponse()` erkennt `scan_type=data_health_score`.
  - Kein `EnsureReadyForScan()`.
  - Sendet Payload an `POST /scan/sync`.

Backend Save:

- `backend/app/routers/scans.py`
  - Normalisiert `scan_type=data_health_score`.
  - Ueberspringt Deep-Scan-Credit-Pruefung.
  - Aktualisiert vorhandenen queued Scan ueber `scan_id`.
  - Speichert KPIs, Modulwerte, Datenprofil, Issues und berechnete Commercials.

Analytics Read:

- `backend/app/routers/analytics.py`
  - Liest den aktualisierten `Scan`.
  - KPIs kommen aus echten Feldern:
    - `data_score`
    - `checks_count`
    - `issues_count`
    - `total_records`
    - `estimated_loss_eur`
    - `potential_saving_eur`
  - Premium-Bereiche bleiben ueber Product Access gesperrt.

## Suche: Credit-/Monitoring-Fehlermeldung

Gefundene aktive Stellen:

- `DHApiClient.Codeunit.al`
  - `EnsureReadyForScan()`
  - Weiterhin erreichbar fuer Premium-/alte API-Scan-Methoden, aber nicht mehr fuer finalen Data-Health-Score-Sync.
- `DHDeepScanMgt.Codeunit.al`
  - `EnsureDeepScanAllowed()`
  - Weiterhin erreichbar fuer `QueueDeepScan()`, aber nicht fuer `QueueDataHealthScore()`.

Fuer `scan_type=data_health_score` im finalen Sync ist diese Meldung nach dem Fix nicht mehr erreichbar.

## Verifikation

- Python Syntax Check:
  - `python -m py_compile backend/app/routers/scans.py backend/app/routers/analytics.py backend/tests/test_product_licensing_p0.py`
  - Ergebnis: erfolgreich.
- JavaScript Syntax Check:
  - `node --check backend/app/static/js/analytics-dashboard.js`
  - Ergebnis: erfolgreich.
- Backend Regression Tests:
  - `pytest backend/tests/test_product_licensing_p0.py -k "data_health_score"`
  - Ergebnis: 3 passed.
- Relevante Backend Suite:
  - `pytest backend/tests/test_product_licensing_p0.py backend/tests/test_pricing.py backend/tests/test_billing.py backend/tests/test_admin.py`
  - Ergebnis: 82 passed, 47 warnings.
- AL Compile Check:
  - Kein `alc.exe` wurde in Workspace/Userprofil gefunden.
  - Vorhandene AL Artefakte/Pakete wurden erkannt, aber kein lokaler Compiler-Aufruf war verfuegbar.
  - Daher wurde eine statische Quellpruefung per Suchlauf durchgefuehrt.

## Offene Punkte

- Ein echter AL Package Build sollte in der BC-Entwicklungsumgebung nachgezogen werden.
- Progress-Update-Fehler werden weiterhin absichtlich per TryFunction toleriert. Das betrifft Status/Heartbeat, nicht den finalen Ergebnis-Sync.
- `estimated_loss_eur` und `potential_saving_eur` werden weiterhin serverseitig berechnet. Das ist konsistent mit Deep Scan und vermeidet lokale/Backend-Abweichungen.
