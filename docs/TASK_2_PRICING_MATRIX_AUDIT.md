# Task 2 Pricing Matrix Audit

Datum: 2026-06-16

## Ziel

Task 2 bereitet die neue datensatzbasierte Pricing Matrix fuer BCSentinel vor und integriert sie in Backend, Admin, Dashboard, Checkout-Vorbereitung und Landingpage. Es wurden keine Stripe-Produkte angelegt und keine bestehenden Daten geloescht.

## Pricing Tiers

| Tier | Datensaetze |
| --- | ---: |
| starter | bis 100.000 |
| professional | bis 250.000 |
| business | bis 500.000 |
| enterprise | ab 500.001 / Contact Sales |

Die Berechnung nutzt weiterhin den neuesten Deep-Scan-`total_records`-Wert.

## Matrix Defaults

| Produkt | starter | professional | business | enterprise |
| --- | ---: | ---: | ---: | --- |
| Full Analysis | EUR 79 | EUR 99 | EUR 129 | Contact Sales |
| Validation Check | EUR 49 | EUR 79 | EUR 99 | Contact Sales |
| Monitoring Monthly | EUR 149 | EUR 199 | EUR 299 | Contact Sales |
| Monitoring Annual | EUR 1490 | EUR 1990 | EUR 2990 | Contact Sales |

## Implementierung

- Neue Tabelle `product_pricing_matrix_config` mit Produkt, Tier, Max-Records, Betrag, Intervall, Namen, `stripe_price_id`, Aktiv-Flag und Timestamp.
- Neue Migration: `backend/alembic/versions/0019_product_pricing_matrix.py`.
- Admin-Bereich erweitert um editierbare Matrix-Zeilen inklusive Stripe Price ID je Produkt/Tier.
- Public Pricing API liefert weiterhin eine einfache Landingpage-Zusammenfassung:
  - Data Health Score: kostenlos
  - Full Analysis: ab EUR 79
  - Validation Check: ab EUR 49
  - Monitoring: ab EUR 149 / Monat
- Optional kann `/pricing/public?include_matrix=true` die aktive Matrix fuer Transparenz liefern.
- Checkout loest jetzt anhand von Produkt und Record Count die Matrix-Zeile auf.
- Enterprise-Tiers werden als Contact Sales vor Stripe blockiert.
- Wenn eine Matrix-Zeile keine Stripe Price ID hat, bleibt ein vorhandener Legacy-ENV-Fallback nutzbar; produkt-/tierbezogene Matrix-IDs haben Vorrang.
- Dashboard-Payload enthaelt `tenant_pricing` mit exakten Preisen fuer den aktuellen Tenant-Tier.
- Subscription-Ansicht zeigt den konkreten Monitoring-Monats- und Jahrespreis bzw. Contact Sales auch vor aktivem Monitoring.
- Landingpage-Fallbacks und statische Preise wurden auf die neuen Startpreise aktualisiert.

## Nicht umgesetzt

- Keine Stripe-Produkte oder Stripe-Prices wurden erstellt.
- Keine Bestandsdaten wurden geloescht.
- Keine destruktiven Docker- oder Datenbankaktionen wurden ausgefuehrt.

## Verifikation

- `python -m pytest backend\tests\test_product_licensing_p0.py backend\tests\test_pricing.py backend\tests\test_billing.py backend\tests\test_admin.py`
  - Ergebnis: 76 passed, 37 warnings.
- `node --check landingpage\script.js`
- `node --check landingpage_neu\assets\js\pricing.js`
- `node --check landingpage_neu\assets\js\config.js`
- `python -m py_compile` fuer geaenderte Backend-Module und Migration.
