# S02 Pricing & Checkout Truth Audit

Status: **AUDIT COMPLETE — MIGRATION CLOSURE STILL OPEN**

## Canonical commercial offers

The normative customer-facing model is:

- Free Entry — controlled entry, not a paid commercial offer;
- Assessment — one-time commercial offer;
- Validation — one-time follow-up commercial offer;
- Monitoring — recurring commercial offer with monthly/annual billing variants.

## Current storage/API compatibility codes

The Core intentionally keeps legacy/current storage codes for compatibility:

| Storage/API code | Canonical offer | Billing |
| --- | --- | --- |
| `data_health_score` | Free Entry / no paid offer | one-time entry |
| `full_analysis` | Assessment | one-time |
| `assessment` | Assessment legacy alias | one-time |
| `validation_check` | Validation | one-time |
| `monitoring_monthly` | Monitoring | monthly |
| `monitoring_annual` | Monitoring | annual |

The executable mapping lives in `backend/app/core/product_model.py` and is covered by product-model contract tests.

## Audit findings

1. The runtime compatibility mapping already prevents Assessment/Validation/Monitoring from being inferred only from display names.
2. Landing/checkout still exposes legacy storage codes such as `full_analysis` and `validation_check`. This is acceptable as an implementation compatibility layer, but not as the normative product vocabulary.
3. `config/pricing_canonical.json` still models `free` and `premium` as pricing plans. This remains a migration concern because `premium` is not a canonical commercial offer.
4. Public landing copy previously advertised future Business Central actions inside Monitoring. This has been removed from the current offer presentation.
5. Existing persisted customer rights must not be rewritten without an explicit compatibility/migration plan.

## Closure required for DRIFT-003

Before DRIFT-003 can be resolved:

- define migration/compatibility treatment for `premium` pricing configuration;
- bind checkout/API product codes to canonical offer IDs and entitlement sets;
- add migration tests proving no existing customer rights are lost;
- update Product System drift/evidence binding;
- perform final pricing/checkout runtime verification.

This audit completes the discovery/truth-audit portion of S02 but does not claim product-model migration closure.
