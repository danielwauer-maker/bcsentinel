# Billing E2E Test Matrix

Datum: 2026-06-10

Status: CODE VERIFIED / LIVE E2E NOT EXECUTED.

Diese Matrix beschreibt den Go-Live-relevanten Billing-E2E-Stand fuer die aktuelle Produktstruktur. Stripe und pytest wurden in dieser Umgebung nicht live ausgefuehrt, weil `python`, `pytest`, `docker`, `alembic` und Stripe CLI nicht verfuegbar waren.

## Aktuelle Preisquelle

Zentrale Quelle ist Product Pricing:

- Admin UI: `/admin/config/license-pricing` zeigt Product Pricing.
- API: `GET /pricing/public`
- Model: `ProductPricingConfig`
- Defaults/Seed: `backend/app/services/product_pricing_service.py` und Alembic `0016_product_pricing_config.py`
- Landingpage: laedt `GET /pricing/public`, Fallback in `landingpage/script.js` und `landingpage/pricing-snapshot.js`
- Dashboard: nutzt Monitoring Pricing Breakdown aus Product Pricing.

Alte License-Pricing-/Plan-Pricing-Strecken werden nicht mehr fuer neue Billing-Flows verwendet.

## Produkte und Zielpreise

| Produkt | product_code | Preis | Intervall | Stripe ENV | Checkout Mode | Status |
|---|---|---:|---|---|---|---|
| Assessment | `assessment` | EUR 79 | one_time | `STRIPE_PRICE_ID_ASSESSMENT` | payment | CODE VERIFIED |
| Validation Check | `validation_check` | EUR 49 | one_time | `STRIPE_PRICE_ID_VALIDATION_CHECK` | payment | CODE VERIFIED |
| Monitoring Monthly | `monitoring_monthly` | EUR 99 / Monat | month | `STRIPE_PRICE_ID_MONITORING_MONTHLY` | subscription | CODE VERIFIED |
| Monitoring Annual | `monitoring_annual` | EUR 990 / Jahr | year | `STRIPE_PRICE_ID_MONITORING_ANNUAL` | subscription | CODE VERIFIED |

Hinweis: Stripe Price IDs bleiben in ENV. Wenn Stripe-Prices andere Betraege enthalten, muss Stripe manuell angepasst werden. Der Code zeigt weiterhin die Product-Pricing-Preise aus DB/API an.

Wenn genau ein Produkt mit HTTP 503 fehlschlaegt, ist in DEV/PROD sehr wahrscheinlich die zugehoerige Stripe Price ID nicht gesetzt. Beispiel: Assessment braucht `STRIPE_PRICE_ID_ASSESSMENT`. Nach ENV-Aenderungen muss der Backend-Container neu gestartet werden.

## Checkout Tests

| Check | Assessment | Validation Check | Monitoring Monthly | Monitoring Annual |
|---|---|---|---|---|
| Request nutzt `product_code` | CODE VERIFIED | CODE VERIFIED | CODE VERIFIED | CODE VERIFIED |
| Alter `plan_code` Checkout-Fallback entfernt | CODE VERIFIED | CODE VERIFIED | CODE VERIFIED | CODE VERIFIED |
| Stripe Price ID aus ENV | CODE VERIFIED | CODE VERIFIED | CODE VERIFIED | CODE VERIFIED |
| Checkout Mode | CODE VERIFIED payment | CODE VERIFIED payment | CODE VERIFIED subscription | CODE VERIFIED subscription |
| Metadata enthaelt Tenant | CODE VERIFIED | CODE VERIFIED | CODE VERIFIED | CODE VERIFIED |
| Metadata enthaelt Product | CODE VERIFIED | CODE VERIFIED | CODE VERIFIED | CODE VERIFIED |
| Success URL | CODE VERIFIED config-basiert | CODE VERIFIED config-basiert | CODE VERIFIED config-basiert | CODE VERIFIED config-basiert |
| Cancel URL | CODE VERIFIED config-basiert | CODE VERIFIED config-basiert | CODE VERIFIED config-basiert | CODE VERIFIED config-basiert |
| Stripe Redirect Success | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED |
| Stripe Redirect Cancel | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED |

## Webhook Tests

| Check | Assessment | Validation Check | Monitoring Monthly | Monitoring Annual |
|---|---|---|---|---|
| `checkout.session.completed` erkannt | CODE VERIFIED | CODE VERIFIED | CODE VERIFIED | CODE VERIFIED |
| One-time Purchase gespeichert | CODE VERIFIED | CODE VERIFIED | Nicht relevant | Nicht relevant |
| Scan Credit erzeugt | CODE VERIFIED +1 | CODE VERIFIED +1 | Nicht relevant | Nicht relevant |
| Subscription gespeichert | Nicht relevant | Nicht relevant | CODE VERIFIED | CODE VERIFIED |
| Monitoring Entitlement aktiv | Nicht relevant | Nicht relevant | CODE VERIFIED | CODE VERIFIED |
| Duplicate Webhook Schutz | CODE VERIFIED | CODE VERIFIED | CODE VERIFIED | CODE VERIFIED |
| Stripe Signaturpruefung | CODE VERIFIED | CODE VERIFIED | CODE VERIFIED | CODE VERIFIED |
| Live Stripe Webhook | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED |

## Erwartete DB-/License-Auswirkungen

| Produkt | Erwartete DB-Auswirkung | Erwartete License API |
|---|---|---|
| Assessment | `TenantProductPurchase`, `TenantScanCredit` +1, Access Window 7 Tage | `scan_credits_available >= 1`, `assessment_access_active`, Dashboard/Issue/Report Access |
| Validation Check | `TenantProductPurchase`, `TenantScanCredit` +1, Access Window 7 Tage | `scan_credits_available >= 1`, `validation_access_active`, Dashboard/Issue/Report Access |
| Monitoring Monthly | `Subscription`, `TenantProductEntitlement`, Monitoring aktiv | `monitoring_active=true`, wiederholte Scans, Dashboard/Issue/Report Access |
| Monitoring Annual | `Subscription`, `TenantProductEntitlement`, Monitoring aktiv | `monitoring_active=true`, wiederholte Scans, Dashboard/Issue/Report Access |

Status: CODE VERIFIED, live DB-Pruefung NOT EXECUTED.

## Erwartete Anzeige

| UI | Assessment | Validation Check | Monitoring Monthly | Monitoring Annual | Status |
|---|---|---|---|---|---|
| Admin Product Pricing | sichtbar/editierbar | sichtbar/editierbar | sichtbar/editierbar | sichtbar/editierbar | CODE VERIFIED |
| Admin Audit | Preisupdate loggt vorher/nachher | Preisupdate loggt vorher/nachher | Preisupdate loggt vorher/nachher | Preisupdate loggt vorher/nachher | CODE VERIFIED |
| Public Pricing API | EUR 79 | EUR 49 | EUR 99 | EUR 990 | CODE VERIFIED |
| Landingpage Pricing Cards | API-first, Fallback korrekt | API-first, Fallback korrekt | API-first, Fallback korrekt | API-first, Fallback korrekt | CODE VERIFIED |
| Billing Success | produktneutral | produktneutral | produktneutral | produktneutral | CODE VERIFIED |
| Billing Cancel | produktneutral | produktneutral | produktneutral | produktneutral | CODE VERIFIED |
| Dashboard | Buy Assessment / Credits | Buy Assessment / Credits | Start/Manage Monitoring | Start/Manage Monitoring | CODE VERIFIED |
| BC Setup | Checkout Actions vorhanden | Checkout Actions vorhanden | Checkout Action vorhanden | Checkout Action vorhanden | CODE VERIFIED, AL compile NOT EXECUTED |

## Manuelle Live-Testschritte pro Produkt

1. DEV sauber starten und Migrationen auf Head bringen.
2. Testtenant registrieren.
3. Product Pricing im Admin pruefen.
4. `GET /pricing/public` pruefen.
5. Checkout Session mit `product_code` starten.
6. Stripe Checkout Success testen.
7. Stripe Checkout Cancel testen.
8. Stripe Webhook an `/billing/webhook` senden.
9. License Status in Backend und BC Setup refreshen.
10. Dashboard/Issue/Report Access pruefen.
11. Admin Audit pruefen.
12. Bei Monitoring: Customer Portal und Subscription Cancel pruefen.

## Container-Teststrategie

Production Images sollen keine Tests enthalten. Deshalb gibt es im Dockerfile getrennte Targets:

- `runtime`: API Runtime ohne Tests.
- `test`: basiert auf Runtime und kopiert `backend/tests` nach `/app/tests`.
- `production`: testfreier Default-/PROD-Target.

DEV Compose stellt dafuer den Service `backend-tests` bereit.

Pflichtbefehle auf DEV:

```bash
docker compose --env-file .env.dev -f docker-compose.dev.yml run --rm backend-tests python -m pytest -p no:cacheprovider tests/test_product_licensing_p0.py
docker compose --env-file .env.dev -f docker-compose.dev.yml run --rm backend-tests python -m pytest -p no:cacheprovider tests/test_billing.py
docker compose --env-file .env.dev -f docker-compose.dev.yml run --rm backend-tests python -m pytest -p no:cacheprovider tests/test_executive_report.py
docker compose --env-file .env.dev -f docker-compose.dev.yml run --rm backend-tests python -m pytest -p no:cacheprovider tests/test_localization.py
```

Aktueller Status:

| Testdatei | Status | Hinweis |
|---|---|---|
| `tests/test_product_licensing_p0.py` | NOT EXECUTED | Container-Testservice vorbereitet |
| `tests/test_billing.py` | NOT EXECUTED | Enthaelt noch alte Planmodell-Testannahmen und muss ggf. auf `product_code` aktualisiert werden |
| `tests/test_executive_report.py` | NOT EXECUTED | Container-Testservice vorbereitet |
| `tests/test_localization.py` | NOT EXECUTED | Container-Testservice vorbereitet |

## Aktueller Befund zu alten Begriffen

CODE VERIFIED:

- Neuer Checkout benoetigt `product_code`.
- Alter `plan_code` Checkout-Fallback wurde entfernt.
- Alte Stripe ENV-Fallbacks fuer Monitoring wurden entfernt.
- Alte `/public/pricing` Plan-Pricing API wurde entfernt; gueltig ist `/pricing/public`.
- Admin zeigt keine Compatibility-Pricing-Box mehr.

NOT FULLY REMOVED:

- BC Extension enthaelt weiterhin alte AL-Feld-/Enum-/Objektnamen fuer das fruehere Planmodell.
- Einige Backend-Modelle und alte Tests nutzen noch `current_plan`, `license_status` und alte Testdaten.
- Vollstaendige Entfernung benoetigt einen separaten Schema-/AL-Migrationsblock.

## Go/No-Go

Billing Code Readiness: GO nach Code Review, aber Tests muessen in einer Python/Docker-Umgebung laufen.

Billing Live E2E: NO-GO bis Stripe Checkout und Webhooks mindestens fuer ein one-time Produkt und ein Monitoring-Produkt live getestet sind.
