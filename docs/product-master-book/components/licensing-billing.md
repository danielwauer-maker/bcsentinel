# Lizenzierung, Credits und Billing

## Zusammenfassung
Produktbasierte Berechtigungen für Assessment, Validation und Monitoring plus Stripe-Checkout, Portal und Webhooks.

## Erkannte Verantwortlichkeiten
Preismatrix, Checkout, Subscription/Invoice, Credits/Ledger, Entitlements, Ablaufdaten und License Status.

## Erkannte Unterbereiche
Billing-/License-Router und Billing-, Pricing-, Product-License-, Entitlement- und Access-Control-Services.

## Vorhandene Features
BILL-PRICE-001, BILL-CHECK-001, BILL-WEB-001, BILL-CREDIT-001, BILL-ENT-001, BILL-PORTAL-001.

## Teilweise vorhandene Features
Keine Code-Teilkette; Providerausführung bleibt manuell.

## Stubs oder statische Inhalte
Stripe-Aufrufe sind in Tests gemockt, nicht im Produktcode.

## APIs und Schnittstellen
Stripe SDK, Billingrouten, Analytics-Billingrouten, Admin-Grants und License Status.

## Datenmodelle
Subscription, Invoice, Purchase, Credit, StartRequest, Ledger, Entitlement, WebhookEvent, Pricing.

## Tests
`test_billing.py`, `test_product_licensing_p0.py`, `test_p0b_atomic_credit.py`, `test_pricing.py`.

## Dokumentation
`docs/BILLING_E2E_TEST_MATRIX.md`, `docs/product/pricing*.md`, `config/pricing_canonical.json`.

## Technische Auffälligkeiten
Webhookereignisse werden idempotent persistiert; Creditstart besitzt eigene Request-/Ledger-Tabellen.

## Manuell zu prüfen
Echte Stripe-Produkte/Price IDs, Zahlung, Kündigung, Refund und Webhookzustellung.

## Belegverzeichnis
`backend/app/routers/billing.py`; relevante Services/Modelle/Migrationen.
