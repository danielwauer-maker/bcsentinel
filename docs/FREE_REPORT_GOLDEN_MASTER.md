# BCSentinel Free Report Golden Master

Status: **FROZEN for Fiverr Go-Live**

Frozen on: 2026-11-01

This document defines the approved customer-facing visual and information architecture for the **BCSentinel Free Health Check Report**. It is the canonical design reference for implementation and visual QA. The design is frozen; future work should reproduce it faithfully rather than redesign it.

## Purpose

The Free Report must communicate enough value to establish trust and make the next commercial step obvious, while preserving the Free product boundary. It must feel like a premium executive report, not an exported dashboard.

Information story:

**Health status → Scan scope → Severity → Risk areas → Business impact preview → Locked assessment detail → Next step**

## Page format

- Exactly **1 page**.
- **DIN A4 portrait** aspect ratio.
- Executive-report layout with generous whitespace and clear card hierarchy.
- No landscape or dashboard-like widening.
- Final implementation target: deterministic A4 HTML/CSS rendered from backend data; no generative text or numbers in production output.

## Frozen visual direction

- Large dark-navy photographic hero area at the top with premium mountain imagery matching the BCSentinel landing-page visual language.
- BCSentinel shield/logo and claim **“Clean Data – Higher Impact”** in the hero.
- Primary accent orange; functional blue; white/light cards; severity colors red/orange/yellow/green/gray.
- Brand tokens remain authoritative:
  - Navigation `#14213D`
  - Interaction `#246BFD`
  - Success `#11A36A`
  - Warning `#D98E04`
  - Critical `#CF3A3A`
  - Background `#F7F9FC`
  - Cards `#FFFFFF`
  - Brand Orange `#FF921F`
  - Foreground on Orange `#082138`
- Typography follows the BCSentinel brand system; Inter remains the implementation default.
- Rounded cards, subtle borders/shadows, clean iconography, strong numeric hierarchy.
- No redesign of the approved page structure for Fiverr go-live.

## Frozen page structure

### 1. Hero / Report identity

Content:

- BCSentinel logo
- Claim: `Clean Data – Higher Impact`
- Badge: `Free Health Check`
- Report title: `Ihr Data Health Check für Microsoft Dynamics 365 Business Central`
- Supporting line: `Kompakte Bewertung Ihrer Business-Central-Datenqualität, identifizierter Risikobereiche und des modellierten Business Impacts.`
- Optional small label: `Unternehmensreport (Vorschau)` for example/demo assets only; live customer report should use the real delivery context rather than imply preview unless actually a preview.

### 2. Scan identification strip

Four compact metadata cells:

- Company name
- BC environment
- Scan date/time
- Scan ID

Backend fields must be authoritative. Company name must use the real historical scan-run company name, with tenant ID only as legacy fallback.

### 3. Health + Scan Scope

Left card: **Data Health Score**

- Score prominently displayed out of 100.
- Status label, e.g. `Verbesserungsbedarf`, driven by the canonical score-status logic.
- Short interpretation only; do not repeat score elsewhere on the page.

Right card: **Scan Scope**

Four metrics:

- Analyzed Records
- Checks Run
- Modules Analyzed
- Findings total

These values must be populated from the real backend contract.

### 4. Finding severity distribution

Heading: `Verteilung der Findings nach Schweregrad`

Exactly five categories:

- Critical / Kritisch
- High / Hoch
- Medium / Mittel
- Low / Niedrig
- Info

Preferred visual: one compact horizontal stacked distribution bar with the five counts listed beneath or alongside it.

Do not use a large donut chart.

Counts and percentages must reconcile to total findings.

### 5. Top risk areas (aggregate only)

Heading: `Top-Risikobereiche (aggregiert)`

Preferred table columns:

- Rank
- Area
- Highest Severity
- Findings
- Affected Records

Do **not** show a separate Impact Band per risk area in the Free report unless a future reviewed backend contract explicitly introduces it.

Do not expose finding titles, issue codes, root causes, recommendations, sample records or exact EUR amounts.

### 6. Business Impact preview

Heading: `Business Impact (Vorschau)`

Show one aggregate band only:

- Low / Niedrig
- Medium / Mittel
- High / Hoch
- Very High / Sehr hoch

Current headline style:

`Business Impact: Hoch`

Supporting wording should make clear that detailed modeled financial evaluation is part of Full Assessment.

No exact EUR values in Free.

### 7. Locked assessment details

Dark-navy premium strip/card with lock treatment for three groups:

1. `Detaillierte Findings`
   - all identified data-quality problems including description and cause
2. `Finanzieller Impact`
   - modeled financial loss and potential saving
3. `Maßnahmen & Roadmap`
   - prioritized recommended actions with effort, value and time horizon

Use blurred/locked visual previews only. They may communicate category and structure, but must not leak protected customer detail.

### 8. Commercial next step

Primary CTA:

`Zum Quick Assessment`

Supporting line:

`Die 5 priorisierten Findings im Fokus – mit konkreten nächsten Schritten.`

Secondary path:

`Für die vollständige Analyse mit finanziellem Impact, Root Cause und Maßnahmenplan: Full Assessment starten`

Quick remains the primary Free-report upsell; Full remains available directly.

### 9. Footer

- BCSentinel logo/wordmark
- `Clean Data – Higher Impact`
- `Free Health Check`
- `Seite 1 von 1`

## Non-repetition rules

The Free Report follows the project-wide reporting principle that each important number has one primary owner.

- Health Score: once, prominently.
- Total findings: once as a scope metric; severity section decomposes the same total rather than repeating it as another KPI.
- Severity distribution: once.
- Risk areas: once.
- Business Impact Band: once.
- Exact financial values: never in Free.
- No trend charts in Free; the initial assessment is point-in-time. Trend charts belong to Monitoring.

A later section may interpret an earlier metric, but must not repeat it as another KPI card or duplicate chart.

## Free product boundary

The design must remain consistent with the server-side aggregate-safe Free contract.

Allowed:

- Data Health Score
- score status
- analyzed-record count
- checks count
- modules analyzed
- findings count
- five-level severity aggregates
- aggregate risk areas with highest severity / findings / affected records
- overall Business Impact Band
- company/environment/scan metadata

Blocked:

- finding titles
- issue codes
- exact EUR values
- full root-cause analysis
- full recommendations/remediation
- record-level/sample data
- detailed paid drilldown

Locked previews must never bypass these server-side boundaries.

## Golden Master rule

For Fiverr go-live, this visual and information architecture is **frozen**.

Allowed implementation changes:

- pixel-level spacing/alignment corrections needed to faithfully reproduce the reference
- deterministic data binding
- accessibility improvements that do not alter the visual hierarchy
- localization corrections
- technical print/PDF fixes

Not allowed without an explicit new design decision:

- changing the page story or section order
- adding/removing KPI blocks
- adding duplicate charts or repeated numbers
- replacing the hero direction
- changing the Free/Paid information boundary
- turning the page back into a dashboard-style layout
- introducing trend/history visuals
- adding exact financial values

The approved Fiverr Free Report should be evaluated against this document during final visual QA and treated as the **Free Report Golden Master**.