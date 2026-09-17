> Superseded runtime status: the real SaaS export is now reconciled in [EXT-50-12C.2](EXT_50_12C_RUNTIME_DETECTION_RECONCILIATION.md). Historical evidence below is retained. The 165 runtime check count is correct; intermediate counter drift is overwritten.

# EXT-50-12C — Generator Detection Accuracy & Benchmark Validation

**CORRECTION (12C.1):** The backend sync applies last-row-per-code projection after
computing commercials. Therefore it does not preserve all BC finding rows; BC and
backend occurrence sums can differ. The normal response is already deduplicated, so
the surviving last-group impact updates the first BC row for that code. See the
12C.1 pipeline section for the corrected analysis; original runtime conclusions below
remain unverified.

Historical 12C audit, preserved for provenance. Follow-up: EXT_50_12C_1_RUNTIME_RECONCILIATION.md.
The later 12C.1 user report confirms app 1.0.2.21, CRONUS origin and 7/10 modules;
statements below about missing confirmations describe the original audit. The separate
12C.1 branch now has explicit authorization to commit/push/create its own PR.

Audit date: 2026-09-16. Decision: **NOT_READY_FOR_LARGE**.
Evidence status: **AWAITING_MANUAL_BC_RUNTIME_EVIDENCE**.
This is a source audit plus local automated verification, not a replay of the SaaS run.

## 1. Executive Summary

The 2,000 counter is understood and exactly reconstructible: 600 missing customer emails,
200 missing vendor phones, 600 zero item selling prices and 600 zero item unit costs.
All four intentional scenario types map to actual productive predicates and aggregate
findings: **4/4 types (100%) and 2,000/2,000 intended instances (100%) statically covered**.
This is mapping coverage, **not measured detection accuracy**. No per-check runtime counts
were provided. Observed detection coverage is unmeasured, not 0% or 100%.

95 is a finding-row count, not a count of defective records or necessarily distinct rules.
224,999 is a sum of affected occurrences across findings, not unique records.
The generated masters intentionally leave many fields outside the injection budget empty.
Under the documented fixture assumptions those fields and the four injections alone
contribute **216,000 occurrences across 30 check IDs**. This explains the mechanism and
scale, but does not prove the remaining 8,999 occurrences or the identity of all 95 rows.

Score 38 is reproducible from the seven non-100 module scores if Service/Jobs/HR are
disabled. With all ten modules enabled the same scores give **44**, not 38. The run's
enabled-module payload is required. Showing 100 for an unexecuted module is not evidence
that its checks passed. EUR 2,202,021.49 → EUR 2,202,021 is expected KPI formatting;
recalculation of the underlying amount requires the actual findings and impact settings.

Two existing source defects were identified: duplicate group markers are searched but
never stored, and declared check counts overstate actual checks by three. A further
multi-row-per-code impact round-trip defect is documented below. None is evidence that
the four intended generator predicates fail. No product or generator behavior was changed.

### Repository and PR provenance

| Surface | Verified state |
|---|---|
| Repository | `danielwauer-maker/bcsentinel` |
| Initial branch / HEAD | `sprint/ext-50-12a-test-data-generator` / `89faeb721ed5488ee97c07a620c5184deba6f2e8` |
| Audit branch | `codex/ext-50-12c-detection-accuracy`, same base HEAD |
| staging | `867b1f7cef5f20064a5f61655e1e00edf3d24dd3` |
| PR #38 | OPEN, CLEAN, base staging, head `89faeb721ed5488ee97c07a620c5184deba6f2e8` |
| PR #39 | OPEN, CLEAN, base staging, head `00b7b4ed31b70fd14681f0e3b913337bf29c1f78` |

[PR #38](https://github.com/danielwauer-maker/bcsentinel/pull/38) and
[PR #39](https://github.com/danielwauer-maker/bcsentinel/pull/39) were inspected read-only.
No merge, deployment, cleanup, BC write, commit or push was performed. No new remote PR
was created: the repository instruction requires an explicit commit request; this audit
is delivered as reviewable uncommitted files on its separate branch.

Pre-existing user changes in `docs/EXT_50_12A_TEST_DATA_GENERATOR.md` and
`quality/release/ext-50-12a-test-data-generator-evidence.json` remain untouched.
PR #38 adds the standalone generator, its contracts and CI/build support; productive
scanner/backend/dashboard source matches staging. PR #39 adds copied-company registration
recovery, permission/page support, manifest range/version and CI/test adjustments; its
changed-file inventory contains no detection/scoring/dashboard implementation changes.
It is not merged into this audit branch. Its nine source tests were separately executed
against files read from its exact head, not against a fabricated combined integration.
The installed SaaS extension/backend versions are not established by these Git SHAs.

## 2. Runtime Evidence

User-reported observations, retained without presenting them as independently captured logs:

| Field | Observation |
|---|---|
| Company | BCS-PERF-DEV |
| Generator | DEV; seed 5001; error rate 10%; 6,000 Customer + 2,000 Vendor + 12,000 Item |
| Generator outcome | Completed; 2,000 scenarios; failed batches 0; about 3:20; 99.69 business records/s |
| Scan ID | `RUN_20260916_000001_43F57A071BFF485BAF20C68FF578B` |
| Scan interval | 16 September 2026, approximately 18:31–18:39 |
| Exact displayed duration | 8 minutes 22 seconds 226 milliseconds = 502.226 s |
| Completion | Completed / Synchronized |
| Score / findings | 38 / 95 |
| Impact | EUR 2,202,021.49 in BC; approximately EUR 2,202,021 in dashboard |
| Dashboard | Free Data Score; Critical; 224,999 affected records; Finance highest risk |
| Modules | System 48, Finance 16, Sales 47, Purchasing 44, Inventory 16, CRM 75, Manufacturing 61, Service 100, Projects 100, HR 100 |

Missing: installed app versions, immutable setup/config snapshots, full finding export,
scan request/result payload with secrets removed, module selection, exception state,
impact configuration at scan time, baseline scan and module timings. No authenticated
BC/backend runtime connection was used. Existing 20,000 business records were not touched.

## 3. Generator Semantics

Sources under `bc-performance/src/`:

| Object | Responsibility |
|---|---|
| `BCPPolicy.Codeunit.al` (53400) | DEV/LARGE/XL/STRESS/Custom targets; seed/rate validation; numbering; SaaS sandbox/company guards |
| `BCPConfig.Codeunit.al` (53401) | Immutable nonempty setup-code JSON snapshots, validation, base UOM, attribute inheritance guard |
| `BCPBatch.Codeunit.al` (53402) | Vendor → Customer → Item batches; four injections; business/support ownership tracking |
| `BCPManagement.Codeunit.al` | Run creation, execution/resume, failure and cancellation coordination |
| `BCPCleanup*.al`, `BCPReferences.Codeunit.al` | Ownership-scoped cleanup/refusal logic; read during audit, never executed |
| `BCPRun.Table.al` | Targets, seed/rate/schema/config, counters, phase/batch/time/status; the run is the checkpoint |
| `BCPOwnedRecord.Table.al` | Run/table/SystemId/RecordId/number/modification timestamp, Scenario and Supporting |
| `BCPNewRun.Page.al`, `BCPRuns.Page.al` | Request and metrics; displayed scenario counter binds to Expected Scenarios |
| `BCPSelfTests.Codeunit.al` (53407) | Eight AL policy/dialog/default/seed/config behavior tests; not productive detection tests |
| `backend/tests/test_ext_50_12a_generator_contract.py` | 20 source/safety/profile/ownership/seed/CI cases |

`BCP Batch.Track` writes `Owned.Scenario := Scenario`, inserts ownership, then increments
`GenerationRun."Expected Scenarios"` once **only when Scenario is nonempty**.
Each generated business record has at most one such label. UOM tracking passes an empty
scenario and `Supporting=true`, so it adds no scenario. There are four possible labels,
not 2,000 different rules. The counter records committed labeled business-record injections,
not every field assignment, check execution, detected defect, finding or affected occurrence.

`GenerateBatch` locks/rereads the run; `CommitBehavior::Error` forbids explicit inner commits.
Boolean `Codeunit.Run` commits the business inserts, ownership and counters together.
Failure rolls back that batch; retries start from persisted entity counts. Config is not
re-randomized. Completed requires business count = target. This explains why completed
20,000/10% yields 2,000 even across batch boundaries. Installed subscribers can still affect
business fields; static reconstruction is conditional on the deployed schema/implementation.

DEV also creates **12,000 Item Unit of Measure rows** (table 5404; quantity per UOM = 1)
and **32,000 ownership rows**, plus run metadata. Business records = 20,000; generated
business+support = 32,000; business+support+ownership = 64,000. These are different metrics.
LARGE is 150,000/50,000/300,000, XL 600,000/200,000/1,200,000, STRESS
1,500,000/500,000/3,000,000. Custom bounds/rates are enforced by Policy.

## 4. Error Scenario Catalog

Let `n` be the entity's one-based sequence. Membership is
`((n mod 100)*37 + (seed mod 100)) mod 100 < rate`.
For items the branch uses **floor((n−1)/100) mod 2**; using n/100 would misclassify
the selected boundary n=100. At seed 5001 selected positions in each 100 are
**11, 19, 27, 38, 46, 65, 73, 84, 92, 100**.

| Internal scenario / intended check | Entity / state | Generator function | Activation | DEV count | Multiple / overlap |
|---|---|---|---|---:|---|
| CUSTOMERS_MISSING_EMAIL | Customer 18; E-Mail blank | CreateCustomer | membership | 600 (10% customers) | One label; overlaps incidental customer omissions |
| VENDORS_MISSING_PHONE | Vendor 23; Phone No. blank | CreateVendor | membership | 200 (10% vendors) | One label; overlaps bank/commercial omissions |
| ITEMS_WITHOUT_UNIT_PRICE | Item 27; Unit Price = 0, initial positive Unit Cost retained | CreateItem | membership and even zero-based 100-block | 600 (5% items) | Mutually exclusive with cost injection |
| ITEMS_WITHOUT_UNIT_COST | Item 27; Unit Cost = 0, previously calculated positive Unit Price retained | CreateItem | membership and odd zero-based 100-block | 600 (5% items) | Mutually exclusive with price injection |

These are deliberate data-quality incompleteness states, not necessarily invalid BC
database records. BC permits legitimate blank contact fields or zero prices/costs in
some business contexts. The mapping tests the product's actual generic predicate,
not a universal legal/business requirement. UOM has no intentional error scenario.
Seed 5001 and seed 1 share injection positions; there is no PRNG state.

Additional defaults are outside the error-rate counter: no bank accounts, transaction
history, contacts/default dimensions, VAT IDs, customer commercial fields, and many
item planning/physical attributes. Not generated: negative inventory, posted aging,
invalid email syntax, deliberate duplicates, missing posting configuration or malformed
UOM. These unsupported workload classes are **INTENTIONALLY_NOT_COVERED by the generator**,
not proof of product coverage gaps.

## 5. BCSentinel Check Catalog

Complete audit appendix: [all 199 checks with exact AL table/filter/condition blocks](EXT_50_12C_PRODUCT_CHECK_CATALOG.md).
Machine-readable version: `quality/release/ext-50-12c-static-audit.json`.
`scripts/audit_ext_50_12c.py` reproduces both artifacts without BC/database access.
The catalog test proves equality with all IDs registered by `DHScanCheckMgt.EnsureDefaultChecks`.

`DHDeepScanRunner.Codeunit.al` contains 193 `AddCountFinding` check sites and six duplicate
checks. Category counts: Customer 19, Vendor 19, Item 10, System 13, Finance 16,
Ledger 2, Sales 21, Purchasing 20, Inventory 19, CRM 9, Manufacturing 17,
Service 12, Jobs 10, HR 12. CUSTOMER/VENDOR/LEDGER/FINANCE affect Finance;
ITEM/INVENTORY affect Inventory. Product titles initially equal the check IDs;
backend catalog/localization supplies displayed names.

The four direct mappings have no generator prefix/ownership filter: `Customer.Reset`,
`Vendor.Reset`, `Item.Reset`, then company-wide `FindSet`. Blank/zero predicates increment
once per record unless the exact record SystemId/check has an active exception.
`DHExceptionMgt.IsIssueExcluded` filters table, SystemId, issue code and Active.
`AddCountFinding` applies enabled-check selection and emits only when count > 0.

| Check / display meaning | Module | Base → stored AL severity | Counter condition | Finding/count | Score contribution with DEV-only counts | Default annual impact at EUR 40/h |
|---|---|---|---|---|---:|---:|
| CUSTOMERS_MISSING_EMAIL / missing email | Finance | medium → medium | E-Mail = '' and no matching exception | 1 / 600 | 3 + 4 = 7 | 600 × 7.20 = 4,320 |
| VENDORS_MISSING_PHONE / missing phone | Finance | low → low | Phone No. = '' and no matching exception | 1 / 200 | 1 + 2 = 3 | 200 × 3.20 = 640 |
| ITEMS_WITHOUT_UNIT_PRICE / zero selling price | Inventory | medium → medium | Unit Price = 0 and no matching exception | 1 / 600 | 3 + 4 = 7 | 600 × 67.20 = 40,320 |
| ITEMS_WITHOUT_UNIT_COST / zero unit cost | Inventory | high → critical | Unit Cost = 0 and no matching exception | 1 / 600 | 10 + 4 = 14 | 600 × 57.60 = 34,560 |

The cost check escalates because `IsCriticalImpactIssue` matches WITHOUT_UNIT_COST.
The old per-check penalty argument is not the final score; `RecalculateScoreMetrics`
overwrites it. Backend impact recalculation can also update displayed severities later.
The default four-check sum is EUR 79,840; it is **not** a reconstruction of the reported
EUR 2,202,021.49, which includes other findings and possibly configured rates.

## 6. Generator-to-Check Mapping Matrix

| Scenario state | Expected and actual check | Detection | Aggregation / expected rows | Generated affected contribution | Status |
|---|---|---|---|---:|---|
| Customer email blank | CUSTOMERS_MISSING_EMAIL | Exact predicate match | Count; one row if enabled and positive | 600 | COVERED_AGGREGATED |
| Vendor phone blank | VENDORS_MISSING_PHONE | Exact predicate match | Count; one row if enabled and positive | 200 | COVERED_AGGREGATED |
| Item price zero | ITEMS_WITHOUT_UNIT_PRICE | Exact predicate match | Count; one row if enabled and positive | 600 | COVERED_AGGREGATED |
| Item cost zero | ITEMS_WITHOUT_UNIT_COST | Exact predicate match | Count; one row if enabled and positive | 600 | COVERED_AGGREGATED |
| Supporting UOM present, qty = 1 | No injected defect / no direct UOM scan | Not a detection target | No scenario finding | 0 | INTENTIONALLY_NOT_COVERED |

Per-check expected runtime total = pre-existing matching records + generated matching
records − excluded records, adjusted for intervening changes. Finding-count delta can be
zero when a baseline finding for that code already existed. Price zero does **not** also
match ITEMS_PRICE_BELOW_UNIT_COST, whose guard requires Unit Price > 0. Zero cost with
zero inventory does **not** match INVENTORY_WITHOUT_UNIT_COST (Inventory > 0 required).
Both blank BOM and blank routing do **not** match manufacturing's paired-field checks:
each requires one of the pair nonblank. Customer missing email does not imply a Contact
finding: the generator uses Insert(false) and does not create contacts.

Mapping classifications among four intentional types: COVERED_AGGREGATED 4;
COVERED/PARTIALLY_COVERED/GENERATOR_ONLY/PRODUCT_GAP/GENERATOR_DEFECT/AMBIGUOUS 0.
Runtime classification of each is still awaiting evidence; static status must not be
promoted into an observed success rate.

## 7. DEV Seed 5001 Reconstruction

Multiplication by 37 permutes residues modulo 100. Thus every complete entity block
contributes exactly ten labels. Customer 60 blocks × 10 = 600; Vendor 20 × 10 = 200;
Item 120 blocks alternate evenly: 60 × 10 price and 60 × 10 cost. Sum = **2,000**.
This is deterministic from committed counts/seed/schema; no additional ledger is needed
to derive this configured distribution. It does not establish that subscribers preserved
every intended field or that the deployed app matches this source.

## 8. Explanation of 2,000 Generated Scenarios

One committed labeled master row equals one counter increment. At most one injection
label per row, four labels total, no labels on UOM. Every scenario should contribute to
one direct aggregate count, but many other checks can flag the same row. A completed
counter cannot itself prove downstream detection; it records generator intent.

## 9. Explanation of 95 Findings

`AddCountFinding` inserts one `DH Deep Scan Finding` and increments `IssuesCount` once,
independent of the count (runner L2042). Duplicate checks call `InsertFinding` and increment
separately per detected group/iteration. `ProcessRun` writes Issues Count; BC pages display
that field. `BuildSyncPayload` serializes all finding rows and Issues Count separately;
backend `routers/scans.py` stores both. It does not reinterpret 95 as 95 records.

Therefore 95 means 95 emitted finding rows if the reported run followed this source.
It is not guaranteed to mean 95 distinct check IDs because duplicate checks can emit
several rows for the same ID, including erroneous repetitions described in section 16.
Four injected checks cannot explain the identity of all 95 rows. The source supports
many additional defaults and company-wide baseline findings. No list of 95 was invented.
Required reconciliation: exported finding row count = 95; group by code/category; retain
multiple rows per code; reconcile each count and sum. Until then exact 95-row attribution
is **AWAITING_MANUAL_BC_RUNTIME_EVIDENCE**.

## 10. Explanation of 224,999 Affected Records

AL `RecalculateScoreMetrics` (L2114) sums `Finding."Affected Count"` for the run.
Backend `analytics.py` (L1274) independently sums persisted issue affected_count.
There is no set of record IDs and no cross-check deduplication. A customer flagged by
eight checks contributes eight occurrences. Aging/dead-stock thresholds also overlap;
duplicate-marker defects can repeat an entire group. No estimate is introduced by this
sum, though it inherits any errors in contributing counters.

Company-wide reads include CRONUS or other baseline records **if present**; their actual
presence/count is unverified. Tables include customers/vendors/items, G/L accounts and
entries, customer/vendor/item ledgers, sales/purchase headers/lines, contacts, production
BOM/routing/work/machine-center tables, service, job and employee tables (exact inventory
in the catalog). The generator writes only the three master tables and supporting UOM.
Item UOM and BCP ownership/run rows are neither direct affected-count inputs nor included
in `DHDataProfilingMgt`'s 13-table total. Valid base UOM prevents a missing-base-UOM check;
it is not counted as another affected record.

### Conditional generated contribution, derived from fields and predicates

Assume all relevant modules/checks enabled, no exceptions, unchanged records, standard
blank/zero initial values, no subscriber effects. Existing data is additional.

| Generated state | Checks | Arithmetic | Occurrences |
|---|---:|---|---:|
| Four explicit injections | 4 | 600+200+600+600 | 2,000 |
| Vendors Preferred Bank Account Code blank | 1 | 2,000 | 2,000 |
| Customers VAT ID, salesperson, price group, discount group, reminder terms, finance charge terms, contact, home page blank | 8 | 8×6,000 | 48,000 |
| Vendors VAT ID, purchaser, contact, home page blank | 4 | 4×2,000 | 8,000 |
| Items Standard Cost, Last Direct Cost, Lead Time, Safety Stock, Reorder Point, Maximum Inventory, Minimum Order Qty, Order Multiple, Shelf No., Tariff No., Gross Weight, Net Weight, Unit Volume blank/zero | 13 | 13×12,000 | 156,000 |
| **Total** | **30** | | **216,000** |

These are actual Finance/vendor/inventory predicates, not hypothetical multiplication
of every record by every rule. They are not 216,000 distinct rows. The residual
224,999 − 216,000 = **8,999** is only a reconciliation target under those assumptions;
do not label it CRONUS evidence or assign it to particular checks without an export.
Likewise 95−30 = 65 is a conditional row residual, not a proven baseline finding count.

The UI wording “Affected Records” / “Betroffene Datensätze” lacks this qualification.
Classify **F. DASHBOARD_SEMANTIC_GAP**; proposed wording: “Betroffenheiten über Prüfungen
(Mehrfachzählungen möglich)” with separate table population metrics. No UI change in this audit.

## 11. Score Validation

AL final per-finding penalty = severity penalty (low 1, medium 3, high 6, critical 10;
unknown 2) + affected-count penalty (positive <50:1, ≥50:2, ≥250:4, ≥1,000:6, ≥5,000:8).
Module penalty P is summed across all its finding rows. Module score is
`100 - floor(P*100/(P+40))`; with no penalty it is 100. This is not percent clean records.
Repeated or overlapping findings can penalize the same business record several times.

Weights in runner L2159 onward: System 15, Finance 20, Sales 15, Purchasing 10,
Inventory 15, CRM 5, Manufacturing 10, Service 5, Jobs 3, HR 2. Only enabled modules
enter numerator/denominator. Round via `(weightedSum + enabledWeight div 2) div enabledWeight`.

All ten reported module scores: weighted sum **4,410**, denominator 100 → **44**.
First seven only: weighted sum **3,410**, denominator 90 → **38**.
The latter is a compatible configuration, not a verified fact about this run. Disabled
modules also normalize to 100. Setup does not force all modules on for every free run;
RunChecks honors the individual module flags. Backend sync preserves supplied overall
and module scores rather than recalculating them from post-sync severities.

Status: formula/numeric reconciliation **PASS conditionally**; exact run configuration
and individual module penalties **AWAITING_MANUAL_BC_RUNTIME_EVIDENCE**. If all ten were
actually enabled under this implementation and the same run, 38 would be inconsistent.
Finance and Inventory tie at 16; “Finance highest risk” alone does not establish a score defect.

## 12. Impact Validation

`backend/app/services/impact_service.py` supplies per-code definitions/config overrides.
For each finding: `round(count × minutes/60 × probability × frequency/year × hourlyRate, 2)`.
The scan sums these rounded amounts (two decimals). The default hourly rate is EUR 40,
but runtime IssueImpactConfig/ImpactSettingsConfig may override defaults. This is estimated
annual remediation/operational exposure, not booked financial loss. Overlapping checks
are additive; no cross-check deduplication or causal-independence adjustment exists.

AL initially stores zero impact; the backend response updates scan commercials and
individual findings (`ApplySyncCommercials`, `ApplySyncFindingImpacts`). Dashboard payload
retains a numeric amount with cents. `analytics-dashboard.js:formatCurrency` uses 2 decimals;
`formatKpiCurrency` uses 0 and is called by the KPI loss widget (L1305).
**PASS: 2,202,021.49 formats to 2,202,021; this is not evidence of lost cents.**
The actual JavaScript functions were executed with Node Intl: KPI `2.202.021 €`, detail
`2.202.021,49 €`; evidence: `.build/ext-50-12c/currency-format.json`.
Actual end-to-end payload equality and total recalculation remain unverified. Duplicate
rows of the same code have an additional AL response matching defect, described below.

## 13. Free Scan Semantics

There is no free-only subset in `RunChecks`. The same checks run for every enabled module.
`DHScanCheckMgt.IsCheckEnabled` returns true when Monitoring Active is false; per-check
selection is a Monitoring feature. Module selection and exceptions remain relevant.
The generator's four IDs are therefore not removed just because the run is free.

Important current-version distinction: free does **not** universally mean “all findings hidden”.
`product_license_service.py` computes permanent free result access after a completed free
scan. `can_view_issues`, `can_view_reports`, `can_view_issue_details` use protected access
(including permanent free); actions and record-level details require premium. Analytics
uses these access flags. Some older marketing/preview strings still suggest more restrictive
access; use actual flags rather than those strings. No record-detail entitlement was bypassed.

## 14. Performance Benchmark

20,000 generated business records + 12,000 supporting UOM → scan wall time **502.226 s**.
Normalized business workload rate = **39.8227 business records/s**.
Duration per 1,000 generated business records = **25.1113 s**.
These divide known fixture population by total run wall time; they are not measured
database reads/s or unique affected records/s. The scanner also reads baseline tables,
performs repeated scans/FlowFields, sends progress, profiles tables and synchronizes.
`ProcessRun` starts timing before checks and completes after sync, so this is not pure AL CPU time.
No checks/s is claimed: declared counts are inaccurate and record-level evaluations are unmeasured.
Generator's roughly 200 s / 99.69 records/s describes insertion, a different operation.

One user-reported completed/synchronized DEV run establishes a useful observation, not
repeatability, a performance SLA or LARGE capacity. No linear 500k/2M/5M forecast is made.

## 15. Scaling Risks

| Evidence | Risk / evidence required |
|---|---|
| Master tables read in several module procedures | Repeated O(n) passes; shared counts would need semantic review |
| ItemMasterData and InventoryValue call CalcFields(Inventory) per item | Repeated FlowField queries; capture BC telemetry/query duration |
| GetLastItemMovementDate called for every item, even zero-inventory items | Per-item filtered ledger FindLast; 12,000 probes here, 300,000 at LARGE before baseline |
| VAT/name duplicate outer FindSet + per-value inner FindSet | A repeated group of k can cause k×k visits because marker guard fails; worst-case quadratic. Unique names still cause per-row probes |
| Email query groups values then CountCustomers/VendorsByEmail rescans | N+1 queries, even unique emails; query aggregate is not sufficient because exceptions must be honored |
| ExceptionMgt.IsIssueExcluded per matching predicate | Repeated table/index lookups, plus exception tracking; capture calls and SQL plans |
| FindingExists filters Title with leading wildcard | Non-sargable marker lookup and no matching stored marker; cannot assert index efficiency |
| Table counts in BuildDataProfile occur individually and again in total | Redundant counts; cost depends on BC/SQL indexes and filters |
| BuildSyncPayload accumulates JSON findings | O(finding rows) memory; normally small but repeated duplicate groups can inflate it |
| Progress at module boundaries, final sync | Network overhead is per phase/run, not per generated record; no per-record HTTP found |
| Runner commits at progress/finalization boundaries; generator at bounded batches | No per-record Commit in inspected generation/scan loops; not a license to extrapolate transaction costs |

Unindexed table scans cannot be proven from AL alone; deployed keys/extensions and actual
query telemetry are needed. No timing attribution to a particular risk is claimed.
No unbounded temporary business-record accumulation was found in the relevant generator
batch; ownership persistence is intentionally O(business+support). Baseline transaction
workload is not covered by this master-data benchmark.

## 16. Identified Defects and Gaps

| ID / category | Proven source observation | Consequence / proposed minimal correction |
|---|---|---|
| C12-01 B. AGGREGATION_EFFECT | One row per positive AddCountFinding; sum counts | Expected difference between 2,000 labels, 95 rows, 224,999 occurrences |
| C12-02 A. EXPECTED_BEHAVIOR | Four injection labels; many unrelated defaults | 10% injection rate is not 10% total defects or 90 score |
| C12-03 F. DASHBOARD_SEMANTIC_GAP | Sum labeled as records without uniqueness qualification | Clarify occurrence metric and unexecuted module display; do not change counting silently |
| C12-04 D. PRODUCT_CHECK_DEFECT | VAT/name FindingExists looks for ValueMarker in Title; InsertFinding stores only IssueCode (runner L2759 vs L2733) | Group repetition/inflation and quadratic work; process each exact group once with a local keyed set/buffer, not wildcard text search |
| C12-05 D. PRODUCT_CHECK_DEFECT | System declares 14 but has 13 check sites; InventoryValue declares 21 but has 19 | All-module counter 202 vs catalog 199; correct to 13/19 or count execution centrally with enabled semantics |
| C12-06 D. PRODUCT_CHECK_DEFECT | ApplySyncFindingImpacts matches only run+Issue Code and FindFirst for each response row | When a code has multiple groups, only the first AL row gets repeatedly overwritten; other rows retain initial impact. Introduce stable finding identity, backward-compatible payload, or explicit group aggregation contract |
| C12-07 G. TEST_EVIDENCE_GAP | Existing AL self-tests validate policy/config, not generator → productive scanner | Implement small isolated runtime contract below; source tests are not a substitute |
| C12-08 I. UNKNOWN_NEEDS_RUNTIME_EVIDENCE | No finding export, enabled modules, deployed versions or impact settings | Exact 95/224,999/38/impact totals cannot be signed off |
| C12-09 H. PERFORMANCE_RISK | Nested duplicates, repeated CalcFields/queries and full-table passes | Telemetry and bounded staged benchmarks before LARGE |

No **C. GENERATOR_DEFECT** was established in the four injected scenarios. No
**E. PRODUCT_COVERAGE_GAP** was established for them. Missing transactional generator
workloads are intentionally outside scope, not evidence of absent product checks.

C12-04 constructive reproduction from source: three customers with the same VAT `QA123`
and no exclusions each see no finding title containing QA123, each count three records,
and each emit a row. Result: three rows, nine occurrences instead of one group/three.
Name/Post/City has the same structure. Arbitrary VAT text accidentally matching an issue
code could instead suppress detection; storing a true group key avoids this ambiguity.
Generated VAT IDs are blank and generated names unique, so this does not prove the defect
affected the supplied DEV run. It may affect baseline data. A real AL fixture remains open.

C12-06 is independently reachable even with correctly grouped email duplicates: response
groups of sizes two and three share one code; two loop iterations select the same first AL
row. Scan-level total can still be correct because commercials are assigned separately.
Impact/severity round-trip tests must include multiple groups per code.

Minimal fixes are **designed, not applied** in this audit. C12-04/06 need group identity and
backward-compatibility decisions plus real AL/runtime regression before a safe fix is claimed.
Three new strict expected-failure source tests record C12-04 and both C12-05 discrepancies.
They do not weaken existing tests; XPASS fails so a future correction requires removing
the marker. C12-06 needs a runtime round-trip contract, not a passing source assertion.

## 17. Detection Accuracy Contract and Evidence Ledger

### Implemented offline evidence

`backend/tests/test_ext_50_12c_detection_accuracy.py` checks independent expected DEV totals,
rates, the n=100 alternating boundary, source formula/labels, actual four predicates,
aggregation guard, complete catalog coverage, sum semantics and the two score configurations.
14 pass; three known source-defect expectations remain XFAIL. This is deliberately named
static evidence and does not report that BCSentinel executed against generated data.

### Proposed real BC contract (new isolated QA company only)

1. Pin BC build, installed app hashes/versions, schema=1, setup/config and exceptions.
   Use a new authorized BCS-PERF test company, never alter the preserved BCS-PERF-DEV.
2. Custom targets Customer=100, Vendor=100, Item=200, seed=5001, rate=10. Expected labels
   10/10/10/10, 400 business records, 200 supporting UOM. Snapshot baseline predicates/counts.
3. Call existing generator batch/coordinator normally. Confirm completed, failed batches=0,
   exact ownership counts, exactly one label per intended record, no support label. Read
   generated fields through owned SystemIds and assert the intended blank/zero values.
4. Execute the actual DH Deep Scan Runner with Finance/Inventory enabled. Capture check
   execution explicitly: Last Run fields are Monitoring-only and Checks Count is not a
   reliable per-check trace. A QA test-only observer/event is preferable if instrumentation
   is needed; disabled/exception controls must be separate labeled test cases.
5. Assert exactly one row for each of the four count-check IDs and final affected_count =
   baseline matching non-excluded count + 10. A mere ≥10 assertion is insufficient because
   baseline defects could mask non-detection. If baseline cannot be fixed, independently
   enumerate predicate matches and reconcile ownership-attributed deltas exactly.
6. Check negative controls: generated good rows do not match those four predicates; price
   and cost injection sets are disjoint; UOM has no label; no artificial 40-findings assertion.
7. Aggregate reconciliation: sum all finding counts equals AL Affected Records and backend
   dashboard KPI; finding row count equals Issues Count. No unique-record assertion.
8. Recompute module scores using the **pre-sync AL severities**, enabled module flags and
   exact counts; preserve separately any backend severity promotion. Recompute impact
   using pinned rate/definition snapshots; verify decimal persistence and display formatting.
9. Add baseline-only duplicates (multiple email/VAT/name groups, exclusions and unique values),
   multi-row same-code response mapping, disabled module/check cases and tenant isolation.
   Run against future fixes and before/after deployment; never use the preserved DEV company.

No additional table is currently necessary to reconstruct intended injection counts:
`BCP Owned Record.Scenario` is already an evidence ledger. Prefer a read-only QA export of
Run ID, schema/app version, scenario, table, count, supporting count and expected check ID.
For long-term retention after separately authorized cleanup, consider a QA-only aggregate
snapshot keyed by Run ID+Scenario+Entity, committed atomically with checkpoints or finalized
idempotently. Count committed ownership, never increment twice on resume. Include generator
and check version hashes and detection type; no names, record contents, secrets or production
data. Preserve the distinction intended count / actual field validation / observed detection.
No ledger schema or AL object IDs were changed here.

## 18. Automated Verification and Recommended Next Steps

### Local test evidence

All Python runs used `backend/.venv/Scripts/python.exe`; tests were launched from backend.
The product build used `New-BCBuildWorkspace.ps1 -Profile ReleaseCloud -OutputPath
.build/bc-extension/Ext5012CProduct`, AL compiler 17.0.34.45391 and the existing BC27
symbol cache under `.build/bc-extension/PerformanceQA/.alpackages`. No existing APP,
ZIP, PDF or build artifact was overwritten; outputs are in the new audit workspace.
Full backend regression used the repository's normal disposable SQLite test harness;
PostgreSQL-specific tests were not replaced with SQLite assertions.

| Suite / artifact (repository-relative) | Result |
|---|---|
| Existing 12A + release/fresh/upgrade/remediation/free-findings/pilot contracts; `.build/ext-50-12c/existing-contracts.xml` | **PASS 49**, including 20 generator cases |
| New accuracy contracts; `.build/ext-50-12c/accuracy-contract.xml` | **PASS 14; XFAIL 3** (known defects, not passing tests) |
| Full existing backend suite; `.build/ext-50-12c/backend-regression.xml` and `.log` | **PASS 461; SKIP 7; FAIL 0**, 93 warnings, 164.60 s |
| PR39 exact-head isolated recovery contracts; `.build/ext-50-12c/recovery-contract.xml` | **PASS 9** |
| `Test-ALSourceUniqueness.ps1` | **PASS**, 109 product declarations; no product AL changes |
| `Test-GL01CDHExceptions.ps1` | **PASS**, 7 contracts |
| `Test-GL01FFirstRunUX.ps1` | **PASS** |
| Local PostgreSQL concurrency/transaction suite | **BLOCKED**, Docker engine unavailable, no test PostgreSQL configured; seven skips above |
| Local product AL compile / CodeCop / PTECop; `.build/ext-50-12c/product-compile-cops.log` | **PASS**, exit 0, 270 existing warnings, 0 errors |
| Local product AppSourceCop; `.build/ext-50-12c/product-compile-appsource.log` | **EXPECTED BASELINE FAIL**, exit 1: 3×AS0051 + 1×AS0084 errors, 1×AS0092 warning |
| QA app compile/Cops | Existing exact-head fresh/upgrade CI PASS; not rerun locally |
| Actual dashboard JavaScript currency functions; `.build/ext-50-12c/currency-format.json` | **PASS**, cents retained in detail, integer KPI |
| Real BC generator-to-check detection test | **BLOCKED / AWAITING_MANUAL_BC_RUNTIME_EVIDENCE** |

The 461-test suite was collected before the new 17-case accuracy file was added; these
are separately reported runs, not a claim of 478 tests in one run. Full regression covers
scan lifecycle/sync, impact, dashboard serialization/access, tenant isolation, pilot and
existing release contracts. Warnings include existing deprecations; early contract runs
also encountered pytest cache-write warnings, which did not fail tests.

### Verified existing CI, not new 12C runs

| Head | Gate | Link / observed result |
|---|---|---|
| 89faeb7 (#38) | BC27 compile + CodeCop/PTECop, fresh and upgrade | [35069195954](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35069195954), both success |
| 89faeb7 (#38) | Generator safety contracts | [35069195980](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35069195980), success |
| 89faeb7 (#38) | Automated pilot readiness | [35069195958](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35069195958), success |
| 00b7b4e (#39) | BC27 compile/Cops | [35115002798](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35115002798), success |
| 00b7b4e (#39) | BC27 publish/install gate | [35115002688](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35115002688), success |
| 00b7b4e (#39) | Recovery safety contracts | [35115002915](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35115002915), success |
| 00b7b4e (#39) | Automated pilot readiness | [35115002727](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35115002727), success |

Existing local `.build/ext-50-12a/runtime-fix-upgrade-diagnostics/qa-al-tests.xml` records
eight AL self-tests without failures; deployment text reports QA 1.0.0.1 upgrade installed.
Those policy/dialog self-tests are not SaaS detection evidence. The existing warning summary
contains 270 unique CodeCop warning lines; CI success does not mean warning-free. The local 12C product compilation reproduces all 270 CodeCop warnings and no errors.
AppSourceCop reproduces the known baseline exactly (3×AS0051, 1×AS0084, 1×AS0092);
this remains an expected failure, never a pass. The separate cached PostgreSQL CI artifact
`.build/ext-50-12a/runtime-fix-pilot-ci/backend/pilot-e2e-postgres-junit.xml` was inspected:
7 tests, zero failures/errors/skips. This historical exact-head CI gate does not change
the current local PostgreSQL BLOCKED result.

### Next actions in order

1. Read-only export for the exact DEV run: all finding rows (entry ID, code, category,
   severity, affected count, impact), run counters/module scores and enabled_modules,
   app/BC versions, owned scenario aggregate counts, active exception counts and impact
   definitions/rate at scan time. Exclude API/execution tokens and personal record contents.
2. Reconcile 95 rows and 224,999 sum exactly; compare each of the four direct counts with
   owned records plus baseline/exclusions. Confirm score 38 using actual module flags.
3. Review C12-04/05/06 minimal fixes; implement regressions and fixes separately after this
   audit review, retaining backward compatibility and existing checks. Do not adjust the
   four generator scenarios merely to improve score or reduce unrelated findings.
4. Execute the small runtime contract in a new authorized QA company; retain exact app
   versions, non-SUPER permissions and deterministic evidence. Resolve recovery/adversarial
   and upgrade gates independently. Do not run recovery on the preserved DEV evidence.
5. Capture module/query timings on repeated DEV and an intermediate bounded workload
   before evaluating LARGE. No cleanup, company deletion or production operation is part
   of these recommendations without its own explicit authorization.

## 19. Readiness Decision for LARGE

**NOT_READY_FOR_LARGE**.

| Required criterion | Status |
|---|---|
| Generator semantics / 2,000 counter | PASS, source and deterministic reconstruction |
| Relevant scenario mapping | PASS static 4/4; runtime unverified |
| 95 findings / 224,999 occurrences | Semantics explained; exact run reconciliation OPEN |
| No critical generator defect | None identified statically; deployment/permissions gates remain open |
| No critical product detection defect | NOT established: duplicate grouping/round-trip defects unresolved |
| DEV technically stable | User-reported Completed/Synchronized, one sample; repeatability unverified |
| Performance assessed | Source risks identified; measurement attribution/LARGE capacity OPEN |
| Data safety | Audit preserved all BC data; operational LARGE permission/recovery gates OPEN |
| Score / impact evidence | Conditional score reconciliation; impact display PASS; exact totals OPEN |

Existing successful CI and the completed DEV observation do not close sandbox permissions,
copied-company identity/recovery, adversarial cancellation/resume/rollback, or real SaaS
fresh/upgrade gates. These are separate gates, not replaced by static mapping coverage.
