# LP-GL-07 — Pricing and Conversion Journey

## Scope

- Replaced the legacy four-card pricing grid with the three canonical paid products: Assessment, Validation, and Monitoring.
- Kept technical product keys such as `full_analysis` and `validation_check` compatible with the public pricing API.
- Grouped monthly and annual Monitoring in one product card.
- Added explicit access-window, scan-right, billing, B2B, and tax information.
- Clarified the intended customer journey: Free Scan → Assessment → Validation → Monitoring.
- Preserved the existing Business Central-led purchase path and separated it from pilot and enterprise contact flows.

## Pricing behavior

The visible prices continue to use `GET /pricing/public` with `pricing-snapshot.js` as the static fallback. A dedicated runtime synchronizer updates dynamically inserted price nodes and reacts to language changes.

Mappings:

- `full_analysis` → visible Assessment
- `validation_check` → visible Validation
- `monitoring` / `monitoring_monthly` → monthly Monitoring
- `monitoring_annual` → annual Monitoring

## Canonical access model shown to customers

### Free Scan

- One free scan if the free slot has not already been consumed.
- Permanent but limited preview after completion.
- Limited insight into Issues, Actions, Dashboard, and Executive Report.
- No full record details.
- No monitoring capabilities.

### Assessment

- No scan credit.
- Unlocks the already generated Full Analysis.
- Seven days of complete access.
- Full Issues, Actions, finding details, record details, Dashboard, Executive Report, Estimated Loss, and Potential Saving.
- No monitoring-specific capabilities.

### Validation

- One new scan credit.
- Intended for a new scan after remediation.
- The updated complete analysis is available for another seven-day period.
- Full Issues, Actions, record details, Dashboard, and Executive Report during the access period.
- No monitoring-specific capabilities.

### Monitoring

- Monthly or annual subscription variant.
- Full analysis access throughout the active subscription period.
- Adds dedicated monitoring capabilities such as scheduled and recurring scans, history, trends, progress comparison, exceptions management, monitoring actions, and full analytics.
- Monitoring is not presented as a consumable scan-credit product.

## Technical audit finding

The customer-facing model above is now canonical for the landingpage. The current backend compatibility snapshot still contains a mismatch for the free experience:

- `can_view_actions` is correctly restricted to paid access.
- `can_view_record_details` is correctly restricted to paid access.
- However, `can_view_issue_details`, `can_view_executive_report`, and the corresponding authoritative capabilities are currently granted through `protected_access_active`, which also becomes true for permanent free-result access.

This means the backend may currently grant broader free access than the intended limited-preview model. That discrepancy must be resolved in the product/access alignment branch before Go-Live. The landingpage must not be used as the sole enforcement layer.

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
- `landingpage/content/canonical-messaging.json`
- `scripts/generate_landing_pricing.py`
