# Sprint 3B.01 — Check Coverage & Execution Lifecycle Report

## Status

- **TECHNISCH FERTIG:** BLOCKED — implementation and focused regression scope pass, but final-SHA GitHub CI and AL compilation evidence are unavailable.
- **GO-LIVE-ABNAHME:** OPEN
- **Base commit:** `a8b870eb41d29913cc0837a558c30637be8c57f2` (`integration/sprint3a2-consolidated-20261110`, also the verified PR #162 ref retrieved during preflight)
- **Final feature commit / CI:** recorded in the Draft PR after push; do not treat this document as GitHub CI evidence.

## Executive summary

The current AL catalog contains exactly 199 distinct checks. The generated [CSV matrix](sprint3b01-check-coverage.csv) inventories all of them directly from the catalog and runner: 193 aggregate-count checks and six duplicate-group checks. This change persists an enabled aggregate group's `STARTED` observations before its traversal begins. A group exception can therefore turn those observations into `FAILED`; it cannot silently convert them to `PASS` or `FINDINGS`.

The existing backend contract remains fail-closed: completed scans with a sealed start expectation require a `PASS` or `FINDINGS` observation for every enabled check, observed findings must match submitted finding rows, and execution evidence is canonicalized, lease-bound and retry-immutable. Failed scans use the distinct failure-evidence contract, preserve `FAILED` / `NOT_EXECUTED` / `SKIPPED` where proven, and cannot be completed as a successful scan.

## Lifecycle rules verified in source and backend tests

| Situation | Outcome |
| --- | --- |
| Enabled check completes cleanly | `PASS` with zero findings |
| Enabled check completes with findings | `FINDINGS` with a matching positive finding count |
| Aggregate or duplicate-group exception after start | `FAILED` on persisted `STARTED` observations; scan is failed |
| Disabled check | `SKIPPED` only at its output route |
| Check provably not reached | `NOT_EXECUTED` only in failed-scan evidence |
| Unobserved check in an indeterminate group | Left unobserved; never fabricated as `PASS`, `FINDINGS`, or `NOT_EXECUTED` |
| Incomplete successful evidence | Sync/finalization rejects it |
| Historical completed scan | Cannot be retrofitted with execution evidence |
| Retry | Must retain the original lease, worker, and canonical evidence payload |

## Tests

Focused execution-lifecycle and coverage tests passed locally: **50 passed, 5 skipped**. The skips are PostgreSQL-concurrency tests and were not disabled or weakened. The complete backend suite also passed locally: **961 passed, 22 skipped, 2 xfailed** in 154.88 seconds. This is local evidence only; verify the exact final commit in GitHub Actions before integration.

The NuGet diagnosis was repeated: the public Microsoft AL compiler URL for the pinned `16.2.28.57946` package returns HTTP 200, but the CI's pinned BC27 Azure DevOps symbol feed (`dynamicssmb2.pkgs.visualstudio.com`) returns HTTP 403 for both Platform and Application symbols. No cached compiler or symbol packages exist in this checkout. No compiler result is claimed; the existing `BC Extension AL Build (Sandbox Test)` GitHub Actions workflow remains the required compiler gate.

Relevant test files include:

- `backend/tests/test_sprint3b01_check_coverage.py`
- `backend/tests/test_scan_runtime_catalog_routing.py`
- `backend/tests/test_partial_check_execution_al_contract.py`
- `backend/tests/test_scan_expectation_start.py`
- `backend/tests/test_partial_check_execution_sync.py`

## Runtime, DEV, and CI limits

No authenticated DEV runtime, Docker image digest, migration database, or BC sandbox connection was available from this environment. No values have been invented. GitHub REST/GraphQL access was denied (HTTP 403), so PR state and Actions runs cannot be verified here after push.

The feature branch was pushed successfully, but GitHub's API permission denial also prevented automated Draft PR creation. The feature branch can be opened for a Draft PR from the repository's branch comparison page once credentials with pull-request write access are available.

The exact comparison page was verified in a browser and is available at [GitHub comparison](https://github.com/danielwauer-maker/bcsentinel/compare/integration%2Fsprint3a2-consolidated-20261110...feature%2Fsprint3b01-check-coverage?expand=1). The current browser session is signed out; the available `GH_TOKEN` is invalid and no alternate `gh` login is configured. Creating a Draft PR and observing pull-request CI therefore remain externally blocked.

The BC27 runbook remains `PREPARED / NOT EXECUTED / NO-GO`. Required manual acceptance remains: exact extension artifact/hash, installed version 1.0.2.58, real in-place upgrade, non-SUPER roles, completed clean scan, findings scan, interrupted aggregate group, retry, and backend persistence verification at the same SHA. The executable scenario checklist is [SPRINT3B01_BC27_EXECUTION_LIFECYCLE_ACCEPTANCE.md](SPRINT3B01_BC27_EXECUTION_LIFECYCLE_ACCEPTANCE.md).

## Sprint 3B.02 interface

This change does not modify tenant/company/scan/lease provenance schema, source record identity, or record-comparison logic. It relies on the existing expectation and execution-evidence envelope; Sprint 3B.02 can consume the status observations without treating them as per-record identity evidence.

## Recommendation for tracker item 2.01

Keep **technisch fertig: BLOCKED** until this feature branch's exact final SHA is green in GitHub Actions, including the AL build. Keep **Go-Live-Abnahme: OPEN** until the BC27 runtime scenarios above have real, sanitized evidence. The next required step is a controlled review and CI verification, followed by the BC27 sandbox acceptance runbook—not deployment or merge.
