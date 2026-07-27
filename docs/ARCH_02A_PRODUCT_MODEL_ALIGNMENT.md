# ARCH-02A Product Model Alignment

Status: Review Ready  
Base branch: `staging`  
Working branch: `arch-02a-product-model-alignment`

## Goal

Align the Core Product with the canonical Product System model without changing existing customer rights, persisted product codes, Stripe references or access windows.

## Canonical separation

- Commercial offers: Assessment, Validation, Monitoring
- Billing variants: one-time, monthly, annual
- Experience modes: free, assessment, validation, monitoring, locked
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
- customer-facing copy uses Assessment, Validation and Monitoring.
- technical compatibility identifiers such as `full_analysis` remain stable.
- Dashboard, Executive Report, Landingpage and BC Setup copy are contract-tested.
- BC Extension compile, CodeCop and PTECop are executed in GitHub Actions.
- `.app` and warning diagnostics are published as workflow artifacts.

## Final verification

### ARCH-02A Compatibility Gate — Run 61

- Product model contract: PASS
- License and storage compatibility: PASS
- Access snapshot product context: PASS
- TTL and legacy API regression: PASS
- Dashboard, BC, report and landing product copy contract: PASS
- Full backend regression: PASS

### BC AL Compile and Cop Gate — Run 12

- Business Central 27 AL compile: PASS
- CodeCop: PASS
- PTECop: PASS
- `.app` artifact: PASS
- warning diagnostics artifact: PASS
- detected AL, CodeCop and PTECop warnings: 0

The tests use an explicit isolated test environment and do not require a product-data migration or production database.

## Intentional compatibility debt

- `product_license_service.py` remains the runtime and storage compatibility layer.
- access snapshots intentionally retain historical `premium_*` fields.
- monitoring cadence remains encoded in the existing storage code.
- legacy translation keys and technical action names remain until all consumers are migrated.

These items are deliberate compatibility boundaries, not unresolved defects in ARCH-02A.

## Safety rules

- No destructive migration.
- No change to active customer rights.
- No Stripe price remapping in this phase.
- No removal of legacy API fields before all consumers are migrated.
- All new access decisions fail closed.
- Merge to `staging` only after explicit approval.
