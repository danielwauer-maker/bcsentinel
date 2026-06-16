# Task 4.2 Audit: BC Post-Run Save Error & Loss Sync Fix

Datum: 2026-06-16

## Root Cause Fehler 1: Stale DH Setup Record nach Free Score

Der Fehler trat nach Abschluss von `Start Free Data Health Score` auf.

Gefundener Ablauf:

1. `DHSetup.Page.al` erzeugte eine lokale Kopie:
   - `Setup := Rec`
2. `DeepScanMgt.QueueDataHealthScore(Setup)` startete den Scan synchron.
3. Der Scan lief durch Runner, Backend-Start, Progress und finalen Sync.
4. Danach schrieb die Page auf dem alten Page-Record:
   - `Rec."Data Health Score Completed" := true`
   - `Rec."Can Run Data Health Score" := false`
   - `Rec.Modify(true)`
5. Wenn der Setup-Datensatz waehrend des laengeren Scanablaufs neu gelesen/angepasst wurde, war der Page-`Rec` nicht mehr aktuell.
6. Business Central meldete deshalb einen stale record fuer Primary Key `SETUP`.

Fix:

- Vor dem post-run `Rec.Modify(true)` wird `Rec.Get('SETUP')` ausgefuehrt.
- Dadurch schreibt die Page auf dem aktuellen `DH Setup`-Datensatz.
- Danach bleiben `UpdateActionState()` und `CurrPage.Update(false)` erhalten.

Geaenderte Stelle:

- `bc-extension/app/src/pages/DHSetup.Page.al`
  - Nach `QueueDataHealthScore(Setup)` wird `Rec.Get('SETUP')` ausgefuehrt, bevor lokale Completion-Flags gespeichert werden.

## Root Cause Fehler 2: Loss EUR in BC Scan-History blieb 0

Die BC Scan-History `DH Deep Scan Runs` liest nicht direkt `DH Deep Scan Run`, sondern `DH Scan Header`.

Gefundener Ablauf:

1. Der Runner berechnet Score/Checks/Issues lokal.
2. `ClearDeepScanCommercials()` setzt vor dem Backend-Sync lokale Commercials auf 0:
   - `Estimated Loss (EUR)`
   - `Potential Saving (EUR)`
3. `EnsureDashboardHeaderForDeepScan()` schrieb vor dem finalen Backend-Sync einen Header mit diesen 0-Commercials.
4. Danach sendete `BuildSyncPayload()` die Ergebnisse an `/scan/sync`.
5. `ApplySyncCommercials()` uebernahm die Backend-Response:
   - `estimated_loss_eur`
   - `potential_saving_eur`
   - `total_records`
   - `estimated_premium_price_monthly`
   - `roi_eur`
6. Der Header wurde dort zwar teilweise aktualisiert, der finale History-Header wurde aber nicht nochmals vollstaendig aus dem aktualisierten Run geschrieben.

Fix:

- Nach `ApplySyncCommercials()` und `ApplySyncFindingImpacts()` ruft der Runner erneut `EnsureDashboardHeaderForDeepScan(DeepScanRun)` auf.
- Danach wird committed.
- Dadurch landen die finalen Run-Werte zuverlaessig im `DH Scan Header`, den die Scan-History anzeigt.

Geaenderte Stelle:

- `bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al`
  - Nach finaler Sync-Response wird der Scan Header erneut vollstaendig aus `DeepScanRun` aktualisiert.

## Geaenderte Dateien

- `bc-extension/app/src/pages/DHSetup.Page.al`
- `bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al`
- `docs/TASK_4_2_BC_POST_RUN_SAVE_AND_LOSS_SYNC_FIX_AUDIT.md`

Keine Backend-, Stripe-, Docker-, Deployment-, Mail- oder Login-Dateien wurden geaendert.

## Angepasste Modify-/Refresh-Stellen

- `DHSetup.Page.al`
  - Angepasst:
    - Nach `QueueDataHealthScore(Setup)` jetzt `Rec.Get('SETUP')` vor `Rec.Modify(true)`.
  - Unveraendert:
    - `ResetLocalRegistrationState()` nutzt weiter `Rec.Modify(true)`, aber ohne langen Scanlauf dazwischen.
    - `EnsureSetupExists()` nutzt weiter `Rec.Modify(true)` fuer Setup-Defaults.
    - `RefreshLicenseStatus(Rec)` in Register/Refresh Product Access bleibt unveraendert.
- `DHApiClient.Codeunit.al`
  - Keine Aenderung in diesem Task.
  - Relevante `Setup.Modify(true)`-Stellen wurden geprueft:
    - Registrierung,
    - License Refresh,
    - Setup URL Normalisierung.
- `DHDeepScanMgt.Codeunit.al`
  - `QueueDataHealthScore()` wurde geprueft und nicht geaendert.
- `DHDeepScanRunner.Codeunit.al`
  - Keine Licensing-/Premium-Gates geaendert.
  - Nur finaler Header-Refresh nach Commercial-Sync ergaenzt.

## Loss / Potential Saving Sync

Finale Werte werden jetzt so uebernommen:

1. Backend Sync Response wird in `ApplySyncCommercials()` gelesen.
2. Werte werden auf `DH Deep Scan Run` gesetzt:
   - `Estimated Loss (EUR)`
   - `Potential Saving (EUR)`
   - `Total Records`
   - `Est. Premium Price`
   - `ROI`
3. `ApplySyncCommercials()` aktualisiert weiterhin die Commercial-Felder im `DH Scan Header`.
4. Zusaetzlich ruft der Runner danach `EnsureDashboardHeaderForDeepScan(DeepScanRun)` auf.
5. Dadurch werden auch `Data Score`, Checks, Issues, Modulwerte, Records, Loss, Saving und ROI final synchron in den History-Header geschrieben.

## Verifikation

- Statische Quellpruefung:
  - Suche nach `Setup.Modify(true)`, `Rec.Modify(true)`, `RefreshLicenseStatus`, `QueueDataHealthScore`, `CurrPage.Update(false)`.
  - Suche nach Commercial-Feldern in Runner, Mgt, Run- und Header-Tabellen.
  - Suche nach `EnsureDashboardHeaderForDeepScan(DeepScanRun)`.
- Ergebnis:
  - Free-Score post-run Page-Speicherung laedt nun aktuellen Setup-Datensatz.
  - Header wird nach finalem Backend-Commercial-Sync erneut geschrieben.
  - Premium-Gates und Premium Deep Scan wurden nicht veraendert.
- AL Compile:
  - Kein lokaler `alc.exe` wurde gefunden.
  - Ein echter AL Package Build wurde daher nicht ausgefuehrt.

## Offene Punkte

- In der Business-Central-Entwicklungsumgebung sollte ein echter AL Compile/Package Build ausgefuehrt werden.
- Falls Loss EUR trotz finalem Header-Refresh weiter 0 bleibt, sollte die konkrete Sync-Response in BC geloggt/geprueft werden, insbesondere ob `commercials.estimated_loss_eur` im Response-Body vorhanden ist.
- Mail/Passwort/Login bleibt unveraendert Folge-Task.
