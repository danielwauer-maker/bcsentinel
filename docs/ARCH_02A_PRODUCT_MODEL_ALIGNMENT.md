# ARCH-02A Product Model Alignment

Status: In Progress  
Base branch: `staging`  
Working branch: `arch-02a-product-model-alignment`

## Goal

Align the Core Product with the canonical Product System model without changing existing customer rights, persisted product codes, Stripe references or access windows.

## Canonical separation

- Commercial offers: Assessment, Validation, Monitoring
- Billing variants: one-time, monthly, annual
- Experience modes: free, assessment result, validation result, monitoring, locked preview
- Entitlements: explicit capability identifiers
- Access states: active, inactive, expired, locked

## Compatibility boundary

Existing storage and API codes remain valid during ARCH-02A:

| Existing code | Canonical offer | Billing variant |
| --- | --- | --- |
| `data_health_score` | free entry, no paid offer | one-time |
| `full_analysis` | Assessment | one-time |
| `assessment` | Assessment legacy alias | one-time |
| `validation_check` | Validation | one-time |
| `monitoring_monthly` | Monitoring | monthly |
| `monitoring_annual` | Monitoring | annual |

No migration or customer-access change is introduced by the initial contract.

## Initial implementation

- `backend/app/core/product_model.py` defines the canonical vocabulary and compatibility mapping.
- `backend/tests/test_product_model_contract.py` verifies aliases, billing cadence, entitlements and fail-closed behavior.

## Confirmed current drift

- `product_license_service.py` treats `assessment` as a legacy alias of `full_analysis`.
- Display copy still exposes `Full Analysis` instead of the canonical Assessment offer.
- Feature sets are legacy string flags rather than canonical entitlement IDs.
- Access snapshots still expose historical `premium_*` fields and capability names.
- Monitoring cadence and commercial offer are encoded in the same product code.

## Planned implementation sequence

1. Make `product_license_service.py` consume the canonical mappings while preserving exported compatibility constants.
2. Add canonical offer, billing variant and entitlement fields to access snapshots additively.
3. Update dashboard/report copy without breaking stored data or API consumers.
4. Map BC Extension captions and access handling.
5. Add regression tests for checkout, credits, expiration and existing tenants.
6. Remove historical vocabulary only in a separately reviewed deprecation phase.

## Safety rules

- No destructive migration.
- No change to active customer rights.
- No Stripe price remapping in the first phase.
- No removal of legacy API fields before all consumers are migrated.
- All new access decisions fail closed.
