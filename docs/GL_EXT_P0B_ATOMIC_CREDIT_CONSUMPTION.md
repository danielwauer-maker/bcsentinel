# GL-EXT-P0B – Atomic Credit Consumption & Idempotent Scan Charging

Stand: 16.07.2026  
Scope: ausschließlich P0-03

## Ergebnis

P0-03 ist auf Code- und automatisierter Testebene behoben. Ein bezahlter logischer Scanstart erzeugt in einer Datenbanktransaktion genau einen Scan, genau eine Credit-Zuordnung und genau einen `SCAN_CONSUMED`-Ledger-Eintrag. Wiederholungen mit derselben tenantgebundenen Request-ID liefern dasselbe Ergebnis. Das Produkt-Gate bleibt wegen P0-04, P0-05 und fehlender BC-/PostgreSQL-Staging-Abnahme **NO-GO**.

## Ausgangsrisiko und Root Cause

Der bisherige Startpfad führte nacheinander `Creditanzahl lesen → Scan anlegen → Credit verbrauchen` aus. Mehrere Sessions konnten denselben verfügbaren Bestand sehen. Die Scan-ID begrenzte zwar einzelne Duplikate, war aber kein tenantgebundener Idempotency-Vertrag zwischen AL und Backend. Bei Timeout oder verlorener Antwort konnte AL einen neuen logischen Start erzeugen. Der Legacy-Syncpfad besaß eine zweite, ebenfalls nicht atomare Verbrauchslogik.

## Fachliches Credit-Modell

| Scanart | Zugriff | Creditbewegung |
|---|---|---|
| Assessment | verfügbarer `full_analysis`-/Assessment-Credit | exakt `-1` |
| Validation | verfügbarer `validation_check`-Credit | exakt `-1`; kein Assessment-Fallback |
| Monitoring | aktive Monthly-/Annual-Subscription oder explizites aktives Monitoring-Entitlement | keine |
| Data Health Score | einmaliger Free-Slot je Tenant | keine |
| Legacy `deep` | Monitoring, falls aktiv; sonst ältester verfügbarer One-time-Credit | wie aufgelöster Zugriff |

Monitoring schaltet Assessment oder Validation nicht kostenlos frei. Admin-/Testzugriff bleibt nur über bestehende geschützte Admin-/Testpfade möglich; der Kundenendpunkt hat keinen Bypass-Parameter.

Ein Credit gilt als verbraucht, sobald der neue logische Scan dauerhaft angenommen wurde. Idempotency-Record, Credit-Claim, Scan, Queue-Status und Ledger werden gemeinsam committed. Ein Fehler davor rollt alles zurück. Ein späterer Laufzeitfehler erstattet nicht automatisch; Refunds bleiben eine explizite fachliche Operation und gehören nicht zu P0B.

## Idempotency Contract

`Idempotency Scope = Tenant Identity + Client Scan Request ID`

- AL erzeugt eine GUID einmal je bewusst neuem logischem Start und speichert sie vor dem HTTP-Aufruf.
- Backend normalisiert und validiert die GUID und speichert sie in `scan_start_requests`.
- Ein SHA-256-Hash bindet den Key an Run-ID, normalisierten Modus, Modulzahl, Company und Environment.
- Identischer Retry liefert dieselbe Scan-ID und `idempotent_replay=true`.
- Derselbe Key mit verändertem Payload liefert HTTP 409 ohne neue Buchung.
- Derselbe GUID-Wert darf bei einem anderen Tenant verwendet werden; er erhält dort einen getrennten Scope.
- Legacy-Clients ohne Key erhalten deterministisch UUIDv5 aus Tenant und Run-ID. Auch `/scan/sync` führt bezahlte Starts durch denselben atomaren Service.

## Transaktionsgrenze

`accept_scan_start()` führt in einer SQLAlchemy-Session aus:

1. authentisierten Tenant und Produktzugriff prüfen;
2. vorhandenen Idempotency-Record prüfen oder neuen Record flushen;
3. passenden Credit mit `SELECT … FOR UPDATE SKIP LOCKED` auswählen;
4. ihn zusätzlich per bedingtem `UPDATE … WHERE status='available'` claimen;
5. Scan und `ScanRunStatus` anlegen;
6. `SCAN_CONSUMED` mit Request, Scan, Credit und Kauf verknüpfen;
7. Request auf `accepted` setzen und gemeinsam committen.

Unique Constraints auf `(tenant_id, client_request_id)`, `scan_id`, `(tenant_id, free_scan_slot)`, `consumed_scan_id`, `(scan_start_request_id, operation_type)` und `(scan_id, operation_type)` bilden die letzte Datenbankbarriere. `IntegrityError` wird zurückgerollt; ein inzwischen committeter identischer Request wird anschließend als Replay gelesen. SQL-/Constraint-Details werden nicht an Kunden ausgegeben.

## Credit Ledger und Datenmodell

Neue Tabelle `scan_start_requests`:

- Tenant, Client Request ID, Payload-Hash und Scan-ID;
- angeforderter Modus, aufgelöstes Produkt, optionaler Credit;
- Free-Slot, Status und Zeitstempel.

Neue append-only Tabelle `credit_ledger_entries`:

- Tenant, Credit, Kauf, Startrequest, Scan und Produkt;
- Operation, Betrag, optionaler Bestand danach, Grund, optionale Metadaten und Zeitstempel.

Verwendete Operationen sind `PURCHASE_GRANTED`, `SCAN_CONSUMED`, `MANUAL_ADJUSTMENT` und `MIGRATION`; das Schema lässt explizite spätere `REFUND`-Buchungen zu. Grants und Admin-Entnahmen/-Resets schreiben jetzt Ledger-Einträge. Das Ledger enthält keine Tokens, Secrets oder personenbezogenen Daten. Die bestehende Creditzeile bleibt der operative Einzel-Credit; es gibt keinen reduzierbaren Integerbestand und damit keinen negativen Bestand.

## AL Request-ID- und Retry-Lifecycle

`DH Deep Scan Run` speichert `Client Request ID`, Startstatus (`Pending`, `Accepted`, `RetryRequired`), Versuchszahl und letzten Versuch. Die lokale Zeile wird vor dem Senden committed.

Bei bestätigter Antwort wird der Status `Accepted`. Bei Timeout/Fehler bleibt dieselbe Zeile mit `RetryRequired` erhalten. Der nächste manuelle oder Scheduler-Aufruf findet `Pending` oder `RetryRequired`, sendet dieselbe GUID und startet nach Annahme denselben lokalen Run. Ein bewusst neuer Start nach `Accepted` erhält eine neue GUID. Historische Runs mit leerer GUID werden trotz des AL-Options-Defaultwerts `Pending` nicht als Retry interpretiert.

Assessment und Validation werden anhand produktspezifischer Snapshot-Zähler ausgewählt. Monitoring nutzt den Modus `monitoring`; Data Health Score bleibt separat. Keine sensiblen Werte wurden der AL-Tabelle hinzugefügt.

## Fehlerverhalten

| Fall | Ergebnis |
|---|---|
| kein passender Credit / Monitoring abgelaufen | HTTP 402; keine Teilbuchung |
| Free-Slot bereits verwendet | HTTP 409 |
| gleicher Key, anderer Payload | HTTP 409 |
| ungültige GUID/Scanart | HTTP 422 |
| fremder Tenant/Token | bestehende Authentisierung blockiert |
| konkurrierender DB-Konflikt | Rollback; HTTP 503 mit Aufforderung, denselben Key zu wiederholen |
| Queue-/Statusanlage scheitert | vollständiger Rollback |
| Antwort nach Commit verloren / Backend-Neustart | persistierter Replay liefert dieselbe Scan-ID |

Eine durchgängige Correlation-ID existiert weiterhin nicht und bleibt P1. P0-04-Laufzeit-/Refund-Recovery wurde bewusst nicht verändert.

## Migration 0023

`0023_atomic_scan_credit.py` folgt auf 0022. Vor dem Constraint prüft sie doppelte nichtleere `consumed_scan_id` und bricht mit einer eindeutigen Sanierungsaufforderung ab. Bestehende Credits werden mit `MIGRATION`, Betrag `0`, übernommen; historische Verbrauchsvorgänge werden nicht erfunden. Frische DB, Upgrade über 0022 mit Legacy-Credit und Head-Revision wurden erfolgreich geprüft.

Rollback ist technisch als Downgrade vorhanden, darf nach produktiven P0B-Starts aber nur im Wartungsfenster erfolgen: Die neuen Idempotency-/Ledgerdaten gingen verloren und alte Anwendungslogik wäre wieder race-anfällig. Empfohlen ist Roll-forward.

## Automatisierte Evidenz

| Prüfung | Ergebnis |
|---|---|
| neue P0B-Suite mit echten Threads/separaten Sessions | 12/12 bestanden |
| P0B + Product Licensing + Billing + Scan Status | 76/76 bestanden |
| vollständige Backend-Suite | 178 bestanden, 2 bekannte fachfremde Altfehler, 5 Windows-Temp-Setupfehler |
| Temp-Setupfehler mit Workspace-Basetemp erneut | 5/5 bestanden |
| Python `compileall` | bestanden |
| Migration frisch / von 0022 | bestanden |
| AL ReleaseCloud + CodeCop + PerTenantExtensionCop | Compile ohne Fehler; bestehende Warnungen |
| AppSourceCop | bekannte Manifest-/ID-Range-Fehler, keine P0B-Regression |
| Localization / Pricing Consistency | bekannte Altfehler, außerhalb P0B |
| `git diff --check` | bestanden |

Die P0B-Tests decken Assessment/Validation-Trennung, Monitoring-Ablauf, identische und unterschiedliche Parallelstarts, Payload-Konflikt, Tenant-Scope, Free-Slot, ungültige GUID, gemeinsamen Rollback, Scheduler-/Retry-Semantik und neue Starts ab. SQLite wurde für die schnelle Suite verwendet. Die Implementierung verwendet explizite PostgreSQL-Sperr- und Conditional-Update-Mechanismen; ein echter PostgreSQL-Concurrencylauf bleibt als Releaseevidenz offen, solange die lokale Docker Engine nicht verfügbar ist.

## Manuelle BC-/Production-Verifikation

In einer BC-Sandbox mit PostgreSQL-Staging sind auszuführen und mit Request-ID, Scan-ID, Creditzeile und Ledger zu protokollieren:

1. Assessment mit genau einem Credit;
2. Doppelklick auf Start;
3. Timeout/Antwortverlust und Wiederholung;
4. zwei parallele unterschiedliche Starts bei einem Credit;
5. Validation mit passendem Credit;
6. Validation ohne passenden Credit;
7. Monitoring mit aktiver Subscription;
8. Monitoring nach Ablauf;
9. Scheduler-Doppeltrigger;
10. Backend-Restart zwischen Commit und Retry.

Erwartung: ein logischer Request, ein Scan, maximal eine Consumption-Buchung; bei bezahlten Starts genau eine. Diese Punkte sind vorbereitet, mangels Sandbox aber **nicht bestanden**.

## Bekannte Grenzen und Folgeentscheidung

- echter PostgreSQL-/Deadlock-/Restart-Nachweis und BC-Sandbox-CAT offen;
- keine AL-Test-App vorhanden;
- spätere Scanfehler/Refund und terminaler Lifecycle bleiben P0-04;
- Finding-Zugriff bleibt P0-05;
- AppSource, Lokalisierung und Pricing besitzen bekannte P1-Gates.

Bewertung: **P0-03 behoben: Ja. Bereit für GL-EXT-P0C: Ja. Aktuelles Produkt-Gate: NO-GO.**
