# Task 1.1 Product Model v2.0 Audit

## Gefundene Objekte

- Produkt-/Entitlement-Logik: `backend/app/services/product_license_service.py`
- Product Pricing Config: `backend/app/services/product_pricing_service.py`, Tabelle `product_pricing_config`
- License-Status-API: `backend/app/routers/license.py`
- Billing/Checkout/Webhooks: `backend/app/routers/billing.py`
- Tenant-, Scan-, Subscription-, Purchase-, Credit- und Entitlement-Tabellen: `backend/app/models.py`
- Dashboard-Gating: `backend/app/routers/analytics.py`, `backend/app/static/js/analytics-dashboard.js`
- Admin-Tenant-Detail und Product Pricing UI: `backend/app/routers/admin.py`, `backend/app/templates/admin_tenant_detail.html`
- BC Extension License Refresh/Checkout/Setup: `bc-extension/app/src/codeunits/DHApiClient.Codeunit.al`, `bc-extension/app/src/pages/DHSetup.Page.al`
- Landingpage Pricing/Public Pricing: `landingpage/script.js`, `landingpage/lang/*.json`, `landingpage_neu/assets/js/config.js`, `landingpage_neu/assets/js/pricing.js`
- Tests: `backend/tests/test_product_licensing_p0.py`, `backend/tests/test_pricing.py`, bestehende Billing/Admin/Access-Tests

## Wiederverwendung

- `TenantScanCredit`, `TenantProductPurchase` und `TenantProductEntitlement` bleiben die Grundlage fuer 7-Tage-Produkte.
- `Subscription` bleibt die Grundlage fuer Monitoring Monthly/Annual.
- `Scan.total_records` wird als vorhandene Datensatzbasis fuer Pricing Tiers verwendet. Es wurde keine neue Spalte angelegt.
- `assessment_access_active`, `validation_access_active`, `dashboard_access_until`, `issue_access_until`, `can_view_dashboard` und `can_view_issue_details` bleiben als Backward-Compatible-Felder erhalten.
- `STRIPE_PRICE_ID_ASSESSMENT` bleibt als vorhandene Preis-ID-Konfiguration fuer Full Analysis nutzbar, ohne neue Stripe-Produkte anzulegen.

## Produktmodell v2.0

- Neu vorbereitet: `data_health_score`
- Neu kanonisch: `full_analysis`
- Weiterhin eigenstaendig: `validation_check`
- Weiterhin eigenstaendig: `monitoring_monthly`
- Weiterhin eigenstaendig: `monitoring_annual`
- Legacy-Alias: `assessment` wird intern zu `full_analysis` normalisiert. Alte gespeicherte Credits, Purchases und Entitlements mit `assessment` werden beim Zugriff weiter beruecksichtigt.

## Access Flags

Die License-Status-Antwort liefert zusaetzlich:

- `can_view_free_insights`
- `can_view_issues`
- `can_view_actions`
- `can_view_reports`
- `can_view_record_details`
- `can_use_monitoring`
- `full_analysis_access_active`
- `validation_check_access_active`
- `premium_access_until`
- `record_count`
- `pricing_tier`

Free Insights werden aktiv, sobald mindestens ein Scan-Ergebnis fuer den Tenant existiert. Premium-Details bleiben ohne Full Analysis, Validation Check oder Monitoring gesperrt.

## Pricing Tiers

Die Tier-Funktion ist vorbereitet:

- `starter`: bis 100000 Datensaetze
- `professional`: bis 250000 Datensaetze
- `business`: bis 500000 Datensaetze
- `enterprise`: ueber 500000 Datensaetze

Die Berechnung basiert auf dem neuesten `Scan.total_records`. Eine Stripe-Preiszuordnung oder Matrix-Pricing-Engine wurde nicht eingefuehrt.

## Risiken

- Bestehende produktive `product_pricing_config`-Zeilen mit `assessment` bleiben in der Datenbank bestehen, werden aber in der Public-Pricing-Ausgabe zugunsten von `full_analysis` ausgeblendet.
- Landingpage und BC Extension enthalten noch einzelne historische Textstellen ausserhalb der zentralen Pricing-/Checkout-Pfade. Diese sollten in einem Content-Cleanup separat konsolidiert werden.
- Die Voraussetzung "Validation Check nur nach Full Analysis" wird noch nicht hart erzwungen. Der Code trennt das Produkt fachlich, laesst aber bestehende Kauf-/Admin-Flows unveraendert.
- Free-Scan-Endpoint und finaler Free-Insights-Datenschnitt sind noch nicht implementiert.

## Offene Folge-Tasks

- Task 2: Free-Scan-/Free-Insights-Flow fachlich komplett definieren und API/UI-seitig umsetzen.
- Full Analysis und Validation Check in Stripe final anlegen oder bestehende Price IDs bewusst mappen.
- Validation-Check-Voraussetzung gegen historische Full Analysis/Purchase/Scan-Daten durchsetzen.
- Pricing-Tier-Logik an finale Stripe-/Admin-Matrix anbinden.
- Landingpage-Texte und BC XLIFF-Translations vollstaendig redaktionell nachziehen.
- Dashboard gezielt auf Free-Insights-Ansicht mit Top 5 Findings, Top 5 Business Impacts und gesperrten Detailbereichen ausbauen.
