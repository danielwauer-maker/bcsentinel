# EXT-50-12C.3 — Lossless Finding Identity

## 1. Ausgangslage und Branch-Basis

Repair branch: `sprint/ext-50-12c-3-lossless-findings`, based on audit PR #40 at
`f312eaf322b7e1083fffbb15b2001e04c32e9523`. Its PR targets
`sprint/ext-50-12c-runtime-detection-evidence`, explicitly depending on #40.
Integration staging was `867b1f7cef5f20064a5f61655e1e00edf3d24dd3`.
PR #38 (`89faeb721ed5488ee97c07a620c5184deba6f2e8`) and #39
(`00b7b4ed31b70fd14681f0e3b913337bf29c1f78`) remain untouched.
Neither generator changes nor copied-company recovery changes are incorporated.
The immutable #39 source is used ONLY as an isolated CI upgrade baseline.

Historical `quality/release/ext-50-12c-dev-run1-evidence.json` remains byte-identical:
SHA256 `4914706b1f8d259a0c46e4002a7dda20ac347be08b5bee5c46226504e4ba179f`.
The real scan contains 95 rows and 95 distinct checks, 224999 occurrences,
EUR 2202021.49 impact, EUR 1541415.04 savings, score 38 and 165 checks.
It does NOT demonstrate loss caused by repeated check IDs. No historical values
or generator data were changed.

## 2. DEF-001: persistence

`scans.py` previously projected recalculated issues into a dictionary keyed by
check code after computing commercial totals. Last row won; the database also
required unique `(scan_id, code)`. The replacement preserves every issue and
upserts by `(scan_id, finding_id)`.

## 3. DEF-002: impact return mapping

The AL response handler previously selected the first row matching run and check.
It now parses `finding_id`, rejects duplicate/malformed identities and incomplete
row counts, and uses `GetBySystemId` with explicit run/check validation.
All identities are checked before any group impact write because AL TryFunction
does not automatically roll back writes. A missing identity is accepted only when that run/check has exactly one BC row.
Ambiguous old-backend responses fail synchronization instead of silently corrupting
individual group impacts. Backend must be upgraded before the BC candidate.

## 4. DEF-003: duplicate markers

Email, VAT and name/postcode/city duplicate checks queried title suffixes that
InsertFinding never persisted. All six insertion paths now persist a SHA256
Group Key and query the run/check/group index. Name components use a JSON tuple,
not truncated delimiter concatenation. The pre-existing temporary duplicate
buffer is a work list and cannot provide persistent run-level finding identity.

## 5. DEF-004: metric semantics

German: **Prüftreffer**. English: **Check occurrences**.
Definition: sum of finding counts; a business record may contribute to multiple
checks. No unique-record metric is invented. `affected_records` remains a
compatible technical API name with explicit occurrence semantics.

## 6. Old data flow

BC check -> one or more BC rows -> payload without row identity -> impact over
all payload rows -> last row per code -> one stored row per code -> dashboard
sum of stored counts -> response applied to first BC row per code.

## 7. New data flow

BC check -> persisted group marker and existing SystemId -> payload `finding_id`
-> impact over all rows -> unique run/finding upsert -> all stored counts summed
-> response with identity -> exact BC row update. No impact/score formula changed.

## 8. Finding identity

BC SystemId is generated on record creation, never on an API attempt. The same
persisted finding therefore retains its UUID on retry. Local Group Key hashes
run SystemId, check code and canonical marker; raw emails/VAT/names are not sent
as new keys. Hashes are pseudonymous, not a claim of cryptographic anonymization.
Backend accepts optional UUID `finding_id`; database keys are scoped to the
already authenticated scan. Different runs may use the same UUID safely.

## 9. Idempotency and update semantics

The existing endpoint accepts a complete scan snapshot, not incremental deltas.
Existing rows with the same identity update in place (including database row ID).
Rows absent from a replacement snapshot of that SAME run are removed, preserving
the previous endpoint's snapshot semantics. Other scan history is untouched.
The scan row is locked for existing-run updates. Changing the check associated
with an existing identity returns 409; duplicate identities return 422.

## 10. Backend schema

`ScanIssueRecord.finding_id`: non-null String(128).
Unique index changes from `uq_scan_issues_scan_code` to
`uq_scan_issues_scan_finding (scan_id, finding_id)`. Check code remains a check
identifier, not a group identity. Existing quick-scan writers receive the
compatible singleton default `legacy:<code>`.

## 11. Migration

Alembic `0029_finding_identity` follows `0028_exception_count`. Upgrade adds the
column, backfills `legacy:<code>`, makes it non-null, and changes uniqueness.
No existing finding rows are deleted or inferred into new groups. Downgrade
first rejects any run/check with multiple groups BEFORE schema mutation. It
otherwise restores the old constraint and drops the identity column. A subsequent
upgrade restores deterministic legacy identities, not prior explicit UUIDs.
SQLite and real PostgreSQL upgrade/downgrade/upgrade tests retain original row
IDs and values. Alembic revision tracking governs repeated execution.

Coordinate migration and backend application rollout: the new non-null identity
has an application-side default, not a database default for old server binaries.
Older API payloads remain supported by the new backend; this does not promise
mixed old/new backend writers against the migrated schema. Complete backend
migration/application rollout before installing the new BC client.

## 12. BC sync and versioning

Product becomes **1.0.2.22** because table 53129 gains field 13 `Group Key`
(Text[64]) and a supporting index. Existing SystemId provides public identity;
no second GUID field is introduced. Historical blank group keys are preserved;
new scans populate them. Runner 53128 handles six duplicate paths and identity
serialization/response parsing. Table 53129 provides the validated domain update
and hash procedure used by temporary-record AL tests.

Other changed objects are display captions: tables DH Deep Scan Run / DH Scan
Header and pages DH Dashboard Issues / Issues List / Deep Scan Findings /
Findings List / Deep Scan Monitor. Existing IDs are retained. Separate QA objects:
codeunit 53460 (three temporary-record tests), page 53461 (read-only export),
permission set 53462 (no SUPER). DE/EN XLIFF accompanies new visible strings.

## 13. Dashboard

Queries already sum stored issue rows; lossless storage makes those sums complete.
Premium finding and action rows expose finding_id. JavaScript uses identity for row/action matching;
check code is displayed separately. Ambiguous duplicate titles are not treated as
identity. Free aggregate output still excludes protected finding details.

## 14. Reports

Report aggregation continues summing all issue rows. HTML/PDF and report labels
now call this value Prüftreffer / Check occurrences; technical schema compatibility
is retained. Existing report layout and commercial calculations are unchanged.
The changed metric is localized in DE/EN; the existing executive HTML template's other German editorial copy is not redesigned
into a new localization architecture in this sprint.

## 15. Free / Full access

No product entitlement, access-control or recommendation visibility rule changed.
Tests cover free aggregate sums and absence of IDs, codes and recommendation
previews, and full access preserving individual groups.

## 16. Security

Existing API-token and registration authorization remains before persistence.
IDs are matched only against issues of the authenticated scan. Foreign scan IDs,
company identities, malformed/duplicate IDs and attempts to change a finding's
check are rejected. QA export requires SaaS Sandbox, excludes Production and
requires exact company `BCS-FINDING-QA`; it reads selected run/finding rows only,
exports no credentials and cannot run scans, generate records or clean up data.

## 17. Legacy compatibility

Omitted finding_id remains accepted. One row per code uses legacy:<code>.
Multiple rows use a canonical payload SHA256 plus ordinal for identical rows,
preserving the complete multiset independently of ordering. Exact retries are
stable. Legacy clients cannot identify a mutable group reliably: changing its
content can replace its fallback identity under full-snapshot semantics. Historical
collapsed groups cannot be reconstructed. Old BC clients can still mis-map
multi-group responses because they ignore identity; deploy the new BC client for
lossless end-to-end behavior. New BC fails safely against ambiguous old responses.

## 18. Tests and matrix

Repository-relative evidence sources:
`backend/tests/test_ext_50_12c_3_identity.py`,
`backend/tests/test_ext_50_12c_3_migration.py`,
`backend/tests/test_ext_50_12c_sync_regression.py`,
`backend/tests/test_ext_50_12c_real_evidence.py`,
`bc-finding-tests/src/BCSFindingIdentityTests.Codeunit.al`.

| Requirements | Automated coverage |
|---|---|
| T01–T04 | 1/2/3/1000 groups, reordered retries, stable DB IDs, updates |
| T05–T07, T22–T23 | Separate runs, registrations/companies, cross-tenant attacks |
| T08–T10 | Individual and total impact/count assertions; AL 100/250 => 350 |
| T11–T14 | Free/full dashboard and report sums and disclosure boundaries |
| T15–T17 | Legacy retry multiset; existing-row migration cycle; guarded rollback |
| T18–T21 | AL exact response mapping, persisted hashes, different groups/runs |
| T24–T25 | Unchanged historical fixture, score/check and financial assertions |

Initial complete local regression: **518 PASS / 1 FAIL / 8 SKIP / 2 XFAIL**.
Only FAIL is unchanged billing fixed-date expiry:
`test_subscription_created_cannot_downgrade_active_monitoring_annual` (also fails
on audit baseline). SKIP includes seven real PostgreSQL cases and the new PG
migration case without local database; these are separate CI gates, not simulated
with SQLite. Two XFAIL remain the previously known intermediate counter assertions;
final 165-check count is unchanged. The resolved marker XFAIL is now a passing test.
Focused new backend tests: 14 PASS, 1 PG SKIP. CI outcomes are recorded below
when available; missing BC SaaS execution is never represented as PASS.

## 19. Performance

Python creates one existing-row dictionary, one pass over incoming rows, and one
pass over obsolete rows: O(n), with a unique database index. AL response matching
uses the SystemId index and a dictionary of seen IDs; group existence has a
run/check/hash index. There is no response-wide nested linear search. Existing
per-group business checks are not rewritten. The 1000-group test asserts full
preservation, retry/update behavior and sums without unstable timing thresholds.

## 20. Remaining risks

Real BC27 SaaS multi-group round trip remains required. Product 1.0.2.22 on this
stack does not contain PR39 recovery behavior, so DO NOT install over the existing
DEV environment: use a dedicated QA sandbox until integration is resolved.
Downgrade refuses lossy multi-group conversion. No historical group recovery is
promised. New fields require schema synchronization/upgrade. The known billing
baseline failure remains visible and unresolved. All installs below are manual
future QA actions; no deployment occurred during this sprint.

The three AL behavior tests use temporary finding records. CI install/upgrade
and those tests do not prove a real SaaS HTTP round trip or preservation of an
existing SaaS company's data during upgrade. These remain distinct from the
PostgreSQL existing-row migration checks and the manual multi-group evidence.

## 21. BC27 SaaS runtime test plan

German operator checklist: [Manual runtime retest](EXT_50_12C_3_MANUAL_RUNTIME_RETEST.md).

1. Provision a separate BC27 SaaS Sandbox with company **BCS-FINDING-QA**. Do not
   copy over or modify BCS-PERF-DEV or its completed scan. An operator prepares the
   candidate backend (migration 0029) and installs product 1.0.2.22 plus the
   separate Finding Identity Tests app in this isolated environment only.
2. Assign ordinary BCSentinel permissions plus **BCS FINDING QA** for the export.
   Register that company normally; never share tokens in evidence. Confirm normal
   connectivity and module activation using existing setup procedures.
3. Create five small customer QA records using valid posting setup: two customers
   with name `QA Group A` and the same valid, non-empty postcode and city, three with a
   different name `QA Group B` and their own identical valid, non-empty postcode/city tuple. Use unique customer numbers and unique
   valid emails so groups are distinguishable. Do not weaken validation rules.
   These records must exist only in the new QA company. Keep other records out of
   those tuples. The customer name/postcode/city duplicate check must produce two
   rows with the same check ID, distinct SystemIds and Group Keys, counts 2 and 3.
4. Run a normal entitled BCSentinel scan. Wait for Completed and Synchronized.
   Open **BCSentinel Finding QA Evidence** using Tell Me (Alt+Q), select that run,
   choose **Download group evidence**. The JSON export is read-only.
5. Verify two target rows, distinct stable finding_id/group_key values, individual
   returned impacts, count sum 5 for that check, and total run impact equals the
   sum of exported row impacts. Compare the authenticated backend response/stored
   snapshot and full-dashboard rows if licensed; free access must remain aggregate.
   Other checks may contribute additional occurrences; never expect whole-run sum 5.
6. API tests prove reordered retry idempotency. For SaaS retry evidence, use only
   an existing supported synchronization retry after an actual transient sync
   failure; do not edit scan state or invoke a debug endpoint. If no retry action
   is available in that state, mark manual retry NOT EXECUTED and return the first
   round-trip export. Do not claim retry PASS from a new scan.
7. Provide the exported JSON and backend evidence without credentials. A second
   normal scan is separate history, not a retry. Review SaaS evidence before
   declaring DEF-001/002/003 runtime closure.

## 22. LARGE stop-gate

LARGE remains blocked until automated repair checks, real SaaS multi-group
round trip, generator recovery/cleanup and relevant permission/no-SUPER gates
all pass. Maximum status is READY_FOR_MANUAL_BC_RUNTIME_RETEST, never LARGE GO.

## Execution evidence (updated after CI)

### Final verified implementation — 18 September 2026

Tested implementation commit: `44c9a4b8b3b2e003926f579fbde3c5098eb66c81`.
The following closing documentation commit changes only this report and the
German manual checklist; product, migration, test and workflow sources are
unchanged from the tested commit. Later documentation-triggered CI runs must not
be confused with these completed, source-identical implementation checks.

| Gate | PASS | FAIL | SKIP | XFAIL |
|---|---:|---:|---:|---:|
| Complete backend suite | 518 | 1 known baseline | 8 | 2 |
| SQLite + PostgreSQL migration cycles | 2 | 0 | 0 | 0 |
| Real PostgreSQL identity/API/concurrency | 23 | 0 | 0 | 0 |
| BC27 fresh install + AL behavior tests | 3 | 0 | 0 | 0 |
| BC27 pilot 1.0.2.21 -> 1.0.2.22 + AL behavior tests | 3 | 0 | 0 | 0 |

[BC CI 35313449737](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35313449737)
completed SUCCESS in both matrix jobs. Each `qa-al-tests.xml` has exactly three
executed cases and no failure/error/skipped elements. Both deployment result files
confirm QA 1.0.0.0 installed. The upgrade transcript explicitly records installing
BCSentinel 1.0.2.21, then synchronizing and upgrading to 1.0.2.22. The corrected
temporary-record identity and uppercase severity assertions now pass, including
the original exact per-group impacts, reordered retry and total of 350.

[Backend CI 35313449743](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35313449743)
completed with the unchanged billing fixed-date failure deliberately visible.
The migration, PostgreSQL and real Chromium dashboard steps passed. XML files
are `repair-full.xml`, `repair-migration.xml`, and `repair-postgres.xml` in that
run's artifact. Eight skips in the default suite are not called passes; the
database-specific cases run in the separate real PostgreSQL gates.

Downloaded evidence is under `.build/ci-al-44c9a4b/` and
`.build/ci-backend-44c9a4b/`. AL CI artifacts expire after 14 days; these local copies
retain the delivered evidence. The two **fresh-job CI-tested packages** for the
isolated manual QA sandbox are in
`.build/ci-al-44c9a4b/bc-al-compile-output/`:

- `BCSentinel Analytics - Daniel Wauer_BCSentinel_1.0.2.22.app` — SHA256
  `8afe7bcbce8bc16bcbc11fb520e19918b82f5810cf84262f3ce18fd5c72ff847`
- `BCSentinel Analytics - Daniel Wauer_BCSentinel Finding Identity Tests_1.0.0.0.app` — SHA256
  `aaeb77f5c166a86ad9b5970b40a4e211dde5b57b44a8ee1f7d8fcb287685f23d`

These supersede the earlier local compile-only candidates for manual delivery;
all earlier artifacts remain untouched. They are not installed in any real BC
environment by this work. DEF-001/002/003 have automated repair evidence and still
require the real SaaS multi-group round trip. DEF-004 has DE/EN UI/report evidence.
The historical DEV JSON hash and its 95/224999/2202021.49/1541415.04/38/165 results
remain unchanged. Status: **READY_FOR_MANUAL_BC_RUNTIME_RETEST**. LARGE is blocked.

### Earlier runs and supporting local checks

Repair PR: https://github.com/danielwauer-maker/bcsentinel/pull/41 (draft).
First backend CI: https://github.com/danielwauer-maker/bcsentinel/actions/runs/35234706980
— full regression 518 PASS / 1 baseline FAIL / 8 SKIP / 2 XFAIL;
separate migration gate 2 PASS (SQLite + real PostgreSQL), real PostgreSQL API/
identity/concurrency gate 23 PASS / 0 FAIL / 0 SKIP. Overall CI deliberately stays
red because the known billing failure is not hidden.

Local AL compiler 17.0.34.45391 against BC27 symbols: product and QA PASS.
CodeCop/PTECop product: 270 warnings, exactly the same filename/code/message
multiset as audit f312eaf; zero new warnings. QA: zero warnings/errors, three
namespace informational notices. AppSourceCop: existing 3 AS0051 + 1 AS0084 errors,
1 AS0092 warning; not an AppSource PASS. Source uniqueness: 109 canonical product
objects PASS; GL01C seven contracts PASS; GL01F source contracts PASS.

Chromium 130 (Playwright 1140): synthetic large-number executive report two PDF
pages; both page boxes 794x1123 without horizontal/vertical overflow; visible
224999 occurrences and EUR 2202021.49 / 1541415.04, footers visually inspected.
This is a layout sample, not another runtime evidence file. The reproducible
`scripts/verify_ext_50_12c_3_dashboard.py` executes real JavaScript for separate
same-check rows, reordered action mapping, legacy row keys and DE/EN units.
Local UI regression after supplementary metric labels: 41 PASS.

BC CI fresh/upgrade: https://github.com/danielwauer-maker/bcsentinel/actions/runs/35234706976
Fresh first attempt blocked at PowerShell Gallery WAF download; no AL tests ran
in that job. The first run was superseded by later repair commits. These infrastructure outcomes
are separate from local compile evidence. Final-head run results are available in
[BC CI](https://github.com/danielwauer-maker/bcsentinel/actions/workflows/ext-50-12c-3-al.yml)
and [backend CI](https://github.com/danielwauer-maker/bcsentinel/actions/workflows/ext-50-12c-3-backend.yml).
An unfinished or failed fresh/upgrade runtime gate is NOT a runtime PASS. The
completion response records exact run IDs and observed outcomes.

Local evidence stays under `.build/`; CI uploads XML/logs/packages. No merge,
production deployment or real BC data mutation has been performed.

### Changed AL objects

- codeunit 53128 `DH Deep Scan Runner` — `bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al`
- page 53135 `DH Dashboard Issues` — `bc-extension/app/src/pages/DHDashboardIssues.Page.al`
- page 53161 `DH Dashboard Issues List` — `bc-extension/app/src/pages/DHDashboardIssuesList.Page.al`
- page 53131 `DH Deep Scan Findings` — `bc-extension/app/src/pages/DHDeepScanFindings.Page.al`
- page 53160 `DH Deep Scan Findings List` — `bc-extension/app/src/pages/DHDeepScanFindingsList.Page.al`
- page 53158 `DH Deep Scan Monitor` — `bc-extension/app/src/pages/DHDeepScanMonitor.Page.al`
- table 53129 `DH Deep Scan Finding` — `bc-extension/app/src/tables/DHDeepScanFinding.Table.al`
- table 53128 `DH Deep Scan Run` — `bc-extension/app/src/tables/DHDeepScanRun.Table.al`
- table 53120 `DH Scan Header` — `bc-extension/app/src/tables/DHScanHeader.Table.al`
- permissionset 53462 `BCS FINDING QA` — `bc-finding-tests/src/BCSFINDINGQA.PermissionSet.al`
- codeunit 53460 `BCS Finding Identity Tests` — `bc-finding-tests/src/BCSFindingIdentityTests.Codeunit.al`
- page 53461 `BCS Finding QA Export` — `bc-finding-tests/src/BCSFindingQAExport.Page.al`

### Local installable candidates

These packages are for the isolated QA sandbox only; CI/runtime gates apply.

- `.build/bc-extension/ReleaseFinal/BCSentinel.1.0.2.22.validated.app` — SHA256 `467d1a2b45f4be636be62048430d0edf7f31dc7f1891f697e66e31ebc94fda30`

- `.build/bc-extension/FindingTestsQA/BCSentinel.Finding.QA.normalized-severity.app` — SHA256 `de78858f35941669795126c746f46d57dcc67f782756c01717cd5ef917c7db09`


### Final-product backend run and CI infrastructure correction

At product commit `4cb591caf55c95c6418ca3db3911e5a1117c19bf`, backend run
https://github.com/danielwauer-maker/bcsentinel/actions/runs/35236375730 repeats
518 PASS / 1 unchanged billing FAIL / 8 SKIP / 2 XFAIL; separate migrations 2 PASS,
PostgreSQL identity/concurrency 23 PASS; Chromium behavior PASS. Local complete
regression agrees. English report metric assertions now check the English caption,
while DE/EN identity tests require each respective localized caption.

BC run 35236375727 found the hosted upgrade runner's Docker service unavailable
before compilation. The dedicated repair workflow now explicitly starts the
existing Docker service on the disposable hosted runner and requires a Windows
engine before running the unchanged install/upgrade/test gates. This does not
operate on local Docker or any real BC environment. Final workflow results remain
a prerequisite; neither this infrastructure correction nor local compilation is
an AL runtime pass.


### Executed AL test finding and fixture repair

The fresh job of run 35236375727 completed product/QA installation and executed
all three AL tests: two PASS, one FAIL in the first group-impact assertion.
The temporary-record fixture reused the SystemId while calling Init/Insert.
It now explicitly assigns CreateGuid only when creating each temporary record,
uses Insert(false, true), and asserts non-null/distinct IDs before mapping.
All original impact, retry, count and sum assertions remain. Production persisted
record creation and per-sync identity are unchanged. The corrected QA package
compiles with zero warnings/errors; a subsequent real AL execution is required
to close this reproduced fixture failure.


### Fresh and upgrade execution at 973a455

BC run https://github.com/danielwauer-maker/bcsentinel/actions/runs/35265597254
compiled and installed both apps in fresh and upgrade jobs, including the pilot
1.0.2.21 -> 1.0.2.22 upgrade. Each job executed three AL tests: two PASS, one FAIL.
The identity fixture correction advanced the first test beyond its impact
assertion to the severity assertion (procedure line 18). AL Code fields normalize
values to uppercase; the test incorrectly expected lowercase strings. The fixture
now requires exact MEDIUM/HIGH and additionally their severity sort values 2/1.
No product behavior or impact assertion was changed. Corrected test compilation
has zero errors/warnings. A passing runtime repetition is still required.


## Real BC27 SaaS closure evidence – 22.09.2026

The previously outstanding manual SaaS multi-group gate is now **PASS**.

The isolated candidate was exercised from BC27 SaaS company `BCS-FINDING-QA` with product 1.0.2.22 and Finding Identity QA 1.0.0.1. Registration completed through the guarded QA-only temporary invite path; the invite was immediately cleared afterwards. The candidate intentionally had no SMTP configuration, so the post-registration dashboard invitation reported `SMTP not configured`; tenant registration itself completed successfully.

Post-merge PR #41 CI run #17 is green for backend regression, BC27 fresh and BC27 upgrade. The first fresh attempt was cancelled after a hosted BC container hang at `Mount-NAVTenant`; the targeted rerun succeeded without a product-code change, so that event is recorded as CI infrastructure noise rather than a reproduced product defect.

Real scan `RUN_20260922_000001_E6F8A317D080420FBDAFB03FB4A79` completed and synchronized with score 52, 199 checks, 89 persisted finding rows, 5,733 occurrences and EUR 50,289.68 total impact. Exported row impact reconciles exactly to the run impact.

Most importantly, `CUSTOMERS_DUPLICATE_NAME_POST_CITY` persisted two independent rows for the same check:

- finding `a2608ae6-0fb6-f111-aaa8-7ced8d032edd`, group `76EA...91C7`: count 2, EUR 100.00
- finding `a3608ae6-0fb6-f111-aaa8-7ced8d032edd`, group `755F...0EC1`: count 3, EUR 150.00

The two distinct `finding_id` values and two distinct persisted `group_key` values survived the real BC → HTTPS → backend/PostgreSQL → BC synchronization round trip. Target-check total is 5 occurrences / EUR 250.00.

Therefore DEF-001, DEF-002 and DEF-003 are runtime-verified and closed. DEF-004 remains closed by the automated DE/EN UI/report evidence. EXT-50-12C.3 is **RUNTIME_VERIFIED / READY_TO_CLOSE**. A synthetic manual retry was not created; reorder/retry behavior remains covered by automated tests.

Detailed operator evidence is recorded in `docs/EXT_50_12C_3_MANUAL_RUNTIME_RETEST.md`. LARGE remains blocked pending integration/closure of copied-company recovery, performance-generator cleanup/recovery, and no-SUPER permission gates.
