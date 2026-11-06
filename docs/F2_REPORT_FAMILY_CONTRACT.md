# F2 — Professional Report Family Contract

Status: Draft baseline for Fiverr pilot and later SaaS use.

## Objective
Create one channel-neutral report system with three customer-facing report families generated from the same canonical Deep Scan data:

1. Free Health Report
2. Assessment Report
3. Validation Report

No Fiverr-specific report variant is allowed. Sales channel may affect delivery and CTA text, but never scan depth, findings, calculations, or report semantics.

## Product boundaries

### Free Health Report
Purpose: high-value preview after the one initial Free Entry Deep Scan.

Allowed:
- Data Health Score
- checks/issues counts
- severity distribution
- aggregate risk areas/categories
- impact band only
- high-level management summary
- clear upgrade CTA

Not allowed:
- finding titles
- issue codes
- record-level detail
- root causes
- recommendations/worklists
- concrete Estimated Loss / Potential Saving EUR values
- paid report sections

### Assessment Report
Purpose: professional one-time decision document for the qualifying existing Deep Scan.

Access model:
- 7 days full live access after Assessment activation
- report remains the customer's delivered artifact after live access expiry

Required content:
- executive summary
- Data Health Score and module scores
- scan scope and coverage
- severity/risk distribution
- detailed findings
- root-cause interpretation where available
- concrete business impact / Estimated Loss / Potential Saving where supported
- prioritization matrix
- actionable recommendations
- remediation roadmap / next steps
- methodology and limitations

### Validation Report
Purpose: prove remediation progress using a genuinely new Deep Scan.

Access model:
- new Validation scan credit
- new Deep Scan after remediation
- 7 days full live access

Required content:
- baseline vs validation score
- resolved / improved / remaining / new findings
- before/after module scores
- before/after financial exposure where supported
- remaining priorities
- recommended next actions
- Monitoring CTA where appropriate

## Design system
Use the frozen BCSentinel brand system:
- Navigation: #14213D
- Interaction: #246BFD
- Success: #11A36A
- Warning: #D98E04
- Critical: #CF3A3A
- Background: #F7F9FC
- Cards: #FFFFFF
- Brand Orange: #FF921F
- Foreground on Orange: #082138
- Font: Inter
- Claim: “Clean Data – Higher Impact”

The report must feel like a professional management/consulting deliverable, not a raw technical export.

## Delivery surfaces
The same canonical report family must support:
- HTML view
- PDF generation
- secure signed report link
- opening from the BC Extension
- backend lifecycle-email link
- formal delivery through Fiverr for Fiverr-origin orders

## Security / entitlement rules
- Report access must be tenant-bound.
- Free report routes must never expose paid fields in HTML, JSON, PDF, or share-link payloads.
- Assessment/Validation report routes must verify current entitlement for live access.
- Signed links must be authenticated/signed and expire.
- No API token, secret, or hidden tenant credential may appear in reports or URLs.

## F2 implementation phases
1. Inventory current report builders, renderers, routes, templates, tests, and Extension report actions.
2. Introduce explicit report type / entitlement contract instead of one generic executive-report assumption.
3. Build production Free Health Report.
4. Redesign Assessment Report to premium client-delivery quality.
5. Build Validation comparison report.
6. Wire secure links/PDFs into the Extension and later lifecycle mail flow.
7. Add regression tests for Free-field leakage, tenant isolation, PDF/HTML consistency, and entitlement expiry.

## Acceptance target
F2 is complete when all three report families render from real backend scan data, obey their entitlement boundary, pass automated contract/security tests, and are visually suitable for direct customer delivery without manual redesign.
