# LP-GL-07 — Pricing and Conversion Journey

## Scope

- Replaced the legacy four-card pricing grid with three canonical products: Assessment, Validation, and Monitoring.
- Kept technical product keys such as `full_analysis` and `validation_check` compatible with the public pricing API.
- Grouped monthly and annual Monitoring in one product card.
- Added explicit scan-credit, access-window, billing, B2B, and tax information.
- Clarified the intended customer journey: Assessment → remediation → Validation → Monitoring.
- Preserved the existing Business Central-led purchase path and separated it from pilot and enterprise contact flows.

## Pricing behavior

The visible prices continue to use `GET /pricing/public` with `pricing-snapshot.js` as the static fallback. A dedicated runtime synchronizer updates dynamically inserted price nodes and reacts to language changes.

Mappings:

- `full_analysis` → visible Assessment
- `validation_check` → visible Validation
- `monitoring` / `monitoring_monthly` → monthly Monitoring
- `monitoring_annual` → annual Monitoring

## Access model shown to customers

- Assessment: one scan credit and seven days of dashboard, findings, and report access.
- Validation: one scan credit and a new seven-day access period.
- Monitoring: access remains active while the subscription is active.

## CTA behavior

The pricing cards route to the existing contact/onboarding page with a product query parameter. This avoids inventing a direct web checkout before the intended Business Central purchase flow has been fully validated.

## Safety and trust

- Prices are identified as B2B list prices in EUR.
- Potential statutory taxes are disclosed.
- Checkout or contract terms remain authoritative.
- No unsupported discount or cancellation promise was added.
- Annual Monitoring is described as including two months based on the current EUR 149 monthly / EUR 1,490 annual relationship.

## Files

- `landingpage/css/pricing-conversion-journey.css`
- `landingpage/js/pricing-conversion-journey.js`
- `landingpage/js/pricing-runtime-sync.js`
- `landingpage/js/product-proof.js`
- `landingpage/pricing-snapshot.js`
- `scripts/generate_landing_pricing.py`
