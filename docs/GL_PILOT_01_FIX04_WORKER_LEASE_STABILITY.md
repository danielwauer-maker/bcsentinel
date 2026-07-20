# GL-PILOT-01-FIX04 – Worker Lease Stability and Scan Sync Recovery

Stand: 21. Juli 2026  
Pilot: `BCSentinel-Pilot`, Business Central 28.3  
Betroffener Run: `RUN_20260721_000001_1900DB01735748078C3E9C4EE599F`  
Extension nach Fix: `1.0.2.10`

## Ergebnis

FIX04 stabilisiert die Ausführungslease für synchrone Business-Central-Scans, ohne Token-, Worker- oder Tenantprüfung zu lockern. Eine noch gültige Lease wird nicht mehr allein wegen eines älteren Heartbeats rotiert. Standardlease und Heartbeat-Stale-Fenster betragen vier Stunden; nach sechs Stunden greift weiterhin die harte maximale Laufzeit. Jeder erfolgreiche Status-Call erneuert die Lease mit Serverzeit.

Bekannte Lease-Konflikte liefern stabile strukturierte Codes. BC zeigt dafür genau eine lokalisierte Meldung, beendet weitere Statusversuche und bewahrt lokale Ergebnisse. Lokaler Ausführungsstatus und Backend-Synchronisierungsstatus sind getrennt: Ein lokal abgeschlossener Scan mit fehlgeschlagener Synchronisierung bleibt `Completed` und wird als `Completed; sync failed` beziehungsweise `Scan completed locally; backend synchronization failed` angezeigt.

Automatisierte Tests und Compile-Gates sind grün. Der reale Post-Fix-CAT ist noch offen; deshalb bleibt das Pilot-Gate **NO-GO**.

## Reproduktion und Timeline

1. BC erzeugt den global eindeutigen Run und sendet `/scan/start`.
2. Ein erster Startversuch liefert 409; der zweite wird mit HTTP 200 akzeptiert.
3. Der akzeptierte Start liefert Execution Token und Correlation-ID. BC speichert sie vor Beginn der Scanberechnung.
4. Der erste `/scan/status/update` claimt den queued Run mit der stabilen Worker-ID aus der Client-Request-ID und setzt die Lease.
5. BC arbeitet danach synchron innerhalb eines Moduls. Während dieser Zeit kann dieselbe AL-Session keinen parallelen Heartbeat senden.
6. Die periodische Backend-Recovery sah den älteren Heartbeat nach 15 Minuten als stale an, obwohl die Lease auf 20 Minuten ausgestellt war, setzte den Run zurück auf queued und rotierte das Token.
7. Alle folgenden Calls verwendeten korrekt das in BC gespeicherte, nun aber absichtlich invalidierte alte Token und erhielten 409. `/scan/sync` wurde ebenfalls abgewiesen.

Die beobachtete Meldung `The scan execution token is no longer current` entsteht exakt im queued-Claim-Pfad nach einer Recovery-Tokenrotation. Normale Statusupdates selbst rotieren das Token nicht.

## Root Cause

Die primäre Ursache war eine Inkonsistenz zwischen dem synchronen BC-Ausführungsmodell und der Backend-Recovery:

- BC sendete Heartbeats nur vor/nach Modulen, nicht während eines lang laufenden Moduls.
- `SCAN_STALLED_AFTER_SECONDS` betrug 900 Sekunden.
- `SCAN_LEASE_SECONDS` betrug 1200 Sekunden.
- Recovery verwendete `lease_expired OR heartbeat_stale` und konnte daher bereits vor Ablauf einer gültigen Lease requeue und rotieren.
- BC verwendete danach weiterhin korrekt sein ursprünglich akzeptiertes Token; gelesen oder formatiert wurde es nicht falsch.

Zusätzlich waren Lease-Konflikte nur unstrukturierte `detail`-Texte. AL behandelte Statusfehler über TryFunction zwar als nichtfatal, versuchte aber bei jedem weiteren Modul erneut. Der abschließende Sync-Fehler lief in den allgemeinen Scan-Failure-Handler und schrieb einen lokal vollständig berechneten Scan in der Historie als fehlgeschlagen um.

Bei der Tenant-Prüfung wurde außerdem geschlossen, dass `update_scan_progress` einen bestehenden Run vor der Mutation nicht explizit gegen den übergebenen Tenant verglich. Diese Prüfung erfolgt nun vor jeder Statusmutation.

## Korrigierter Lifecycle

### Start und Eigentum

- `/scan/start` liefert `execution_token`, `worker_id` und `correlation_id` konsistent.
- `worker_id` entspricht der stabilen Client-Request-ID.
- BC validiert die zurückgegebene Worker-ID.
- Ein erfolgreicher Start überschreibt Execution Token und Correlation-ID und committet sie vor dem Scanlauf.
- Ein idempotenter Start-Retry liefert die aktuell gültige Lease und verbraucht keinen zweiten Credit.

### Lease und Recovery

- Lease und Stale-Fenster: 14.400 Sekunden.
- Harte maximale Laufzeit: 21.600 Sekunden.
- Alle Zeitvergleiche verwenden Backend-UTC/Serverzeit.
- Statusupdates erneuern Heartbeat und Lease.
- Ein alter Heartbeat allein rotiert keine noch gültige Lease.
- Erst abgelaufene Lease plus stale Heartbeat oder die harte maximale Laufzeit lösen Recovery aus.
- Nach kontrollierter Recovery bleibt das alte Token ungültig.

### Strukturierte Konflikte

- `scan_execution_token_stale`
- `scan_execution_lease_expired`
- `scan_worker_mismatch`
- `scan_execution_not_owned`

Die 409-Antwort enthält `code`, englische Fallbackmeldung, `message_de` und einen nicht-sensitiven Retry-Hinweis. Authentifizierung, Tenant-Header und Workerprüfung bleiben vorgeschaltet.

### Business Central Statusmodell

- `Status`: lokale Scanberechnung (`Queued`, `Running`, `Completed`, `Failed`).
- `Backend Sync Status`: `NotStarted`, `Pending`, `Synchronized`, `Failed`, `RetryRequired`.
- `Backend Sync Error`: lokalisierte, handlungsorientierte Synchronisierungsmeldung.

Bei einem terminalen Lease-Konflikt:

- keine weiteren automatischen Statusupdates,
- kein zusätzlicher generischer Technikfehler,
- lokale Findings und Score bleiben erhalten,
- lokaler Status bleibt `Completed`, wenn die Berechnung beendet wurde,
- Historie zeigt `Completed; sync failed`,
- Dashboard bleibt gesperrt, bis das Backend ein vollständiges Ergebnis akzeptiert und der Access Snapshot Zugriff erlaubt.

## Datenbank und Migration

- Alembic-Migration: **Nein**.
- Backend-Schema: unverändert.
- Credit- und Ledger-Semantik: unverändert.
- BC-Schema: zwei neue Felder am Ende von `DH Deep Scan Run`; Extension-Upgrade erforderlich.
- App-Version: `1.0.2.10`.

Die lokal erreichbare Compose-Datenbank ist nicht autoritativ: Revision `0021_dashboard_users`, Pilot-Run nicht vorhanden. Die autoritative Revision 0025 konnte nicht abgefragt werden. Kein Pilotdatensatz wurde gelöscht oder verändert.

Der bestehende fehlgeschlagene Pilot-Run bleibt Diagnoseevidenz und darf nicht als erfolgreicher Post-Fix-CAT umgedeutet werden. Eine spätere kontrollierte Reparatur wäre nur mit gültiger aktueller Lease und explizitem Sync zulässig; sie erfolgt nicht automatisch.

## Automatisierte Verifikation

| Prüfung | Ergebnis |
|---|---|
| FIX04 Backend Lease-/Sync-Tests | 6/6 PASS |
| FIX04 Source Contracts | 5/5 PASS |
| P0C Lifecycle + P0B Atomic Credit | PASS |
| Python `compileall` | PASS |
| AL ReleaseCloud Compile | PASS, 84 Dateien |
| AL Localization Audit | PASS |
| XLF-Parsing | PASS |
| CodeCop/PTECop | Abschlusslauf ausstehend |
| vollständige Backend-Suite | Abschlusslauf ausstehend |
| `git diff --check` | Abschlusslauf ausstehend |
| realer Sandbox-CAT | nicht ausgeführt |

## Manuelle Deployment-Schritte

1. Pilot-Datenbank sichern und Revision 0025 bestätigen.
2. Den bestehenden Pilot-Run read-only inklusive Runstatus, Token-Fingerprint, Leasezeiten, Worker, Correlation-ID, Request und Ledger dokumentieren.
3. Backend-FIX04 bereitstellen; keine Alembic-Migration ausführen.
4. Effektive Werte für Lease 14.400, Stale-Fenster 14.400 und Max Runtime 21.600 Sekunden kontrollieren.
5. Extension 1.0.2.10 als Upgrade publishen/installieren, nicht deinstallieren.
6. Upgrade und Berechtigungen prüfen; keine Pilotdaten löschen.

## Manueller Post-Fix-CAT

1. Den fehlgeschlagenen alten Run nicht als erfolgreichen CAT wiederverwenden.
2. Genau einen neuen freien oder autorisierten Scan starten.
3. `/scan/start` muss einmal HTTP 200 liefern; Token-/Worker-/Correlation-ID-Fingerprints dokumentieren.
4. Jeder `/scan/status/update` muss HTTP 200 liefern und dieselbe Ownership verwenden.
5. Während eines langen Moduls prüfen, dass kein `scan_retry_scheduled` oder `late_worker_result_rejected` entsteht.
6. `/scan/sync` muss HTTP 200 liefern.
7. Backend-Run muss `completed` mit Ergebniszeitpunkt erreichen.
8. BC Monitor und Historie müssen beide lokale Completion plus `Synchronized` zeigen.
9. Access Snapshot aktualisieren; Dashboard darf erst danach freigeschaltet werden.
10. Dashboard öffnen und Scan/Findings prüfen.
11. Genau einen Creditverbrauch und genau ein Ledger-Ereignis nachweisen.
12. Negativtests mit falschem Token, Worker und Tenant müssen strukturierte 409 liefern.

## Verbleibende Risiken und Entscheidung

- Autoritative Pilot-DB-Evidenz ist offen.
- Reale Laufzeit eines großen BC-Tenants muss gegen Vier-/Sechs-Stunden-Grenzen gemessen werden.
- Sandbox-Upgrade und Post-Fix-CAT sind offen.
- Bestehender Pilot-Run benötigt keine automatische Mutation; eine optionale Reparatur ist separat zu autorisieren.

Entscheidung: **NO-GO**, bis vollständige Regression, Sandbox-Upgrade und alle zwölf CAT-Schritte PASS sind.

Commit-Vorschlag: `fix(scan): keep BC worker lease stable and separate sync failures`
