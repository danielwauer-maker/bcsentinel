# BCSentinel release contract + PR CI economy (2026-11-13)

## Control planes / no implicit promotion
- The authoritative `main` controller `.github/workflows/deploy.yml` is **manual PROD-only**.
  After security PR #184: PROD promotion additionally requires:
  exact 40-character `main` HEAD SHA, matching repository variables
  `PROD_RELEASE_ENABLED=true` and `PROD_RELEASE_SHA=<reviewed SHA>`,
  operator input `PROMOTE_TO_PROD`, release regression and the
  `production` GitHub environment. Missing approval values must fail closed.
- The authoritative **DEV** controller is `main:.github/workflows/dev-release.yml`,
  manually dispatched with current `staging` HEAD and independent
  `DEV_STAGING_DEPLOY_ENABLED` and `DEV_STAGING_RELEASE_SHA` approval.
  Its backup and checkout safety conditions remain authoritative.
- The divergent historical `staging:.github/workflows/deploy.yml`
  had an unsafe `main` push-PROD branch. This branch reconciles it to the
  reviewed main PROD-only controller; no automatic deployment on branch push.
- The frontend's own manual DEV controller / main-to-PROD route is a
  separate release system. Frontend PR #14 must not be merged to `main`
  before explicit production-path approval.
- Do **not** promote `staging` wholesale into `main`. Their histories
  diverge and unrelated code must not be deployed to PROD accidentally.
- Changes to `main` release contracts require a deliberately scoped,
  verified PR targeting `main`, not rebasing the entire staging codebase.

## CI optimization implemented
- Original CI-OPT-01 already isolates cancellation to obsolete PR attempts
  for seven selected heavy workflows.
- This sprint adds the same **per-PR/per-workflow** cancellation to:
  `ext-50-12c-3-backend.yml`,
  `report-native-access-qa.yml`,
  `arch-02a-compatibility.yml`.
  New commits replace obsolete instances of those three workflows. A manual
  dispatch or a staging push has a unique ID group and is NEVER superseded.
- No existing PR trigger, full backend test, PostgreSQL job, Windows AL
  compiler matrix, required check name or release gate is removed.
  Existing terminal check counts therefore do not shrink; **superseded
  compute waste** is reduced when commits are pushed during an active PR.
- Batch commits before opening PRs to avoid unnecessary CI repeats.
  Avoid empty commits, manual reruns of succeeded workflows, and doc-only
  commits to wide AL PRs (GitHub paths are evaluated against the entire PR diff).

## Central change classification (Phase 1 continuation)

`.github/workflows/ci-change-classification.yml` is an always-present, lightweight **policy** check for PRs and merge-queue entries targeting `main` or `staging`.

- Its Git diff uses `--diff-filter=ACMRD`: additions, copies, modifications, renames and **deletions** are classified. Deleted workflow and security paths cannot become invisible.
- Unknown, empty or unreadable input becomes `all_critical=true`; it is never reported as harmless.
- It publishes a decision and validates the static routing contract. It does **not** dispatch, await or aggregate backend, migration or BC27 workflows, and is not evidence that every conditional profile completed.

Direct filters still execute the work. Classifier/workflow changes route to existing AL/BC27, migration and Core-Pilot gates. The broad EXT-50-12C.3 backend regression runs for unknown, backend, security and workflow changes; only `docs/**`, `quality/**` and `tools/ai-control-center/**` are ignored. GitHub PR path filtering includes deleted files; regression tests also prove deletion classification.

### Classic Branch Protection recommendation

No required checks are selected yet. Use only checks present on **every** PR; do not globally require conditional BC27 or migration checks.

| Branch | exact job check |
| --- | --- |
| `staging` | `Classify changes (fail closed)` |
| `staging` | `Reject implicit PROD deployments` |
| `main` | `Classify changes (fail closed)` |
| `main` | `Reject implicit PROD deployments` |

Both are lightweight and always present: the classifier runs on both protected branches, and the PROD-controller static guard is now triggered for every PR to either branch. They are policy/safety checks, **not** a fabricated cross-workflow merge aggregator. Do not require conditional checks such as `BC 27 AL compile with CodeCop and PTECop (fresh)`, `P0-04 PostgreSQL Migration Cycle`, or `EXT-50-12B BC27 Runtime Gate`; documentation-only PRs correctly omit them. Reviewers must verify relevant conditional runs according to the classified paths. A future aggregator is acceptable only if it fails on missing or failed runs for the exact PR head.

### Trigger / cost matrix (source-level contract)

| change set | direct safeguards |
| --- | --- |
| curated docs/evidence or isolated AI Control Center | stable policy and PROD-controller checks; no BC27/AL or broad backend regression |
| backend | EXT-50-12C.3 backend regression; Core Pilot for `backend/app/**` |
| BC27/AL | BC AL compile, BC27 runtime and BC finding-identity gates |
| security/migration | broad backend; Core Pilot for security; P0-04/P0-05 for migrations |
| workflow/classifier or deleted workflow/security | conservative AL/BC27, migration and Core-Pilot routing |
| unknown | broad backend and fail-closed policy decision |

The historical PR #172 run `BC AL Compile and Cop Gate` (run `43325450205`) completed in 26 minutes, with two Windows BC27 compile jobs. This is a simulation, not a measured saving.
## Remaining authorization and rollout gates
- The GitHub connector cannot read branch protection (HTTP 403).
  An authorized operator must verify required status checks and production
  environment reviewers before considering future fast-only PR tiers.
- Do not remove duplicate BC27 matrices or relax tests before that review;
  green checks on the final SHA are mandatory.
- Any release variables need explicit operator approval, and after
  deployment should be reset to disabled / NOT_APPROVED.
- Neither PR #184 nor this CI contract PR deploys anything.
  Status is CODE+CI review, never automatic DEV or Fiverr GO.
