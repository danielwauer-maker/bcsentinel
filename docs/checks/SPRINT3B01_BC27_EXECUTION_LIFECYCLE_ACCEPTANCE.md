# Sprint 3B.01 — BC27 Execution Lifecycle Acceptance Checklist

**State:** PREPARED / NOT EXECUTED / NO-GO

This is an executable acceptance procedure for the execution-lifecycle scope. It complements, but does not replace, `docs/SPRINT3A2_BC27_ACCEPTANCE_RUNBOOK.md`. Run it only in an explicitly authorized disposable BC27 sandbox and dedicated synthetic test company.

## Preconditions

Record before any installation or scan:

- Feature commit, GitHub Actions URLs and all-green workflow conclusion for the exact commit.
- Extension `.app` version, SHA-256, application/platform/runtime version, and install/upgrade screenshots.
- DEV backend commit, image digest, migration head, registered tenant/company/environment binding, and a read-only health check.
- Test company, authorized test tenant, scan allowance, non-SUPER scan user and recovery SUPER administrator.
- Export/backup and rollback steps for the existing sandbox application and synthetic data.

Stop with **FAIL** if the package version/hash differs, an upgrade demands ForceSync/recreate, schema data would be removed, the backend is not the recorded revision, or the test user has SUPER.

## Scenario matrix

| ID | Procedure | Required evidence | PASS criterion |
| --- | --- | --- | --- |
| LIF-01 | In-place upgrade the exact package; preserve existing data. | Artifact hash, Extension Management state, table/upgrade outcome, rollback record. | Upgrade succeeds without data loss, ForceSync or recreation. |
| LIF-02 | Run a complete 199-check scan as `BCSENTINEL SCAN` without SUPER. | User roles, scan/run ID, sanitized status/evidence rows. | All enabled checks have terminal `PASS` or `FINDINGS`; scan finalizes only after backend result persistence. |
| LIF-03 | Create authorized synthetic data that produces at least one aggregate finding and one duplicate-group finding. | Sanitized source setup, finding count, local check evidence and backend payload. | Matching checks are `FINDINGS`; finding counts agree with submitted finding rows. |
| LIF-04 | Run a clean synthetic scenario. | Run ID, no finding rows, local/backend check evidence. | Every enabled check is `PASS`; no missing evidence is inferred as PASS. |
| LIF-05 | Disable a declared check in the accepted start expectation and scan. | Frozen expectation, local check execution row, backend evidence. | Only the disabled check is `SKIPPED`; it is not marked `STARTED`. |
| LIF-06 | Cause a controlled exception **before** an aggregate traversal in an approved test-only manner. | Error timestamp, run status, check-evidence rows, failure payload. | Scan is `FAILED`; no successful terminal state is fabricated. Checks provably never reached are `NOT_EXECUTED`; indeterminate checks remain unobserved. |
| LIF-07 | Cause a controlled exception **during** an aggregate traversal in an approved test-only manner. | Error timestamp, affected group evidence, failure payload and backend row. | Persisted `STARTED` aggregate checks become `FAILED`; none become `PASS` or `FINDINGS` due to absence of findings. |
| LIF-08 | Retry failure-evidence delivery without rerunning the failed scan. | Original lease token/worker (redacted), canonical payload hash, retry response. | Same evidence is idempotently accepted; altered, omitted, foreign, or stale-lease evidence is rejected. |
| LIF-09 | Attempt a completed sync with one enabled observation omitted or contradictory. | Sanitized rejected request/response and unchanged persistence state. | Backend rejects finalization; no completed scan and no invented evidence are stored. |
| LIF-10 | Review historical completed scan and retry behavior. | Historical run ID and persistence query/result. | No execution evidence is backfilled or retrofitted. |

## Evidence rules

- Use opaque run IDs, hashes and masked SystemIds only. Never commit tokens, customer names, VAT values, headers, or raw payloads.
- Capture local `DH Check Execution` rows and backend `scan_execution_evidence` only from the authorized test environment.
- For each scenario record UTC timestamps, exact code SHA, artifact SHA, user role, expected result, actual result, and reviewer.
- Mark a scenario `BLOCKED` rather than `PASS` when a prerequisite or controlled fault mechanism is unavailable.

## Decision

Sprint 3B.01 **GO-LIVE-ABNAHME remains OPEN** until LIF-01 through LIF-10 have individually passed with sanitized real evidence. A green static/backend CI result is necessary but never substitutes for these BC27 runtime scenarios.
