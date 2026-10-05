# BCSentinel Executive Summary Report — Go-Live Design Spec

## Product rule
The report mirrors the canonical subscription experience and never reveals paid detail in Free.

### Free
- Maximum 2 A4 pages.
- Executive score, aggregated risk areas, high-level estimated financial impact and generic next steps only.
- No exact finding names, affected-record detail, causes, concrete recommendations, owners, action plans or validation history.
- Strong CTA to Assessment.

### Assessment
- Full executive summary for a single completed analysis.
- Detailed findings, severity, affected areas/records, financial impact, top recommendations, implementation effort, priorities and action plan.
- Executive Report may span multiple pages; target 5–7 A4 pages for normal datasets.
- Monitoring-only history/trend sections remain absent or explicitly locked in HTML.

### Monitoring
- Everything from Assessment plus historical comparison, trend, regressions, new/resolved findings, action progress, re-validation, realised savings and current-vs-baseline metrics.
- Target 6–8 A4 pages depending on data.

## HTML version
- Primary digital experience.
- Same BCSentinel navy/white/orange design DNA as Landingpage, Pilotpage and Dashboard.
- Sticky section navigation where useful.
- Interactive drill-down links may open the relevant dashboard view.
- Avoid fake controls in exported PDF.

## Print/PDF version
- A4 portrait, print-safe margins.
- Predominantly white background.
- Dark navy only for headings, separators and small brand elements.
- Orange/blue/green used sparingly for meaning, not decoration.
- Charts must remain legible in grayscale.
- Repeat report title, tenant and page number in footer/header.
- No full-page dark backgrounds.

## Canonical section order
1. Cover / Report context
2. Executive Summary
3. Data Health / Overall assessment
4. Risk areas and financial impact
5. Findings (Assessment/Monitoring only)
6. Recommended actions (Assessment/Monitoring only)
7. Implementation plan (Assessment/Monitoring)
8. Trend, validation and realised impact (Monitoring only)
9. Next steps

## Design principles
- Management first, technical detail second.
- Financial impact is a signature element.
- Explain calculated values as estimates unless directly realised/validated.
- Do not claim certifications or compliance states that are not evidence-backed.
- Backend entitlements remain authoritative; report generation must use the same product-access source of truth as the dashboard.
