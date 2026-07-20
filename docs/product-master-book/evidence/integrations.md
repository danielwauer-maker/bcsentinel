# Integrationen

| System | Zweck | Code/Konfiguration | Auth/Schutz | Laufzeitnachweis |
|---|---|---|---|---|
| Microsoft Dynamics 365 Business Central | Datenprofiling, Scansteuerung, UI/Drilldown | `bc-extension/app/src/` | Permission Sets, Secret Mgt., Tenant-/BC-Kontext | Code vorhanden; Sandbox manuell |
| PostgreSQL 15 | persistente Backenddaten | SQLAlchemy/Alembic, Compose | `DATABASE_URL`, Netzwerk/Secrets | Migration-/PG-Tests vorhanden; BOOK nicht ausgeführt |
| Stripe | Checkout, Subscription, Portal, Webhook | `billing.py`, Stripe SDK, Settings | Secret Key, Webhooksignatur, Idempotenz | gemockte Tests; echte Zahlung manuell |
| SMTP | Einladungen/Partner/Testmail | Invite Service, Partnerrouter, Settings | TLS, optionale Credentials | Code vorhanden; Zustellung manuell |
| Playwright Chromium | PDF-Rendering | Executive Report Service, Dockerfile | interner Runtimeprozess | Buildprüfung/Testcode vorhanden; BOOK nicht ausgeführt |
| Nginx/Let's Encrypt | TLS-Termination/Proxy | `config/nginx/bcsentinel.conf` | HTTPS, Proxyheader | Konfiguration vorhanden; externer Betrieb manuell |
| GitHub Actions/SSH | Deployment | `.github/workflows/deploy.yml` | GitHub Secrets/SSH | Workflowcode vorhanden; Laufhistorie nicht Teil des Repos |
| BC Control Add-in | Analytics im BC-Client | `AnalyticsFrameAddIn.al`, JS/CSS | signierter Embedtoken/Cookie | Code vorhanden; Client manuell |

Power BI, Azure Service Bus oder ein externer Scheduler wurden nicht als implementierte Integrationen nachgewiesen; „Analytics“ ist eine eigene HTML/JS-Anwendung.
