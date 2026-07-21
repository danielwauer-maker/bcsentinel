# LIC-02 License Model Simplification

Status: implemented in source; migration and sandbox CAT not yet deployed/executed. This document is the normative license contract for go-live.

## Root cause and inventory

The previous implementation normalized legacy `assessment` purchases to `full_analysis`, but then granted a `TenantScanCredit`. Snapshot code counted that row as an Assessment Credit, admin grants repeated the behavior, Business Central cached and displayed it, and atomic scan start consumed it for `assessment` mode. Premium dates were recomputed independently from purchases, credits, and entitlements. Free usage was inferred from scan history and the unique `scan_start_requests.free_scan_slot` rather than represented explicitly.

Authoritative persisted sources before LIC-02 were:

- free scan: scan history plus the unique free start slot;
- premium: purchase, credit, and entitlement timestamps;
- scan credits: `tenant_scan_credits`, with mixed Full Analysis and Validation meanings;
- monitoring: Stripe `subscriptions` and `tenant_product_entitlements`;
- product purchase: `tenant_product_purchases` and idempotent webhook events;
- pricing/tier/Stripe Price ID: active pricing matrix, with product fallback and environment Stripe IDs;
- audit: immutable `credit_ledger_entries` and admin audit events.

Legacy Assessment Credit paths existed in checkout fulfillment, admin product grants and adjustments, access snapshots, atomic start mode selection, BC cached fields/actions, dashboard labels, tests, and billing/CAT documentation.

## Normative state and decisions

Tenant entitlement state is `free_assessment_used`, `premium_until_utc`, available `validation_check` credit rows, and the authoritative Monitoring period. One-time events apply `premium_until = max(existing, event time + 7 days)`.

Accepted scan-start order is Monitoring, Validation Credit, free assessment, reject. The free claim, Validation Credit claim, start request, scan placeholder, lifecycle lease/token binding, and ledger event remain one transaction. An idempotent replay returns the original accepted result. Full Analysis never enters this decision and never grants a credit.

Premium authorization is active `premium_until_utc` or active Monitoring. Full Dashboard, complete Findings, Issues, Actions, premium analytics, and the full Executive Report use that authorization. Monitoring controls additionally require Monitoring. The free dashboard remains available after a scan.

## API contract

`GET /license/status` adds `free_assessment_used`, `free_assessment_available`, `premium_active`, `premium_until`, `validation_credits`, `monitoring_until`, `dataset_tier`, and `entitlement_capabilities` flags for free/full dashboards, findings, issues, actions, report, Monitoring, and manual scan.

The existing decision-shaped `capabilities` object remains for BC P0D compatibility. `assessment_scan_credits_available` is deprecated, always zero, and must be removed after all supported BC clients consume LIC-02. `scan_credits_available` temporarily aliases Validation Credits. Neither compatibility field is used for authorization.

Rejection text is: `A new scan requires a Validation Check or active Monitoring.` Full Analysis is intentionally absent.

## Fulfillment and pricing

| Product | Fulfillment | Scan authorization |
|---|---|---|
| Data Health Score | one free claim, no credit | once per scope |
| Full Analysis | extend premium by seven days | none |
| Validation Check | add one Validation Credit and extend premium by seven days | exactly one accepted scan |
| Monitoring Monthly/Annual | activate through authoritative period end | unlimited while active |

The active product-by-dataset-tier pricing matrix remains authoritative. Fallback cents are 0, 7900, 4900, 14900, and 149000. Starter/professional/business prices are not flattened. Enterprise remains contact-sales unless an active matrix row has an explicit Stripe Price ID.

## Migration 0026

`0026_license_simplification` adds `tenants.free_assessment_used` and `tenants.premium_until_utc`.

Backfill rules:

1. Mark free use when an accepted free start slot or a `data_health_score`/`quick` scan proves use.
2. Preserve the latest active Full Analysis/legacy Assessment/Validation entitlement date.
3. Consider paid/completed one-time purchases at purchase time plus seven days.
4. Preserve existing Validation Credits exactly.
5. Do not convert unused Full Analysis/Assessment credits. They remain historical rows and ledger evidence but authorize nothing.
6. Preserve Monitoring subscriptions/terms, scans, findings, purchases, and ledger rows unchanged.

For pilot tenant `ten_47ca6ef7cc4f`, run read-only verification before upgrade and verify derived state after upgrade. Do not reset history or grant compensating credit without purchase/ledger evidence and an explicit audited decision.

## Business Central and admin

BC stores Free Assessment Used, Validation Credits, Premium Until, and Monitoring Until from the snapshot. Customer pages no longer show Assessment Credits or generic Scan Credits. Actions are behavior-oriented: Start Free Data Health Score, Start Validation Check, and Start Monitoring Scan. Cached state is guidance; backend start authorization remains authoritative.

Tenant Detail shows Free Assessment, Premium Until, Validation Credits, Monitoring and dataset tier. Full Analysis admin grant is premium-only; Validation grant adds one credit plus premium; Monitoring grants no credit. Historical mixed credit rows remain visible only as audit evidence.

## Manual CAT matrix

- CAT-LIC-01: register; verify free available; accept one free request and replay; reject a second logical request; verify free dashboard and premium locks.
- CAT-LIC-02: purchase/grant Full Analysis; verify zero credits, existing results unlocked for seven days, and a new scan remains blocked after free use.
- CAT-LIC-03: purchase/grant Validation Check; verify one credit, seven-day premium, one consumption/ledger row, replay stability, then block.
- CAT-LIC-04/05: activate Monthly/Annual; run repeated manual and scheduled scans; verify no credit delta and period-end behavior.
- CAT-LIC-06: resolve starter/professional/business matrix rows and Enterprise contact-sales behavior.
- CAT-LIC-07: expire premium/Monitoring; verify locks return without deleting history.
- CAT-LIC-08: repeat all admin grants/revocations and preserve actor, old/new state, deltas, source, reason, and timestamp evidence.

For every accepted scan retain tenant/company/environment, client request GUID, scan ID, worker ID, execution-token correlation, credit before/after, and ledger row. Re-run FIX03/FIX04 wrong-worker, wrong-token, cross-tenant, retry, lifecycle update, and sync regressions.

## Deployment and release gate

1. Back up PostgreSQL and record revision `0025_dashboard_memberships`.
2. Audit pilot purchases, credits, ledger, free starts/scans, entitlements, and subscriptions read-only.
3. Deploy backend and upgrade to `0026_license_simplification` through the normal maintenance process.
4. Verify backfill and `/license/status`; confirm the legacy Assessment balance reports zero.
5. Verify tier matrix Stripe Price IDs and webhook retries in sandbox.
6. Publish BC only after DE-DE/EN-US XLIFF validation and sandbox CAT.
7. Run CAT-LIC-01..08 plus FIX03/FIX04 regressions.

Go-live is **NO-GO until** migration verification, complete automated regressions, AL compilation/XLIFF regeneration, Stripe sandbox fulfillment, and BC sandbox CAT are green.
