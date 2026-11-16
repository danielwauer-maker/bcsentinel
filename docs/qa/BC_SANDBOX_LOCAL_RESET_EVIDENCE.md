# BCSentinel Sandbox Local Reset Evidence

Status: source-level evidence prepared for 1.0.2.61. This document is not a deployment approval and does not replace Business Central runtime evidence.

## Scope and safety boundary

- The administrative action is available from `DH Setup` only to a user who can execute `DH Sandbox Reset Mgt.` (the `BCSENTINEL ADMIN` permission set).
- `DH Sandbox Reset Mgt.` is the authoritative server-side boundary: it rejects every environment for which `Environment Information`.IsSandbox() is false.
- The action requires two independent confirmations. The reset manager makes no HTTP or backend-cleanup call.
- A queued/running deep scan stops the reset before mutation. A non-empty legacy scheduled-task ID also stops the reset because this source revision has no scheduler manager capable of proving task cancellation.

## Curated local-data purge inventory

The reset uses `DeleteAll(false)` only after the sandbox and activity gates. This deliberately bypasses normal immutability/retention triggers for a sandbox-only administrative purge.

| Area | Local tables purged |
| --- | --- |
| Scan history, findings and selections | `DH Deep Scan Run`, `DH Deep Scan Finding`, `DH Scan Header`, `DH Scan Issue`, `DH Dashboard Issue`, `DH Scan Trend`, `DH Scan Check Selection`, `DH Duplicate Buffer` |
| Exceptions and remediation | `DH Issue Exception`, `DH Issue Action Log`, `DH Remediation Action`, `DH Remediation Audit` |
| Notification evidence and configuration | `DH Notification Delivery`, `DH Notification Event`, `DH Notification Config Audit`, `DH Notification Recipient`, `DH Notification Rule`, `DH Notification Template`, `DH Notification Setup` |

No table outside the BCSentinel object range is referenced. No CRONUS business table and no table belonging to a QA extension is targeted.

## Registration reset proof points

- The company-scoped `BCSentinel.ApiToken` isolated-storage value is deleted.
- Tenant binding, legacy token field, access snapshots, credit/license/monitoring state, report access, run IDs and scheduler residue are reset to their defined unregistered values.
- API Base URL, data-processing consent, invite configuration, enabled modules and lifecycle profile fields are retained so a new Free registration can be initiated.

## Automated source evidence

Run from repository root:

```text
python3 scripts/validate_bc_sandbox_local_reset.py
```

Expected result: `BC sandbox local reset contract: PASS`.

Curated check recorded 2026-11-16: the reset contract, BC compatibility contract, legacy-schema contract and controlled-pilot static readiness checks passed. No BC package compiler, BC29 symbols or sandbox runtime was available in this workspace, so this is source evidence only.

## Required manual sandbox evidence (still pending)

1. Build the 1.0.2.61 BC29 package and install it only in the nominated sandbox after separate approval.
2. Capture the two confirmation dialogs and the successful reset outcome; do not capture tokens.
3. Prove a reset is refused in a production environment, and prove it is refused for a queued/running scan and a legacy task ID.
4. Before/after: verify all inventory tables above are empty, the token and old tenant binding are unavailable, and a new Free registration succeeds.
5. Verify the three QA extensions and their M/L/XL test data remain unchanged.

No Go-Live approval is implied by this evidence.
