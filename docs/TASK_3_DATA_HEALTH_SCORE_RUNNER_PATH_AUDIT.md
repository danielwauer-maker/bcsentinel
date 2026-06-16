# Task 3 Runner Audit: Data Health Score Execution Path

Datum: 2026-06-16

## Vollstaendig analysierte Datei

- `bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al`

Ergebnis der Analyse:

- In `DHDeepScanRunner.Codeunit.al` gibt es keinen direkten Aufruf von `EnsureReadyForScan()`.
- In `DHDeepScanRunner.Codeunit.al` gibt es keinen direkten Aufruf von `EnsureDeepScanAllowed()`.
- In `DHDeepScanRunner.Codeunit.al` gibt es keine direkte Pruefung von `Can Run Deep Scan`.
- In `DHDeepScanRunner.Codeunit.al` gibt es keine direkte Pruefung von `Scan Credits Available`.
- In `DHDeepScanRunner.Codeunit.al` gibt es keine direkte Pruefung von `Monitoring Active`.
- Relevant waren dennoch drei indirekte Premium-/Lizenz-nahe Stellen:
  - `ProcessRun()` setzte bisher immer Deep-Scan-Headline und verwendete nach dem Sync immer `RefreshLicenseStatus()`.
  - `EnsureDashboardHeaderForDeepScan()` setzte `Premium Available` aus `Setup."Premium Enabled"`.
  - `BuildSyncPayload()` bestimmte `scan_type` bisher ueber die Headline und setzte `premium_available` aus `Setup."Premium Enabled"`.

## Gefundene Gate-Stellen ausserhalb des Runners

- `bc-extension/app/src/pages/DHSetup.Page.al`
  - Premium-Aktion `Start Premium Deep Scan` ruft `ApiClient.EnsureReadyForScan(Setup)` auf.
  - Diese Stelle bleibt unveraendert und betrifft nur Premium-Deep-Scans.
- `bc-extension/app/src/codeunits/DHDeepScanMgt.Codeunit.al`
  - `QueueDeepScan()` ruft `EnsureDeepScanAllowed(Setup)` auf.
  - `EnsureDeepScanAllowed()` fuehrt `RefreshLicenseStatus(Setup)` aus und prueft `Setup."Can Run Deep Scan"` bzw. `Setup.IsPremiumLicenseActive()`.
  - Diese Stelle bleibt fuer Premium-Deep-Scans unveraendert.
- `bc-extension/app/src/codeunits/DHApiClient.Codeunit.al`
  - `EnsureReadyForScan()` fuehrt `RefreshLicenseStatus(Setup)` aus und prueft `Setup."Can Run Deep Scan"` bzw. `IsPremiumAllowed(Setup)`.
  - Mehrere alte Quick-/API-Scan-Methoden rufen `EnsureReadyForScan()` auf. Diese Methoden wurden nicht fuer den Free-Score-Pfad verwendet.

## Anpassungen fuer separaten Data-Health-Score-Pfad

- `bc-extension/app/src/tables/DHDeepScanRun.Table.al`
  - Feld `55; "Scan Mode"; Text[30]` hinzugefuegt.
  - Zweck: Der Run speichert dauerhaft `deep` oder `data_health_score`.
  - Bestehende alte Runs ohne Wert werden im Code als `deep` behandelt.
- `bc-extension/app/src/codeunits/DHDeepScanMgt.Codeunit.al`
  - `QueueDeepScan()` setzt `DeepScanRun."Scan Mode" := 'deep'`.
  - `QueueDataHealthScore()` setzt `DeepScanRun."Scan Mode" := 'data_health_score'`.
  - `QueueDataHealthScore()` ruft weiterhin weder `EnsureDeepScanAllowed()` noch `EnsureReadyForScan()` auf und prueft nur API Base URL, Tenant ID und aktivierte Module.
- `bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al`
  - `ProcessRun()` verwendet `GetRunningHeadline()` und `GetStartedEventMessage()` anhand von `"Scan Mode"`.
  - `ProcessRun()` ruft `ApiClient.RefreshLicenseStatus(Setup)` nach dem Sync nur noch fuer Nicht-Data-Health-Score-Laeufe auf.
  - `EnsureDashboardHeaderForDeepScan()` setzt `Premium Available` ueber `IsPremiumAvailableForRun()`. Fuer `data_health_score` ist das immer `false`.
  - `BuildSyncPayload()` setzt `scan_type` ueber `GetRunScanMode()` statt ueber die Headline.
  - `BuildSyncPayload()` setzt `premium_available` ueber `IsPremiumAvailableForRun()`. Fuer `data_health_score` ist das immer `false`.
  - Neue Hilfsfunktionen:
    - `GetRunScanMode()`
    - `IsDataHealthScoreRun()`
    - `GetRunningHeadline()`
    - `GetStartedEventMessage()`
    - `IsPremiumAvailableForRun()`
- `bc-extension/app/src/codeunits/DHApiClient.Codeunit.al`
  - `UpdateScanProgress()` sendet `scan_mode` nun ueber `GetDeepScanRunMode(DeepScanRun)`.
  - Dadurch bleiben Progress-Updates fuer Free-Score-Laeufe bei `data_health_score`; alte/blanke Runs bleiben `deep`.

## Bewusst unveraendert

- Backend-Start mit `scan_mode=data_health_score` bleibt unveraendert in `StartDataHealthScore()`.
- Premium-Deep-Scan-Pfad bleibt unveraendert:
  - `Start Premium Deep Scan` -> `EnsureReadyForScan()` -> `QueueDeepScan()` -> `EnsureDeepScanAllowed()`.
- Es wurden keine Daten geloescht.
- Es wurden keine bestehenden Premium-Scans in ihrer Gate-Logik entschaerft.

## Verifikation

- Quellscan auf Gate-Begriffe:
  - `EnsureReadyForScan`
  - `EnsureDeepScanAllowed`
  - `Can Run Deep Scan`
  - `Scan Credits Available`
  - `Monitoring Active`
  - `RefreshLicenseStatus`
  - `scan_mode`
  - `scan_type`
- Ergebnis:
  - Free-Score-Aktion und `QueueDataHealthScore()` laufen ohne Credit-, Monitoring- oder Premium-Gate.
  - Runner behandelt `data_health_score` ueber `"Scan Mode"` separat.
  - Premium-Deep-Scan-Gates bleiben auf dem Premium-Pfad erhalten.

Hinweis: Ein echter AL Compiler/Package-Build wurde in dieser Umgebung nicht ausgefuehrt.
