# Infrastruktur und Operations

## Zusammenfassung
Docker-Images/Compose für Dev/Prod/P0E, PostgreSQL 15, Nginx TLS-Proxy und SSH-Deployment per GitHub Actions.

## Erkannte Verantwortlichkeiten
Build, Migration, Healthchecks, Deployment, TLS-Proxy, Runbooks, Releasepaketierung und PDF-Runtime.

## Erkannte Unterbereiche
Dockerfile, drei Compose-Dateien, Nginx, Workflow, `scripts/`, `docs/ops/`.

## Vorhandene Features
OPS-CONT-001, OPS-DEP-001, OPS-HEALTH-001.

## Teilweise vorhandene Features
OPS-BACKUP-001 ist nur dokumentiert; CI enthält keine Tests; Rollback ist extern/manuell.

## Stubs oder statische Inhalte
Keine Infrastruktur-Stubs; `.env.example` enthält Konfigurationsvorlage.

## APIs und Schnittstellen
Docker, PostgreSQL, SSH, Nginx/Let's Encrypt, GitHub Actions.

## Datenmodelle
PostgreSQL-Volume pro Compose-Umgebung.

## Tests
Deployment-Readiness, Security Header, Playwright-Packaging; Workflow-Healthchecks.

## Dokumentation
`docs/ops/`, `DEPLOYMENT_DRY_RUN.md`, Pilot-/Go-live-Runbooks.

## Technische Auffälligkeiten
GitHub-Workflow führt auf Zielserver `git reset --hard`/`git clean -fd` aus; das ist dokumentierter Deploymentcode, in diesem Sprint nicht ausgeführt.

## Manuell zu prüfen
Backup/Restore, Secrets, Monitoring, Rollback, Zertifikatserneuerung und Mehrinstanzbetrieb.

## Belegverzeichnis
Root-Compose-Dateien, `backend/Dockerfile`, Nginx und Workflow.
