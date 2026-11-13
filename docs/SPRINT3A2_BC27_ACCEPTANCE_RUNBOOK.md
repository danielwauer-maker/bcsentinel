# BCSentinel Sprint 3A.2 — BC27 sandbox acceptance runbook

**State: PREPARED / NOT EXECUTED / NO-GO.** This document is a reproducible test procedure, **not** evidence of an actual BC27 runtime PASS. No live BC connection or deployment was made while preparing this runbook. Do not merge PR #162 or deploy to staging/main/PROD on the strength of static CI alone.

## 0. Frozen scope and safety

- GitHub: `danielwauer-maker/bcsentinel`, isolated PR **#162**. Record **exact tested branch commit SHA** in evidence before installation. Do not assume a later run of a mutable branch is identical.
- Manifest `bc-extension/app.json`: extension ID `8c7f0f9c-0c1a-4a4e-9c6f-111111111111`, version `1.0.2.58`, BC application/platform 27.0 and runtime 16.0. Confirm actual artifact matches; a successful compilation is not a successful upgrade.
- Backend: migration **0040_scan_record_identity_evidence** after 0039, `/scan/start` expectation v2, `/scan/sync` optional `bc-record-evidence-v1` for **CUSTOMERS_DUPLICATE_VAT** only. Confirm tested DEV backend is built from the exact same code. **No auto-deploy** in this runbook.
- Work **only in a disposable BC27 sandbox and a dedicated test Company** with synthetic or authorized non-production data. Never modify a production VAT registration number. Preserve current app backup/export, screenshots of existing configuration and a rollback plan **before** an upgrade.
- Keep the current SUPER admin untouched as recovery access. Execute separate tests with `BCSENTINEL SCAN` without SUPER, `VIEWER`, `SETUP`, `SCHEDULER` and `ADMIN` (one BCSentinel role at a time, documented baseline BC roles); never treat an admin SUPER session as non-SUPER evidence.
- Never paste Tenant API tokens, email addresses, customer names, VAT strings, PII, authorization headers or full raw scan payloads into GitHub, logs or acceptance JSON. Use opaque run IDs, Customer SystemIds only with authorized handling (prefer masked/salted references when publishing), hashes, UTC timestamps, artifact IDs and redacted logs. Customer SystemIds still deserve data protection.
- Confirm that the test tenant is entitled to **two** scans before starting; Free Entry by design permits one initial scan only. Use an explicitly licensed/sandbox allowance for the second scan, **not** an unapproved credit bypass. If this cannot be provided, mark BC27-04 BLOCKED, not PASS.

## 1. Preflight: tests, artifact and backend

1. Confirm both GitHub workflows green **on the same exact HEAD SHA**:
   - `BC Extension AL Build (Sandbox Test)` (.github/workflows/bc-extension-build-test.yml)
   - `BC Native Report Access Integration Tests` (.github/workflows/report-native-access-qa.yml), including full suite, SQLite + PostgreSQL where configured.
2. In the AL-build run download artifact `BCSentinel-BC27-Sandbox-Extension-<run_number>` containing `BCSentinel_1.0.2.58.app`, `SHA256SUMS`, and `build.log`. Compare the hash of the downloaded app to `SHA256SUMS`; record it in acceptance JSON. Artifact retention is **14 days**; do not rely on older artifacts.
3. Confirm that this actual `.app` was compiled from the frozen SHA, has extension ID and version above, and check the runtime warnings. Do **not** assume the artifact is code-signed, or that an AL compiler's metadata inspection proves installation compatibility.
4. Verify DEV backend exact commit, database migration head `0040_scan_record_identity_evidence`, schema/table presence, and valid HTTPS. Use a **read-only** database query or a controlled local verification command. Do not run Alembic against PROD.
5. Confirm no existing failed migration, unresolved upgrade error or permission gap. Earlier BC upgrades rejected removed fields/tables: any such BC27 result is an immediate **FAIL**, not grounds to force-reinstall with data loss.
6. Record installation roles, sandbox BC version, locale and package SHA in `quality/release/sprint3a2-bc27-acceptance-template.json` (copy to a new run-specific, sanitized evidence document). Do not overwrite the template.

## 2. Synthetic test data and expected membership

Create or choose two **new, clearly marked synthetic** Customer records in the dedicated Company (e.g., TEST-CUST-A and TEST-CUST-B). In the sandbox only, assign the **same valid test VAT string** to both; if BC validation rejects the chosen test VAT, choose a syntactically valid test value without disabling standard BC validation. Use two different non-sensitive names and ensure neither customer is excluded from `CUSTOMERS_DUPLICATE_VAT`. Record each source `Customer.SystemId` securely (the *business* record GUID, not BCSentinel Finding.SystemId, Entry No. or run-scoped Group Key).

Avoid existing customers with the same VAT string, other exclusions and concurrent background changes. If there are more than two members in the group, do not force an expected count of two; record the actual count and document the environment contamination.

**Scan A** expected for this group: check terminal `FINDINGS`, one relevant group finding with `affected_count=2` (assuming no other groups), two distinct source Customer SystemIds, `source_record_evidence.schema_version=bc-record-evidence-v1`, check code `CUSTOMERS_DUPLICATE_VAT`, `table_id=18`, `completed=true`, `affected_records_count=2`. Check `observed_at_utc` and confirmed tenant/company/scan binding. There may be other catalog findings; do not claim their record identities.

**Between scans:** change only TEST-CUST-B to a *different*, valid test VAT value, or clear it if permitted by the synthetic scenario. Reopen both records to verify the edit committed. Preserve both original Customer SystemIds; a value edit should not recreate them.

**Scan B** expected: `CUSTOMERS_DUPLICATE_VAT` terminal `PASS`, no matching grouped finding and `affected_records_count=0`, `records=[]` — **only if there are no other VAT duplicate groups in the Company**. If there are other groups, the check legitimately remains `FINDINGS`; inspect group members instead of demanding zero. The same registered tenant/company/environment and unchanged methodology/catalog/exception scope are required for any later pairwise assertion.

## 3. Execute and verify each scenario (BC27-01..08)

| ID | Action | Evidence / acceptance |
|---|---|---|
| BC27-01 | Install or upgrade the exact sandbox artifact using Extension Management, preserving existing data. | Extension ID, version, installed status; new table 53198 accessible to appropriate role; no schema removal, upgrade failure or destructive reinstall. |
| BC27-02 | With a non-SUPER SCAN user, start an authorized scan; separately check VIEWER cannot write evidence. | Effective permissions / BC user role screenshots, no unauthorized writes, no excess grants. |
| BC27-03 | Create synthetic duplicate Customers, start/finish Scan A, capture Run ID and timestamps. | Completed + synchronized scan; terminal check `FINDINGS`; member count matches group findings; two source SystemIds available to internal verification; no private source fields in transport. |
| BC27-04 | Change one test VAT string, then start authorized Scan B. | Both same original Customer SystemIds still exist, check status as specified in §2, separate completed Run ID, unchanged relevant scope. |
| BC27-05 | Read back the canonical DB evidence for A and B via the internal verifier or a **read-only** query; check SHA-256 and lifecycle. | Two immutable rows (check `CUSTOMERS_DUPLICATE_VAT`) with matching tenant/company/run/check, valid hashes, source record sets, observation + completion times. Do not write to DB to manufacture PASS. |
| BC27-06 | Replay identical original sync (or test in controlled isolated backend test); try altered members, missing evidence and stale lease. | Exact retry idempotent; conflicting retry rejected with no extra DB rows. **Never** send forged tenant headers to a shared real customer environment. |
| BC27-07 | Reproduce early abort, wrong-company setup and incomplete member evidence safely in isolated tests. | Incomplete scan remains unverified; wrong company/tenant and missing member IDs fail closed; no false record comparison. |
| BC27-08 | Validate >2000-member cap with synthetic test harness rather than creating 2001 real customer records; check Validation/Monitoring guards. | Optional record envelope omitted above limit, aggregate scan remains possible, record transition/report gates still **not** opened. |

## 4. Evidence capture and security

Use `quality/release/sprint3a2-bc27-acceptance-template.json` as the structure. For every scenario capture `PASS`, `FAIL` or `BLOCKED`; include **redacted** links/paths to CI run, app package hash, BC screenshot, scan run ID, backend read-only verification result and the test case's expected-vs-actual notes. Evidence paths must be real and resolvable; never invent report files, screenshots or workflow statuses.

Capture on test failure: redacted HTTP status and request/correlation ID; BC App version, AL runtime error text, check code, scan ID, times; exact repeatable reproduction. Preserve prior successful artifacts separately; a later successful retry does not erase a failure.

Do not log raw authorization headers, API tokens, VAT values, customer emails or complete body payloads. Use anonymized Customer GUID references only as required to demonstrate membership continuity. Store detailed restricted evidence outside publicly readable GitHub.

## 5. Hard GO/NO-GO gate

Accept Sprint 3A.2 for **DEV release consideration only** if:
- Both CI workflows PASS at exactly the candidate commit; no pending failed checks;
- Upgrade and role tests are PASS on actual BC27 with no SUPER workaround or destructive schema changes;
- Two **real authorized** completed scans A/B yield verified source-record evidence as in §2 and matching backend readback;
- Retries, wrong-scope, partial and changed-member cases fail closed;
- No unrelated scoring/impact/Validation/Monitoring comparison or customer report unlock has been introduced;
- Evidence JSON is complete, references real artifacts, reviewer approves and the product Master State is updated if technical truth changes.

Any failed item is **NO-GO**. A missing external prerequisite is **BLOCKED / NO-GO**, not PASS. Successful DEV acceptance does **not** authorize PROD; PROD requires separate approval and release gates. No merging or deployments are performed by this document.

## 6. Commands / quick references

- `python -m pytest -q backend/tests/test_source_record_evidence_contract.py backend/tests/test_source_record_sync_integration.py backend/tests/test_record_evidence_storage_migration.py` (run in properly configured project test environment; backend tests normally use `cd backend && python -m pytest -q tests/...`).
- `python scripts/check_sprint3a2_bc27_acceptance.py --evidence <sanitized-run-evidence.json>` (offline, fail-closed evidence validator; no network or credentials).
- Existing no-SUPER plan: `docs/EXT_50_04_RUNTIME_NO_SUPER_CHECKLIST.md`. That historic 1.0.2.25 PASS is **not** a 1.0.2.58 runtime PASS.
- Existing broader customer suite: `docs/BC_EXTENSION_CUSTOMER_ACCEPTANCE_TEST.md`, which contains historical statuses and must not be treated as a current release assertion.

**Pending owner action for real runtime:** provide/confirm isolated BC27 sandbox, the exact verified artifact, DEV backend revision, an authorized second scan and non-SUPER test user. Everything else in this runbook is preparation, not execution evidence.
