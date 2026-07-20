# Workflow-Inventur

Die technischen Schrittketten stehen strukturiert in [data/workflows.yaml](data/workflows.yaml). Alle 24 Workflows besitzen explizite `components`, einen `execution_mode` sowie Schritte mit gültigen `feature_id`-Referenzen.

| Workflow | Status | Belegkette / nicht belegbarer Teil |
|---|---|---|
| Registrierung aus BC | implemented | `DHApiClient.RegisterTenant` → `POST /tenant/register` → `tenant_registration_service.py`; reale Sandbox manuell |
| Tenant-/Environment-Bindung | implemented | `DHTenantIdentityMgt` + Registration Identity/Unique Constraint |
| Lizenzstatus abrufen | implemented | `DHApiClient` → `GET /license/status` → `product_license_service.py` |
| Assessment/Validation kaufen | implemented | Checkout-Session + Stripe-Webhook + Credit-Tabellen; echte Zahlung manuell |
| Monitoring abonnieren | implemented | Subscription-Checkout/Webhook/Entitlement; echte Zahlung manuell |
| Manuellen Scan starten | implemented | `DHSetup`/Dispatcher/Runner → `/scan/start`, Status und `/scan/sync` |
| Geplanten Scan starten | implemented | AL TaskScheduler → Scheduled Runner → Scan Dispatcher |
| Credit verbrauchen | implemented | `atomic_scan_start_service.py` und Migration `0023`; PostgreSQL-Konkurrenztest nicht lokal bestätigt |
| Scanabschluss/Fehler | implemented | AL Failure-Codeunits + Backend Status Service/Recovery |
| Findings speichern | implemented | AL Findingtabellen + `/scan/sync` + `ScanIssueRecord` |
| Health Score berechnen | implemented | AL Scan-/Profiling-Logik + Backend `scoring_service.py` |
| Report/PDF erzeugen | implemented | Reportrouter → Executive Report Service → Jinja/Playwright |
| Dashboardzugriff/-öffnung | implemented | Analytics-Token, Embed-Cookie, Dashboard-Session/BC-Control-Add-in |
| Analytics öffnen | implemented | `/analytics/embed` und `analytics-dashboard.js` |
| Zugriff ablaufen lassen | implemented | Entitlement-/Access-Control-Services und frischer Access Snapshot |
| Stripe-Webhook | implemented | Signaturprüfung, Idempotenz und Entitlement-Aktualisierung |
| Scheduler erneut planen | implemented | `DHScanSchedulerMgt` und `DHSetup.RescheduleEnabledScheduler` |
| E-Mail versenden | implemented | zusammenhängender SMTP-Code vorhanden; reale Zustellung/Clientdarstellung manuell |
| Übersetzungen laden | implemented | Website-JSON, Dashboard-JSON/Service und AL-XLF |
| Extension installieren/upgraden | implemented | Install-/Upgrade-Codeunits; reale Upgradeausführung manuell |

„Implemented“ bedeutet hier: zusammenhängende statische Codekette nachgewiesen. Externe Systemausführung ist davon getrennt.
