# BCSentinel Landingpage Phase 1

Neue Landingpage-Struktur fuer die Phase-1-Seiten. Die bestehende `landingpage/` bleibt unveraendert.

## Seiten

- `index.html`
- `pricing.html`
- `about.html`
- `trust.html`
- `support.html`
- `contact.html`
- `executive-reports.html`
- `why-bcsentinel.html`

## Laufzeitverhalten

- Sprache: `assets/js/i18n.js` laedt `lang/de.json` und `lang/en.json`.
- Theme: `assets/js/theme.js` speichert den Modus in `localStorage`.
- Pricing: `assets/js/pricing.js` laedt `/pricing/public` und nutzt bei Fehlern Fallback-Werte fuer `assessment`, `validation_check`, `monitoring_monthly` und `monitoring_annual`.
- Sichtbarkeit: `assets/js/visibility.js` laedt `/landingpage/pages/visibility`. Ist die API nicht erreichbar, bleiben alle Seiten sichtbar.
- Deaktivierte Seiten: Direkte Aufrufe werden clientseitig nach `index.html` umgeleitet. Home ist im Admin geschuetzt sichtbar.
- Checkout-CTAs: Buttons behalten die Produktcodes ueber `data-product-code` und `data-checkout-product`. Der eigentliche Checkout bleibt mandantenautorisiert im bestehenden Business-Central-/Dashboard-Flow.
- Kontaktformular: Frontendseitig vorbereitet. Im bestehenden Backend wurde kein dedizierter oeffentlicher Kontakt-Endpunkt gefunden.

## Smoke Checks

Ausgefuehrt:

- `python -m pytest backend\tests\test_landingpage_visibility.py backend\tests\test_pricing.py`
- HTML-i18n-Key-Abdeckung fuer alle neuen Seiten
- JSON-Validitaet fuer `lang/de.json` und `lang/en.json`
- Legacy-Begriff-Scan in `landingpage_neu/`
- Lokaler HTTP-Smoke-Check fuer `index.html`, `pricing.html`, `lang/de.json` und `assets/js/site-shell.js`

Hinweis: Die in-app Browser-Verifikation wurde versucht, war aber in dieser Windows-Sandbox durch den Browser-Start blockiert.
