# EXT-50-12B – Copied Company Registration Recovery

## Problem

A Business Central company copy can contain the company-scoped BCSentinel setup and isolated-storage API token of the source company while Business Central assigns the copied company a different company identity. The backend correctly refuses an attempt to authenticate the old BCSentinel tenant against the new BC identity with `REGISTRATION_IDENTITY_CONFLICT`.

The observed runtime case is a copy of CRONUS into `BCS-PERF-DEV`. The copied company contains prepared performance/business data that must not be deleted.

## Root cause and security boundary

The BC registration identity is the combination of Entra tenant ID, environment name, environment type and Company SystemId. The backend binds a BCSentinel tenant to the resulting identity key and intentionally rejects rebinding an existing tenant to another identity.

EXT-50-12B does **not** weaken this guard. It introduces no backend endpoint, force flag, tenant delete, tenant rebind or authentication bypass.

## Detection

The extension already stores the identity returned with the product-access snapshot in:

- `Access Snapshot Tenant ID`
- `Access Snapshot Environment`
- `Access Snapshot Env. Type`
- `Access Snapshot Company ID`

The recovery service compares these values with the current identity from `DH Tenant Identity Mgt.` and reports:

- `Matched` – stored snapshot belongs to the current BC company.
- `Mismatch` – at least one stable identity component differs.
- `Legacy` – no complete identity snapshot exists.

No schema migration is required. Existing installations without a complete snapshot remain `Legacy`; a healthy registered legacy company is not offered recovery. A stale unregistered legacy binding can be recovered explicitly.

## Recovery semantics

`Reset Copied Company Registration` is an explicit BCSENTINEL ADMIN action. Confirmation defaults to **No**.

After confirmation the current company only is changed locally:

1. copied scheduler state is disabled and detached;
2. copied BCSentinel-local scan/history/remediation state is deleted;
3. company-scoped API token is removed through `DH Secret Mgt.`;
4. copied Tenant ID and registration state are cleared;
5. product-access, entitlement, credit and monitoring state is reset fail-closed;
6. the existing normal registration flow can register the current company as a separate BCSentinel tenant.

The recovery deliberately does **not** call `TaskScheduler.CancelTask` for the copied task ID. The copied GUID may identify the source company's scheduler task. Clearing the copied task reference prevents the copy from using it without risking a change to the source company.

## Data removed from the copied company

The following BCSentinel-local state is cleared because it belongs to the source registration or represents copied BCSentinel history:

- Tenant ID and company-scoped API token;
- registration date/status;
- access/license/entitlement snapshots and credits;
- monitoring state and copied scheduler runtime state;
- local scan headers/issues;
- deep-scan runs/findings;
- scan trends and dashboard issue cache;
- BCSentinel issue exceptions/action logs;
- duplicate work buffer;
- local last-score/run counters.

Table delete triggers retain the existing cascade behavior for scan issues and deep-scan findings.

## Data explicitly preserved

The recovery does not reference or delete standard Business Central master or ledger tables. In particular it does not modify customers, vendors, items, G/L entries, customer/vendor ledger entries or item ledger entries.

It also preserves:

- API base URL;
- contact email and privacy consent;
- pilot invite code;
- scan-module configuration;
- scan-check selection;
- schedule preferences (frequency/time/weekdays/monthly day), while disabling execution.

Therefore the existing `BCS-PERF-DEV` performance dataset is outside the recovery deletion scope.

## Permissions

Execution is added only to `BCSENTINEL ADMIN` through a permission-set extension. The setup action uses `AccessByPermission`, so normal setup/viewer/scan/scheduler roles do not receive the destructive recovery capability. The recovery codeunit carries only the indirect permissions required for BCSentinel-local tables.

PR #37 remains untouched.

## Backend behavior

No backend source is changed. The existing `RegistrationConflictError` and `_bind_identity` invariant remain authoritative. After local recovery, normal `RegisterTenant` is used without the old `existing_tenant_id`/token binding, producing a tenant derived from the current BC identity.

## Automated evidence

`tests/test_ext_50_12b_copied_company_recovery.py` verifies the local-only boundary, four-part identity comparison, no standard BC business-table access, scheduler detachment without source-task cancellation, default-No cancellation semantics, admin-only permission, unchanged backend conflict guard, copied-history cleanup and fail-closed access reset.

The dedicated `EXT-50-12B Copied Company Recovery` workflow runs these contracts. The existing BC AL compile/Cop gate and pilot readiness workflow remain the compilation/regression authority.

## Manual SaaS runtime evidence required

Status remains `AWAITING_MANUAL_BC_RUNTIME_EVIDENCE` until tested in the real BC 27 SaaS sandbox.

Use `BCS-PERF-DEV` and record counts before recovery. Expected sequence:

1. Verify `Registration Identity` reports a mismatch (or the guarded stale-legacy recovery is offered).
2. Record that the prepared DEV dataset is present (expected 6,000 generated customers, 2,000 generated vendors, 12,000 generated items / 20,000 business records total).
3. Select `Reset Copied Company Registration`.
4. First choose **No** and verify no state/data changed.
5. Run it again, review the warning and choose **Yes**.
6. Verify registration is unregistered, Tenant ID is empty, API token is not configured, monitoring/scheduler are disabled and old BCSentinel scan history is gone.
7. Verify the 20,000 generated business records still exist.
8. Verify the source CRONUS company remains registered and unchanged.
9. Register `BCS-PERF-DEV` through the existing registration action.
10. Verify registration succeeds without `REGISTRATION_IDENTITY_CONFLICT`, the new company has its own Tenant ID/token, and product access refresh succeeds.
11. Only then continue the DEV BCSentinel performance scan.

Do not mark runtime PASS from CI/container evidence alone.
