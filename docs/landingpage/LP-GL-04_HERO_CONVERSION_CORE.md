# LP-GL-04 — Hero and Conversion Core

Status: Implemented on `landingpage-redesign-01`

## Goal

Replace the weak first-screen experience with a credible enterprise SaaS hero while preserving the existing pricing, language, theme and downstream landingpage sections.

## Implemented

- Light enterprise hero with controlled navy, blue and orange palette
- German and English hero copy
- Primary CTA to Assessment pricing
- Secondary proof CTA to `loss-examples.html`
- Product composition showing dashboard KPIs, findings and executive report
- Trust strip below the hero
- Header-level Assessment CTA
- Responsive desktop, tablet and mobile layouts
- Keyboard-visible focus states
- Reduced-motion handling
- Canonical fallback product names for Assessment and Validation
- Generator persistence for the pricing snapshot bootstrap

## Current conversion hierarchy

1. `Assessment starten` / `Start assessment`
2. `Estimated Loss verstehen` / `Understand Estimated Loss`
3. Header Assessment CTA

The sample-report download is deliberately deferred until a verified local PDF asset exists. No broken placeholder link is shipped.

## Technical integration

The hero is isolated in:

- `landingpage/css/hero-conversion-core.css`
- `landingpage/js/hero-conversion-core.js`

The existing `pricing-snapshot.js` bootstraps the homepage-only module. The generator was updated so regeneration preserves this behavior and the canonical visible product names.

## Safety

- No change to `main`
- No change to production
- No change to `arch-02a-product-model-alignment`
- Existing lower landingpage sections remain available
- Existing public pricing data and fallback object shape remain compatible
- Internal technical code `full_analysis` remains unchanged

## Follow-up

LP-GL-05 should replace the legacy problem and business-impact sections with the approved enterprise storytelling and a full Estimated Loss example block.
