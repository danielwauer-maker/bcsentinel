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

No migration or customer-access change is introduced by the current contract.

## Implemented

- `backend/app/core/product_model.py` defines canonical vocabulary, mappings and entitlements.
- `backend/app/services/access_control_service.py` exposes an additive `product_model` section.
- the authoritative snapshot version is `p0d-v2-product-model`.
- existing capability names and legacy access fields remain unchanged.
- tests cover contract mapping, license/storage compatibility, product context, TTL and legacy API behavior.
- `.github/workflows/arch-02a-compatibility.yml` runs the compatibility gate for relevant pull requests.

## Verified compatibility gate

The GitHub Actions run for ARCH-02A completed successfully.

Successful test groups:

- Product model contract;
- License and storage compatibility;
- Access snapshot product context;
- TTL and legacy API regression.

The tests use an explicit isolated test environment and do not require a product-data migration or production database.

## Confirmed current drift

- `product_license_service.py` still acts as the runtime and storage compatibility layer.
- Display copy still exposes `Full Analysis` and historical `Premium` vocabulary in several surfaces.
- Feature sets still contain legacy string flags alongside the new entitlement model.
- Access snapshots intentionally retain historical `premium_*` fields for compatibility.
- Monitoring cadence and commercial offer remain encoded in the existing storage code.

## Next controlled steps

1. Inventory product copy in Dashboard, Reports and BC Extension.
2. Classify `Premium`, `Full Analysis` and similar terms as compatibility, marketing or obsolete copy.
3. Replace only approved UI copy with Assessment, Validation and Monitoring terminology.
4. Keep existing storage/API fields until consumers are migrated and regression-tested.
5. Run broader backend regression and complete PR review.

## Safety rules

- No destructive migration.
- No change to active customer rights.
- No Stripe price remapping in this phase.
- No removal of legacy API fields before all consumers are migrated.
- All new access decisions fail closed.
