# LP-GL-10 — Estimated Loss Examples Redesign

## Scope

- Rebuilt `landingpage/loss-examples.html` as a focused Enterprise information page.
- Preserved the existing public URL and shared site shell.
- Separated directly measured values, model assumptions, and calculated values.
- Added five complete worked examples across sales, inventory, receivables, overdue ledger entries, and purchasing.
- Added broader issue-group coverage for customers, vendors, inventory, purchasing, finance, and dimensions.
- Added explicit business interpretation and recommended action for each detailed example.
- Added a prominent non-guarantee disclaimer.
- Connected the page to pricing/access and findings on the homepage.
- Kept German and English presentation support.

## Calculation model

The public examples use the general model:

`affected records × probability × minutes / 60 × hourly rate × annual frequency`

The page makes clear that individual findings can use finding-specific weighting and that the displayed examples are illustrative decision-support calculations.

## Trust boundaries

- Estimated Loss is not described as an accounted financial loss.
- Potential Saving is not presented as guaranteed.
- The measured record count is visually separated from assumptions.
- Customers are instructed to validate hourly rate, frequency, and handling time against their own processes.
- No unsupported external benchmark or certification is referenced.

## Product-model alignment

The final CTA follows the canonical access model:

- free scan first,
- Assessment unlocks the already generated complete analysis for seven days,
- Assessment grants no scan credit,
- Validation is the later paid rescan product,
- Monitoring adds ongoing monitoring capabilities.

## Files

- `landingpage/loss-examples.html`
- `landingpage/css/loss-examples-redesign.css`
- `landingpage/js/loss-examples-redesign.js`
