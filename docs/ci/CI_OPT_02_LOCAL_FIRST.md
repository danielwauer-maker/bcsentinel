# CI-OPT-02 — Local-first / Draft-first BC27 verification

**Review candidate, not an authorization to deploy, activate pilot enrollment, or bypass CI.**

## Development sequence

Choose exactly one active workspace per sprint: either the operator's Windows laptop (LOCAL) or ChatGPT/Codex working remotely in the GitHub feature branch (REMOTE). Never modify the same feature branch simultaneously. Finish, commit, synchronize and review before transferring ownership.

The Lenovo Windows laptop already has VS Code/AL and Docker and has successfully published a BCSentinel extension to a Microsoft **Business Central Cloud Sandbox**. Therefore a local Windows BC container is not necessary for routine AL source validation and development publishing. Backend tests may run locally with disposable PostgreSQL; the DEV/PROD application databases must never be used for regression tests.

## Exact GitHub CI behavior

Three expensive Windows BC27 workflows remain unchanged in their actual build, install, Fresh and Upgrade steps:

- `.github/workflows/bc-al-compile.yml`
- `.github/workflows/ext-50-12b-bc27-runtime-gate.yml`
- `.github/workflows/ext-50-12c-3-al.yml`

For matching PR changes, the Windows jobs are now **skipped while the PR is Draft**. The explicit `ready_for_review` event launches the full jobs. Further pushes to a **Ready for review** PR launch them again, so the final code is actually tested. A Draft's skipped jobs are **not** a BC27 PASS. Draft PRs cannot be merged.

Relevant `push: staging` triggers have conservative path filters: AL, product policy and CI-control changes still trigger BC27, while documentation/evidence-only staging merges no longer trigger those Windows workflows. Manually dispatched runs and staging push runs remain independent and are never cancelled by PR supersession.

**Important:** Existing branch protection requires two universal policy checks, NOT every conditional BC27 test. Therefore reviewing the actual conditional jobs on the final PR SHA is a mandatory human integration control. No skipped, pending, cancelled or missing BC27 job may count as success. A future mandatory fail-closed aggregator would be stronger; do not misrepresent this iteration as having one.

## Practical local workflow (Windows PowerShell)

1. Check pending changes: `git status --short`. Preserve all existing local/untracked work.
2. `git fetch origin`; start one local feature branch based on the reviewed `origin/staging` when the LOCAL work phase begins. Never check out over uncommitted changes.
3. Use VS Code with BC27 AL symbols to compile. For local backend tests from the `backend` directory use `.\\.venv\\Scripts\\python.exe -m pytest -c pytest.ini -q tests/test_pilot_enrollment_security.py` for a focused example.
4. PostgreSQL concurrency and Alembic must be verified against a disposable, isolated PostgreSQL test database. Never use production or deployed DEV database or silently substitute SQLite for PostgreSQL-only tests.
5. If needed, use VS Code to publish into the **correct isolated BC Cloud Sandbox**. Preserve registration/history; no `Recreate` or `ForceSync`. Test non-SUPER authorization, installation and relevant workflows. Cloud Sandbox results are supplemental to GitHub CI.
6. `git diff --check`, bundle and push one tested batch to a **Draft PR**. The REMOTE actor may not edit this branch while the operator owns the LOCAL phase.
7. Only when coding and targeted tests are finished: mark the PR **Ready for review**. Check all relevant GitHub gates, including BC27 Fresh/Upgrade and Runtime tests, on the final SHA. A later commit requires updated evidence.
8. After controlled merge to `staging`, obtain operator approval for any **separate exact-SHA DEV deployment**. Never promote to `main` automatically.

## Trigger/acceptance table

| Scenario | Windows BC27 PR jobs | Allowed to merge? |
| --- | --- | --- |
| Draft AL PR, opened or synchronized | SKIPPED (low-cost) | NO |
| Draft AL PR -> Ready for review | Full BC27 matrix | Only after actual PASS and review |
| Review-ready AL PR, later synchronized | Full BC27 matrix | Only after updated PASS and review |
| AL/product policy/CI change pushed to staging | Full BC27 post-merge checks | No automatic deployment |
| Documentation-only staging push | No BC27 Windows jobs | Separate normal review/controls |
| Manual workflow dispatch | Full BC27 work | No deployment implied |

## Rollback criteria

If ready-for-review fails to schedule the complete suite, if any CI-contract test fails, or if the final checks are missing, **do not merge**. Repair the workflow on a single reviewed branch and retest the routing contract. Never disable required branch protection to work around a missing CI result.
