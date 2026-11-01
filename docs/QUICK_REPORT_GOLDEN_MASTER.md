# BCSentinel Quick Assessment Report — Golden Master

Status: **FROZEN / APPROVED**

Freeze date: **2026-11-01**

Approved quality target: **9.8/10**

This document is the binding visual, information-architecture and disclosure specification for the BCSentinel Quick Assessment Report. The approved two-page design must not be structurally redesigned or expanded without an explicit product decision and a reviewed Golden Master update.

## Product purpose

The Quick Assessment Report is the permanent paid disclosure layer between Free Health Check and Full Assessment. It must work as the customer's **first BCSentinel report** while still providing genuine new value when the customer has already seen the Free Health Report.

Canonical management question:

> **Which data-health problems have the highest priority now, and in what order should I review them?**

Quick uses the same existing full Data Health Scan. It does not trigger a second scan, does not create a Validation baseline and does not expire automatically.

## Approved customer story

**Context → Prioritize → Interpret → Decide → Upgrade if deeper analysis is required**

Page 1 answers: **What matters most?**

Page 2 answers: **What should I look at first, and what additional depth does Full Assessment unlock?**

The Quick Report is not a remediation plan. It is a prioritization and decision report.

## Data boundary

Quick may disclose, for at most five prioritized findings:

- rank 1–5;
- finding title and short description;
- normalized severity: Critical / High / Medium / Low / Info;
- canonical risk area plus localized display label;
- affected-record count;
- non-monetary impact band: Low / Moderate / High / Very high;
- one short deterministic **Recommended Next Step** / **Empfohlener nächster Schritt**.

Quick may also show standalone scan context:

- company;
- BC environment;
- scan date and scan ID;
- Data Health Score and score status;
- overall Business Impact Band;
- analyzed records;
- modules analyzed.

The approved visible Page-1 Scan Scope intentionally does **not** show separate Checks or total Finding count. Those values may remain available internally or in the API contract but are not primary visual KPIs in the frozen Quick layout.

Quick must never disclose:

- exact modeled EUR values;
- issue codes;
- recommendation previews copied from Full;
- full root-cause analysis;
- record-level drilldown or sample records;
- complete remediation instructions;
- full finding catalogue;
- a Validation baseline claim.

The schema, not CSS hiding, enforces the disclosure boundary.

## Ranking and interpretation

The server may use exact modeled finding impact internally as a ranking signal. Exact values never enter the Quick customer disclosure. Only the derived non-monetary impact band is shown.

Tie-breaking is deterministic and may use normalized severity, affected count and finally an internal issue code. Internal issue codes are never exposed.

Management Interpretation must use only observable patterns inside the disclosed Top 5, for example:

- concentration in one or more risk areas;
- count of Critical/High findings inside the Top 5;
- count of High/Very-high impact findings;
- concentration of priorities into a small number of business areas;
- statement that displayed order follows modeled business priority.

It must not invent effort, remediation duration, savings, likely root cause or ease of fixing.

# Page 1 — Executive Priorities

Primary question: **What has the highest priority?**

## Frozen header

Use the BCSentinel mountain hero / brand-family visual DNA.

Required content:

- BCSentinel logo and claim `Clean Data – Higher Impact`;
- blue `Quick Assessment` badge;
- right-side context label `Prioritätsreport (Top 5 Findings)` or localized equivalent;
- headline: `Quick Assessment für Microsoft Dynamics 365 Business Central`;
- supporting line communicates that the five prioritized findings provide clear priorities and concrete next steps.

The header may be translated, but its hierarchy, product identity and visual weight are frozen.

## Identity strip

Four fields in one horizontal white strip:

1. Company
2. BC Environment
3. Scan Date
4. Scan ID

## Standalone decision context

Exactly three top-level cards:

1. **Data Health Score**
   - score /100;
   - score status;
   - restrained visual indicator.
2. **Business Impact**
   - overall non-monetary impact band only;
   - neutral explanation;
   - no exact EUR values and no financial-savings promise.
3. **Scan Scope**
   - analyzed records;
   - modules analyzed;
   - no separate visible Checks KPI;
   - no separate visible total-Findings KPI.

These cards are deliberately compact. Their role is to make Quick understandable when Free was never seen, not to recreate the Free Report.

## Main focus — Top 5 Findings

This is the visual center of Page 1.

Frozen information columns / row ownership:

- `#`
- `Finding (Kurzbeschreibung)`
- `Schweregrad`
- `Risikobereich`
- `Betroffene Datensätze`
- `Impact-Band`
- `Empfohlener nächster Schritt`

English localization must preserve the same information ownership.

Rows must remain readable and executive-friendly. White space is preferred over dashboard density.

The final label is **Empfohlener nächster Schritt**, not `Maßnahme`, `Remediation` or wording that implies a complete Full-Assessment recommendation.

## Management Interpretation

Use a dark navy interpretation panel at the bottom of Page 1.

The preferred frozen structure is three compact evidence-based insight blocks such as:

- **Focus: Stammdatenprozesse** / dominant risk-area concentration;
- **Kritische Schwerpunkte** / count and concentration of critical priorities;
- **Prioritäten bündeln** / visible concentration into a limited number of areas.

Exact labels may adapt to the real Top-5 pattern, but all claims must be deterministic and derived from disclosed data.

No dominant Full Assessment CTA is allowed on Page 1.

A restrained continuation hint may point to Page 2, e.g. priority matrix, recommended sequence and Full-Assessment comparison.

Footer: `Quick Assessment · Seite 1 von 2` / localized equivalent.

# Page 2 — Decision & Next Steps

Primary question: **How should I sequence attention, and what does Full unlock?**

## Frozen header

Use the same BCSentinel mountain/brand family as Page 1, with slightly reduced or equivalent visual weight depending on renderer constraints.

Required content:

- BCSentinel logo / claim;
- `Quick Assessment` badge;
- context `Entscheidung & Nächste Schritte`;
- headline equivalent to `Ihre nächsten Schritte für mehr Datenqualität und Geschäftswirkung`;
- short subtitle about classifying priorities and deciding where to continue.

Do not create a visually unrelated second-page design system.

## Priority Matrix — Severity × Impact

Required:

- Severity on the vertical axis;
- Impact Band on the horizontal axis;
- numbered markers 1–5 matching Page 1;
- restrained green/yellow/orange/red priority field;
- no exact EUR values.

A compact `Einordnung` panel may summarize only observable matrix patterns, such as concentration in High/Very-high impact or Critical/High severity.

The matrix must add interpretation; it must not simply repeat Page-1 rows.

## Recommended Sequence

Show the recommended order derived from ranks 1–5.

The frozen visual may group the sequence into concise executive stages such as:

- `Sofort angehen`
- `Danach umsetzen`
- `Anschließend konsolidieren`

Any grouping must be deterministic from ranking and disclosed findings and must not invent duration, effort, owner or implementation certainty.

A compact `Ergebnis` panel may explain the decision value of following the priority order, but it must not promise guaranteed operational or financial outcomes.

## Quick Assessment vs. Full Assessment

Two-column comparison.

Quick Assessment includes:

- Top 5 prioritized findings;
- Severity and Risk Area;
- affected records;
- Impact Band;
- recommended next step;
- permanent access to this Quick disclosure layer.

Full Assessment additionally unlocks:

- all identified findings;
- exact modeled financial values / Estimated Loss / Potential Saving;
- root-cause analysis;
- detailed recommendations;
- prioritized remediation roadmap;
- eligibility as a later Validation baseline.

The comparison must be factual and professional, not pressure-based sales copy.

## Full Assessment CTA

Exactly one dominant CTA on Page 2.

Preferred label:

`Zum Full Assessment (vollständige Analyse)`

Supporting copy should remain concise: all findings, deeper causes, concrete recommendations and a structured remediation plan.

No second competing CTA.

Footer: `Quick Assessment · Seite 2 von 2` / localized equivalent.

# Anti-repetition rules

- Page-1 KPI cards are not repeated on Page 2.
- Full Top-5 rows are not repeated on Page 2.
- The Priority Matrix must provide a new perspective.
- Recommended Sequence must turn rank into decision order rather than restating metrics.
- Each KPI has one primary visual owner.
- Free-report aggregate charts/tables such as full Severity Distribution or full Risk-Area overview are not repeated in Quick.

# Visual freeze

Use the existing BCSentinel family DNA, not a new design system.

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

Format: A4 portrait, exactly two pages.

Style: premium executive B2B report; mountain hero; strong navy/orange brand family; white cards; light borders; restrained shadows and rounding; clear hierarchy; high information density only where necessary; sufficient whitespace; no generic dashboard look.

# Approved visual target

The approved visual target is the two-page mockup reviewed on 2026-11-01 and rated **9.8/10** after final polish.

Key visual decisions from that approval:

- Quick remains independently understandable without the Free Report;
- Page 1 retains Data Health Score + Business Impact + compact Scan Scope;
- Scan Scope visually prioritizes analyzed records and modules only;
- Top 5 remain the primary Page-1 content;
- wording is `Empfohlener nächster Schritt` rather than a full-remediation term;
- Management Interpretation is evidence-based and compact;
- Page 2 contains Priority Matrix, Recommended Sequence, Quick-vs-Full and one CTA;
- the CTA is present only as the primary conversion element on Page 2;
- no new charts, sections or KPIs may be added without revisiting this Golden Master.

Illustrative mockup data such as company name, scan ID, score, record counts and finding titles are examples only. Production values always come from the report contract.

# Freeze rule

From this freeze onward, the following require an explicit product decision and reviewed change to this Golden Master:

- page count;
- section order;
- visible KPI set;
- Top-5 disclosure fields;
- Quick-vs-Full boundary;
- management-interpretation logic;
- Priority Matrix semantics;
- CTA count or placement;
- visual design system / brand tokens;
- permanent-access semantics.

Small implementation fixes are allowed without redesign when they only improve fidelity to this specification, such as typography, spacing, A4 overflow prevention, localization, accessibility or renderer consistency.

# Implementation authority

Canonical implementation files:

- `backend/app/schemas/quick_assessment_report.py`
- `backend/app/services/quick_finding_selection_service.py`
- `backend/app/services/quick_assessment_report_service.py`
- `backend/app/templates/quick_assessment_report.html`
- `backend/app/services/quick_assessment_report_pdf_service.py`
- `backend/tests/test_f8b_quick_assessment_report.py`
- `backend/tests/test_f8c_quick_top5_boundary.py`

The approved target is now frozen. Future implementation work should increase renderer fidelity to this Golden Master, not reinterpret the product.