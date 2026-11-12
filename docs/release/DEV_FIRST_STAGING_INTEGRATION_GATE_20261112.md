# DEV-first staging integration preflight — 2026-11-12

Candidate: Draft PR #172. Source BC27 head 114a206ac3f84587a787894823a6a96936577c7a; original staging 59fd0fcfa98114a4366bb89428c6956b8a9d2236.
NO MERGE OR DEPLOY AUTHORIZATION. Core main and PROD excluded. Dashboard 8092 is being edited independently by the operator.

## Confirmed operational risks
- Staging has an automatic GitHub Actions push-to-DEV deployment that resets the DEV checkout, replaces nginx, runs Alembic migrations and recreates Docker services.
- Main has a different development deploy workflow. Branch names alone do not identify running DEV image or deployed migrations.
- Staging and main have diverged; do not merge main blindly. Candidate contains a 341-commit / 263-file staging delta and must be reviewed as a whole.
- BC27 extension installation is a separate manually controlled in-place upgrade; no ForceSync, uninstall, table deletion or non-SUPER bypass.
- Paid checkout must remain disabled until commercial security and payment E2E acceptance.

## Required gates before staging merge
1. Full PR graph/diff and exact-HEAD CI for backend, AL, migration, report and tenant isolation checks.
2. Read-only DEV runtime inventory: deployed Git SHA, image ID, Alembic head, flags, service status and report URL configuration.
3. Verified backup plus isolated restore of DEV PostgreSQL, deterministic migration dry run and documented downgrade/forward recovery plan.
4. Feature flags default to deny, no automatic paid grants, legacy Quick/7-day entitlements preserved pending normative migration.
5. Secure company/tenant-scoped Full-v6 report, Free archive, Validation evidence fail-closed and Monitoring lifecycle regression.
6. Actual BC27 installed package comparison and Non-SUPER upgrade, with record/history and registration retention; separate from backend deploy.
7. Reviewed staging pipeline: immutable release SHA, serialized migrations, backup/rollback, safe nginx validation, health checking the newly deployed image, no PROD impact.
8. DEV deployment authorized for exactly one reviewed ref only after gates 1–7 pass.

## Controlled rollout and dashboard evidence
- Core candidate #172 is for DEV-first integration review, not yet a safe automatic staging merge.
- Frontend #13 is a separate isolated DEV viewer candidate; preserve public port 3000 while wiring authenticated report route.
- Product System #33 is a non-active normative candidate; buyer kit #165, website #166 and price discounts still require projection/parity review.
- AI-PM 2.2 evidence changes stay in separate #170. Preserve running 8092 and pending operator edits, then plan snapshot/backup and controlled rollout.
- Always distinguish code ready, integrated, deployed, BC27 DEV accepted, commercial contract and Fiverr Go-Live. Global NO_GO.

## Evidence verified from real DEV host, 2026-11-12

- Current checkout before integration: `594112ea161b8255e7a8911031166f5a24c2a5d1`; running backend image `bcsentinel-dev-s3a2:a8b870eb41d2`, PostgreSQL 15 healthy, Alembic `0040_scan_record_identity_evidence`, DB readiness OK.
- Actual operator database dump: `/home/daniel/bcsentinel-dev-backups/dev-pre-pr172-20261112T210953Z.dump` (325K as reported by `ls -lh`); SHA256 `540657ed371e797bde5b2463ec8f50eb87c94033ee2870bc9b869348b79592c1`.
- Actual host restore test using immutable `scripts/dev_verify_isolated_restore.sh` at `f90d25de65c54545f07d15ef115f535c1137b616`: checksum PASS, isolated networkless/tmpfs PostgreSQL15 restore transaction PASS, 66 public tables, Alembic 0040, `RESTORE_TEST=PASS`. Actual container cleanup after exit not separately inventoried.
- `nginx -t` PASS and DEV/PROD config files separate. Operator identified untracked `landingpage_neu -> landingpage` symlink, safely unlinked the symlink, then `git status --short` was empty. Repeat at actual release.

## Explicit single-SHA staging release authorization

- Staging previously deployed on push before CI completion. Candidate workflow now gates all four DEV steps (snapshot, deploy, health, web smoke) on `vars.DEV_STAGING_DEPLOY_ENABLED == 'true'` AND `vars.DEV_STAGING_RELEASE_SHA == github.sha` plus staging push event.
- Without those exact repository Actions variables, the DEV steps SKIP even though the overall workflow may look green. A skipped deployment is **not** release success.
- After merging, get the actual new **staging SHA** (do not use PR branch HEAD). Complete independent CI verification, approve the release explicitly, then set the two variables in GitHub repository Settings → Secrets and variables → Actions → Variables, and rerun the matching staging push workflow. Afterwards unset `DEV_STAGING_DEPLOY_ENABLED` and remove the release SHA. The behavior of rerunning with updated variable values must be validated; if unsupported, stop and use a separately reviewed manual release mechanism.
- The pipeline takes a new custom-format PostgreSQL dump and checks its TOC, verifies checkout has zero tracked/untracked changes, fetches and resets exactly to `github.sha`, retains operator files (no `git clean`), checks `nginx -t`, and leaves live DEV nginx + webroot untouched. The full restore rehearsal above is a separate proof, not performed automatically per release.
- The pipeline does not automatically prove compatibility of the previous backend image with newer schema, does not guarantee automatic rollback and does not install a BC27 extension.

## Required remaining approval checks (fail closed)

- [x] DEV runtime DB health and migration head verified by operator.
- [x] Real isolated full restore test, 66 public tables and Alembic 0040.
- [x] nginx syntax and distinct DEV/PROD sites.
- [x] Clean DEV checkout after validated symlink removal.
- [x] Source-only deployment gate for staging exact SHA and preservation of nginx/webroot.
- [ ] ALL workflows at final PR HEAD PASS, including long BC27 Windows jobs.
- [ ] Independent push-run `EXT-50-12C.3 BC finding identity` (fresh AND upgrade) verified; lossless-findings backend PASS does not replace it.
- [ ] SSH-based read-only GitHub Actions host inventory run independently verified; operator inventory is separate evidence.
- [ ] Effective DEV access-v2 and paid checkout flag values confirmed safe WITHOUT leaking secrets.
- [ ] PR #172 entire change graph and release diff reviewed for unexpected changes before merge.
- [ ] Exact staging merge SHA authorized and proof all 4 DEV stages actually EXECUTED, not skipped; record new pre-migration backup SHA.
- [ ] On-host checkout SHA, backend container image ID, Alembic, `/health/ready` and public DEV API rechecked after release.
- [ ] Tenant/company isolation; Free once; archive; Full 14d from qualifying existing scan; renewal and validation evidence; monitoring; disabled paid checkout exercised with synthetic tenants.
- [ ] BC27 in-place sandbox upgrade with history/registration retention and Non-SUPER account; separate viewer HTML/PDF and access routes.
- [ ] Owner approval of commercial/product/website/price readiness. Fiverr NO_GO pending all gates.

## Recovery / rollback constraints

Preserve the original DEV checkout `594112ea161b` and prior backend image identification and the restored pre-release dump. A failed post-deploy health check must halt progression and capture actual SHA, image ID and Alembic state. Do NOT blindly downgrade evidence migrations or restore a prior DB into a live, writable application: new writes would be lost. First review schema compatibility, isolate writers, snapshot the failed state, and obtain explicit authorization for app rollback / database restore in a maintenance window. Published nginx and webroot remain unchanged by this candidate. PROD and AI dashboard 8092 untouched.

## Post-release smoke and evidence

Check the staging Actions four DEV steps are executed (not skipped), then on DEV: `git rev-parse HEAD`, `git status --short`, `docker compose -f docker-compose.dev.yml --env-file .env.dev ps`, `docker inspect --format '{{.Image}}' dhm-dev-backend`, `docker exec dhm-dev-backend alembic current`, `curl -fsS http://127.0.0.1:8001/health/ready`, `curl -4 -fsS https://dev-api.bcsentinel.com/health`. Check public DEV website smoke. Record redacted synthetic tenant E2E evidence, BC27 sandbox package version and non-SUPER results separately.
