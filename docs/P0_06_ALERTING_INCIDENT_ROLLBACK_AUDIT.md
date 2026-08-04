# P0-06 Alerting, Incident und Rollback Audit

**Stand:** 2026-08-05  
**Produktstand:** BCSentinel 1.0.2.20  
**Gate:** G6 Betrieb / Sprint P0-06

## 1. Ziel

P0-06 schafft einen reproduzierbaren technischen Mindeststandard für Betreiberwarnungen. Kritische Zustände müssen eindeutig als P0 oder P1 klassifiziert, einem Runbook zugeordnet und als maschinen- sowie menschenlesbare Evidenz ausgegeben werden.

## 2. Umgesetzte Komponenten

| Komponente | Pfad | Zweck |
| --- | --- | --- |
| Alert-Evaluator | `backend/scripts/evaluate_operator_alerts.py` | bewertet einen konsolidierten Betriebs-Snapshot gegen definierte Schwellenwerte |
| Szenariotests | `backend/tests/test_p0_06_operator_alerts.py` | prüft gesunden, kritischen und warnenden Zustand |
| gesunder Referenzzustand | `quality/p0-06/healthy-snapshot.json` | CI-Baseline ohne P0/P1-Alarm |
| GitHub-Gate | `.github/workflows/p0-06-operator-alerting.yml` | automatischer Test und Evidenzartefakt |

## 3. Überwachte Zustände

- API-Readiness
- PostgreSQL-Readiness
- Worker-Readiness
- Scheduler-Readiness
- fehlgeschlagene Scans
- hängende Scans / Heartbeat-/Lease-Überschreitung
- fehlgeschlagene Recovery-Versuche
- Queue-Alter und Rückstau
- Datenträgerauslastung
- Backup-Alter
- SMTP-Fehler
- TLS-Zertifikatsrestlaufzeit
- Container-Restarts und Restartschleifen

## 4. Priorisierung

### P0

Ein unmittelbarer Betreiber- oder Pilotblocker, zum Beispiel:

- API, Datenbank, Worker oder Scheduler nicht bereit
- hängender Scan
- Recovery fehlgeschlagen
- mehrere Scanfehler in kurzer Zeit
- Queue-Rückstau ab 15 Minuten
- Disk ab 90 %
- Backup älter als 48 Stunden
- mindestens fünf SMTP-Fehler pro Stunde
- Zertifikat höchstens sieben Tage gültig
- mindestens drei Container-Restarts pro Stunde

### P1

Eine wichtige Warnung mit noch möglicher manueller Reaktion, zum Beispiel:

- einzelner Scanfehler
- Queue-Alter ab fünf Minuten
- Disk ab 80 %
- Backup älter als 24 Stunden
- einzelner SMTP-Fehler
- Zertifikatsrestlaufzeit höchstens 30 Tage
- einzelner Container-Restart

## 5. Runbook-Zuordnung

Jeder Alert enthält einen stabilen Code und eine Runbook-ID, unter anderem:

- `RB-API-01`
- `RB-DB-01`
- `RB-WORKER-01`
- `RB-SCHED-01`
- `RB-SCAN-01/02`
- `RB-RECOVERY-01/02`
- `RB-QUEUE-01`
- `RB-DISK-01`
- `RB-BACKUP-01`
- `RB-SMTP-01`
- `RB-TLS-01`
- `RB-CONTAINER-01`

## 6. CI-Evidenz

Der Workflow erzeugt:

- `operator-alerts.json`
- `operator-alerts.md`
- Status PASS/FAIL
- Anzahl P0/P1
- Alertcodes, Detailtexte und Runbook-Referenzen
- 30 Tage aufbewahrtes GitHub-Artefakt

Verifizierter Lauf:

- Workflow: `P0-06 Operator Alerting`
- Run: `#4`
- Run-ID: `30958166322`
- Ergebnis: `success`
- Head-SHA: `0f971f23d6b7300722571d9cbca075f8e9d9cddf`
- Evidenzartefakt: `p0-06-operator-alerting-evidence`
- Artefakt-ID: `8911876261`
- Digest: `sha256:2665e9e19177e6223588bd2ff1e796f45e9dccfc73c61ee1e156e6a83ce18c4a`
- Aufbewahrung bis: `2026-09-03`

Zusätzlich erfolgreich auf demselben Head:

- `PILOT-E2E-01A Automated Readiness #55`
- `P0-04 PostgreSQL Migration Cycle #16`
- `P0-05 PostgreSQL Backup Restore #11`

## 7. Auditstatus

**Aktueller Status:** `VERIFIED_IN_CI / PASS`

Die Schwellenwert-, Klassifizierungs- und Runbook-Zuordnungslogik ist auf dem aktuellen PR-Head erfolgreich getestet. Der zuvor fehlerhafte dynamische Testimport wurde korrigiert; die vollständige Backend-Regression und das Pilot-E2E-Gate sind anschließend ebenfalls erfolgreich durchgelaufen.

## 8. Noch offenes reales Betriebs-Gate

Die CI-Prüfung ersetzt nicht den produktiven Alarmweg. Vor Kunde 1 müssen noch gemeinsam nachgewiesen werden:

1. reale Betriebsmetriken werden in das Snapshot-/Monitoringformat eingespeist,
2. mindestens Daniel und ein Ersatzkontakt sind hinterlegt,
3. ein P0-Testalarm erreicht den Empfänger,
4. Empfangszeit und Eskalationsweg werden protokolliert,
5. ein ungefährlicher Incident wird nach Runbook bearbeitet,
6. ein Backend-Rollback wird auf der Pilot-Infrastruktur durchgeführt,
7. anschließend bestehen Readiness- und Produkt-Smoke-Tests.

## 9. Bewertung

Die Repository- und CI-Seite von P0-06 ist abgeschlossen. Für das vollständige betriebliche Gate G6 bleiben reale Alarmzustellung, Incident-Drill und Rollback-Nachweis offen.
