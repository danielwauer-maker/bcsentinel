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
