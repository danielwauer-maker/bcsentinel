# LP-GL-05 — Product Story and Business Impact

## Goal

Replace the legacy problem, impact, solution, and workflow sections on the start page with one coherent enterprise narrative that explains why Business Central data quality matters, how Estimated Loss is derived, how BCSentinel works, and how Assessment, Validation, and Monitoring form a connected lifecycle.

## Implemented

- New bilingual problem and business-impact section.
- Illustrative cost-of-poor-data breakdown with explicit example labeling.
- Dedicated Estimated Loss transparency section.
- Clear separation between directly measured values and model assumptions.
- Concrete calculation example linked to `loss-examples.html`.
- Simplified four-step customer process: Connect, Assess, Prioritize, Improve.
- Product lifecycle for Assessment, Validation, and Monitoring.
- Responsive desktop, tablet, and mobile layouts.
- Start-page-only runtime integration without changing other landingpage pages.
- Legacy sections are removed at runtime only after the new hero/trust strip is present.

## Design principles

- Business impact is explained without presenting illustrative values as guaranteed savings or losses.
- Assessment remains the recommended entry point.
- Validation is positioned as a distinct post-remediation product, not a smaller package.
- Monitoring is positioned as continuous governance and control.
- The Estimated Loss example visibly identifies measured values and assumptions.

## Files

- `landingpage/css/product-story-business-impact.css`
- `landingpage/js/product-story-business-impact.js`
- `landingpage/js/hero-conversion-core.js`

## Validation notes

- The module is loaded by the existing hero conversion core, so no additional direct script tag is required in `index.html`.
- The module only runs for `/` and `/index.html`.
- Existing pricing, security, partner, FAQ, final CTA, footer, pricing API fallback, language switch, and theme switch remain available.
- `loss-examples.html` remains the canonical deep-dive page for calculation methodology.
