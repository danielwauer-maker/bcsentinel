# BCSentinel MVP launch gates — 2026-11-10

Status: **NO-GO / work in progress**. This document records the intended customer-facing MVP and the ordered release gates; it is not a deployment authorization or a claim of runtime acceptance.

## MVP product truth (target; formal product-system signoff outstanding)

Customer entry point: Business Central Online extension supplied directly by the operator (AppSource later). Customer starts **one** Free Deep Scan per tenant. Original aggregated Free report remains accessible. There is **no separate customer analytics dashboard** at launch; existing code and historical data are preserved but hidden from customer navigation.

Paid product flows:
- **Full Assessment:** 14 days premium access to eligible original Free scan; **0** additional scan credits; scope confirmation before Full report access.
- **Access Renewal:** 14 additional days premium, **0** scan credits; honor existing remaining paid term.
- **Renewal + Validation:** 14 additional days premium, **exactly 1** Deep Scan credit; report comparison only when verified scan provenance and methodical comparability exist.
- **Monitoring:** premium while an operator-confirmed valid subscription period exists, entitled manual/scheduled scanning, auditable trends and report; no invented payment confirmation.
- HTML/PDF and DE/EN for the included report families. Never relax existing export guards to conceal missing evidence.

Distribution: Fiverr with operator-confirmed orders first. Website at bcsentinel.com may publish information and inquiry/order routes following legal/security approval. **Automated public Stripe self-service checkout is a separate explicit payment/security gate**; no hidden enabling of payment flags. No prices are changed by this document.

## Known code/release baselines

- Core PR #156: commercial grants, registration; PR #157: Free-to-Full and company isolation; PR #158: legacy report guards.
- Core PR #159: comparison and scan evidence (draft). Head last independently checked: `54a8876772e007393071cdcc024e2856d6d0b531`.
- WIP local 1.0.2.58 checkpoint pushed as `checkpoint/sprint3a2-al-runtime-20261110` at `1f432182779b4a40f45405f9443b67e80ee09266`. This **does not imply validated CI**.
- Viewer PR #11 layered on PR #10. Verify live contract and exact SHA pair before any cutover.
- Backend migrations 0038 and 0039 are code-tested, but actual DEV database state requires revalidation.
- Historical company/scan/check provenance must not be synthesized or silently backfilled.

## Ordered remaining engineering and acceptance gates

| Gate | Deliverable | Pass evidence | Current assessment |
| --- | --- | --- | --- |
| G1: Sprint 3A.2 AL provenance | Complete actual BC execution evidence (pre-start snapshot, terminal check status, abort/resume, scope), stable comparison IDs where technically supported; authoritative comparability adapter | AL, backend, PostgreSQL, identity/security tests; at least one positive evidence-backed scan pair | **Open P0**; partial implementation in WIP 1.0.2.58 |
| G2: Sprint 3A.3 reports | Full Validation + Monitoring projections with verified check comparability and data-bound HTML/PDF DE/EN; appropriate unavailable states | Cross-repo contracts, actual outputs/screenshots/PDF and security regression | **Open P0**; export guards stay enabled |
| G3: Safe DEV release candidate | Exact backend SHA, viewer SHA, extension artifact/hash, feature flags, migrations, immutable backup/restore rehearsal and rollback runbook | Verified manifest, isolated restore, authorized DEV cutover and health checks | **Open P0**; DEV previously ran old image |
| G4: BC Online Sandbox | Confirm installed version, migration/schema compatibility, in-place upgrade, preserved data, non-SUPER permissions, scan execution and report links | Real sandbox test log with version, identity/roles, timestamps and observed results | **Open P0** |
| G5: End-to-end products/security | Real Free→Full→Renewal→Validation→Monitoring journeys, scheduled scans, tenant/company isolation, expiry, refunds/revokes, PDF DE/EN | Test matrix marked PASS with evidence, not mocked or inferred | **Open P0** |
| G6: Commercial/legal/operations | Product-system contract reconciliation, Fiverr listings/prices/delivery, GDPR/AVV/TOMs/privacy, support/revoke policy, monitoring cadence, PROD backup/restore, incident/rollback | Owner signoff and operator dry run with non-live orders | **Open P0** |
| G7: Controlled Fiverr + website launch | Freeze tested release manifest, signoff of all P0, controlled PROD deployment, post-deploy smoke, one controlled order/delivery | Real non-customer smoke and operator signoff; no independent dashboard exposure | **NO-GO until G1–G6 pass** |
| G8: Optional public checkout/AppSource | Stripe/public self-service and future AppSource publication | Separate provider, billing, security and Microsoft marketplace acceptance | **Post-MVP** |

## Branch / environment policy

- `main` -> PROD, `staging` -> DEV via `.github/workflows/deploy.yml`. Existing deployment action uses `git reset --hard`, `git clean -fd` and DB migrations.
- Development and review remain on isolated branches/Draft PRs. Never merge into `main` or `staging` as a side effect of passing CI.
- DEV reset is acceptable only after confirming the target, taking a restorable backup and obtaining explicit operator authorization for the particular operation; no customer data is currently declared, but configuration and identities still matter.
- Prod deployment and payments require explicit separate signoff.
- Full/Validation/Monitoring are all part of the intended Fiverr MVP, so no partial-feature GO is implied here.

## Execution discipline

1. One small technical objective per change. Preserve previous checkpoints.
2. Focused tests on every change; full regression/CI on frozen candidate SHA.
3. Every PASS includes a verifiable SHA/artifact/environment and links to test evidence.
4. Clearly distinguish static contract tests, synthetic integrations, BC AL compile and **real BC sandbox runtime**.
5. The authoritative product-system currently contains older Quick/7-day/no-Monitoring wording and must be formally reconciled before marketing or orders.
6. Update this file after each accepted gate rather than extrapolating an unsupported overall completion percentage.
