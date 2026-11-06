# BCSentinel Validation Report — Golden Master

Status: **FROZEN / APPROVED**

Freeze date: **2026-11-02**

Approved quality target: **9.9/10**

This document is the binding visual, information-architecture and disclosure specification for the BCSentinel Validation Report. The approved three-page design must not be structurally redesigned or expanded without an explicit product decision and a reviewed Golden Master update.

## Product purpose

Validation measures whether remediation performed after a paid Full Assessment produced measurable improvement. Validation always compares a new Validation scan against the exact Full Assessment baseline and must never silently use a Quick, Free or earlier Validation scan as baseline.

Canonical management question:

> **Did the implemented measures measurably improve data quality and modeled business impact, and what still needs attention?**

Customer story:

**Baseline → Re-scan → Compare → Verify progress → Identify remaining/new risk → Continue with Monitoring if needed**

## Approved page architecture

Exactly three fixed A4 portrait pages plus an optional dynamic Finding Appendix when a complete detailed delta listing is required.

### Page 1 — Validation der Maßnahmen

Primary question: **Did the measures work overall?**

Required identity/context:
- BCSentinel logo and claim `Clean Data – Higher Impact`;
- blue `Validation Report` badge;
- Microsoft Dynamics 365 Business Central context;
- Company, BC Environment, Baseline Date, Validation Date, Validation ID.

Required KPI comparisons:
- Data Health Score: Baseline → Validation + signed delta;
- Modeled Business Impact: Baseline → Validation + signed delta and percentage where valid;
- Findings total: Baseline → Validation + signed delta;
- Affected Records: Baseline → Validation + signed delta.

Required Finding lifecycle overview:
- Resolved;
- Improved;
- Remaining;
- Regressed;
- New.

Lifecycle arithmetic must be internally consistent:
- Baseline findings = Resolved + Improved + Remaining + Regressed;
- Validation findings = Improved + Remaining + Regressed + New.

`New` is not part of the Baseline denominator and should not be shown with a misleading baseline percentage.

Required Management Interpretation:
- overall direction;
- strongest evidence-backed improvement;
- remaining/new/regressed attention point.

All text must be deterministic from contract values. No free-form AI conclusions, invented root causes, guaranteed savings or unsupported causality.

The bottom result banner is dynamic:
- positive scenario: measurable progress;
- mixed scenario: progress visible but individual risks need more action;
- negative scenario: renewed action required.

### Page 2 — Bereichsentwicklung & Fortschritt

Primary question: **Where did the situation improve or deteriorate?**

Show all ten canonical Business Areas using the same taxonomy as Full Assessment:
- Finance / Finanzen
- Sales / Verkauf
- Purchasing / Einkauf
- Inventory / Lager & Artikel
- CRM / CRM & Stammdaten
- Manufacturing / Produktion
- Service
- Jobs / Projekte
- HR / Personal
- System / System & Plattform

For every area show:
- Data Health Score Baseline → Validation + delta;
- Findings Baseline → Validation;
- Modeled Impact Baseline → Validation;
- deterministic trend indicator.

A net finding count must not hide lifecycle changes. When count is unchanged but composition changes, show concise detail, e.g. `3 → 3 (1 neu · 1 gelöst)`.

Required summary blocks:
- Top Improvements;
- Needs Attention.

`Regressed` means a worsened existing finding, not an additional finding.

### Page 3 — Finding-Änderungen & nächste Schritte

Primary question: **Which concrete findings changed and what requires action now?**

Required priority order:
1. Regressed
2. New
3. Remaining
4. Improved
5. Resolved

`Remaining` means **unchanged still present**. It must not imply that every remaining finding is Critical/High.

Finding rows may show:
- code;
- short title;
- canonical Business Area + localized label;
- status;
- Severity Baseline → Validation;
- Affected Records Baseline → Validation;
- Modeled Impact Baseline → Validation.

The area field must always use the canonical Business Area taxonomy; finding titles may be more specific.

Required final summary:
- resolved count;
- improved count;
- regressed count;
- new count;
- remaining count;
- overall Findings delta;
- Affected Records delta;
- Modeled Business Impact delta.

Preferred next-step banner:
`Nächster Schritt: Kontinuierlich mit Monitoring überwachen`

This is a product-continuation recommendation, not a guaranteed-outcome or pressure CTA.

## Data and methodology rules

- Financial values are always labeled modeled / modelliert.
- Validation must preserve signed deltas; deterioration must remain visible.
- `estimated_exposure_reduction_eur` may remain as a compatibility field, but report semantics must use the signed Business Impact delta where direction matters.
- No root-cause claims unless a real root-cause field exists in the contract.
- No invented effort or remediation duration.
- No causal business claims unless explicitly encoded by deterministic rules.
- Baseline provenance must be traceable through the Validation credit/operator binding or explicit legacy fallback source.

## Visual freeze

Use the BCSentinel report family DNA:
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

Style: premium executive B2B report; mountain hero; strong navy/orange family; green used more prominently for measured improvement; red/orange reserved for regressions and attention; white cards; restrained borders/shadows; executive-first hierarchy.

Footer pattern:
- `Validation Report · Seite 1 von 3`
- `Validation Report · Seite 2 von 3`
- `Validation Report · Seite 3 von 3`

## Approved illustrative arithmetic

The reviewed mockup example uses:
- Baseline Findings: 27
- Validation Findings: 18
- Resolved: 10
- Improved: 6
- Remaining: 9
- Regressed: 2
- New: 1

This is illustrative only. Production values always come from the Validation report contract.

## Freeze rule

The following require an explicit product decision and Golden Master review:
- page count;
- section order;
- visible KPI set;
- lifecycle semantics;
- Business Area taxonomy;
- Management Interpretation logic;
- CTA/next-step placement;
- visual design system.

Implementation-only fixes such as spacing, typography, localization, A4 overflow prevention, accessibility, renderer fidelity or test hardening are allowed without redesign.

## Implementation authority

Canonical Validation foundation:
- `backend/app/schemas/validation_report.py`
- `backend/app/services/validation_report_service.py`
- `backend/tests/test_validation_vr1_vr5.py`
- baseline binding migration introduced with V-R4

V-R1 through V-R5 are merged to `main` and form the approved data-contract basis. Future renderer work should increase fidelity to this Golden Master, not reinterpret Validation semantics.
