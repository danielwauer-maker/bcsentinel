# LP-GL-11A — Translation & Content Management

## Goal

Provide one consistent DE/EN content contract for the redesigned landing page, remove mixed-language product mockups, preserve static fallbacks, and prepare an explicit integration point for published Admin Backend content.

## Implemented

- Added centralized locale payloads:
  - `landingpage/lang/redesign.de.json`
  - `landingpage/lang/redesign.en.json`
- Added `landingpage/js/content-runtime.js`.
- Refactored Product Story and Product Proof to consume the centralized payload.
- Localized process steps, finding examples, severity labels, dashboard navigation, report labels, and product-preview copy.
- Added a DE/EN parity validator: `scripts/validate_landing_translations.py`.

## Runtime priority

1. Published content endpoint, when configured.
2. Versioned static locale payload.
3. Existing page remains readable if no Admin endpoint is configured.

The optional published endpoint is configured through either:

```html
<meta name="bcsentinel-landing-content-endpoint" content="/public/landing-content" />
```

or:

```js
window.BCSENTINEL_LANDING_CONTENT_ENDPOINT = "/public/landing-content";
```

The runtime sends the selected language as the `locale` query parameter and deep-merges a valid published response over the static fallback.

## Admin Backend status

No authoritative public Landing Content endpoint could be verified through the currently discoverable repository search. The runtime therefore does not invent or hard-code an API path. The next backend integration step must map the existing Admin translation publishing workflow to this explicit endpoint contract.

## Localized product preview

German mode now uses, among others:

- Verbinden / Prüfen / Priorisieren / Verbessern
- Übersicht / Maßnahmen / Datenqualität
- Priorisierte Findings
- Kreditoren-Bankverbindungen
- Kunden ohne Zahlungsbedingungen
- Inaktive Artikel in offenen Belegen
- Kritisch / Hoch / Mittel
- Betroffene Datensätze

Canonical product terms such as Assessment, Validation, Monitoring, Health Score, Estimated Loss, Potential Saving, and Executive Report remain intentionally stable.

## Validation

Run:

```bash
python scripts/validate_landing_translations.py
```

The validator fails on:

- missing DE or EN paths,
- empty values,
- visible translation-key fallbacks.

## Remaining scope

The first implementation wave covers the Product Story and Product Proof areas where mixed-language content was visible. Pricing, Security, Audience, FAQ, Footer, Loss Examples, metadata, alt text, and remaining subpages must be migrated to the same central contract before LP-GL-11A is considered fully complete.
