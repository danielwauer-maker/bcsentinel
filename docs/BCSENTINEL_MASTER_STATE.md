# BCSentinel Master State

Last updated: 2026-10-28

This document is the human-readable entry point for the current BCSentinel product state. The machine-readable source is [`release/current-product-state.json`](../release/current-product-state.json).

## Purpose

BCSentinel has evolved across several repositories, Lovable projects, runtime artifacts and acceptance branches. This document exists to prevent a feature branch, old roadmap, old percentage or stale manifest from becoming an accidental parallel truth.

The rule from now on is:

- `danielwauer-maker/bcsentinel/main` = canonical technical Core/Backend truth after reconciliation.
- `danielwauer-maker/bcsentinel-frontend/main` = canonical deployed customer-facing frontend truth.
- `danielwauer-maker/bcsentinel-product-system/main` = canonical normative product/UX truth.
- `danielwauer-maker/enterprise-data-ai-portfolio/main` = derived portfolio/readiness view, never the primary technical truth.
- Lovable = design and frontend authoring workspace; approved work must flow back to GitHub before it becomes release truth.

## Current verified references

### Core / Backend

- Repository: `danielwauer-maker/bcsentinel`
- `main`: `625192deb09608c0c242979fd001041b621c8c91`
- `dev-acceptance`: `3bd50178d1a47c552ff6212e3e374aead9b4bc5a`
- Status: `main` is currently stale relative to the latest DEV acceptance work and must be reconciled in Sprint 0.

### Frontend

- Repository: `danielwauer-maker/bcsentinel-frontend`
- Current `main`: `e84deb14afe90ae3326cd9622d78aa5363d6fc63`
- Lovable `BCSentinel Frontend` is synchronized to the same SHA.
- Real routes currently implemented: `/`, `/overview`, `/findings`.
- Additional SaaS routes still need runtime implementation/integration.

### Business Central Extension

- Current verified built artifact: `BCSentinel 1.0.2.25`
- Target: Business Central Online / Cloud
- Runtime: 16.0
- Real SCAN runtime without SUPER: PASS, 10/10 modules, 199/199 checks.
- Roles: VIEWER, SCAN, SETUP, SCHEDULER, ADMIN.
- Remaining runtime acceptance: VIEWER, SETUP, SCHEDULER, ADMIN.

Important discrepancy: the Core repository manifest on `dev-acceptance` still reports `1.0.2.6`. The built 1.0.2.25 artifact therefore represents newer Extension work than the current Core branch manifest. Sprint 0 must reconcile that gap rather than silently treating either source as complete truth.

### Product System

- Repository: `danielwauer-maker/bcsentinel-product-system`
- `main`: `b61c08d58dc095cd277961eebd3d53acfc8fda67`
- Role: normative product model, UX contracts, design/system rules and access semantics.

### Portfolio / Control Center

- Repository: `danielwauer-maker/enterprise-data-ai-portfolio`
- `main`: `c623074646aacb2ff7b04ddb4d1106656458e75f`
- Current BCSentinel status data is stale relative to the runtime and frontend work completed after 2026-10-10.
- Existing readiness synchronization currently reads selected evidence from `bcsentinel/staging`; it must be extended to consume this Master State and relevant cross-repository evidence.

## Current Lovable references

- BCSentinel Frontend
  - Project ID: `6c392bec-8b44-40e1-a79d-d41962e7eb09`
  - Commit: `e84deb14afe90ae3326cd9622d78aa5363d6fc63`
  - Status: synchronized with `bcsentinel-frontend/main`.

- Business Central Risk Radar / Landing Master
  - Project ID: `267ee2cd-c9a4-4d98-9835-e35659839a03`
  - Commit: `768c1049715aba547075b738e3d1d9bf54750a91`
  - Status: current landing visual reference.

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

- Core `main` is stale against `dev-acceptance`.
- Extension repo manifest is stale against the verified 1.0.2.25 artifact.
- Landing hero/dashboard/logo assets currently depend on Lovable-hosted assets and must be localized before PROD.
- New frontend currently implements only `/`, `/overview` and `/findings` as real routes.
- Remaining sidebar destinations require real routes and backend integration.
- Multi-tenant switching needs a final real two-tenant isolation acceptance.
- Stripe needs full real-provider E2E acceptance.
- Transactional mail needs full DE/EN and DNS/provider acceptance.
- Real off-host restore/RTO/RPO evidence is still required.
- PROD release candidate and complete PROD E2E acceptance remain open.
- AppSource submission package is not complete.
- Portfolio readiness data is stale and must be derived from current evidence.

## Release gates

### Controlled pilot

Required before calling the controlled pilot release complete:

- Core `main` reconciled with current valid work.
- VIEWER, SETUP, SCHEDULER and ADMIN runtime acceptance complete.
- Real two-tenant switching and negative isolation tests pass.
- Lovable-hosted production assets localized.
- Impressum and Datenschutz reachable from the current frontend.
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
- No placeholder navigation in the SaaS frontend.

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

Current next sprint:

**Sprint 0 – Source of Truth & Repository Consolidation**

Definition of Done:

> `main` and release metadata identify one unambiguous current technical product state, and the portfolio derives status from evidence instead of stale manually maintained readiness values.

## Using this file in future ChatGPT/Codex sprint chats

A new sprint chat can start with:

> Use `docs/BCSENTINEL_MASTER_STATE.md` and `release/current-product-state.json` from `danielwauer-maker/bcsentinel` as the initial BCSentinel project context. Revalidate relevant SHAs and evidence before making changes. Work only on Sprint X and update the Master State when the sprint changes product truth.

This avoids copying the complete historical project context into every new chat.
