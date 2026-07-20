# Komponenten-Inventur

| Komponente | Status | Primärbelege | Detail |
|---|---|---|---|
| Business-Central-Extension | implemented | `bc-extension/app/src/` | [Detail](components/business-central-extension.md) |
| Backend/API | implemented | `backend/app/main.py`, `backend/app/routers/` | [Detail](components/backend-api.md) |
| Scan Engine/Checks | implemented | `DHQuickScanMgt`, `DHDeepScanRunner`, `backend/app/routers/scans.py` | [Detail](components/scan-engine.md) |
| Customer Dashboard | implemented | `analytics_embed.html`, `analytics-dashboard.js`, `dashboard.py` | [Detail](components/customer-dashboard.md) |
| Admin-Backend | implemented | `admin.py`, Admin-Templates | [Detail](components/admin-backend.md) |
| Landingpage | partial | `landingpage/`, nicht eingebundenes `landingpage_neu/` | [Detail](components/landingpage.md) |
| Executive Reporting/PDF | implemented | `reports.py`, `executive_report_service.py` | [Detail](components/executive-reporting.md) |
| Lizenzierung/Billing | implemented | `billing.py`, Produkt-/Entitlement-Services | [Detail](components/licensing-billing.md) |
| E-Mail/Notifications | partial | SMTP in Invite-/Partner-/Template-Code | [Detail](components/email-notifications.md) |
| Übersetzungen | implemented | XLF, JSON, Translation-Services | [Detail](components/translations-localization.md) |
| Authentifizierung/Benutzer | implemented | Tenant-Token, Dashboard-Sessions, Partner-JWT, Basic Admin | [Detail](components/authentication-users.md) |
| Datenbank/Migrationen | implemented | `models.py`, 25 Alembic-Revisionen | [Detail](components/database-migrations.md) |
| Infrastruktur/Operations | partial | Docker, Nginx, Deploymentworkflow, Runbooks | [Detail](components/infrastructure-operations.md) |
| Security/Compliance | partial | Securitymodule und Datenschutzdokumente | [Detail](components/security-compliance.md) |
| Testing/Quality | partial | 224 Pytest-Funktionen; keine CI-Testausführung/AL-Test-App | [Detail](components/testing-quality.md) |
| Dokumentation/Release | implemented | `docs/`, `go-live-readiness-2026/` | [Detail](components/documentation-release.md) |

Status bezeichnet nur den technischen Inventurstand, nicht Produktreife.
