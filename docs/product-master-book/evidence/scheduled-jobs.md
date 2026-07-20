# Scheduled Jobs und Background Tasks

| Job | Mechanismus/Start | Verantwortung | Fehler/Retry | Tests/Beleg |
|---|---|---|---|---|
| Geplanter BC-Scan | `DHScanSchedulerMgt` registriert `TaskScheduler` mit `DHScheduledScanRunner` und Failure-Codeunit | Zeitpunkt berechnen, Scan dispatchen, Resultat speichern, neu planen | Failure Count/Error/Result in `DH Setup`; Failure Codeunit | AL-Dateien, `DHSetup`-Schedulerfelder; reale BC-Ausführung manuell |
| Monitor Refresh | `DHMonitorRefreshTask` | Deep-Scan-Monitor aktualisieren | statisch begrenzter UI-Task | AL-Codeunit/Page; manuell |
| Backend Lifecycle Recovery | Startup-/In-Process-Schleife in `backend/app/main.py` mit `scan_status_service.py` | stale queued/running Runs requeue/fail, Lease/Backoff | max attempts/backoff/interval aus Settings | `test_p0c_scan_lifecycle.py`, optionale PG-Konkurrenz |
| Deployment Healthcheck | GitHub Actions Schleifen nach Deployment | lokale und öffentliche `/health` prüfen | 20 Versuche, Workflowfehler | `.github/workflows/deploy.yml` |
| Docker Healthchecks | Compose | `/health/ready`, PostgreSQL `pg_isready` | Container-Restart/Healthstatus | drei Compose-Dateien |

Kein separater Celery/RQ/Sidekiq-ähnlicher Worker oder Queue-Service wurde gefunden. Stripe-Webhooks und E-Mails werden requestgebunden verarbeitet.
