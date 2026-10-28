# BCSentinel Master State

Last updated: 2026-10-28

This document is the human-readable entry point for the current BCSentinel product state. The machine-readable source is [`release/current-product-state.json`](../release/current-product-state.json).

## Purpose

BCSentinel has evolved across several repositories, Lovable projects, runtime artifacts and acceptance branches. This document exists to prevent a feature branch, old roadmap, old percentage or stale manifest from becoming an accidental parallel truth.

The rule from now on is:

- `danielwauer-maker/bcsentinel/main` = canonical technical Core/Backend and release/product truth after reconciliation.
- `danielwauer-maker/bcsentinel-frontend/main` = canonical deployed customer-facing frontend truth.
- `danielwauer-maker/bcsentinel-product-system/main` = canonical normative product/UX truth.
- `danielwauer-maker/enterprise-data-ai-portfolio/main` = derived portfolio/readiness view, never the primary technical truth.
- `staging` remains a valid DEV integration/evidence branch; it is not the canonical product authority.
- `dev-acceptance` is the current automatic DEV deployment/acceptance branch and remains evidence/work history after reconciliation.
- PROD is promoted manually from an immutable reviewed `release_ref`; the newest `main` HEAD is not automatically equivalent to the currently deployed PROD release.
- Lovable = design and frontend authoring workspace; approved work must flow back to GitHub before it becomes release truth.

For the Core repository, the canonical technical baseline is recorded as the commit that changed technical/runtime truth. Later commits that only update this Master State or release metadata do not supersede that technical baseline unless they also change product/runtime behavior.

## Current verified references

### Core / Backend

- Repository: `danielwauer-maker/bcsentinel`
- Reconciled technical baseline: `cc1017fd5ba2b90ceb7be609c79e564fdad58bcf`
- Baseline date: 2026-10-28
- `dev-acceptance` evidence head previously reconciled: `3bd50178d1a47c552ff6212e3e374aead9b4bc5a`
- Core reconciliation PR: `#119` – `S0: reconcile dev-acceptance into canonical main`
- Extension source reconciliation PR: `#120` – `S0: reconcile BC extension source with verified 1.0.2.25`
- Evidence: DEV deploy for `3bd50178d1a47c552ff6212e3e374aead9b4bc5a` passed; post-core-reconciliation `Record Pricing Quality Gate` run `40711567073` passed; after Extension reconciliation, `Remediation Quality Gate` run `40717607682` and `Notification Quality Gate` run `40717607483` both passed.
- Status: current valid DEV acceptance work and the verified 1.0.2.25 Extension source contract are reconciled into canonical `main`.

### Frontend

- Repository: `danielwauer-maker/bcsentinel-frontend`
- Current `main`: `742e3257c8db6af6d732fcca02da0047a48b69b5`.
- S2 technical closure commit: `20464e4c8e15f139a21b6226f974cfc951ae180d`.
- Real routes implemented: `/`, `/overview`, `/findings`, `/actions`, `/financial-impact`, `/reports`, `/scans`, `/validation`, `/monitoring`, `/settings`, `/subscription`, `/support`, `/datenschutz`, `/impressum`.
- Runtime Lovable asset dependency removed; sidebar placeholder navigation removed; Free Entry route-level aggregate-only boundary preserved.
- DEV deployment run `40747919204`: PASS including verify, immutable image deployment, routing diagnostics and public DEV smoke.
- Manual responsive/visual acceptance and final legal/provider review remain later gates.

### Business Central Extension

- Current verified built artifact: `BCSentinel 1.0.2.25`
- Canonical Core manifests: `app.json = 1.0.2.25`, `app.cloud.json = 1.0.2.25`.
- Target: Business Central Online / Cloud
- Runtime: 16.0
- Real SCAN runtime without SUPER: PASS, 10/10 modules, 199/199 checks.
- Verified permission contract preserved: SCAN has no direct `DH Setup` Modify grant; required writes use the relevant codeunits' indirect `RM` permission.
- Roles: VIEWER, SCAN, SETUP, SCHEDULER, ADMIN.
- Real runtime evidence: VIEWER PASS without SUPER (dashboard/history readable; setup and manual scan denied, PR #46); SCAN PASS without SUPER on 1.0.2.25 (10/10 modules, 199/199 checks).
- Remaining runtime acceptance: SETUP, SCHEDULER, ADMIN.
- Status: the previous manifest/source discrepancy is closed. Canonical source and manifests now align with the verified 1.0.2.25 line.

### Product System

- Repository: `danielwauer-maker/bcsentinel-product-system`
- `main`: `b61c08d58dc095cd277961eebd3d53acfc8fda67`
- Role: normative product model, UX contracts, design/system rules and access semantics.

### Portfolio / Control Center

- Repository: `danielwauer-maker/enterprise-data-ai-portfolio`
- Current generated `main`: `db99adb8938477b706e1eddb12e30312c094fe37`
- Reconciliation PR: `#85` – `S0: make BCSentinel main the canonical readiness authority`.
- Canonical authority source: `bcsentinel/main/release/current-product-state.json`.
- DEV evidence source remains: `bcsentinel/staging/quality/portfolio-readiness-evidence.json`.
- The sync validates canonical `main` first, then applies mapped DEV evidence; manually maintained planning percentages are explicitly not imported as readiness evidence.
- PR validation passed for Readiness Sync, Control Center Validation and Portfolio Website.
- Post-merge main sync run `40718463973` completed successfully and wrote generated readiness commit `db99adb8938477b706e1eddb12e30312c094fe37`.
- Status: portfolio readiness is now derived from canonical product state plus evidence instead of treating `staging` as the sole product truth.

## Current Lovable references

- BCSentinel Frontend
  - Project ID: `6c392bec-8b44-40e1-a79d-d41962e7eb09`
  - Commit: `e84deb14afe90ae3326cd9622d78aa5363d6fc63`
  - Status: historical Lovable authoring reference; canonical `bcsentinel-frontend/main` has advanced through S2.

- Business Central Risk Radar / Landing Master
  - Project ID: `267ee2cd-c9a4-4d98-9835-e35659839a03`
  - Commit: `768c1049715aba547075b738e3d1d9bf54750a91`
  - Status: visual reference only; S2 removed the runtime dependency on its hosted landing assets.

- BCSentinel Report Assessment
  - Project ID: `a4c54214-d67a-47eb-99ca-dda8de9340fd`
  - Commit: `366b81ddeca7a542b921d09cb73f8ec45247cee2`
  - Status: design is advanced; static report data still needs complete runtime backend integration.

- BCSentinel Report Free
  - Project ID: `bed92b82-67f5-442b-aef4-c38d84fdb823`
  - Commit: `7397effa73bd4d584c88b17c981988f48dd79e08`
  - Status: design is advanced; runtime integration remains.

## Product model

BCSentinel is currently Business Central Online only.

Canonical progression:

1. Free Entry
2. Assessment
3. Validation
4. Monitoring

Canonical pricing:

| Data class | Assessment | Validation | Monitoring monthly | Monitoring annual |
|---|---:|---:|---:|---:|
| <=250k | EUR 249 | EUR 129 | EUR 199 | EUR 1,990 |
| <=1m | EUR 399 | EUR 199 | EUR 299 | EUR 2,990 |
| <=5m | EUR 699 | EUR 349 | EUR 499 | EUR 4,990 |
| <=20m | EUR 1,190 | EUR 590 | EUR 799 | EUR 7,990 |
| >20m | Custom | Custom | Custom | Custom |

Free Entry must remain aggregate-only: no detailed finding titles, no concrete financial values and no root causes.

## Design system

- Font: Inter
- Claim: `Clean Data – Higher Impact`
- Navigation: `#14213D`
- Interaction: `#246BFD`
- Success: `#11A36A`
- Warning: `#D98E04`
- Critical: `#CF3A3A`
- Background: `#F7F9FC`
- Cards: `#FFFFFF`
- Brand Orange: `#FF921F`
- Foreground on Orange: `#082138`

Approved frontend workflow:

`Lovable -> feature branch -> backend/API integration -> DEV -> responsive/functional QA -> PR -> main`

## Known current gaps

The following are not hidden by readiness percentages and must stay visible until evidence closes them:

- VIEWER, SETUP, SCHEDULER and ADMIN still require final real runtime role acceptance.
- Frontend S2 technical closure is complete; manual responsive/visual acceptance remains open.
- Legal routes are reachable, but final provider facts and legal review remain required before public launch.
- Current report-family integration/polish and visual acceptance remain later release gates.
- Multi-tenant switching needs a final real two-tenant isolation acceptance.
- Stripe needs full real-provider E2E acceptance.
- Transactional mail needs full DE/EN and DNS/provider acceptance.
- Real off-host restore/RTO/RPO evidence is still required.
- PROD release candidate and complete PROD E2E acceptance remain open.
- AppSource submission package is not complete.

## Release gates

### Controlled pilot

Required before calling the controlled pilot release complete:

- SETUP, SCHEDULER and ADMIN runtime acceptance complete; existing real VIEWER and SCAN evidence remains valid unless the environment changes materially.
- Real two-tenant switching and negative isolation tests pass.
- Current report designs integrated with real backend data and visually accepted.
- Real backup/restore drill completed.
- One frozen RC deployed to PROD and full E2E smoke passes.

### Public paid launch

Additionally:

- Complete Stripe product/lifecycle/provider matrix.
- Complete transactional email DE/EN matrix.
- SPF/DKIM/DMARC/bounce/spam acceptance.
- Final legal/provider review.
- PROD recovery evidence.
- Staged scale/soak evidence.

### Fully polished High-End SaaS + AppSource

Additionally:

- All SaaS pages and global states complete.
- Validation and Monitoring report families complete.
- Desktop/tablet/mobile polish complete.
- AppSource metadata, analyzers, screenshots, listing, support/help/privacy/terms, onboarding and certification package complete.

## Sprint model

The final program is executed in parallel tracks:

- Track A – Design & Frontend: Lovable -> GitHub -> backend integration -> DEV -> main.
- Track B – Core & Platform: Backend, Extension, Stripe, mail, security and infrastructure.
- Track C – Acceptance & Release: runtime acceptance, PROD, recovery, scale and AppSource.

## Sprint 0 closure

**Sprint 0 – Source of Truth & Repository Consolidation: COMPLETE**

Final S0 status:

- Core `main` reconciliation with current valid `dev-acceptance` work: COMPLETE.
- Canonical technical baseline semantics: COMPLETE.
- Extension source/manifests vs. verified 1.0.2.25 artifact reconciliation: COMPLETE.
- Portfolio readiness synchronization from canonical `main` plus DEV evidence: COMPLETE.

Definition of Done:

> `main` and release metadata identify one unambiguous current technical product state, and the portfolio derives status from evidence instead of stale manually maintained readiness values.

This Definition of Done is satisfied.

## Current Sprint 1

**Sprint 1 – Runtime Acceptance & Real Tenant Isolation: IN PROGRESS**

Tracking: GitHub issue `#121`.

The remaining S1 manual acceptance gates are intentionally deferred by the owner while autonomous technical sprints proceed. This does not close S1.

Already verified with real evidence:

- VIEWER without SUPER: PASS – dashboard/history readable; setup and manual scan denied (PR #46).
- SCAN without SUPER: PASS on 1.0.2.25 – synchronized, 10/10 modules, 199/199 checks, Executive Report generated (PR #46).
- Automated tenant-security attack matrix exists and remains supporting evidence only; it does not replace the real two-tenant test.

Remaining S1 gates:

- SETUP real BC SaaS runtime acceptance without SUPER.
- SCHEDULER real BC SaaS runtime acceptance without SUPER.
- ADMIN real BC SaaS runtime acceptance without SUPER.
- Real DEV switch between two tenants with different roles/entitlements plus negative cross-tenant access evidence.

Definition of Done:

> SETUP, SCHEDULER and ADMIN pass real BC SaaS runtime without SUPER, and the real two-tenant DEV switching/isolation test passes. Existing VIEWER and SCAN evidence is reused unless the environment changes materially.

## Sprint 2 closure

**Sprint 2 – Frontend Production Closure: AUTONOMOUS TECHNICAL SCOPE COMPLETE**

Evidence:

- Frontend closure commit: `20464e4c8e15f139a21b6226f974cfc951ae180d`.
- Current frontend `main`: `742e3257c8db6af6d732fcca02da0047a48b69b5`.
- Tests: PASS.
- Production build: PASS.
- Lint: PASS after full frontend formatting.
- Hygiene checks: PASS – no Lovable runtime asset URL, no sidebar `href="#"`, no relative Executive Report `/api/reports/executive/...` link.
- Free Entry direct service routes preserve aggregate-only boundaries; concrete financial values and action/finding details are not rendered there in Free mode.
- Validation/Monitoring navigation remains entitlement-aware.
- DEV deploy run `40747919204`: PASS through public DEV smoke.
- One-shot S2 finalizer/helper files were removed after successful closure.

Manual responsive/visual acceptance and final legal/provider review remain deferred acceptance gates; they are not claimed as complete.

## Using this file in future ChatGPT/Codex sprint chats

A new sprint chat can start with:

> Use `docs/BCSENTINEL_MASTER_STATE.md` and `release/current-product-state.json` from `danielwauer-maker/bcsentinel` as the initial BCSentinel project context. Revalidate relevant SHAs and evidence before making changes. Work only on Sprint X and update the Master State when the sprint changes product truth.

This avoids copying the complete historical project context into every new chat.
