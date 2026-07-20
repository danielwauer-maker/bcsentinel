# Technische Gaps

Nur direkt belegbare Lücken sind enthalten; `severity` bleibt unbewertet.

1. **GAP-TEST-001:** Deployment-CI führt keine Pytest-Suite aus (`.github/workflows/deploy.yml`).
2. **GAP-TEST-002:** Keine AL-Test-App/Testcodeunits im BC-Quellbaum (`bc-extension/app/src/`).
3. **GAP-WEB-001:** `landingpage_neu/` besitzt keine erkennbare Deployment-Einbindung; Docker kopiert `landingpage/` (`backend/Dockerfile`).
4. **GAP-WEB-002:** Rechtstexte enthalten explizite Platzhalter, unter anderem Telefonnummer, Register und USt-ID (`landingpage/impressum.html`).
5. **GAP-MAIL-001:** SMTP-Sendewege überspringen Versand bei fehlender Konfiguration; reale Zustellung ist nicht automatisiert belegt (`dashboard_invite_service.py`, `partners.py`).
6. **GAP-OPS-001:** Backup/Restore ist dokumentiert, aber keine automatisierte Backup-/Restore-Implementierung im Repository nachgewiesen (`docs/ops/backup-restore.md`).
7. **GAP-DOC-001:** Root-`README.md` ist leer.
8. **GAP-DB-001:** Tests erzeugen Tabellen aus SQLAlchemy-Metadaten und umgehen Startup-Migrationschecks; vollständige Modell-/Migrationsgleichheit wird dadurch nicht in jeder Suite geprüft (`backend/tests/conftest.py`).
9. **GAP-WEB-003:** `landingpage/support.html` bezeichnet Inhalte selbst als MVP/auszubauend und enthält Screenshot-Mockup-Text.
10. **GAP-OPS-002:** Kein eigener Scheduler-/Worker-Service im Docker-Stack; Backend-Recovery läuft als In-Process-Task, BC-Scheduling über TaskScheduler (`main.py`, Compose, `DHScanSchedulerMgt`). Mehrinstanzverhalten ist nur teilweise testbar.

Strukturierte Daten: [data/gaps.yaml](data/gaps.yaml).
