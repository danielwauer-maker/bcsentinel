# S02 Legacy Compatibility Closure

Status: **AUTOMATED COMPATIBILITY CLOSURE COMPLETE — FINAL CHECKOUT RUNTIME SMOKE MANUAL**

## Decision

BCSentinel does not destructively rewrite historic customer product codes merely to make storage names look canonical.

The canonical commercial model remains:

- Assessment
- Validation
- Monitoring

Existing storage/API codes remain a compatibility layer:

- `assessment` and `full_analysis` -> Assessment
- `validation_check` -> Validation
- `monitoring_monthly` / `monitoring_annual` -> Monitoring

The historic tenant plan value `premium` is **not** a canonical commercial offer and does not grant Monitoring by itself.

## Closure policy

DRIFT-003 is technically closed by compatibility rather than destructive migration:

1. persisted historic rights stay readable;
2. canonical offer identity is derived by explicit mapping;
3. new writes normalize to current storage codes;
4. legacy `premium` plan state alone grants no canonical entitlement;
5. checkout responses carry canonical offer/billing metadata;
6. contract tests protect all mappings and the no-rights-loss invariant.

A final real checkout/grant smoke remains a manual pilot gate because it requires the external payment/runtime environment.

## Evidence

- `backend/app/core/product_model.py`
- `backend/app/services/product_license_service.py`
- `config/pricing_canonical.json`
- `backend/tests/test_s02_legacy_compatibility_closure.py`
