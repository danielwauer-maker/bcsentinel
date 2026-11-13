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

`.github/workflows/ci-change-classification.yml` is an always-present, lightweight PR and merge-queue control that obtains the exact changed path set from the checked-out Git graph and calls `scripts/ci_change_classification.py`. Its classification is intentionally conservative:

- `documentation_evidence`: curated `docs/**`, `quality/**` and the AI-PM evidence status file;
- `dashboard`: AI Control Center and dashboard source;
- `backend`, `migrations`, `security_auth_tenant`, `bc_al_bc27`, and `report_frontend`;
- `release_ci`: workflows, release contracts, controller validators and `AGENTS.md`.

A path can belong to more than one class. Security, migration and release/CI changes set `requires_full_validation=true`; unknown, missing or unreadable path input yields `all_critical=true` and every class instead of a silent skip. Existing targeted workflow `paths` filters remain the execution mechanism; no required check name, production gate, AL matrix or backend regression was removed. The classifier and its regression cases protect that filter policy from being narrowed without review.

### Trigger / cost matrix (source-level simulation)

| change set | classifier result | existing required work retained | intentionally avoided work |
| --- | --- | --- | --- |
| curated docs/evidence only | documentation/evidence | lightweight classifier | BC27/AL, backend and migration workflows |
| AI Control Center/dashboard only | dashboard | dashboard-specific workflow(s) | backend/AL workflows |
| backend only | backend | backend regressions | BC27 unless an AL path also changes |
| BC27/AL only | BC/AL | AL/BC27 gates | backend-only regressions unless shared paths change |
| security, migration or release/CI | critical profile | all prescribed relevant gates | none by classifier policy |
| unclassified/ambiguous | all critical | manual routing / full validation required | none |

The historical PR #172 run `BC AL Compile and Cop Gate` (run `43325450205`) completed in 26 minutes, with two Windows BC27 compile jobs. Therefore one superseded in-progress AL run can conservatively avoid **up to about 26 wall-clock minutes** (and two Windows job attempts); this is a simulation based on that historical run, not a measured saving. PR #185 already extends safe per-PR cancellation to ten heavy workflows. No historical runs are cancelled by this change.

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
