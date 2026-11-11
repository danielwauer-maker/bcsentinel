---
title: Sprint 6.02 – Synthetic Report Examples EN
status: editorial_demo_only
owner: Product Content
locale: en
updated: 2026-11-11
---

# BCSentinel – Report examples (English)

> **FICTIONAL DEMO DATA ONLY.** All companies, dates, scores, volumes and findings are invented for copy and layout review. No customer references, benchmarks, or runtime acceptance evidence. Production reports must source data, access level and scope from the backend.

## Example 1: Free Health Report

**H1:** Your data health at a glance  
**Subtitle:** Aggregate signals for an initial assessment.  
**Context (Demo):** Example Ltd · BC Online Sandbox · 10 Nov 2026 · Scan DEMO-FREE-001  
**Data Health Score (Demo):** 78/100  
**Analyzed records (Demo):** 24,000  
**Risk areas (Demo):** Purchasing 12 anomalies · Inventory 8 · Finance 3  
**Severity (Demo):** Critical 2 · High 7 · Medium 10 · Low 4  
**Overall Business Impact Band (Demo):** High  
**Management view:** The fictional aggregates illustrate risk concentrations in purchasing and inventory. Aggregate results alone do not establish root causes or specific correction plans.  
**CTA:** Explore priorities with Quick Assessment [approved channel and entitlement only].  
**Disclosure:** No finding titles, issue codes, record samples, exact EUR values, root causes, full recommendations or hidden detail links.

## Example 2: Quick Assessment – two-page format

### Page 1 – Executive Priorities

**Context (Demo):** Example Ltd · BC Online Sandbox · 10 Nov 2026 · Scan DEMO-QUICK-001  
**Data Health Score:** 78/100 · **Business Impact:** High · **Scan Scope:** 24,000 analyzed records; 10 modules.

**Top 5 findings (all fictional):**

| # | Finding (short description) | Severity | Risk area | Affected records | Impact band | Recommended next step |
|---|---|---|---|---:|---|---|
| 1 | Incomplete supplier payment terms | High | Purchasing | 43 | Very high | Review completeness of supplier payment terms |
| 2 | Inconsistent bin references | High | Inventory | 85 | High | Reconcile bin references with responsible teams |
| 3 | Missing mandatory customer master fields | Medium | Sales | 27 | High | Review affected fields against business requirements |
| 4 | Inconsistent dimension assignments | Medium | Finance | 64 | Moderate | Compare dimension policies and assignments |
| 5 | Outdated supplier contact details | Low | Purchasing | 19 | Low | Review contact-data maintenance process |

**Management Interpretation:** Two of the five visible priorities are High severity. Two concern Purchasing. Two have High or Very high impact bands. Ranking represents modeled priority, not verified loss or remediation time.

### Page 2 – Decision & Next Steps

**Severity × Impact Matrix (DEMO):** #1 High/Very high · #2 High/High · #3 Medium/High · #4 Medium/Moderate · #5 Low/Low. Axes: *Severity* × *Impact Band*.  
**Recommended sequence:** Review #1–#2 first; then #3–#4; finally #5. This is a review order, **not** a verified implementation plan.  
**Quick vs Full:** Quick reveals up to five titles, counts, severity, risk area, impact band and short next steps. With the proper access, Full may provide all findings, detailed causes and recommendations, and modeled exact financial amounts.  
**Single primary CTA:** Ask about Full Assessment [approved sales route only].  
**Quick disclosure:** Never expose exact EUR values, issue codes, complete root causes, record drilldown or full remediation. Quick is **not** a Validation baseline. This editorial example follows `docs/QUICK_REPORT_GOLDEN_MASTER.md`, not a rendered PDF proof.

## Example 3: Full Assessment / Executive Report

**H1:** Data quality and modeled business impact  
**Context (Demo):** Example Ltd · BC Online Sandbox · Scan DEMO-FULL-001  
**Executive summary:** The fictional assessment identifies five representative priorities. Start by investigating purchasing and inventory processes.  
**Data Health Score:** 78/100  
**Finding detail:** The same five examples from Quick, with gated full-access placeholders for root cause, complete recommendation, relevant source references and confirmed business owner.

**Illustrative fin-v1 calculation (Demo; not customer data):**
- Fictional affected occurrences: 100
- Assumptions: 15 minutes per occurrence × 4 times per year × €40/hour × 50% probability
- **Estimated Loss:** €2,000/year (modeled, **not an actual booked loss**)
- Assumed recoverability of 40%: **Potential Saving:** €800/year (**neither guaranteed nor realized**)

These arbitrary demonstration parameters illustrate fin-v1 semantics. Do not treat them as production report values. No realized ROI claims.  
**Management next steps:** Verify source data and policy, confirm responsible teams, make any corrections within Business Central, and consider Validation after a paid Full baseline.

## Example 4: Validation Report

**H1:** What changed after your review?  
**Status:** **Content/layout simulation, not a claim that the current Validation pipeline has passed acceptance.**  
**Demo baseline:** DEMO-FULL-001 · **Demo follow-up:** DEMO-VAL-002. Direct comparisons require proven scan provenance, same company, comparable scope and compatible methodology.

| Example finding | Baseline | Validation | Fictional classification |
|---|---:|---:|---|
| Missing payment terms | 43 | 15 | Improved |
| Inconsistent bin references | 85 | 0 | Resolved |
| Inconsistent dimensions | 64 | 64 | Remaining |
| Outdated contact details | 19 | 24 | Regressed |
| Newly detected missing address details | 0 | 6 | New |

**Interpretation:** All counts are fictional. When provenance or scope is not comparable, the report must show that limitation rather than presenting unsupported validated deltas. Even a valid modeled financial delta is **not** a Realized Saving.  
**CTA:** Review the findings with your BC business team.

## Example 5: Monitoring – concept only

**H1:** Track data health over time  
**Status:** Planned/separately approved product phase, **not part of the initial controlled Fiverr pilot**.  
**Possible future view:** Data Health Score trend, focus areas, scan history and alerts where explicitly implemented and approved.  
**Suggested copy:** “Explore changes in key data-health indicators over time.” / “Investigate emerging or recurring risks in the context of your scans.”  
**CTA:** Request an availability update [no unapproved checkout].

## Visual and publication notes

Use Product System semantic design tokens: Orange for brand/primary marketing CTA, Blue for analytics, Amber for warnings. Prominently label **FICTIONAL DEMO DATA** in every example and output. Never present these as actual customers, benchmarks or achieved savings. Free/Quick must not leak financial detail through responsive UI, exports, PDF or accessible text. Real runtime and visual acceptance remains a separate gate.
