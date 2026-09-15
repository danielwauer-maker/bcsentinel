# EXT-50-12A — BCSentinel Performance Test Data Generator

Status: **AWAITING_MANUAL_BC_RUNTIME_EVIDENCE**. No merge, production deployment,
or XL/STRESS execution is authorized by this implementation.

## 1. Repository audit and decision

Audit on 2026-09-15: the checkout started on clean local `staging`, behind the
fetched `origin/staging`. The sprint branch starts at the fetched integration
branch; existing local staging commits were not reset. GitHub identified one
open PR, **#37**, `sprint/ext-50-04-permission-role-matrix` -> `staging`. Neither
that branch nor its permission design is changed here.

The current product manifest is **1.0.2.20**, application/platform **27.0.0.0**,
runtime **16.0**, range **53100–53202**. The older local manifest ended at 53201;
the integration branch already includes remediation objects at 53202. Object
IDs are unique per object type, not across all types. The existing manual
installation evidence records BC 28.3; that does not change the BC 27 build target.

Audited architecture:

- `bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al` runs the actual
  productive checks. `DHScanDispatcher`, `DHDeepScanMgt`, background runners and
  scheduler own scan execution; `DHApiClient` synchronizes aggregates with FastAPI.
- `DHDataProfilingMgt` counts Customer, Vendor, Item, customer/vendor/item ledgers,
  sales/purchase headers and lines, G/L, value and warehouse entries.
- `DH Deep Scan Run/Finding`, scan headers/issues, setup, exceptions, action logs,
  scan check selection and dashboard tables remain unchanged. This tool writes
  **no BCSentinel findings, scores, scan history, or backend data**.
- `DHInstall` initializes setup; `DHUpgrade` preserves data and invalidates access
  snapshots. Neither installs, invokes, or depends on the generator.
- Five product permission sets exist (VIEWER, SCAN, SETUP, ADMIN, SCHEDULER).
  None receives generator access. EXT-50-04 remains a separate release gate.
- No existing AL Test app or reusable BC seed/demo generator was present.
  Existing automation uses Python source/evidence contracts, PowerShell source
  uniqueness/GL contracts, and the central Windows AL/Cop workflow. Legacy quick
  scoring in `scoring_service.py` is not the scenario oracle.

**Architecture A: separate sandbox-only extension**, `bc-performance/app.json`,
app ID `1bf95437-93b6-4329-bc49-40585f1272a0`, version 1.0.0.0, schema 1,
reserved range **53400–53449**. No dependency on the customer extension is needed:
both operate on the same standard company tables. Separate packaging keeps the
tool out of normal customer installations and install/upgrade hooks. A customer
release must select the BCSentinel package, never the QA package from CI artifacts.

## 2. Profiles and counting

The single source of profile defaults is `BCP Policy.SetProfile`. Custom runs
configure each count separately; presets intentionally overwrite custom counts.

| Profile | Customer (18) | Vendor (23) | Item (27) | Business records | Supporting Item UOM (5404) | Ownership rows |
|---|---:|---:|---:|---:|---:|---:|
| DEV | 6,000 | 2,000 | 12,000 | 20,000 | 12,000 | 32,000 |
| LARGE | 150,000 | 50,000 | 300,000 | 500,000 | 300,000 | 800,000 |
| XL | 600,000 | 200,000 | 1,200,000 | 2,000,000 | 1,200,000 | 3,200,000 |
| STRESS | 1,500,000 | 500,000 | 3,000,000 | 5,000,000 | 3,000,000 | 8,000,000 |

One run metadata row is additional. Setup and three configuration source records
are existing supporting data and never count toward the generated profile.
Custom requires 1–5,000,000 per entity and at most 10,000,000 business records.
Batch size defaults to 1,000; allowed range 1–5,000. Seed range: 0–1,000,000.

This is deliberately a **master-data scan workload**: structurally valid synthetic
customers, vendors and a large product catalog stress existing scan loops,
duplicate checks and aggregation. It is not a claim that a typical tenant has
these entity ratios. No unposted/posted transaction counts are fabricated to
reach the target. Ledger aging, stock balances, posting, sales/purchase line,
warehouse and scheduler load coverage must be added through real posting flows
in a later workload. EXT-50-12 must benchmark those separately.

## 3. Configuration and deterministic data

Create a dedicated disposable **SaaS sandbox** company named `BCS-PERF-...`.
Use configured synthetic Customer, Vendor and Item source records. The dialog
copies only nonempty setup codes into immutable JSON snapshots on the run:

- Customer/Vendor: posting group, general/VAT business posting group, country,
  payment terms and payment method.
- Item: base UOM, inventory/general/VAT product posting groups and item category.

Names, addresses, VAT identifiers, dimensions, financial balances, media and
other fields are never copied from source records. Source records/setup are not
modified. The synthetic address is intentionally independent of the source
country; this is a scan fixture, not postal-validation evidence.

Numbers are `BCP` + six-digit run ID + `C`/`V`/`I` + seven-digit sequence, e.g.
`BCP000001I0000001` (17 characters, within Code[20]). No collision is overwritten;
an existing number makes the batch fail atomically. Run IDs over 999999 fail.
Email addresses use reserved `example.invalid`, never a real delivery domain.

For sequence `n`, scenario membership is
`((n mod 100) * 37 + (seed mod 100)) mod 100 < error_rate`.
This is an exact permutation of each full block of 100; configured rates are
**1, 5, 10, 20 %**. Item scenario type alternates every 100 records so that price
and cost problems each receive half the item error budget. Prices/costs also
vary by seed and sequence. Identity/run timestamps/SystemIds necessarily vary.
The same schema, configuration snapshots, seed, profile, BC version and installed
extensions reproduce business structure and scenario positions. Seeds separated
by 100 share scenario positions; the seed is not a cryptographic random source.
Changing reference setup or installed subscribers can change validation results.

## 4. Scenario mapping and expected observations

| Scenario | BC data | Actual Deep Scan check | Category | Error allocation | LARGE, seed 5001, 10% |
|---|---|---|---|---|---:|
| Missing customer email | Customer.`E-Mail` = blank | `CUSTOMERS_MISSING_EMAIL` | CUSTOMER | r% of customers | 15,000 records |
| Missing vendor phone | Vendor.`Phone No.` = blank | `VENDORS_MISSING_PHONE` | VENDOR | r% of vendors | 5,000 records |
| Missing item selling price | Item.`Unit Price` = 0 | `ITEMS_WITHOUT_UNIT_PRICE` | ITEM | r/2% of items | 15,000 records |
| Missing item cost | Item.`Unit Cost` = 0 | `ITEMS_WITHOUT_UNIT_COST` | ITEM | r/2% of items | 15,000 records |

All four are deterministic. `Expected Scenarios` should be **50,000** for the
first LARGE run. The ownership record stores each injected check ID. The product
uses `AddCountFinding` for these checks: expect aggregate finding rows and their
affected-record counts, **not 50,000 finding rows**. Enabled check selections,
exceptions, entitlements, pre-existing data and scan thresholds still apply.

Baseline noise is explicit: vendors have no generated bank accounts; new masters
have no transaction history/default dimensions; other checks may report those
conditions. Missing unit cost can also trigger related cost checks. Capture a
pre-generation scan, evaluate the four mapped check deltas, and retain ownership
counts as the oracle. The error rate controls these four injected scenarios,
not the total fraction of records flagged by all 199 checks. There is no claim
of an otherwise completely clean dataset.

Not implemented: negative inventory, overdue open entries, negative prices,
invalid email formats, deliberate duplicates, missing dimensions/posting setup.
Negative stock/aging would require proper journal/document posting and is not
safely reversible through deleting master records. Invalid email validation is
not bypassed. Posting setup is reused and validated rather than corrupted.

## 5. Import behavior, batches, recovery and metrics

Configuration relation fields use `FieldRef.Validate`; names/descriptions and
item vendor/base UOM use their standard Validate logic. Synthetic contact text,
explicit number, prices and the intentional blank/zero scenario fields use direct
assignment. The customer/vendor/item `Insert(false)` is a controlled master-data
import: it avoids number series consumption, automatic contacts, default dimension
propagation and implicit item unit group creation. Blank global dimensions are
intentional. No ledger tables are written. Unit-of-measure rows use Validate and
`Insert(true)`; item base UOM is validated after its supporting row exists.
Standard integration events/installed subscribers still execute according to BC
semantics; use the clean QA baseline and verify side effects during DEV first.
The import explicitly calls the standard `UpdateReferencedIds` methods and sets
master modification timestamps; API reference IDs are not left stale merely
because the OnInsert trigger is skipped. UOM ownership is captured after final
item validation so its timestamp reflects the final state of the batch.

Generation order: vendors -> customers -> items. Every item references a vendor
from its own run. `BCP Batch` locks and rereads the run, performs at most one
configured batch and writes counters and ownership in the same transaction.
`CommitBehavior::Error` rejects explicit commits inside the worker. The Boolean
`Codeunit.Run` boundary commits on success and rolls back the failed batch.
The coordinator persists the failure text and increments failed batches after
rollback. No TryFunction write transactions are used.

The core is GUI independent. `Execute(runId, true)` executes one bounded batch;
`Execute(runId, false)` continues until completion. The UI offers both. `Running`
may mean a paused checkpoint with no active session; resuming is safe because
workers serialize on the run lock and reread counters. A second caller cannot
recreate a committed sequence. Cancel serializes on that same lock and is observed
at the next boundary; it keeps tracked data. Cancelled is terminal for generation.
Resume Pending/Running/Failed; cleanup requires Completed/Cancelled/Failed/Cleaning.
Cleaned is terminal. Completed is only assigned at exact target equality.

Hard session termination may leave Running without a caught diagnostic; the last
committed batch timestamp/checkpoint remains authoritative. Resume that run.
Counts preserve historical generation totals after cleanup; Cleanup Count records
actual deletions separately. No resuming a cleaned run or silent reclassification.

Page metrics: run ID/profile/seed/rate, entity counters, target/progress, phase,
batch, start/end, wall duration, average business records/sec, injected scenarios,
failed batches, error text and cleanup count. Refresh in a second client while
generation runs; there is no claim of automatic UI refresh or a measured throughput.
Wall duration includes pauses and retries. A future Job Queue wrapper can call
the same bounded API; automatic queue installation is intentionally absent.
STRESS requires substantial database capacity: business + support + tracking
totals **16 million rows**, before indexes and normal BC data.

## 6. Sandbox and least-privilege design

Every mutation entry point/worker checks `Environment Information.IsSaaS`,
`IsSandbox`, `IsProduction` and the `BCS-PERF-` company name. Unknown environments,
on-prem containers and production fail closed. A company name alone never enables
production. Sources:
[Environment Information](https://learn.microsoft.com/en-us/dynamics365/business-central/application/system-application/codeunit/system.environment.environment-information),
[Codeunit.Run transaction semantics](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/methods-auto/codeunit/codeunit-run-method).

- `BCP GENERATE`: QA pages/worker execution; read setup/master data; **indirect**
  insert on owned masters/support/ownership and modify on run/item where needed.
- `BCP CLEANUP`: independent capability; indirect delete on the three masters,
  item UOM and ownership; indirect modify on run. No generation permission is
  included. Assign both only to a QA operator who needs both actions.
- Neither permission set gives direct write access to ownership or persistent
  run configuration. UI configuration uses a temporary record. Product roles,
  installer and customer manifest are unchanged. No SUPER dependency is present.
- Normal BC sign-in/system execution permissions are still needed. Cleanup's
  conservative reference inventory requires **read-only access to every inspected
  table** and standard delete-trigger dependencies. A missing permission refuses
  cleanup; it is never skipped. Capture denied objects during DEV and grant only
  the needed read/standard execution permissions in the QA operator role. This
  exact non-SUPER runtime matrix remains an acceptance gate, not a compile claim.

## 7. Ownership and safe cleanup

`BCP Owned Record` stores run ID, allowlisted table ID, SystemId, RecordId,
reserved number, original SystemModifiedAt, supporting flag and scenario.
Ownership and the business insert commit together. Cleanup never searches only
by a prefix to choose deletion targets and never calls DELETEALL on a business
table. Prefixes serve as an additional guard and as conservative dependency filters.

Preview reports the tracked **candidate count**, including supporting rows. It
is not a full dry run of BC delete triggers or a claim all candidates are deletable.
UI confirmation defaults to No and displays the count. Cleanup API is itself a
dedicated privileged capability; unattended callers must explicitly authorize it.

Deletion order: items with their owned UOM -> customers -> vendors. Each batch:

1. Locks/rereads the run and requires Cleaning.
2. Scans declared references plus conservative polymorphic number fields for the
   run/entity namespace. Foreign references refuse the phase before deleting it.
   Missing read permissions fail closed. This check is per batch, not per row.
3. Locks each tracked target and verifies table allowlist, run namespace, exact
   SystemId, exact RecordId and original modification timestamp. Missing, renamed,
   replaced or externally edited targets refuse the batch; there is no force flag.
4. Refuses record links/approval records. For items, every UOM row must be tracked
   by the same run and unchanged before the standard item cascade can delete it.
5. Calls standard `Delete(true)` and verifies supporting records disappeared,
   then removes ownership. The batch's deletes/counters commit atomically.

No existing setup, configuration-source record, unrelated customer or unrelated
prefix collision is deleted. Ordinary existing BC delete checks remain active.
Reference probes are deliberately conservative: a same-number polymorphic
reference may block cleanup even if semantically unrelated. Cleanup is more
expensive than generation and may require several attempts after genuine issues
are investigated. Do not manually remove ownership to suppress a refusal.

**Operational boundary:** no concurrent business entry/posting, extension install,
or editing of generated records during cleanup. Standard relation metadata and
known RecordId links do not describe arbitrary third-party subscriber side effects
or arbitrary GUID/text references. Such extensions require an expanded safety
audit and DEV cleanup test first. The tool is for an isolated disposable sandbox
company, not mixed customer operations. Never grant broad delete permissions as
a shortcut. Uninstall only after cleanup: uninstall/delete-extension-data can
remove ownership while leaving standard master rows; BC does not provide a safe
automatic master-data uninstall rollback. Retain the QA package and ownership.

## 8. Build, source tests and CI

Build workspaces must be created with
`bc-extension/scripts/New-BCBuildWorkspace.ps1 -Profile PerformanceQA`, under
`.build/bc-extension/PerformanceQA`. This copies only QA sources and BC 27 symbols,
never nests a second project inside the customer AL root. Existing APP/ZIP/PDF
artifacts are not removed. Use a new output APP filename for each local compile.

The existing `.github/workflows/bc-al-compile.yml` compiles customer and QA apps
with CodeCop/PTECop. The separate `ext-50-12a-test-data-generator.yml` runs source,
safety, evidence and existing extension regression contracts plus GL/source checks.
BC runtime tests are not enabled by the central compile workflow.

`BCP Self Tests` contains four real AL test methods: preset counts; exact rates
across 10,000 sequences and multiple seeds; namespace isolation/bounds; rejected
configuration values. They require the BC Test Tool to execute. Merely compiling
them is **not PASS** for AL behavior. Python tests are explicitly source contracts,
not an emulator of BC insertion, triggers, permissions, rollback or cleanup.

Local contracts: from `backend`, use only `.venv/Scripts/python.exe -m pytest
--noconftest ...` with the repository pytest.ini. No PostgreSQL migration, database
write or SQLite substitution is part of this sprint. Existing product AppSourceCop
baseline remains 3×AS0051, 1×AS0084, 1×AS0092; QA uses CodeCop/PTECop and is not an
AppSource customer release. No existing test is removed or weakened.

## 9. Manual acceptance, then first LARGE run

1. Prepare a disposable SaaS sandbox company `BCS-PERF-LARGE`. Install the QA APP
   alongside BCSentinel 1.0.2.20. Set the BCSentinel backend to the approved test
   endpoint, with valid scan access. Keep a before snapshot of normal records/setup.
2. Assign a non-SUPER QA operator the separate generate/cleanup permissions plus
   necessary BC read/system rights. Prepare three **synthetic** source masters with
   the configuration fields above. Record BC version and installed app inventory.
3. Open **INTERNAL QA - Performance runs**. First use Custom (e.g. 3/2/5), seed
   5001, 10%, batch 2: run one batch, resume, cancel a second run and preview/clean.
   Run the four AL tests. Test a deliberate number collision and a validation
   failure: no business/ownership/counter changes from the failed batch may remain.
4. In independent DEV fixtures, test concurrent resume, session interruption,
   cancellation at a batch boundary, changed/renamed/replaced/missing targets,
   added foreign UOM/comment/dimension/document/record-link references, a normal
   untracked master with the same prefix, and missing delete/read permissions.
   Cleanup must refuse unsafe targets and preserve normal rows. Verify the
   production/unknown-environment guard without generating any production data.
5. Create **LARGE, seed 5001, error rate 10%, batch 1000**, choose the configuration
   sources and confirm **Start / resume**. Record the Run ID. Refresh the list from
   another client and record responsiveness, elapsed time and failures.
6. Require Completed, **150,000 customers + 50,000 vendors + 300,000 items**, 300,000
   supporting UOM rows, 800,000 tracking rows and 50,000 injected scenarios.
   Record generation duration/records per second; retain exports/screenshots.
7. Run the normal BCSentinel scan. Compare the four mapped affected-record counts
   against baseline plus 15,000/5,000/15,000/15,000, respecting enabled checks and
   exceptions. Measure scan duration; review Findings, dashboard and reports.
8. Preview cleanup: **800,000 candidates** for an untouched full run. Confirm
   cleanup only after retaining benchmark evidence. Require Cleaned, zero ownership
   rows for that run and no remaining generated masters/UOM. Before/after evidence
   must show normal source masters/setup unchanged. Record any refusal verbatim.

Save genuine results in
`quality/release/ext-50-12a-test-data-generator-evidence.json`, including Run ID,
actual counts, timing and evidence paths. Do not replace PENDING with PASS using
source inspection or a compile log. Overall status stays
**AWAITING_MANUAL_BC_RUNTIME_EVIDENCE** until these gates pass.

## 10. Later XL/STRESS and EXT-50-12

Do not automatically start XL or STRESS after LARGE. Evaluate generation and scan
duration, database growth, memory/locking, BC responsiveness, timeout behavior,
finding counts, dashboard/report behavior and cleanup first. Only then approve XL;
STRESS comes last. This sprint supplies fixtures and generation metrics. It does
not certify 50-tenant/customer readiness, production performance, scheduler scale,
or a GO decision for release. Outstanding sandbox and permission gates block GO.
