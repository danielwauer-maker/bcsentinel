# LP-GL-09 — Audience, FAQ, Final CTA and Footer

## Scope

- Added audience-specific value views for Management & CFO, IT & ERP owners, BC partners and consultants, and managed service providers.
- Replaced the legacy partner section with an integrated partner strip and explicit separation between customer and partner access.
- Rebuilt the FAQ around the authoritative access model.
- Replaced the legacy final CTA with a free-scan-first conversion path.
- Replaced the compact global footer on the homepage with a structured enterprise footer.
- Promoted Estimated Loss examples as a primary resource.

## FAQ access contract

The homepage now states:

- Free scan: permanent limited preview of dashboard, issues, actions, and Executive Report.
- Assessment: unlocks the existing Full Analysis for seven days and grants no scan credit.
- Validation: grants one new scan credit and another seven-day full-access period after the new scan.
- Monitoring: includes full analysis plus scheduled scans, history, trends, comparisons, exceptions, and additional monitoring functionality during the active monthly or annual term.

## Conversion path

The final CTA no longer implies that Assessment starts the initial scan. The sequence is:

1. Start the free scan in the Business Central extension.
2. Review the limited preview.
3. Unlock Assessment only if the business case is convincing.
4. Use Validation for a later rescan.
5. Use Monitoring for continuous control.

## Footer information architecture

The homepage footer is grouped into:

- Product
- Resources
- Company / legal / partner access

Customer activation is not represented as a generic public login because the verified product activation path is through the Business Central extension. Partner registration and Partner Login remain explicit separate routes.

## Trust constraints

- No unverified customer portal URL was invented.
- No unsupported Microsoft partnership, compliance, or customer claims were introduced.
- AppSource remains described as in preparation.
- Estimated Loss links lead to the existing methodology page.

## Files

- `landingpage/css/audience-faq-footer.css`
- `landingpage/js/audience-faq-footer.js`
- `landingpage/js/security-trust-legal.js`
