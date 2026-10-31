# BCSentinel Master State

Last updated: 2026-10-31

This document is the human-readable authority entry point for the current BCSentinel product state. The machine-readable companion is [`release/current-product-state.json`](../release/current-product-state.json).

## Authority

- `danielwauer-maker/bcsentinel/main` is canonical Core/Backend/Extension and release/product truth after reviewed merges.
- `danielwauer-maker/bcsentinel-frontend/main` is canonical deployed customer-frontend truth.
- `danielwauer-maker/bcsentinel-product-system/main` is normative product/UX truth.
- Feature, staging, acceptance and release-candidate branches are work/evidence only until reviewed and merged.
- PROD is promoted manually from an immutable reviewed release ref; newest `main` is not automatically the deployed PROD release.

## Frozen product model

BCSentinel targets Microsoft Dynamics 365 Business Central Online and is positioned as **Data Health + Business Impact** with the claim **“Clean Data – Higher Impact”**.

Customer stages: Free Entry → Assessment → Validation → Monitoring.

There is only one customer-facing scan engine/depth: the full BCSentinel Data Health / Deep Scan. Free vs paid products differ by result access, not scan depth.

### Free Entry

- A newly registered tenant receives exactly one initial `free_entry` scan credit.
- The first scan executes the full enabled Deep Scan.
- The full result is stored server-side.
- Free surfaces expose aggregate-only information: score/counts/severity/risk areas/impact band.
- Free must not expose finding titles, issue codes, root-cause detail, full recommendations, record-level detail or concrete financial EUR values.
- After the initial Free Entry credit is consumed, a second unpaid scan is blocked.

### Assessment

- Assessment unlocks the qualifying existing scan; canonical Fiverr/operator Assessment does **not** create a new scan credit.
- Full detail/report access is fixed to 7 days after activation.
- The stored scan remains after expiry and can be used as Validation baseline/history.
- After expiry, live paid detail access falls back to Free aggregate access.
- One +7-day Assessment extension is allowed for the same entitlement; it does not create a new scan.

### Validation

- Validation requires evidence of a prior paid Assessment baseline.
- Validation grants exactly one new `validation_check` scan credit.
- Grant/purchase alone does not unlock Validation detail access.
- The customer runs a new full Data Health Scan after remediation.
- Consuming the Validation credit anchors the 7-day Validation result/comparison window at `consumed_at`.
- Validation Report accepts only a scan that actually consumed a Validation credit and compares it with the recorded paid Assessment baseline.

### Monitoring

- Monitoring permits recurring full scans and continuing paid-detail access while the subscription is active.
- Monitoring polish is not a Fiverr controlled-pilot blocker unless selected pilot scope requires it.

## Pricing truth for direct BCSentinel

| Record class | Assessment | Validation | Monitoring monthly | Monitoring annual |
|---|---:|---:|---:|---:|
| ≤250k | €249 | €129 | €199 | €1,990 |
| ≤1m | €399 | €199 | €299 | €2,990 |
| ≤5m | €699 | €349 | €499 | €4,990 |
| ≤20m | €1,190 | €590 | €799 | €7,990 |
| >20m | Custom | Custom | Custom | Custom |

Fiverr pricing/order truth remains on Fiverr. Fiverr is a sales channel and must not create Fiverr-specific product codes, scan engines or Extension forks.

## Fiverr channel architecture

- One standard BCSentinel Extension/backend serves Fiverr, direct, partner and future marketplace channels.
- Generic product codes remain `assessment`, `validation_check`, `monitoring_monthly`, `monitoring_annual`.
- Sales origin is separate metadata such as `fiverr`, `direct`, `malt`, `contra`, `appsource`, `partner` or `support`.
- External order references are audit metadata, not entitlements.
- Fiverr payment/contract remains on Fiverr; do not redirect Fiverr purchases to Stripe and do not scrape Fiverr order/chat state.
- Controlled pilot permits one manual operator action after payment confirmation. Everything after entitlement/credit grant is automated.

## Extension state

Current source target: **1.0.2.28**, BC Online / BC 27.x, runtime 16.0.

1.0.2.28 includes initial Free Entry, Free/Assessment/Validation report actions, `Report & Notification Email`, preferred DE/EN report language and lifecycle-profile synchronization after registration.

Last previously verified real BC artifact/runtime evidence predates 1.0.2.28. Therefore 1.0.2.28 is **source-complete but still requires real BC SaaS artifact/runtime acceptance before paid pilot launch**.

Known prior real non-SUPER evidence: SCAN PASS (10/10 modules, 199/199 checks) and VIEWER PASS. SETUP still needs final real runtime acceptance. SCHEDULER/ADMIN can be deferred for a one-off Free/Assessment/Validation Fiverr pilot unless used by the selected workflow.

## Report family – automatic implementation complete

F2 established separate product report contracts:

- **Free Health Report**: aggregate-safe JSON/HTML/PDF + secure share links.
- **Assessment Report**: full-detail Assessment JSON/HTML/PDF + secure share links; legacy Executive route retained for compatibility.
- **Validation Report**: true before/after model with resolved, improved, remaining, regressed and new findings plus score/issue/exposure deltas.
- Monitoring report remains existing/later polish and is not required for the first one-off Fiverr pilot.

Free redaction is enforced by a separate aggregate-safe data contract rather than CSS hiding.

## Lifecycle email – automatic implementation complete

F3 introduced backend-owned transactional lifecycle email infrastructure: tenant lifecycle profile, DE/EN language, idempotent retryable outbox, internal worker, concurrency-safe claims, stale-claim recovery, signed report links without API tokens and no historical retroactive mail flood.

Lifecycle events include registration, scan start/completion/failure, Assessment activation/expiry warning/expiry/extension and Validation availability/completion/expiry warning.

Real sender DNS/provider acceptance (SPF/DKIM/DMARC, bounce and spam placement) remains manual.

## Operator/Admin – automatic implementation complete

F4 provides a channel-neutral operator flow and console at `/admin/operator`: tenant/environment/email/order search, Grant Assessment, Extend Assessment, Grant Validation, Revoke and Resend lifecycle mail. Writes are CSRF-protected and the console requires admin Basic auth.

Canonical operator semantics:

- Assessment: existing scan + fixed 7 days, no credit.
- Validation: paid Assessment prerequisite + exactly one scan credit, no premature detail access.
- Extension: maximum once, +7 days, old scheduled expiry mails suppressed/replaced.

The old internal `admin_manual` credit grant retains a narrowly scoped compatibility behavior for legacy internal tests/tools. It is **not** the canonical Fiverr/direct commercial grant path.

## Security and recovery evidence

Automated gates repeatedly verify tenant ownership/isolation contracts, entitlement/report boundaries, operator auth/CSRF, backend compile/Alembic graph, dashboard build, report/lifecycle contracts and PostgreSQL backup/checksum/isolated restore/data-probe automation.

Automated evidence does not replace the required real two-tenant BC SaaS test or real off-host PROD restore drill.

## Fiverr RC / F5 automatic gate

`docs/FIVERR_PILOT_RELEASE_CANDIDATE.md` is the release-candidate checklist.

The F5 lifecycle regression must prove in one contract:

registration → one Free Entry scan → Free report/paid block → Assessment unlock without rescan/credit → Assessment expiry/fallback → Validation grant → new scan credit consumption → Validation full access/comparison report.

## Brand freeze

Navigation `#14213D`; Interaction `#246BFD`; Success `#11A36A`; Warning `#D98E04`; Critical `#CF3A3A`; Background `#F7F9FC`; Cards `#FFFFFF`; Brand Orange `#FF921F`; Foreground on Orange `#082138`; typography Inter; claim “Clean Data – Higher Impact”.

## Manual release gates still authoritative

Before the first paid Fiverr pilot customer:

1. Build/install/upgrade final 1.0.2.28 artifact in real BC Online.
2. Complete required non-SUPER runtime role acceptance, at minimum SETUP for the selected one-off pilot flow.
3. Perform real tenant A/B switching and negative cross-tenant isolation.
4. Manually visually inspect real Free, Assessment and Validation HTML/PDF with representative data.
5. Configure/test real lifecycle SMTP sender including SPF/DKIM/DMARC, bounce behavior and inbox/spam placement.
6. Perform real off-host/operational PROD backup and restore procedure.
7. Freeze immutable reviewed RC and manually promote exactly that ref to PROD.
8. Run fresh external-like PROD E2E through registration, initial scan, Free boundary, Fiverr Assessment grant, expiry/fallback, Validation grant, new scan and comparison report.
9. Complete privacy/DPA/legal/provider-facts signoff.
10. Publish/activate Fiverr Gig and execute one real Fiverr order dry-run.

AppSource, full public Stripe E2E, public self-service, Monitoring polish, mobile polish and partner program are not controlled-pilot blockers unless scope changes.
