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
