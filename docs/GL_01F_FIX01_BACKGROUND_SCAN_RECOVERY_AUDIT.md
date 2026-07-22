# GL-01F-FIX01 – Manual Background Scan Execution & Orphan Recovery

## Analyse vor der Implementierung

### Reproduzierter Call-Flow

`DH Setup.RunScheduledScanNow` ruft `DH Scan Scheduler Mgt.RunNow()` auf. Der manuelle Pfad verwendet `StartManualScheduledScan()` und anschließend `DH Deep Scan Mgt.QueueDeepScanInNewSession()`. Nach lokaler Vorprüfung und erfolgreichem Backend-Start wird folgende Plattformfunktion aufgerufen:

```al
Session.StartSession(SessionId, Codeunit::"DH Deep Scan Runner", CompanyName(), DeepScanRun)
```

Der Parameterweg ist strukturell korrekt:

- Zielcodeunit 53128 `DH Deep Scan Runner` besitzt `TableNo = "DH Deep Scan Run"`.
- `OnRun` ruft den vorhandenen vollständigen `ProcessRun(Rec)` auf.
- `CompanyName()` übergibt den aktuellen Company-Kontext.
- Der Run-Datensatz enthält Entry No., Run-ID, Execution Token, Scan Mode und Backend-Bindung.
- Der beobachtete Zustand `Running / 0 % / Preparing scan checks` beweist, dass die Kind-Session `OnRun`, die Run-ID-Auflösung und den ersten Backend-/Heartbeat-Schritt tatsächlich erreicht.

### Root Cause

`ProcessRun()` setzt und committet zunächst lokal `Running`, ruft `TryUpdateBackendProgress(..., 'Preparing scan checks', ...)` auf und startet danach `RunChecks()`. `OnRun` besitzt jedoch keine TryFunction-/Failure-Grenze. Tritt ab diesem Punkt ein AL-Fehler auf, beendet Business Central die Kind-Session. Der bereits committete lokale und serverseitige Running-Zustand bleibt bestehen.

Der synchrone Pfad ist gegen denselben Fehler abgesichert, weil `DH Deep Scan Mgt.RunDeepScanNow()` den Runner über `TryRunDeepScan()` aufruft und anschließend `DH Deep Scan Failure.MarkRunAsFailed()` verwendet. Diese Grenze wurde beim neuen `StartSession`-Pfad nicht in die Kind-Session übernommen.

Der konkrete ursprüngliche AL-Fehlertext kann nicht ermittelt werden: Er wurde von der unbehandelten Kind-Session weder in `DH Deep Scan Run.Error Message` noch als Backend-Failure-Event gespeichert. Die letzte dauerhafte Position grenzt den Fehler auf den Eintritt in beziehungsweise die frühe Ausführung von `RunChecks()` ein; ein Parameter-, Company- oder OnRun-Problem ist durch den erreichten Running-Zustand ausgeschlossen. Der Fix speichert künftige frühe Fehler deterministisch.

### Zweite Ursache der Dauerblockade

`EnsureNoActiveScan()` prüft ausschließlich lokale `Queued`-/`Running`-Datensätze. Vor dieser Entscheidung wird der Backendstatus nicht aktualisiert. Die bestehende Backend-Recovery aus GL-EXT-P0C kann einen stale Run nach den konfigurierten Lease-/Heartbeat-Regeln requeueen, failen oder expiren; die lokale Startaktion erfährt davon jedoch erst durch einen separaten Monitor-Refresh.

### Bestehende zentrale Recovery

Das Backend verwendet unverändert:

- `SCAN_STALLED_AFTER_SECONDS`
- `SCAN_QUEUED_TIMEOUT_SECONDS`
- `SCAN_MAX_RUNTIME_SECONDS`
- `SCAN_MAX_ATTEMPTS`
- `SCAN_RETRY_BACKOFF_SECONDS`

`recover_stale_runs()` verlangt bei Running sowohl eine abgelaufene Lease als auch einen stale Heartbeat, sofern nicht das bestehende Hard-Runtime-Limit greift. Danach wird derselbe Run kontrolliert requeued oder nach maximalen Versuchen auf Failed gesetzt. Run-ID, Startrequest und Credit bleiben erhalten.

Der Statusendpunkt führt diese zentrale Recovery bereits vor seiner Antwort aus und liefert `recovery_required` für einen requeueten Run. `DH API Client.ParseScanStatusResponse()` mappt dies auf den vorhandenen lokalen Status `RetryRequired`.

## Architekturentscheidung

1. Der bestehende `DH Deep Scan Runner` erhält in seinem eigenen `OnRun` dieselbe terminale Fehlergrenze wie der synchrone Aufruf.
2. Ein abgelehnter Plattform-Sessionstart markiert den bereits akzeptierten Run unmittelbar über `DH Deep Scan Failure` als Failed und meldet den Fehler an die Action zurück. Eine Erfolgsmeldung erscheint nicht.
3. Vor der lokalen Doppelstartentscheidung werden vorhandene lokale aktive Runs über den bestehenden Statusendpunkt aktualisiert. Dadurch greift die zentrale Backend-Recovery ohne neuen Timeout und ohne direkte SQL-Korrektur.
4. Ein durch das Backend requeueter Run wird über seine bestehende Request-ID und Run-ID wiederaufgenommen; es entsteht kein zweiter Run und kein zusätzlicher Creditverbrauch.
5. Ein gesunder aktiver Run bleibt blockierend.
6. Der automatische Schedulerpfad bleibt weiterhin synchron innerhalb der bestehenden TaskScheduler-Session und wird fachlich nicht verändert.

## Auswirkungen

- Keine neue Scan Engine oder Runner-Codeunit.
- Keine Änderung an Regeln, Score, Findings, Credits, Monitoring-Frequenz oder API-Verträgen.
- Keine neuen Timeoutwerte und keine Migration.
- Free- und Validation-Dialogpfade bleiben unverändert.

## Implementierung und Prüfergebnisse

### Implementierte Reparatur

- `DH Deep Scan Runner.OnRun()` führt den vorhandenen vollständigen `ProcessRun()` innerhalb einer TryFunction-Grenze aus. Ein unbehandelter Fehler wird mit `GetLastErrorText()` übernommen und über die bestehende zentrale Failure-Codeunit terminal gespeichert.
- Der synchrone Pfad ruft `RunSynchronously()` derselben Runner-Codeunit auf. Fehler propagieren dadurch wie bisher an `DH Scan Scheduler Mgt.`; dessen bestehende Fehlerzählung und Planung werden nicht semantisch verändert.
- Liefert `Session.StartSession()` `false`, wird der bereits akzeptierte Run vor dem Action-Fehler auf Failed gesetzt. Backend-Failure wird noch mit dem gültigen Execution Token gemeldet; danach werden lokale Lease und Token freigegeben.
- Vor der lokalen Prüfung auf einen aktiven Run werden lokale Queued-/Running-Runs über `DH API Client.RefreshScanStatus()` mit dem Backend abgeglichen. Fehler beim Statusabruf geben einen Lauf nicht frei, sondern lassen ihn sicher blockierend.
- Meldet das Backend `recovery_required`, verwendet der vorhandene `FindUnacceptedRun()`-/`StartBackendScanWithRecovery()`-Pfad dieselbe Client Request ID und Run-ID weiter. Ein neuer Run oder zusätzlicher Creditpfad entsteht nicht.

### Kontext- und Parameterprüfung

- `DH Scan Dispatcher` ist nur der interaktive allgemeine Scan-Einstieg und öffnet anschließend den Monitor. Der manuelle Scheduler-Start läuft direkt über `DH Scan Scheduler Mgt.` und `DH Deep Scan Mgt.`; der Dispatcher ist nicht Ursache des Fehlers.
- `DH Scheduled Scan Runner` ruft unverändert `ExecuteScheduledRun()` auf. Der automatische Scheduler verwendet unverändert `QueueDeepScanInBackground()` und keine zweite Background Session.
- Die Background Session erhält weiterhin den aktuellen `CompanyName()` und den table-bound `DH Deep Scan Run` mit seiner Entry No. Die beobachtete erste Fortschrittsstufe schließt einen fehlenden OnRun-Eintritt oder eine verlorene Run-ID aus.
- Der Runner lädt `DH Setup` im aktiven Company-Kontext über den bestehenden Schlüssel `SETUP`; API Client, Tenant und Secret werden weiterhin durch die vorhandenen Routinen initialisiert.
- Berechtigungsmodell und Permission Sets wurden nicht geändert. Ein künftig auftretender Berechtigungs-/Setup-/Regelfehler wird jetzt als konkreter Run-Fehler persistiert, statt die Session unbemerkt zu beenden.

### Historischer exakter Fehlertext

Für den bereits verwaisten Lauf existiert kein rekonstruierbarer genauer AL-Fehlertext. Vor der Reparatur beendete sich die Kind-Session ohne persistierende Fehlergrenze; weder Run-Datensatz noch Backend-Event enthalten den ursprünglichen Fehler. Eine präzisere Behauptung wäre spekulativ. Die letzte gespeicherte Stufe lokalisiert ihn auf den Eintritt in beziehungsweise die frühe Ausführung von `RunChecks()`.

### Automatisierte Prüfung

- Neue FIX01-Vertragstests: 7 bestanden.
- Kombinierte Scan-/Lease-/Scheduler-/First-Run-Regressionssuite: 74 bestanden.
- Nach der finalen Trennung von Background- und Synchronfehlerpfad: 37 relevante Tests bestanden.
- Vollständige Backend-Suite: 337 bestanden, 7 übersprungen; nur bestehende Deprecation-Warnungen.
- `Test-GL01FFirstRunUX.ps1`: bestanden.
- AL Source Uniqueness Guard: bestanden, 89 Objektdeklarationen und ein kanonischer Source Tree.
- AL-Compiler 17.0.34.45391: 85 Dateien, 0 Fehler, 0 Warnungen.
- `git diff --check`: wird im finalen Gate ausgeführt.

### Ausstehendes Akzeptanz-Gate

Eine echte Business-Central-Sandbox steht in dieser lokalen Arbeitsumgebung nicht zur Verfügung. Der verbindliche End-to-End-Nachweis – manueller Start bleibt bedienbar, erzeugt Fortschritt, erreicht Completed und ein danach geplanter Scheduler-Lauf startet – muss deshalb nach Veröffentlichung des erzeugten Pakets in der Pilot-Sandbox durchgeführt werden. Bis zu diesem Nachweis ist der P0-Fix technisch build- und regressionstestbar, aber noch nicht formal für den Pilot freigegeben.
