# DEV Deployment Readiness — 2026-11-13

## Fixed deployment model

This change is a release-controller bootstrap only. It does not deploy,
merge, migrate, alter production data, or contact the AI Control Center.

The backend controller is deliberately added to the default branch because
GitHub only reliably exposes `workflow_dispatch` for workflow files present on
that branch. It deploys application code only after all of these checks pass:

1. the dispatch input is `target_environment=dev` and a full 40-character SHA;
2. repository variable `DEV_STAGING_DEPLOY_ENABLED` is exactly `true`;
3. `DEV_STAGING_RELEASE_SHA` exactly equals the dispatch SHA; and
4. that SHA is exactly the current `origin/staging` tip.

There is no `push` trigger. A merge to `staging` or `dev-acceptance` cannot
start an SSH deployment. The legacy workflow is now manual and production-only;
DEV releases use only `.github/workflows/dev-release.yml`.

Before any DEV mutation, the controller creates a custom-format PostgreSQL
backup, verifies it with `pg_restore --list`, preserves the existing Nginx and
landingpage configuration, refuses a checkout with any tracked or untracked
operator file, and never runs `git clean`. It then checks out the exact SHA and
only then runs the existing DEV compose migration/start sequence.

## Frontend model

`deploy-dev.yml` is manual-only and has the same full-SHA plus independently
approved repository-variable gate (`FRONTEND_DEV_RELEASE_ENABLED=true` and
`FRONTEND_DEV_RELEASE_SHA=<sha>`). It checks out that SHA directly, so a
reviewed frontend PR can be released to DEV without merging it to `main`.

The ordinary verification build explicitly keeps
`VITE_BCSENTINEL_LIVE_REPORTS=false`. Only the approved DEV image build gets:

```text
VITE_BCSENTINEL_LIVE_REPORTS=true
VITE_BCSENTINEL_REPORT_API_BASE_URL=https://dev-api.bcsentinel.com
VITE_API_BASE_URL=https://dev-api.bcsentinel.com
```

The image is first tested as an isolated candidate on loopback port 3001. The
existing port-3000 container is then renamed to a retained rollback container;
the candidate image is started freshly on port 3000 and must pass root and
`/overview` smoke. A failed replacement restores the old container. The
workflow only validates the established Nginx route and does not modify Nginx
or the landing page.

## Negative checks and local verification

| Check | Result |
| --- | --- |
| Backend workflow negative contract | PASS — no `push` trigger; unauthorized/incorrect SHA, missing flag, stale staging SHA, `git clean`, Nginx copy, and landingpage deletion are rejected by contract test. |
| Frontend workflow negative contract | PASS — no `push` trigger; missing environment/SHA approval is rejected; live viewer is false outside the approved image build. |
| Frontend unit test for workflow contract | PASS — 2 tests. |
| Frontend standard production build | PASS. |
| Docker daemon health | PASS — local socket daemon available. |
| Exact PR #14 Docker smoke | BLOCKED before application startup: Bun resolves a lockfile tarball from `https://europe-west4-npm.pkg.dev/...`, which is outside the managed environment allow-list and returns proxy HTTP 403. Proxy CA trust is now supported securely through an optional BuildKit secret; TLS was not disabled. |

## CI observations for approved consolidation SHAs

Observed from GitHub Actions on 2026-11-13:

- Backend PR #177 / `2bc926c3f996b7bff05d33e8978c0fb0741ef5b4`: completed PostgreSQL backup/restore, PostgreSQL migration cycle, BC27 runtime, sandbox AL build, native report access, AI Control Center, release-baseline, and CI optimization gates are successful. BC27 fresh and upgrade Cop/Compile jobs are still in progress, as is the independent finding-identity workflow. Do not promote until both matrices are successful.
- Frontend PR #14 / `69ab09d5603669570c8e1f9223c65b664b40c636`: `DEV live report integration gate (NO DEPLOY)` is successful. A real DEV viewer deployment and browser acceptance remain manual gates.

## Required merge and release sequence

1. Wait for both backend BC27 fresh/upgrade jobs and the finding-identity job on PR #177 to finish successfully.
2. Review and merge backend PR #177 into `staging`; this must not deploy.
3. Review and merge this backend release-controller PR into `main`; it also must not deploy.
4. Set the backend `development` environment approval and, only after review, set `DEV_STAGING_DEPLOY_ENABLED=true` and `DEV_STAGING_RELEASE_SHA` to the resulting current staging SHA.
5. Manually dispatch **Release approved BCSentinel DEV SHA** from `main`, with `target_environment=dev` and that same SHA. Verify backup checksum, exact remote checkout, local/public `/health/ready`, and no Nginx/landingpage change.
6. Review and merge the frontend release-controller PR into frontend `main`; it has no push deployment.
7. Set frontend `development` environment approval and bind `FRONTEND_DEV_RELEASE_SHA` to PR #14's reviewed SHA. Set its enable variable only for the intended release window, then manually dispatch the frontend workflow with that exact SHA.
8. After frontend root, `/overview`, and `/report/live` show the expected non-secret behavior, separately approve the DEV-backend-only `REPORT_V6_VIEWER_BASE_URL=https://dev.bcsentinel.com` change. It is not part of either deployment workflow.

## Rollback runbook

### Backend

- Record the prior DEV checkout SHA, container image IDs, backup file path and
  checksum before approval.
- A failed health check stops the workflow before public acceptance. Do not use
  `git clean`, force a reset around local operator files, or downgrade the
  schema merely to roll back application code.
- Restore data only from the captured custom-format backup after a separate
  isolated restore rehearsal and explicit incident approval. Verify checksum,
  `pg_restore --list`, schema revision, and tenant isolation before any live
  restore.
- The strict controller deliberately cannot deploy an old SHA. A rollback is a
  separate incident change with its own reviewed SHA, backup, schema-compatibility
  decision, and manual environment approval.

### Frontend

- The previous container remains as
  `bcsentinel-frontend-dev-rollback` after a successful swap.
- On incident approval, stop/remove only the new known container, rename the
  rollback container to `bcsentinel-frontend-dev`, start it, and verify local
  root plus `/overview` before public smoke. Do not modify Nginx or landingpage.
- Do not start a second release while a rollback/candidate container exists;
  that state is intentionally fail-closed for operator review.

## Remaining manual gates

1. GitHub environment approvals, deployment SSH secrets, and repository
   variables are not available to this task and must be set by an authorized
   operator.
2. The managed local Docker smoke needs an allow-list entry for
   `europe-west4-npm.pkg.dev` (or a reviewed artifact/cache strategy). No
   registry credential or network bypass was attempted.
3. The backend BC27 fresh/upgrade and finding-identity workflows must become
   green on the immutable PR #177 SHA before any staging merge.
4. No live browser, non-SUPER BC27, backup restore, or customer-data acceptance
   has been claimed by this source-only preparation.
