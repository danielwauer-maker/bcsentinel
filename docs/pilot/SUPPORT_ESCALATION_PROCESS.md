# BCSentinel Support- und Eskalationsprozess

**Stand:** 2026-08-05  
**Gültigkeit:** betreute Pilotphase

## 1. Supportkanal

Vor Kunde 1 werden ein primärer Supportkanal und ein Ersatzkanal festgelegt. Jeder Vorgang benötigt:

- Zeitstempel,
- Kunde/Tenant,
- meldende Person,
- betroffene Funktion,
- Schweregrad,
- Screenshots oder Fehlermeldung,
- verantwortliche Person,
- Status und Abschlussnotiz.

## 2. Schweregrade

| Klasse | Bedeutung | Zielreaktion Pilot |
| --- | --- | --- |
| P0 | Datenverlust/-leck, falsche Tenantzuordnung, falscher Creditverbrauch, kein Restore, Monitoringstillstand, kritischer Sicherheits- oder Rechtsfall | sofortige Bestätigung und Arbeitsbeginn; Kundenstart oder betroffene Funktion stoppen |
| P1 | Wichtige Funktion gestört, aber manueller Ersatzweg möglich | innerhalb des vereinbarten Pilotfensters bearbeiten |
| P2 | Kosmetik, Terminologie, Komfort oder kleinere Layoutabweichung | dokumentieren und priorisiert ins Backlog übernehmen |

Konkrete Reaktionszeiten werden vor Kunde 1 kaufmännisch festgelegt und dürfen nicht stillschweigend als SLA beworben werden.

## 3. Eskalationsweg

1. Eingang bestätigen.
2. P0/P1/P2 klassifizieren.
3. Daniel als primären Operator zuweisen.
4. Bei P0 Ersatzkontakt aktivieren.
5. Betroffene Kunden proaktiv informieren, sobald Auswirkung und nächster Statuszeitpunkt bekannt sind.
6. Bei Datenschutz, Vertrag oder Haftung externe Fachstelle einbeziehen.
7. Abschluss mit Ursache, Lösung, Nachweis und Präventionsmaßnahme dokumentieren.

## 4. Kommunikationsrhythmus

Für P0 gilt:

- Erstinformation: Problem bestätigt, Umfang wird geprüft.
- Statusupdates: in vorab zugesagtem Rhythmus.
- Abschluss: Ursache, Kundenauswirkung, Datenstatus, Wiederherstellung und nächste Maßnahmen.

Keine Spekulationen oder unbestätigten Ursachen kommunizieren.

## 5. Eskalationsmatrix

| Ereignis | Primär | Ersatz | Runbook |
| --- | --- | --- | --- |
| API nicht bereit | Daniel | festzulegen | RB-API-01 |
| PostgreSQL nicht bereit | Daniel | festzulegen | RB-DB-01 |
| Worker/Scheduler gestört | Daniel | festzulegen | RB-WORKER-01 / RB-SCHED-01 |
| Scan hängt oder schlägt wiederholt fehl | Daniel | festzulegen | RB-SCAN-01 / RB-SCAN-02 |
| Recovery fehlgeschlagen | Daniel | festzulegen | RB-RECOVERY-01 / RB-RECOVERY-02 |
| Queue-Rückstau | Daniel | festzulegen | RB-QUEUE-01 |
| Disk/Backup kritisch | Daniel | festzulegen | RB-DISK-01 / RB-BACKUP-01 |
| SMTP-Ausfall | Daniel | festzulegen | RB-SMTP-01 |
| TLS-Ablauf | Daniel | festzulegen | RB-TLS-01 |
| Container-Restartschleife | Daniel | festzulegen | RB-CONTAINER-01 |

## 6. Abschlusskriterien

Ein Incident ist erst geschlossen, wenn:

- Ursache oder belastbare Zwischenursache dokumentiert ist,
- Kundenauswirkung feststeht,
- Datenintegrität geprüft wurde,
- Readiness und betroffene Produktfunktion wieder grün sind,
- Kunde informiert wurde,
- Nacharbeit mit Owner und Termin erfasst ist.
