# Backend und API

## Zusammenfassung
FastAPI-Monolith mit 120 Routendeklarationen und synchronem SQLAlchemy-Zugriff.

## Erkannte Verantwortlichkeiten
Tenantregistrierung, Scanannahme/-persistenz, Lizenz/Billing, Dashboard/Admin/Partner, Reporting, Lokalisierung und Healthchecks.

## Erkannte Unterbereiche
`main.py`, neun Routermodule, Security-, Schema- und Servicemodule.

## Vorhandene Features
BACK-API-001, BACK-TEN-001, BACK-OBS-001, BACK-HEALTH-001.

## Teilweise vorhandene Features
BACK-JOB-001: Lifecycle-Recovery läuft in-process; kein separater Worker im Compose-Stack.

## Stubs oder statische Inhalte
Root-Route liefert statischen Servicehinweis.

## APIs und Schnittstellen
Vollständig in [api-endpoints.md](../evidence/api-endpoints.md); Stripe, SMTP, PostgreSQL und Playwright/Chromium.

## Datenmodelle
22 ORM-Klassen in `backend/app/models.py`.

## Tests
27 Testdateien; API-, Security-, Billing-, Lifecycle- und Reportingtests.

## Dokumentation
`backend/README.md`, `backend/TESTING.md`, Architektur- und Smoke-Test-Dokumente.

## Technische Auffälligkeiten
Startup validiert Konfiguration und Migrationsstand; produktive HTTP-Requests werden hinter TLS-Proxy kontrolliert.

## Manuell zu prüfen
Mehrinstanzbetrieb, externe Integrationen und Produktionsperformance.

## Belegverzeichnis
`backend/app/main.py`; `backend/app/routers/`; `backend/app/services/`.
