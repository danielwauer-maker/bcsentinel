# API-Endpunkte

## Leseregel

Alle 120 FastAPI-Deklarationen wurden erfasst. Slash-Aliase sind als eine semantische Route mit beiden Pfaden dargestellt. „Tenant“ bedeutet `X-Tenant-Id` plus `X-Api-Token` und serverseitigen Tenantabgleich; „Dashboard“ bedeutet Sessioncookie/Mitgliedschaft; „Admin“ bedeutet HTTP Basic, bei Mutationen zusätzlich Form-/CSRF-Prüfung; „Embed“ bedeutet signiertes Embed-Token/Cookie; „Share“ bedeutet zeitlich begrenztes Reporttoken. Exakte Pydantic-Klassen stehen am Dekorator oder in den genannten Routerdateien.

## Core und Scan

| Methode/Route | Zweck | Auth/Tenant | Request → Response | Services/Tests/Implementierung |
|---|---|---|---|---|
| GET `/health` | Liveness | keine | – → JSON | `main.py:410`; Deploymentchecks |
| GET `/health/ready` | DB-Readiness | keine | – → JSON | `main.py:415`; `db.py` |
| GET `/` | Servicehinweis | keine | – → JSON | `main.py:423` |
| POST `/tenant/register` | idempotente Tenant-/Portalregistrierung | Invite/Rate Limit; Kontext im Payload/Header | `TenantRegisterRequest` → `TenantRegisterResponse` | Registration/Invite Services; `test_tenant_registration.py`, `test_p0a_transport_registration.py`; `main.py:489` |
| POST `/tenant/dashboard-invite/resend` | Einladung erneut senden | Tenant | Contact-E-Mail → JSON | Invite Service; Registrationtests; `main.py:626` |
| POST `/scan/quick` | Quick-Scan speichern | Tenant, Featuregate | `QuickScanRequest` → `QuickScanResponse` | Scoring/Impact/Localization; Licensingtests; `main.py:660` |
| GET `/scan/history/{tenant_id}` | Scanverlauf | Tenant + Pfadabgleich | Pfad → `ScanHistoryResponse` | ORM; Licensingtests; `main.py:850` |
| GET `/scan/trend/{tenant_id}` | Scoretrend | Tenant + Pfadabgleich | Pfad → `ScanTrendResponse` | ORM; Dashboardtests; `main.py:945` |
| POST `/scan/start` | atomaren Scanstart anfordern | Tenant | `ScanStartPayload` → JSON | Atomic Start/Product License; P0B/Licensingtests; `scans.py:233` |
| POST `/scan/sync` | Ergebnis/Findings synchronisieren | Tenant + Run/Lease | `ScanSyncPayload` → JSON | Lifecycle/Scoring/Impact; P0C/Licensingtests; `scans.py:286` |
| POST `/scan/reconcile` | Tenant-Scans abgleichen | Tenant | `ScanReconcilePayload` → JSON | ORM; `test_scans.py`; `scans.py:517` |
| DELETE `/scan/{tenant_id}/{scan_id}` | Scan löschen | Tenant + Pfadabgleich | Pfade → JSON | ORM; `scans.py:561` |
| POST `/scan/status/update` | Fortschritt/Heartbeat/Terminalstatus | Tenant + Lease | `ScanStatusUpdatePayload` → JSON | Scan Status Service; Status/P0C-Tests; `scans.py:589` |
| GET `/scan/status/latest` | letzten Run lesen | Tenant | Query → JSON | Scan Status Service; `test_scan_status.py`; `scans.py:640` |
| GET `/scan/status/{run_id}` | Runstatus lesen | Tenant + Runzuordnung | Pfad → JSON | Scan Status Service; P0C-Tests; `scans.py:663` |

## Lizenz und Billing

| Methode/Route | Zweck | Auth/Tenant | Request → Response | Services/Tests/Implementierung |
|---|---|---|---|---|
| GET `/license/status` | Zugriffssnapshot | Tenant + Identitätskontext | Query → `LicenseStatusResponse` | Product License/Access Control; Licensing/P0D-Tests; `license.py:69` |
| GET `/billing/success` | Checkout-Rückkehr | keine, Session-ID optional | Query → HTML | Billing Service; Billingtests; `billing.py:376` |
| GET `/billing/cancel` | Abbruchseite | keine | – → HTML | `billing.py:396` |
| POST `/billing/checkout/session` | Stripe-Checkout | Tenant | `CheckoutSessionRequest` → `CheckoutSessionResponse` | Pricing/Stripe; Billing-/Licensingtests; `billing.py:580` |
| POST `/billing/portal` | Stripe-Portal | Tenant | `BillingPortalRequest` → `BillingPortalResponse` | Stripe; Billingtests; `billing.py:710` |
| GET `/billing/subscription/status` | Abozustand | Tenant | Query → `BillingSubscriptionStatusResponse` | Billing/Entitlement; Billingtests; `billing.py:766` |
| GET `/billing/checkout/session/status` | Checkout synchronisieren | Tenant | Query → `CheckoutSessionSyncResponse` | Stripe/DB; Billingtests; `billing.py:798` |
| POST `/billing/webhook` | Providerereignis | Stripe-Signatur; manueller Testpfad nur Nicht-Prod | Rohbody/`BillingWebhookPayload` → `BillingWebhookResponse` | Billing Service/Entitlements; Billingtests; `billing.py:898` |

## Dashboard und Analytics

| Methode/Route | Zweck | Auth/Tenant | Request → Response | Services/Tests/Implementierung |
|---|---|---|---|---|
| GET `/dashboard`, `/dashboard/invite` | Portal/Login/Invite UI | optional Dashboardcookie | Query → HTML | Dashboard Template; Multi-Tenant-Tests; `dashboard.py:162-163` |
| POST `/dashboard/invite/activate` | Einladung aktivieren | Invitetoken | `DashboardInviteActivationRequest` → JSON/Cookie | Invite Service; Membershiptests; `dashboard.py:172` |
| POST `/dashboard/login` | Portal anmelden | Credentials | `DashboardLoginRequest` → JSON/Cookie | Tokenhash; Dashboardtests; `dashboard.py:208` |
| POST `/dashboard/logout` | Session beenden | Dashboard | – → JSON/Cookie-Löschung | `dashboard.py:229` |
| GET `/dashboard/tenants` | Mitgliedschaften | Dashboard | – → JSON | Membershipmodell; Multi-Tenant-Tests; `dashboard.py:236` |
| GET `/dashboard/tenant/{tenant_id}` | Tenantkontext | Dashboard + Membership | Pfad → JSON | Membership/Access; Multi-Tenant-Tests; `dashboard.py:251` |
| POST `/dashboard/tenant/switch` | Tenant wechseln | Dashboard + Membership | `DashboardTenantSwitchRequest` → JSON | Membership; Multi-Tenant-Tests; `dashboard.py:273` |
| POST `/dashboard/analytics-token` | Embedtoken aus Session | Dashboard + aktiver Tenant | – → JSON | Analytics Token; Embedtests; `dashboard.py:307` |
| GET `/analytics/get-token` | Embedtoken aus BC | Tenant + exakter BC-Kontext | Query → JSON | Access/Product License; Embed-/P0A-/P0D-Tests; `analytics.py:1516` |
| GET `/analytics/embed/data` | Dashboarddaten | Embed | Query → JSON | Pricing/Translation/Access; Dashboard-/Licensingtests; `analytics.py:1586` |
| GET `/analytics/embed/{section}` | Abschnittsdaten | Embed + Capability | Pfad/Query → JSON | Analytics Payload; Dashboardtests; `analytics.py:1663` |
| POST `/analytics/billing/checkout` | Checkout aus Dashboard | Embed | JSON → JSON | Stripe/Pricing; Licensingtests; `analytics.py:1715` |
| POST `/analytics/billing/portal` | Portal aus Dashboard | Embed | JSON → JSON | Stripe; Billingtests; `analytics.py:1749` |
| GET `/analytics/embed` | Analytics-Shell | Einmal-Token→Cookie oder Embedcookie | Query → HTML | Jinja; Embed-Securitytests; `analytics.py:1818` |

## Executive Reports

| Methode/Route | Zweck | Auth/Tenant | Request → Response | Services/Tests/Implementierung |
|---|---|---|---|---|
| GET `/executive/{scan_id}` | strukturierter Report | Tenant/Produktzugriff | Pfad/Language → `ExecutiveReport` | Executive Report Service; Reporttests; `reports.py:113` |
| POST `/executive/{scan_id}/share-link` | Shared Link erzeugen | Tenant/Produktzugriff | `ExecutiveReportShareLinkRequest` → Response | Token/Service; Reporttests; `reports.py:121` |
| GET `/executive/{scan_id}/html` | HTML-Report | Tenant/Produktzugriff | Pfad/Language → HTML | Jinja/Service; Reporttests; `reports.py:144` |
| GET `/executive/{scan_id}/html/shared` | geteiltes HTML | Sharetoken | Query → HTML | Token/Service; Reporttests; `reports.py:154` |
| GET `/executive/{scan_id}/pdf` | PDF | Tenant/Produktzugriff | Pfad/Language → PDF | Playwright; Reporttests; `reports.py:164` |
| GET `/executive/{scan_id}/pdf/shared` | geteiltes PDF | Sharetoken | Query → PDF | Playwright/Token; Reporttests; `reports.py:178` |

## Öffentliche und Partner-Routen

| Methode/Route | Zweck | Auth/Tenant | Request → Response | Services/Tests/Implementierung |
|---|---|---|---|---|
| GET `/pricing/public` | aktive Produktpreise | keine | Query → `PublicProductPricingResponse` | Pricing; `test_pricing.py`; `public.py:62` |
| GET `/landingpage/pages/visibility` | sichtbare Seiten | keine | – → `PublicLandingpageVisibilityResponse` | Visibility; Tests; `public.py:71` |
| GET `/public/loss-examples-config` | Kostenparameter | keine | – → Response | Cost/Pricing; Tests; `public.py:77` |
| POST `/partners` | Partner anlegen (älterer öffentlicher Vertrag) | keine/Validierung | `PartnerCreateRequest` → Response | Partner Service; `partners.py:335` |
| POST `/api/partners/auth/login` | Partnerlogin | Credentials | LoginRequest → JWT-Response | Token/Partner; `partners.py:367` |
| POST `/api/partners/auth/set-credentials` | Initialcredentials | SetCredentialsRequest → Response | Reset-/Setup-Token | Partner Service; `partners.py:396` |
| POST `/api/partners/auth/reset/confirm` | Reset bestätigen | Resettoken | ResetConfirmRequest → JSON | Partner/SMTP; `partners.py:432` |
| POST `/api/partners/auth/reset/request` | Reset anfordern | Rate/Identifier | ResetRequest → JSON | SMTP; `partners.py:460` |
| POST `/api/partners/register` | Partnerantrag | keine/Validierung | RegisterRequest → JSON | Partner/SMTP; `partners.py:487` |
| GET `/api/partners/me` | Partnerprofil | Partner Bearer | – → `PartnerMeResponse` | Partner Service; `partners.py:530` |
| POST `/api/partners/me/profile` | Profil ändern | Partner Bearer | ProfileRequest → Response | Partner Service; `partners.py:542` |
| GET `/api/partners/me/referrals` | Referrals | Partner Bearer | – → Liste | Partner Service; `partners.py:572` |
| GET `/api/partners/me/commissions` | Provisionen | Partner Bearer | – → Liste | Partner Service; `partners.py:613` |
| POST `/partners/referral/attach` | Referral an Tenant binden | Tenant | AttachRequest → Response | Partner Service; `partners.py:640` |
| GET `/partners/referral/status` | Referralstatus | Tenant | – → Response | Partner Service; `partners.py:676` |

## Admin-Routen

Alle folgenden Deklarationen liegen in `backend/app/routers/admin.py`, verwenden Admin-Basic-Auth; POST-Routen prüfen Formular/CSRF und schreiben bei relevanten Mutationen `AdminAuditEvent`. GET antwortet HTML oder CSV, POST nutzt Formfelder und antwortet Redirect/HTML. Tests: primär `test_admin.py`, `test_pricing.py`, `test_localization.py`, `test_landingpage_visibility.py`.

### GET, HTML

- `/admin` (Übersicht)
- `/admin/tenants` und `/admin/tenants/` (Tenantliste)
- `/admin/tenants/{tenant_id}` und `/admin/tenants/{tenant_id}/` (Detail)
- `/admin/config/issue-costs` und `/admin/config/issue-costs/`
- `/admin/config/license-pricing` und `/admin/config/license-pricing/`
- `/admin/partners` und `/admin/partners/`
- `/admin/partners/commissions` und `/admin/partners/commissions/`
- `/admin/partners/applications` und `/admin/partners/applications/`
- `/admin/commissions/payouts` und `/admin/commissions/payouts/`
- `/admin/audit` und `/admin/audit/`
- `/admin/config/email-templates` und `/admin/config/email-templates/`
- `/admin/config/site-translations` und `/admin/config/site-translations/`
- `/admin/config/dashboard-translations` und `/admin/config/dashboard-translations/`
- `/admin/config/landingpage-pages` und `/admin/config/landingpage-pages/`

### GET, CSV

- `/admin/partners/applications.csv`
- `/admin/commissions/payouts.csv`

### POST, Tenant/Lizenz

- `/admin/tenants/{tenant_id}/license`, `/admin/tenant/{tenant_id}/grant-product`, `/admin/tenants/{tenant_id}/product-grant`, `/admin/tenant/{tenant_id}/revoke-product`
- `/admin/tenant/{tenant_id}/add-credit`, `/admin/tenant/{tenant_id}/remove-credit`, `/admin/tenant/{tenant_id}/reset-credits`, `/admin/tenant/{tenant_id}/extend-access`
- `/admin/tenant/{tenant_id}/enable-monitoring`, `/admin/tenant/{tenant_id}/disable-monitoring`, `/admin/tenant/{tenant_id}/reset-licensing`, `/admin/tenant/{tenant_id}/reset-registration`
- `/admin/tenants/{tenant_id}/delete`, `/admin/tenants/{tenant_id}/referral`

### POST, Konfiguration/E-Mail

- `/admin/config/issue-costs/hourly-rate`, `/admin/config/issue-costs/{code}`
- `/admin/config/product-pricing/{product_key}`, `/admin/config/product-pricing-matrix/{product_key}/{pricing_tier}`
- `/admin/config/email-templates/{template_key}`, `/admin/config/email-templates/{template_key}/test-send`
- `/admin/config/site-translations`, `/admin/config/dashboard-translations`
- `/admin/landingpage/pages`, `/admin/config/landingpage-pages` (Aliasverträge)

### POST, Partner/Provision

- `/admin/commissions/{commission_id}/status`, `/admin/commissions/payouts/close`
- `/admin/partners/create`, `/admin/partners/{partner_id}/update`, `/admin/partners/{partner_id}/credentials`, `/admin/partners/{partner_id}/reset-link`, `/admin/partners/{partner_id}/delete`
- `/admin/partners/applications/{application_id}/status`

## Manuell zu prüfen

OpenAPI-Schema, Statuscodes und reale Clientkompatibilität sollten gegen eine laufende Instanz exportiert werden; diese Datei leitet keine nicht implementierten Endpunkte aus Frontendaufrufen ab.
