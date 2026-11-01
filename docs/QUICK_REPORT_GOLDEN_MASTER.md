# BCSentinel Quick Assessment Report — Golden Master

Status: frozen product/report specification after Quick finalization

## Purpose

The Quick Assessment Report is the permanent paid disclosure layer between Free Health Check and Full Assessment. It must work as the customer's **first BCSentinel report** while still avoiding unnecessary repetition when the customer has already seen the Free Health Report.

Canonical decision question:

> **Which data-health problems have the highest priority now, and in what order should I review them?**

Quick is based on the same existing full Data Health Scan. It does not trigger a second scan, does not create a Validation baseline and does not expire automatically.

## Data boundary

Quick may disclose, for at most five prioritized findings:

- rank 1–5;
- finding title;
- normalized severity: Critical / High / Medium / Low / Info;
- canonical risk area and localized display label;
- affected-record count;
- non-monetary impact band: Low / Moderate / High / Very high;
- one short deterministic next review step.

Quick may also show standalone scan context:

- company;
- BC environment;
- scan date and scan ID;
- Data Health Score and score status;
- overall Business Impact Band;
- analyzed records;
- checks performed;
- modules analyzed;
- total finding count.

Quick must never disclose:

- exact modeled EUR values;
- issue codes;
- recommendation previews copied from Full;
- full root-cause analysis;
- record-level drilldown or sample records;
- complete remediation instructions;
- full finding catalogue;
- a Validation baseline claim.

The schema, not CSS hiding, enforces the boundary.

## Ranking and interpretation

The server may use exact modeled finding impact internally as a ranking signal. Exact values never enter the Quick contract. Only the derived non-monetary impact band is disclosed.

Tie-breaking is deterministic and uses normalized severity, affected count and finally internal issue code. Internal issue code is never exposed.

Management Interpretation must use only observable patterns inside the disclosed Top 5, for example:

- concentration of Top-5 findings in one canonical risk area;
- number of Critical/High findings inside the Top 5;
- number of High/Very-high impact-band findings inside the Top 5;
- statement that the displayed order follows modeled business priority.

It must not invent effort, remediation duration, savings, likely root cause or ease of fixing.

## Page 1 — Executive Priorities

Primary question: **What has the highest priority?**

Required structure:

1. BCSentinel family hero using the frozen visual DNA and Quick Assessment badge.
2. Report identity strip: Company / BC Environment / Scan Date / Scan ID.
3. Compact standalone context:
   - Data Health Score;
   - overall Business Impact Band;
   - Scan Scope with analyzed records, checks, modules and finding count.
4. Main visual focus: Top 5 prioritized findings.
5. Each finding row owns rank, title, severity, impact band, localized risk area, affected-record count and Next Review Step.
6. Management Interpretation at the bottom, based only on Top-5 patterns.
7. Footer: Quick Assessment · Page 1 of 2.

Page 1 must not contain a dominant Full Assessment upsell. Its job is prioritization, not conversion.

## Page 2 — Decision & Next Steps

Primary question: **In what order should I act, and what does Full unlock?**

Required structure:

1. Slim continuation header, not a second cover hero.
2. Priority Map: Severity × Impact Band, with numbered chips 1–5 matching page 1.
3. Recommended Sequence #1 → #5, using the same finding title and Quick-safe next review step.
4. Quick vs Full comparison.
5. One professional Full Assessment CTA.
6. Footer: Quick Assessment · Page 2 of 2.

The Page-1 score/context cards and full Top-5 rows must not be repeated on Page 2.

## Quick vs Full copy boundary

Quick Assessment includes:

- Top 5 prioritized findings;
- Severity and Impact Band;
- affected records and Risk Area;
- one next review step per finding;
- permanent access to the Quick disclosure layer.

Full Assessment additionally unlocks:

- complete finding list;
- exact modeled Business Impact values;
- root-cause analysis;
- detailed recommendations;
- prioritized remediation roadmap;
- eligibility as a later Validation baseline.

## Visual freeze

Use the same BCSentinel family DNA as the Free Report, not a new design system.

Frozen tokens:

- Navigation Navy `#14213D`
- Interaction Blue `#246BFD`
- Success `#11A36A`
- Warning `#D98E04`
- Critical `#CF3A3A`
- Background `#F7F9FC`
- Cards `#FFFFFF`
- Brand Orange `#FF921F`
- Foreground on Orange `#082138`
- Typography: Inter where supported
- Claim: `Clean Data – Higher Impact`

A4 portrait, two pages. White cards, light borders, restrained shadows/rounding, executive hierarchy and generous whitespace. Avoid a dashboard-like density.

## Implementation authority

Canonical implementation files:

- `backend/app/schemas/quick_assessment_report.py`
- `backend/app/services/quick_finding_selection_service.py`
- `backend/app/services/quick_assessment_report_service.py`
- `backend/app/templates/quick_assessment_report.html`
- `backend/app/services/quick_assessment_report_pdf_service.py`
- `backend/tests/test_f8b_quick_assessment_report.py`
- `backend/tests/test_f8c_quick_top5_boundary.py`

Any future Quick Report change that alters data ownership, page count, disclosure boundary or primary information hierarchy must update this Golden Master and the BCSentinel Master State in the same reviewed change.
