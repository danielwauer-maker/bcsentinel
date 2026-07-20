# Repository Map

| Pfad | Zweck / Technologie | Start-, Build- oder Testpunkte |
|---|---|---|
| `backend/` | Python 3.11, FastAPI, SQLAlchemy, Jinja2, Stripe, Playwright | `app/main.py`, `Dockerfile`, `pytest.ini` |
| `backend/app/routers/` | HTTP-Routen für Admin, Analytics, Billing, Dashboard, Partner, Reports, Scans, Lizenz und öffentliche Konfiguration | Einbindung in `backend/app/main.py:178-186` |
| `backend/app/services/` | Berechtigungen, Registrierung, Pricing, Scoring, Reports, E-Mail, Übersetzungen und Lifecycle | Aufruf durch Router/Main |
| `backend/app/templates/`, `static/` | Serverseitige Admin-/Portal-/Report-HTML, CSS, JS, Fonts und Bilder | FastAPI StaticFiles/Jinja in `main.py` |
| `backend/alembic/` | PostgreSQL-Schemahistorie | `alembic.ini`, Revisionen `0001`–`0025` |
| `backend/tests/` | Pytest, standardmäßig isoliertes SQLite; optionale PostgreSQL-URL | `python -m pytest -p no:cacheprovider tests` |
| `bc-extension/` | Microsoft Dynamics 365 Business Central AL, Runtime/Platform 27, Objektbereich 53100–53199 | `app.json`, `app.cloud.json`, PowerShell-Buildskript |
| `bc-extension/app/src/` | Tables, Pages, Page Extensions, Codeunits, Queries, Enums, Permission Sets, Control Add-in | AL-Compiler; kein AL-Test-App-Verzeichnis gefunden |
| `bc-extension/Translations/` | generierte Basis-XLF und Deutsch | `BCSentinel.g.xlf`, `BCSentinel.de-DE.xlf` |
| `landingpage/` | tatsächlich vom Backend-Image kopierter statischer Webauftritt, Vanilla HTML/CSS/JS, DE/EN | `index.html`; API-Aufrufe in JS |
| `landingpage_neu/` | alternative statische Website mit eigener Asset-/Sprachstruktur | `index.html`; keine Deployment-Einbindung gefunden |
| `config/` | Nginx-Reverse-Proxy und kanonische Preise | `nginx/bcsentinel.conf`, `pricing_canonical.json` |
| `.github/workflows/` | Deployment von `main` und `staging` per SSH/Docker Compose | `deploy.yml`; keine Test-Job-Deklaration |
| `scripts/` | Preis-/Lokalisierungsprüfungen, Migration und Release-Paketierung | Python, Shell, PowerShell |
| `docs/` | Architektur-, Produkt-, Operations-, Datenschutz-, Release- und Auditdokumente | siehe `evidence/existing-documents.md` |
| `output/pdf/` | generierte Beispiel-PDFs | fünf Reportbeispiele |
| `.build/`, `bc-extension/.alpackages`, `.snapshots` | Build-/Compilerartefakte und Symbole; durch Namen/Dateitypen als generiert erkennbar | nicht als Produktquellcode gewertet |
| `go-live-readiness-2026/` | Readiness-Artefakte | dokumentarischer Nachweis, keine neue Reifeaussage |

## Konfiguration und Betrieb

`docker-compose.dev.yml` und `docker-compose.prod.yml` starten Backend plus PostgreSQL 15; `docker-compose.p0e.yml` trennt Migration und Backend auf einem vorgebauten Image. Nginx terminiert TLS und proxyt auf lokale Backendports. Umgebungsvariablen sind in `backend/app/core/settings.py` definiert; Geheimnisse werden nicht in diesem Inventar wiedergegeben.

## Statische Assets

Lokale Fonts und Reportlogos liegen unter `backend/app/static/`; Websitebilder liegen in beiden Landingpage-Bäumen. `output/pdf/` enthält Beispielausgaben, nicht die Generierungslogik.
