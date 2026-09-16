# EXT-50-12C.1 — Runtime Finding Reconciliation & Detection Evidence

Status: **AWAITING_MANUAL_BC_RUNTIME_EVIDENCE / NOT_READY_FOR_LARGE**.
No live BC or backend data was changed, no recovery/cleanup/scan was invoked.
This report separates user-reported observations, source-derived behavior and actual exports.
The current evidence contains **no actual finding export**. None of the 95 rows is invented.

## Repository and preservation

The original checkout remains on `codex/ext-50-12c-detection-accuracy`, HEAD
`89faeb721ed5488ee97c07a620c5184deba6f2e8`, with its two pre-existing user edits intact.
Local `staging` is older (`274f9a64596dd23c8546c1c298018c6f05be8277`); verified remote
`staging`/`origin/staging` is `867b1f7cef5f20064a5f61655e1e00edf3d24dd3`.
The new branch `sprint/ext-50-12c-runtime-detection-evidence` starts at the remote staging
head, in `.build/ext-50-12c-runtime-worktree`. Only 12C audit/evidence/test work was copied.
It does not include the implementation commits of either open PR.

The generator's two relevant codeunits are preserved as a hash-checked JSON source snapshot
at PR38 head, `quality/release/ext-50-12c-generator-source.json`. This is not a generator
installation or BC runtime evidence. Tests compare the snapshot to current generator source
as well if that source exists. This keeps the PR independent of the unmerged generator.

PR38: OPEN, head `89faeb721ed5488ee97c07a620c5184deba6f2e8`.
PR39: OPEN, head `00b7b4ed31b70fd14681f0e3b913337bf29c1f78`.
Both target staging; existing CI checks remained green during this audit. Their branches,
content and PR metadata were not modified. PR39's scanner source was fetched read-only
at that exact SHA and compared equal to the staging scanner. Thus its app 1.0.2.21
recovery changes do not invalidate the inspected scanner source. The installed package
hash/backend deployment SHA still need independent capture.

## Updated runtime observations

Source: user's 12C.1 report, not a captured API response.

- BC27 SaaS, company BCS-PERF-DEV, copied from CRONUS; app 1.0.2.21.
- Generator Run 1, seed 5001, rate 10%, 6,000/2,000/12,000 masters, 2,000 injections,
  zero failed batches. The 20,000 masters must remain unchanged.
- Recovery Cancel left data unchanged; confirmed recovery removed copied local binding,
  old scan history and scheduler state; business/generated data survived. New registration
  and current-company identity were successful. This is a **user-reported manual PASS**,
  not an independently executed test or proof of every adversarial recovery case.
- Scan `RUN_20260916_000001_43F57A071BFF485BAF20C68FF578B`, 16 September 18:31–18:39,
  502.226 seconds, Completed/Synchronized, score 38, 95 reported findings.
- Impact EUR 2,202,021.49; dashboard EUR 2,202,021; 224,999 dashboard occurrences;
  potential saving displayed EUR 1,541,415.
- Setup before scan: 7/10 modules, 165/165 active checks.

Machine-readable input: `quality/release/ext-50-12c-runtime-reported.json`.
Its `USER_REPORTED_NOT_RAW_EXPORT` provenance and empty `exports` are intentional.

## Reconciled summary arithmetic

The seven modules with non-100 reported scores are System, Finance, Sales, Purchasing,
Inventory, CRM and Manufacturing. Their catalog contains **165** checks:
199 minus Service 12, Jobs 10 and HR 12. This matches the reported 165/165 selection.
The weighted sum is 3,410, active weight 90, rounded score **38**. These three observations
are internally consistent; the exact named flags should still be retained from the run
payload rather than treating the current setup as an immutable historical snapshot.

The runner's hardcoded counters would report **168** for those same modules (System +1,
InventoryValue +2). Therefore “165/165 Active Checks” is a catalog/selection metric and
does not disprove the previously found counter discrepancy. Export the actual run's
Checks Count separately. Neither value is a record-level evaluation count.

EUR 2,202,021.49 × 0.7 = EUR 1,541,415.043, stored rounded to cents = EUR 1,541,415.04,
displayed at zero decimals = **EUR 1,541,415**. This is consistent with the default saving
factor, but the runtime settings snapshot is needed to confirm that factor was used.
The earlier actual-JavaScript check already demonstrated integer KPI vs cent detail
formatting. No loss of cents is inferred from the display difference.

## Important correction to the original audit: backend deduplication

The original 12C report did not fully trace the same-code projection in `sync_scan`.
The exact current source in `backend/app/routers/scans.py` is:

```python
commercials = _calculate_commercials(payload, db)
recalculated_issues = list(
    {str(issue["code"]): issue for issue in commercials["issues"]}.values()
)
```

Commercials are calculated over **all** incoming rows first. The dictionary then keeps
only the **last row per check code**, not the sum of its groups. `ScanIssueRecord` also has
a unique `(scan_id, code)` constraint. The backend stores the supplied Issues Count
separately; the dashboard sums the affected_count of the **retained** backend rows.
The sync response returns the retained rows. AL `ApplySyncFindingImpacts` finds only
the first matching BC row per returned code and updates that row.

For two same-code groups with counts 2 and 3, the source projection retains 3, not 5.
The offline regression executes that exact AST expression from the product source and
demonstrates the result. It does not pretend to execute a SaaS or database request.

Consequences requiring runtime comparison:

1. BC Issues Count=95 need not equal the number of stored backend issue rows.
2. The BC sum of all finding occurrences need not equal dashboard 224,999.
3. Backend total impact can include all incoming groups while persisted issue impacts
   include only the last group per code. The total can differ from the sum of stored rows.
4. The earlier description of repeated response updates for each duplicate row was too
   broad: normal backend responses already collapse duplicates. The surviving amount is
   assigned to the **first BC row**, although it came from the **last incoming group**.

Classification: **source-proven lossy projection and group-identity mismatch**, not a
proven cause of this DEV run's metrics. If the 95 BC rows all have unique codes, this path
does not change their count. Actual BC and backend inventories decide which case applies.
No product correction, schema change or weakened validation was made.

## Finding inventory: authoritative sources and UI traps

| Source | Identity / contents | Use |
|---|---|---|
| BC table 53128 DH Deep Scan Run | Entry No., Run ID, Issues Count, Checks Count, scores, times, totals | Resolve the exact Run ID within BCS-PERF-DEV; retain its Entry No. |
| BC table 53129 DH Deep Scan Finding | Entry No.; Deep Scan Entry No.; Issue Code; Category; Title; Severity; Affected Count; Estimated Impact (EUR) | Primary persisted BC inventory. Filter by the resolved run entry; preserve all rows and original Entry No. order |
| BC table 53121 DH Scan Issue | Linked by Scan Entry No. | Separate scan/dashboard projection, not a substitute for the deep-run finding inventory |
| BC table 53133 DH Dashboard Issue | Dashboard-facing data | Not an authoritative raw export of table 53129 |
| Backend scans | scan_id, tenant_id, supplied Issues Count, scores, enabled_modules, commercials | Must be selected with authenticated company/tenant context |
| Backend scan_issues | id, scan_id, code, category, severity, affected_count, estimated_impact_eur | At most one row per scan/code; compare with full BC inventory explicitly |
| BCP Owned Record | Run ID, table, SystemId, Scenario, Supporting | Read-only attribution to generator Run 1; export aggregate counts, not identifying master contents |

There is no immutable per-affected-record historical detail table in this finding model.
`DHIssueDrilldownMgt.OpenDeepScanFinding` passes the check ID to the drilldown dispatcher;
that inspects current business records. It is not a snapshot of exactly what matched at
18:31. Current-state attribution is useful only with an explicit unchanged-data assumption.

The Finding pages are temporary views. `DHDeepScanFindingsList.LoadPageData` copies full
rows for premium details, but its free summary path groups by **Category + Severity**
and sums counts. Exporting that displayed free list can lose check IDs and row identity.
Do not upgrade access, change permissions, run remediation or edit data to obtain evidence.
Use an already authorized read-only export of the persisted table, or have the operator
supply the approved sanitized evidence. Do not claim a grouped UI list is all 95 raw rows.

The existing authenticated `GET /analytics/embed/data?scan_id=...` can expose dashboard
findings under the existing access capability. The user's company context and selected
scan must be confirmed. The API's issue list represents the backend projection and lacks
raw BC finding IDs. Its preview arrays are not complete inventory. Never copy embed tokens,
cookies, API tokens or URLs containing tokens into Git, evidence JSON or chat.
No new web service/API page was published and no token was read for this sprint.
A separate local diagnostic package now provides the authorized manual read-only export.

## Read-only evidence acquisition contract

Runtime access available here: browser inventory contained only the empty Codex browser,
no authenticated BC/dashboard tab. No raw finding exports were present in the existing
audit artifacts. The initial instruction ended mid-Phase 2; the user subsequently supplied the
continuation and explicitly requested a minimal read-only SaaS export if no automatic
access was available. That diagnostic has now been built; see the manual export guide.

Required operator-provided exports, preserving source provenance/date and row counts:

1. BC table 53129 for the exact run, all persisted rows ordered by Entry No.; table 53128
   selected counters/scores/times, scan-time enabled modules, installed package versions.
2. Backend selected scan and all persisted scan_issues for that same authenticated tenant
   and scan. Record which fields came from stored rows vs dashboard projections.
3. For each of the four scenario IDs: Run 1 ownership label count, count whose actual owned
   master field matches the check, matching owned exceptions, and matching non-owned,
   non-excluded records. This separates CRONUS/source configuration records from generated
   records. A record can contribute to several different checks; do not deduplicate across codes.
4. Impact definition/rate/saving-factor snapshot at scan time. Retain pre-sync severity
   evidence if available; stored post-sync severity may differ from the one used in AL scores.

These are **read-only requests**. Do not rerun the scan, recover registration, clear history,
cleanup or repair records. Do not export names, addresses, contact data, tokens or full
record contents. Absent historical evidence remains absent; do not fabricate a baseline.
The 216,000 source-derived contribution remains conditional. The 8,999 residual cannot
be assigned to CRONUS without counts; backend deduplication must be considered too.

## Offline normalization and reconciliation

`scripts/reconcile_ext_50_12c.py` uses no network or database library. It accepts a sanitized
JSON input and records its SHA256. Original evidence must not be overwritten.
Add `exports.bc` and `exports.backend` to a local copy of the reported input, each as:

```json
{
  "company": "BCS-PERF-DEV",
  "scan_id": "RUN_20260916_000001_43F57A071BFF485BAF20C68FF578B",
  "complete": true,
  "exported_row_count": 0,
  "rows": []
}
```

The empty envelope is a schema example, **not** a zero-finding observation. Each real row
requires a unique nonempty string `id`, `code`, `category`, `severity` (low/medium/high/critical),
integer `affected_count` and exact-decimal string `impact_eur`. Preserve BC payload order.
For dashboard-only rows use explicitly documented synthetic export-row IDs, not invented BC
Entry Nos.; the acquisition note must state that limitation. Never discard repeated codes.

Optional `scenario_observations` maps each of the four scenario codes to:
`generated_count`, `matching_owned_count`, `excluded_matching_owned_count`,
`non_owned_nonexcluded_matches`. The tool verifies generated field matches separately
from the total count, so baseline defects cannot hide absent generated detections.

From repository root, using the authorized existing backend interpreter:

```powershell
backend\.venv\Scripts\python.exe scripts/reconcile_ext_50_12c.py `
  --input quality/release/ext-50-12c-runtime-reported.json `
  --output quality/release/ext-50-12c-runtime-reconciliation.json
```

In the isolated worktree use the original checkout's absolute interpreter path. Exit 2
means missing evidence/BLOCKED; exit 1 means a numerical mismatch/FAIL. The tool intentionally
cannot grant LARGE readiness. Finding-derived scores and configured impact recalculation
remain explicit open checks; the current implementation does not claim to implement those
without their necessary source snapshots. Module-summary arithmetic alone is not runtime accuracy.

## Tests and readiness

The initial saved static audit tests passed 14 cases with 3 strict XFAILs for known source
defects, unchanged in purpose. New offline tests cover missing exports, mismatched company/run,
partial exports, duplicate row IDs, invalid numbers, same-code row preservation, first/last
impact mismatch, baseline masking, 165-check selection and actual backend source projection.
Synthetic test rows are never saved as real scan evidence.

Exact test/CI results are recorded in the PR and verification artifact. Tests cannot replace
the two missing inventories. Existing PR38/39 CI status is historical evidence and does not
certify the new branch. No BC runtime operation is included in any local test.

**NOT_READY_FOR_LARGE** until both inventories and generator attribution reconcile, source
loss/mismatch paths are classified against the actual run, and score/impact evidence is complete.
Next action: follow [the manual export guide](EXT_50_12C_1_MANUAL_EXPORT.md) and supply
the downloaded JSON. No remaining task text is needed. The successful manual recovery report is retained separately;
it does not close the runtime detection or performance gates.


## Current delivery status — 2026-09-17

**MANUAL_RUNTIME_EXPORT_REQUIRED**. The separate diagnostic app is compiled, locally
verified and ready for manual installation/export in the named sandbox. It has not been
installed or executed in SaaS by this agent. No runtime finding rows have been received.

Local full backend regression on the staging-based branch: **467 PASS, 1 FAIL, 7 SKIP,
3 XFAIL** (149.08 s). The failure is the unchanged staging billing fixture
`test_subscription_created_cannot_downgrade_active_monitoring_annual`: its monthly expiry
is fixed at 2026-08-15, already past on the test date. The single test independently
reproduces the failure; product code and that test are byte-identical to staging. The
existing PR38/39 fixture correction was not copied into this independent audit PR.
No assertion was weakened. The final focused export/reconciliation suite and package
results are in `quality/release/ext-50-12c-1-export-verification.json`. Full regression
was collected before the last focused tests were added; counts must not be combined
as if they were one run. PostgreSQL-specific tests remain skipped locally, not passed.
