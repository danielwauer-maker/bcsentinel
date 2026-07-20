# Frontend-Routen und Seiten

## Customer Dashboard

Serverrouten: `/dashboard`, `/dashboard/invite`, `/analytics/embed`. Portal-Template: `backend/app/templates/dashboard_portal.html`. Analytics-Shell: `analytics_embed.html`; clientseitige Tabs `overview`, `analytics`, `scans`, `issues`, `actions`, `reports`, `subscription`, `settings` in `backend/app/static/js/analytics-dashboard.js`. Datenquelle ist `/analytics/embed/data` plus Abschnitts-, Billing- und Reportrouten. Loading-, Empty-, Error- und Locked-States sind im JS/CSS nachweisbar. Authentifizierung/Multi-Tenant-Auswahl: `dashboard.py`.

## Admin

Serverseiten: `/admin`, Tenantliste/-detail, Issue Costs, License/Product Pricing, Partner, Commissions/Payouts, Applications, Audit, E-Mail-Templates, Site-/Dashboard-Translations und Landingpage-Visibility. Templates: `admin_tenants.html`, `admin_tenant_detail.html`; weitere Views werden in `admin.py` als HTML aufgebaut. CRUD ist für Tenantlizenz/Credits/Produkte, Konfiguration, Partner, Anträge und Provisionen über POST-Routen vorhanden. Eine rollenfeine Adminverwaltung wurde nicht gefunden.

## Ausgelieferte Landingpage (`landingpage/`)

`index.html`, `billing-success.html`, `billing-cancel.html`, `contact.html`, `docs.html`, `help.html`, `impressum.html`, `loss-examples.html`, `partner-login.html`, `partner-portal.html`, `partner-register.html`, `partner-reset-password.html`, `privacy.html`, `security.html`, `support.html`, `terms.html`; DE/EN in `lang/`. `partner-api.js`, Pricing-/Visibility-/Loss-Konfiguration und i18n sind dynamische Quellen; große Teile der Seiteninhalte sind statisches HTML/JSON.

## Alternative Landingpage (`landingpage_neu/`)

`index.html`, `about.html`, `contact.html`, `executive-reports.html`, `pricing.html`, `support.html`, `trust.html`, `why-bcsentinel.html`; eigene Assets und DE/EN. Visibility und Pricing rufen Backend-APIs auf. Keine Einbindung in Docker/Compose/Workflow gefunden: `partial`, nicht `deprecated_or_legacy`.

## Responsive/Localization

Beide Bäume besitzen responsive CSS und Sprachumschaltung im Code. Reale Geräte-/Browserdarstellung und visuelle Qualität sind manuell zu prüfen.
