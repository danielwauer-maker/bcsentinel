# GL-EXT-P0C – Terminal Scan Lifecycle, Recovery & Stale Run Protection

Stand: 16.07.2026  
Scope: ausschließlich P0-04 aus GL-EXT-AUDIT-01

## Ergebnis

P0-04 ist auf Code-, Datenbank-, automatisierter Backendtest- und AL-Compile-Ebene behoben. Jeder angenommene Run besitzt eine Recovery-Frist oder eine aktive Worker-Lease. Claims, Retry und Recovery verwenden denselben logischen Run und denselben bereits verbuchten Credit. Ein BC-Sandbox-CAT und ein echter PostgreSQL-Mehrinstanztest sind weiterhin verpflichtende externe Gates und wurden nicht als bestanden markiert.

## Ausgangsrisiko und Root Cause

Vor P0C waren Scanstatuszeilen Fortschrittsanzeigen, aber kein verbindlicher Ausführungsvertrag. Status konnten ohne Übergangsvalidierung geschrieben werden; AL konnte lokal oder im Backend vor dem konsistenten Resultat `Completed` setzen; Ausnahmen und verlorene HTTP-Antworten ließen Runs offen; `stalled` wurde nur beim Polling und ohne atomaren Claim behandelt. Es fehlten Lease, Execution Token, begrenzter Retry, Startup-/periodische Recovery und Schutz gegen einen zurückkehrenden alten Worker.

## Kanonisches Statusmodell

Persistierte kanonische Werte sind `queued`, `running`, `completed`, `completed_with_warnings`, `failed`, `cancelled` und `expired`. Die Legacy-Werte `preparing`, `finalizing`, `stalled` und `canceled` werden ausschließlich beim Lesen/Übergang normalisiert. Es wurden keine überlappenden `starting`, `processing` oder `failed_retryable`-Zustände eingeführt.

| Status | Bedeutung / Besitzer | Erlaubte Vorgänger | Erlaubte Nachfolger | terminal | maximale Dauer | BC-Verhalten | Resume | Credit / Report |
|---|---|---|---|---|---|---|---|---|
| `queued` | angenommen, noch nicht geclaimt; Backend | neu, Recovery aus `running` | `running`, `failed`, `cancelled`, `expired` | nein | 600 s Default bzw. `next_retry_at` | Queued / RetryRequired | ja, gleicher Run | keine neue Buchung; kein Report |
| `running` | Worker mit Token, Owner und Lease | `queued` | `completed`, `completed_with_warnings`, `failed`, `cancelled`, `expired` | nein | Heartbeat 900 s, Lease 1200 s, Max Runtime konfiguriert | Running mit Fortschritt | nur nach Leaseverlust und Recovery | unverändert; kein Report vor Kernresultat |
| `completed` | Pflichtresultat konsistent persistiert | `running` | nur idempotent selbst | ja | unbegrenzt | Completed | nein | verbuchter Credit bleibt; Report zulässig |
| `completed_with_warnings` | Kernresultat vollständig, nichtkritisches Postprocessing warnte | `running` | nur idempotent selbst | ja | unbegrenzt | Completed plus Warnhinweis | nein | wie Completed |
| `failed` | nicht retryfähig oder Attempts erschöpft | `queued`, `running` | nur idempotent selbst | ja | unbegrenzt | Failed, Supportreferenz | nein | keine automatische Erstattung; kein Erfolgsreport |
| `cancelled` | kontrollierter Abbruch | `queued`, `running` | nur idempotent selbst | ja | unbegrenzt | Canceled | nein | keine automatische Erstattung |
| `expired` | Queuefrist bzw. fachliche Deadline überschritten | `queued`, `running` | nur idempotent selbst | ja | unbegrenzt | Failed/Expired | nein | keine automatische Erstattung |

Ungültige und unbekannte Übergänge liefern serverseitig 409 beziehungsweise eine `InvalidScanTransitionError`; `queued→completed` ist im Kernvertrag verboten. Der authentisierte Legacy-Sync adaptiert explizit über `queued→running→completed`.

## Lease, Heartbeat und atomarer Claim

- `/scan/start` erzeugt pro Run einen zufälligen `lease_token` und eine `correlation_id`.
- Der Claim ist ein Conditional `UPDATE` auf Run-ID, Status, Lifecycle-Version und Token. Dabei werden Owner und Ablauf gesetzt sowie `execution_attempt` atomar erhöht.
- Nur der aktuelle Token darf Fortschritt, Heartbeat oder Completion schreiben. Ein zweiter Worker mit gültiger Fremd-Lease erhält 409.
- Heartbeats erneuern `heartbeat_at_utc`, `lease_expires_at_utc` und `updated_at_utc`.
- Recovery rotiert den Token. Ein alter Worker kann danach weder Fortschritt noch finales Resultat überschreiben.
- Terminale Übergänge löschen Owner und Lease. Der Execution Token wird nicht in normale Status-GET-Antworten ausgegeben; ein idempotenter Replay von `/scan/start` liefert den aktuellen Token.

## Fehler- und Retry-Policy

Fachliche Validierungs-, Authentisierungs-, Payload- und Konfigurationsfehler sind non-retryable und enden `failed`. Worker-/Queue-Unterbrechung, Lease-/Heartbeat-Verlust und klar transiente Infrastrukturfehler dürfen denselben Run erneut queueen. Unerwartete Verarbeitungsfehler werden terminal `failed`; ein Retry erfolgt nicht unbeschränkt aus einer unbekannten Exception heraus.

Defaults: maximal 3 Attempts, exponentieller Backoff ab 30 s, Queue-Timeout 600 s, Stale-Heartbeat 900 s, Lease 1200 s, Recovery alle 60 s in Batches von 100. `next_retry_at_utc` verhindert BC-/Backend-Retryschleifen. Fehler besitzen Code, kundenverständliche Meldung und Correlation ID; Stacktraces bleiben in Serverlogs.

## Recovery-Vertrag

`recover_stale_runs` läuft beim Backendstart und periodisch im FastAPI-Lifespan. Kandidaten werden über indizierte Status-/Lease-/Retryfelder, Batchlimit und `FOR UPDATE SKIP LOCKED` gelesen. Zusätzlich schützt ein Conditional Compare-and-Swap auf Status und `lifecycle_version` Datenbanken ohne wirksames `SKIP LOCKED`, insbesondere SQLite.

- stale `queued`: `expired` mit `queue_timeout`;
- stale `running` unter Max Attempts: derselbe Run zurück nach `queued`, Tokenrotation, Backoff;
- stale `running` ab Max Attempts: terminal `failed`;
- Resultat persistiert, Status nicht final: Recovery finalisiert `completed`/`completed_with_warnings`;
- `completed` ohne Pflichtresultat: kontrolliert `failed` mit `inconsistent_completed_result`;
- wiederholte oder parallele Recovery: keine zweite Mutation und kein zweites Event.

Historische `RetryRequired`-Werte sind AL-Startzustände, keine Backendstatuswerte. BC ruft denselben Start mit derselben Client Request GUID erneut auf und erhält den aktuellen Token. Es entsteht weder ein neuer Run noch eine zweite Creditbuchung.

## Resultat- und Findings-Idempotenz

`scan_issues` besitzt Unique `(scan_id, code)`, Module Unique `(run_id, name)`. Ein Sync ersetzt die Finding-Typen eines Runs transaktional und dedupliziert Codes vor dem Insert. `issues_count` bleibt das fachliche Aggregate betroffener Datensätze; Pflichtkonsistenz verlangt bei positivem Aggregate mindestens einen eindeutigen Finding-Typ und bei null keine Finding-Zeile.

`Completed` ist erst zulässig, wenn Scanheader, nichtleere Headline, nicht-`Pending` Rating und konsistente Findings innerhalb derselben Transaktion persistiert sind. Ein finaler Commitfehler rollt Resultat und Status zurück. Partial Writes erreichen nicht `Completed`.

## Report und Postprocessing

Der Kernscan wird erst nach erfolgreichem Backend-Sync lokal abgeschlossen. Kommerzielle Ableitungen, Impacts, Lizenzrefresh und Report-/sonstiges Postprocessing werden danach als Warnpfad behandelt; ein Fehler darf den bereits konsistenten Kernscan nicht wieder `running` setzen. P0C baut keine Workflow-Engine und verändert die Reportfachlichkeit nicht.

## Business Central und Scheduler

Die Deep-Scan-Tabelle speichert Execution Token, Correlation ID, Attempt und Lease-Ablauf. Start-, Fortschritts- und Sync-Payloads führen Token und stabile Client Request ID mit. Der Monitor normalisiert `completed_with_warnings` und `expired`, beendet Polling bei Terminalstatus und setzt bei Recoverybedarf `RetryRequired`.

Jede AL-Exception wird nach lokalem Commit durch `DH Deep Scan Failure` terminal erfasst und best-effort an das Backend gemeldet. Beim nächsten manuellen oder geplanten Start wird ein unakzeptierter Pending-/RetryRequired-Run vor der Creditprüfung gefunden, über denselben `/scan/start`-Request wiedergebunden und mit demselben Run fortgesetzt. Ein bewusster neuer Scan erhält weiterhin eine neue GUID. Die Schedulerplanung bleibt unabhängig vom späteren Backendstatus erhalten; stale Runs werden serverseitig recovered und blockieren nicht dauerhaft.

## Datenbankmigration 0024

Neu sind `created_at_utc`, Lease-Owner/-Token/-Ablauf, Attempt, Retry Count/Next Retry, Correlation ID, Recovery Count, Lifecycle Version, Result-Persisted-Zeit sowie strukturierte Eventfelder. Status-/Lease-/Retry- und Correlation-Indizes wurden ergänzt.

Die Migration klassifiziert historische Runs nicht automatisch um. `created_at_utc` wird sicher aus `updated_at_utc` befüllt; Attempts/Retry/Recovery starten bei null. Historische `running`-Rows bleiben `running` und werden erst anhand der konfigurierten Recoveryregeln entschieden. Historische `completed`-Rows werden nicht ohne Resultatprüfung als konsistent behauptet. Vor den neuen Unique Constraints bricht die Migration bei vorhandenen Finding-/Modulduplikaten mit einer expliziten Bereinigungsanweisung ab.

Verifiziert: frische Migration bis 0024 sowie Upgrade von 0023 mit erhaltenem historischem `running` und `completed`. Das Downgrade entfernt nur P0C-Spalten/Constraints; ein produktives Rollback nach neuen Writes ist nur als Roll-forward-/Backupentscheidung zulässig.

## Observability

Strukturierte Datenbankevents und/oder Serverlogs existieren für `scan_claimed`, `scan_started`, `scan_heartbeat`, `scan_completed`, `scan_failed`, `scan_retry_scheduled`, `scan_recovered`, `scan_expired`, `scan_lease_lost` und `late_worker_result_rejected`. Enthalten sind soweit anwendbar Run-/Tenantreferenz, Attempt, Worker, Status/Failure, Correlation und Recoverygrund. Eventtexte werden auf 255 Zeichen begrenzt und E-Mail-Adressen redigiert; Tokens und Secrets werden nicht protokolliert. Heartbeats erzeugen nur bei einem tatsächlichen Fortschrittsupdate ein Event.

## Automatisierte Tests und Verifikation

Die P0C-/Scanstatus-Suiten decken mindestens die 28 geforderten Szenarien ab: Erfolg, fachlicher und unerwarteter Fehler, Worker-Abbruch, stale Running/Queued, Leaseablauf, zweiter Worker, paralleler Claim mit echten Sessions, Late Writer, Heartbeat, idempotente Recovery, Max Attempts, Backoff, non-retryable, gleicher Credit/Run, Unique Findings, Partial/Complete Result, Postprocessing, Startup-/Polling-/Schedulerwirkung, Migration und parallele Recovery.

| Prüfung | Ergebnis |
|---|---|
| P0C + Scanstatus + P0B | fokussiert grün nach Race-Korrektur |
| vollständiges Backend-pytest | **204 bestanden**, 66 Deprecation-Warnungen, 654,79 s |
| Python `compileall` | bestanden |
| Migration frisch | bestanden |
| Migration von 0023 mit Legacy-Runs | bestanden |
| AL ReleaseCloud Compile | 81 Dateien, 0 Fehler |
| CodeCop + PerTenantExtensionCop | 0 Fehler |
| AppSourceCop | bekannte Baselinefehler AS0051 EULA/logo/help und AS0084 ID-Range; keine P0C-Regression |
| JSON / XLF | 15 JSON- und 2 XLF-Dateien erfolgreich geparst |
| Localization Check | bekannte Baseline-Gaps; fehlgeschlagen, keine P0C-spezifische neue Ursache |
| Pricing Check | bekannter Assessment-Fallback-Gap; fehlgeschlagen, keine P0C-Regression |
| `git diff --check` | bestanden; nur CRLF-Hinweise |
| PostgreSQL/Docker | nicht ausführbar; externe Verifikation offen |
| BC-Sandbox | nicht verfügbar; CATs nicht ausgeführt |

## Produktionskonfiguration

Die Variablen `SCAN_LEASE_SECONDS`, `SCAN_QUEUED_TIMEOUT_SECONDS`, `SCAN_STALLED_AFTER_SECONDS`, `SCAN_MAX_ATTEMPTS`, `SCAN_RETRY_BACKOFF_SECONDS`, `SCAN_RECOVERY_INTERVAL_SECONDS`, `SCAN_RECOVERY_BATCH_SIZE` und `SCAN_MAX_RUNTIME_SECONDS` sind vor Deployment anhand realer Laufzeiten festzulegen. Recovery-Logs, Queuealter, Attempts und Terminalfehlerrate benötigen Alarme. Mehrere Backendinstanzen setzen PostgreSQL und die Migration 0024 voraus.

## Manuelle BC-CATs – NOT_EXECUTED

Mangels Sandbox sind folgende Tests vorbereitet, aber nicht bestanden: erfolgreicher manueller Scan; Backendausfall während Running; Backendneustart; Scanexception; stale-Running-Recovery; Scheduler bei stale Run; Job-Queue-Retry; Monitor nach Recovery; Reportfehler nach Kernscan; neuer Scan nach terminalem Fehler; kein zweiter Credit; keine doppelten Findings. Pro Lauf sind Run-ID, Client Request ID, Execution Attempt, Backendstatus, Credit-/Ledgerzeile, Findingcodes und Correlation ID zu sichern.

## Bekannte Grenzen und Rollback

- SQLite kann PostgreSQL-Locks nicht vollständig abbilden; CAS-Tests sind grün, ein echter PostgreSQL-Mehrinstanz-/Restart-Test bleibt offen.
- Die AL-Logik ist kompiliert, aber nicht in einer BC-Sandbox ausgeführt.
- AppSource-Metadaten und ID-Range sind bestehende, nicht P0C-bezogene Releaseblocker.
- P0-05 Findings-Zugriffsschutz bleibt absichtlich unverändert.
- Kein automatischer Creditrefund wurde implementiert.

Rollback: periodische Recovery kann per Intervall/Deployment gestoppt werden; fachliche Runs werden nicht automatisch zurückklassifiziert. Nach Nutzung der neuen Token-/Leasefelder ist ein Schema-Downgrade nur mit Backup, Wartungsfenster und expliziter Datenentscheidung zulässig. Bevorzugt wird Roll-forward.

## Definition-of-Done-Bewertung

Alle code- und automatisiert prüfbaren P0C-Kriterien sind erfüllt: terminaler Vertrag, Deadline/Lease, atomarer Claim, Heartbeat, idempotente Recovery, begrenzter Retry, Late-Writer-Schutz, kein neuer Credit/Run, Finding-Idempotenz, Completion erst nach Pflichtresultat, entkoppeltes Postprocessing sowie BC-/Scheduler-Healing. Externe PostgreSQL- und BC-Sandbox-Gates bleiben transparent `NOT_EXECUTED`.

**P0-04 behoben: Ja (Code-/automatisierte Verifikation; externe Gates offen).**  
**Bereit für GL-EXT-P0D: Ja.**  
**P0-Fortschritt: 4 von 5 = 80 %.**  
**Produkt-Gate: NO-GO**, weil P0-05 sowie Sandbox-/Releasegates offen sind.

Commit-Vorschlag: `fix(scans): enforce terminal lifecycle and recover stale runs`
