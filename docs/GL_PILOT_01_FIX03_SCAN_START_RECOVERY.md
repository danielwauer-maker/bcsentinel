# GL-PILOT-01-FIX03 – Scan Start Idempotency Recovery and BC Busy-State Cleanup

Stand: 20. Juli 2026  
Zielumgebung: `BCSentinel-Pilot`, Business Central 28.3  
Extension-Version nach Fix: `1.0.2.9`

## Ergebnis

Der Scanstart verwendet künftig eine global kollisionsfeste, weiterhin lesbare Run-ID und behält pro lokalem Run dieselbe Client-Request-ID über alle sicheren Wiederholungen. Das Backend übernimmt nur einen streng nachgewiesenen, noch leeren Same-Tenant-Pending-Orphan. Fremd-Tenant-Scans, bereits gebundene Scan-IDs und fachlich befüllte Scans bleiben kontrollierte 409-Konflikte. Ein terminaler 4xx-/409-Startkonflikt beendet den lokalen BC-Run mit `Failed/Rejected`, `Finished At`, leerem Heartbeat und ohne weitere automatische Polling-/Retry-Auswahl.

Der Dashboard-Zugriffsfehler wird in einer TryFunction aufgefangen, der LastError kontrolliert übernommen und genau einmal als lokalisierte Nachricht angezeigt. Die Action endet danach normal, wodurch der automatische BC-Busy-Dialog freigegeben wird.

Der Post-Fix-CAT ist noch nicht ausgeführt. Das Pilot-Gate bleibt deshalb **NO-GO**.

## Ausgangsfehler

- lokaler Run: `RUN_20260720_000001`
- Tenant: `ten_47ca6ef7cc4f`
- `POST /scan/start`: HTTP 409
- Backenddetail: `scan_id already exists and is not bound to this client request.`
- lokaler Zustand blieb `Queued / Preparing / Waiting for backend status / 0 %`
- Dashboard-Ablehnung zeigte die richtige Meldung, ließ danach aber den modalen Dialog „Wird bearbeitet …“ sichtbar

## Root Cause

`DH Run ID Mgt.` erzeugte IDs ausschließlich aus Datum und einem lokalen Tageszähler:

`RUN_<YYYYMMDD>_<000001>`

Der Zähler lebt im lokalen BC-Setup. Jede frische Installation, Company oder Umgebung kann daher am selben Tag wieder `000001` erzeugen. Im Backend sind dagegen folgende Schlüssel global eindeutig:

- `scans.scan_id`
- `scan_start_requests.scan_id`
- `scan_run_statuses.run_id`

Der beobachtete erste Pilot-Run kollidierte somit mit einer bereits global vorhandenen Scan-ID. Die neue Client-Request-ID konnte nicht zur bestehenden fremden oder ungebundenen Scan-Zeile gehören und wurde korrekt abgewiesen. Die Atomic-Credit-Härtung war nicht die Ursache und darf nicht gelockert werden.

Der AL-Fehlerpfad klassifizierte den bekannten 409 nicht fachlich und setzte `Start Request Status` nur auf `RetryRequired`. Dadurch blieb der lokale Run nichtterminal und wurde erneut als wartend/pollbar dargestellt.

## Datenbankuntersuchung

Die im Workspace erreichbare lokale Compose-Datenbank ist nicht die autoritative Pilot-Datenbank: Sie steht auf Revision `0021_dashboard_users`, besitzt keine `scan_start_requests`- oder Credit-Ledger-Tabelle und enthält `RUN_20260720_000001` nicht. Sie wurde ausschließlich read-only geprüft und nicht verändert. Der Pilot-Datensatz wurde weder gelöscht noch adoptiert.

Vor dem manuellen Retest sind auf der tatsächlichen Revision 0025 ohne personenbezogene Daten zu erfassen:

1. `scans`: `scan_id`, `tenant_id`, `scan_type`, Status-/Zählerfelder
2. `scan_start_requests`: Bindung aus Tenant, Client-Request-ID, Payload-Hash und Scan-ID
3. `scan_run_statuses`: Tenant, Company, Environment, Status, Lease und Ergebniszeitpunkt
4. `credit_ledger_entries`: Operation, Scan-ID und Credit-ID

## Korrektur

### Globale Run-ID

Neue Form:

`RUN_<YYYYMMDD>_<lokaler Zähler>_<29 GUID-Hexzeichen>`

Die ID bleibt unter 50 Zeichen, lesbar und praktisch global eindeutig. Die Client-Request-ID wird weiterhin genau einmal beim lokalen Run erzeugt und bei Retry unverändert wiederverwendet.

### Backend-Recovery

Ein vorhandener Scan ohne Request-Bindung wird nur übernommen, wenn sämtliche Bedingungen gelten:

- identischer Tenant; damit identische stabile Company-Registrierung
- keine vorhandene `ScanStartRequest`-Bindung
- kein Credit-Ledger-Eintrag für die Scan-ID
- keine vorhandene Issue-Zeile, auch wenn der denormalisierte Issue-Zähler 0 ist
- passender Scanmodus
- Score, Checks und Issues jeweils 0
- Rating `Pending`
- optionaler Lifecycle gehört demselben Tenant, ist `queued`, hat kein Ergebnis und keinen Lease-Owner
- gespeicherte Company/Environment stimmen, sofern vorhanden

Ein isolierter Lifecycle ohne zugehörige Scan-Zeile wird nicht adoptiert: bei fremdem Tenant entsteht `SCAN_ID_TENANT_CONFLICT`, andernfalls `SCAN_ID_CONFLICT`.

Request-Bindung, Credit-Claim, Lifecycle und Ledger entstehen danach in derselben bestehenden Transaktion. Bei Fehlern wird vollständig zurückgerollt. Es gibt keine automatische Erstattung nach einer durabel akzeptierten Starttransaktion.

### Konfliktcodes

- `SCAN_ID_TENANT_CONFLICT`
- `SCAN_ID_REQUEST_CONFLICT`
- `SCAN_ID_CONFLICT`
- `SCAN_REQUEST_PAYLOAD_CONFLICT`
- `FREE_SCAN_ALREADY_USED`

Die 409-Antwort enthält `code`, englische Fallbackmeldung, `message_de` und nicht-sensitive Details. Authentifizierung, Tenant-Header und Tenant-Match bleiben unverändert vorgeschaltet.

### Lokaler Terminalzustand

Bei terminalem 4xx-/409-Startfehler:

- `Start Request Status = Rejected`
- `Status = Failed`
- `Finished At` gesetzt
- `Backend Status = rejected`
- `Current Step = Scan start rejected`
- `Last Heartbeat` geleert
- lokalisierte, handlungsorientierte Fehlermeldung
- keine Auswahl durch `FindUnacceptedRun`, kein automatischer Retry und kein Polling als aktiver Run

Netzwerk-, unvollständige 2xx- und 5xx-Fehler bleiben `RetryRequired`; dieselbe Client-Request-ID wird wiederverwendet.

## Datenbank- und Versionsauswirkung

- neue Alembic-Migration: **Nein**
- Backend-Schemaänderung: **Nein**
- Credit-/Ledger-Semantik: **unverändert**
- BC-Tabellenschema: Optionswert `Rejected` wurde am Ende ergänzt; bestehende Werte bleiben stabil
- BC-App-Version: **Ja, 1.0.2.9**, damit die Sandbox das neue Paket als Upgrade akzeptiert

## Automatisierte Verifikation

| Prüfung | Ergebnis |
|---|---|
| Python `compileall` | PASS |
| FIX03 AL-/Backend-Source-Contracts | 7/7 PASS über dependency-freie lokale Ausführung |
| AL Localization Checker | PASS |
| ReleaseCloud Compile | PASS, 84 Dateien |
| CodeCop/PTECop | PASS, 0 Fehler; 334 bestehende Hinweise |
| AppSourceCop | FAIL/BLOCKER (bekannte Baseline): 3 × AS0051, 1 × AS0084; zusätzlich 1 × AS0092 Warning |
| XLF/JSON Parsing | PASS |
| AL Source Uniqueness | PASS, 88 Objektdeklarationen und ein kanonischer Source-Baum |
| `git diff --check` | PASS; nur CRLF-Konvertierungshinweise |
| fokussierte Backend-Verhaltenstests | erstellt; Ausführung BLOCKED, da Docker-Freigabe am Nutzungslimit abgelehnt und lokale Python-Laufzeit keine pytest/SQLAlchemy-Abhängigkeiten enthält |
| vollständige Backend-Regressionssuite | BLOCKED aus demselben Infrastrukturgrund; letzte Vor-FIX03-Baseline 275 PASS / 7 SKIP |
| Post-Fix-Sandbox-CAT | BLOCKED / nicht ausgeführt |

Der abgelehnte Docker-Aufruf ist kein Test-FAIL. Ein gleichwertiger lokaler Backendlauf war mangels installierter Abhängigkeiten nicht möglich. Vor Pilot-GO müssen die neu erstellten Backendtests und die Gesamtsuite nachgeholt werden.

## CAT-PILOT-SCAN-START

- **Initial state:** Registrierung und Membership erfolgreich; Access Snapshot HTTP 200; kostenloser Scan verfügbar.
- **Reproduction:** erster lokaler Run `RUN_20260720_000001`; `POST /scan/start` HTTP 409; lokaler Run bleibt queued.
- **Root cause:** lokal wiederverwendbare Tageszähler-ID kollidiert mit global eindeutigem Backend-Schlüssel.
- **Fix:** GUID-gestützte Run-ID, stabile Request-ID, strukturierte Konflikte, streng beweisbare Orphan-Recovery, terminaler BC-Reject-State.
- **Expected result:** erster neue Run wird einmal akzeptiert; identischer Retry ist idempotent; Credit/Ledger genau einmal; Konflikt endet lokal terminal.
- **Actual result:** vor Fix FAIL; Post-Fix-CAT noch nicht ausgeführt.
- **Status:** **BLOCKED – automatisierter Code-/Compile-Nachweis grün, Runtime-CAT offen.**

## CAT-PILOT-DASHBOARD-BUSY

- **Initial state:** Dashboard-Zugriff absichtlich nicht verfügbar.
- **Reproduction:** Zugriffsmeldung wird bestätigt; „Wird bearbeitet …“ bleibt stehen.
- **Root cause:** AccessGuard-Error verließ die Action als Fehler, statt den bekannten Zugriffspfad normal nach genau einer Meldung zu beenden.
- **Fix:** `TryEnsureDashboardAccess`, `ClearLastError`, eine `Message`, danach normaler `exit` in allen drei externen Dashboard-Actions.
- **Expected result:** eine lokalisierte Meldung, Busy-State endet, Page ist sofort bedienbar.
- **Actual result:** vor Fix FAIL; Post-Fix-CAT noch nicht ausgeführt.
- **Status:** **BLOCKED – Source-Contract und Compile PASS, realer Client-CAT offen.**

## Manueller Post-Fix-CAT

1. Autoritative Pilot-DB sichern und den bestehenden kollidierenden Run read-only über die vier genannten Tabellen dokumentieren; nicht löschen.
2. Backend-Code bereitstellen; keine Migration ausführen.
3. Extension 1.0.2.9 als Upgrade publishen/installieren, nicht deinstallieren.
4. Bestehenden lokalen `RUN_20260720_000001` erneut starten: kontrollierte Meldung; lokaler Run muss `Failed/Rejected`, `Finished At` und keinen Heartbeat zeigen.
5. Scan erneut starten: neue GUID-gestützte Run-ID, HTTP 200, genau eine Request-Bindung und genau ein Credit-/Ledger-Ereignis.
6. Denselben akzeptierten Request transportseitig wiederholen: HTTP 200 mit `idempotent_replay=true`, kein zweiter Credit.
7. Dieselbe Scan-ID mit anderer Request-ID sowie fremdem Tenant testen: strukturierter 409, keine neue Bindung und kein Creditverbrauch.
8. Polling/Monitor beobachten: terminal abgelehnter Run bleibt terminal und wird nicht automatisch wieder gestartet.
9. Dashboardzugriff absichtlich entziehen, Action in Setup, Scan Monitor und Analytics Page ausführen: genau eine DE-/EN-Meldung, kein verbleibender Busy-Dialog.
10. Request IDs, anonymisierte Tabellenzählungen, Screenshots und tatsächliche Ergebnisse dokumentieren.

## Entscheidung

**NO-GO** für die Fortsetzung des Pilot-Gates, bis fokussierte Backendtests, Backend-Gesamtsuite und beide Sandbox-CATs PASS sind. Der Code ist bereit für diese Verifikation; weder Deployment noch Commit wurden ausgeführt.

Commit-Vorschlag: `fix(scan): recover idempotent starts and close rejected BC runs`
