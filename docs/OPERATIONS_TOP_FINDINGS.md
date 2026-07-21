# Operations Top Findings

Stand: 2026-07-21

## Top 10 Stärken

1. Strukturierte JSON-Logs mit Request-ID, Event, Dauer, Tenantkontext und Fehlerkorrelation.
2. Getrennte Liveness- und DB-Readiness-Endpunkte mit Compose- und Deploymentintegration.
3. Startup blockiert fehlende Pflichtkonfiguration und falschen Alembicstand.
4. Lineare Alembic-Historie mit 27 Revisionen und expliziten Downgrade-Funktionen.
5. Multi-Stage-Dockerfile mit gepinnten Pythonabhängigkeiten, Chromium-Verifikation und non-root Runtime.
6. 29 Backend-Testdateien und 260 Testfunktionen mit Tenancy-, Lifecycle-, Security- und Deploymentfällen.
7. Idempotenz-, Lease-, Retry- und Recoverymechanismen für kritische Background-Job-Zustände.
8. Fünf Business-Central-Permission-Sets trennen Viewer, Scan, Setup, Admin und Scheduler.
9. Admin Audit Events und Run-/Request-IDs schaffen gute Diagnosegrundlagen.
10. Deployment-, Pilot-, Backup-/Restore- und Go-Live-Dokumentation benennt Grenzen offen.

## Top 10 Risiken

1. Deployment erfolgt ohne vorgeschalteten CI-Testjob direkt nach Push.
2. Keine zentrale Monitoring-, Metrics-, Tracing- oder Alertingplattform.
3. Backup und Restore sind manuell und ohne erfolgreichen Drill belegt.
4. Kein Disaster-Recovery-Modell, keine RTO/RPO und Single-Host-Failure-Domain.
5. Keine native AL-Test-App oder aktuelle automatisierte BC-Sandbox-Regression.
6. Backend-Admin nutzt eine einzelne Basic-Identität ohne Enterprise-RBAC/MFA-Nachweis.
7. Secrets liegen als Host-/Actions-Konfiguration ohne belegten Lifecycle oder Rotation.
8. In-process Background Jobs und Rate Limits besitzen kein freigegebenes Mehrinstanzmodell.
9. Keine Performance-, Load-, Soak- oder Capacity-Evidenz.
10. Support und Incident Response sind founder- und expertenabhängig.

## Top 10 Quick Wins

1. Backend-Docker-Testtarget als Pflichtjob vor jedem Deployment ausführen.
2. Deploymentworkflow mit `concurrency` und geschütztem GitHub Environment versehen.
3. Commit, Image-Digest, Alembic-Head und Konfigurationsversion als Release Manifest ausgeben.
4. Externen Uptimecheck für `/health/ready` mit Alarmkanal einrichten.
5. Einen minimalen 5xx-/Latenz-/Restart-/Disk-/DB-/Job-Alertkatalog definieren.
6. Tägliches automatisiertes Off-host-Backup mit Success-/Failure-Signal einrichten.
7. Einen Restore-Drill ausführen, messen und protokollieren.
8. Namentlichen Incident Primary/Backup und eine Severity-/Eskalationsmatrix festlegen.
9. Secret-Inventar mit Owner, Speicherort, Rotation und Notfallwiderruf erstellen.
10. Product-Master-Book-Zahlen für Tests und Migrationen automatisiert gegen HEAD prüfen.

## Top 10 Operational Blocker

1. Kein zuverlässiger Alarm bei Produktionsausfall.
2. Kein nachgewiesener Restore.
3. Kein sicherer, getesteter Rollback.
4. Kein releaseblockierendes Testgate.
5. Kein formeller On-call-/Incident-Prozess.
6. Keine zentrale Logaufbewahrung und -suche als Betriebsevidenz.
7. Keine Job-/Queue-/Scheduler-Gesundheitsmetriken.
8. Keine kontrollierte Environment- und Konfigurationspromotion.
9. Keine benannten Least-Privilege-Operatoridentitäten.
10. Keine belastbare Secretrotation und Leak Response.

## Top 10 Go-Live Blocker

1. CI/CD kann ungetesteten Code produktiv deployen.
2. Monitoring, Telemetry und Alerting sind nicht Enterprise-fähig belegt.
3. Backup, Restore und Disaster Recovery sind nicht operationalisiert.
4. AL-Runtime-Regression fehlt vollständig.
5. Performance- und Skalierungsevidenz fehlt vollständig.
6. Single Host und Single Database ohne belegtes HA-/Failovermodell.
7. Admin-RBAC, MFA/SSO und Access Reviews fehlen.
8. Incident-, Kundenkommunikations- und Supportorganisation ist nicht skalierbar.
9. Release-, Migration- und Rollbackprotokolle sind nicht als aktuelle Evidenz vorhanden.
10. Product System besitzt noch keinen normativen Operations-Vertrag mit SLO, RTO/RPO und Governance.

## Top 10 langfristige Skalierungsrisiken

1. API-Prozess besitzt Background-Job-Ownership und erschwert horizontale Replikation.
2. In-memory Rate Limits verhalten sich über mehrere Instanzen inkonsistent.
3. Lokales PostgreSQL-Volume und App auf demselben Host erhöhen den Blast Radius.
4. Feste Containernamen und Hostpfade sind nicht orchestrator- oder multi-environment-fähig.
5. Kein Capacity Model für Kunden, Scans, Findings, Reports, Jobs oder Datenwachstum.
6. Eine gemeinsame Adminidentität verhindert sichere Delegation an ein wachsendes Team.
7. Manuelle Konfiguration und Secrets skalieren organisatorisch nicht.
8. Fehlende Telemetrie verhindert proaktive Kapazitäts- und Kostensteuerung.
9. Fehlende native AL-Automation vervielfacht Regressionrisiko mit jeder BC-Version.
10. Dokumentation driftet ohne automatische Evidenzgenerierung gegen den Code.

## Evidence Missing

- Grüne CI-Ausführung des bewerteten Commits.
- Produktions- oder Staging-Deployment-/Rollbackprotokoll.
- Backupobjekte, Backupmonitoring und erfolgreicher Restore-/DR-Drill.
- Monitoringdashboards, Alertregeln, Pagerhistorie und SLO-Berichte.
- Security Access Reviews, Secretrotation, Vulnerability-Triage und Incidentübung.
- AL-Sandbox- und Permission-Negativtests.
- Last-/Soak-/Capacity- und Mehrinstanztests.
- Ticket-, Incident-, Postmortem- oder Support-SLA-Historie.
