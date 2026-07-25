from app.core.product_model import (
    BillingVariant,
    CommercialOffer,
    Entitlement,
    billing_variant_for_storage_code,
    canonical_offer_for_storage_code,
    entitlements_for_storage_code,
)


def test_assessment_storage_aliases_resolve_to_same_offer() -> None:
    assert canonical_offer_for_storage_code("assessment") is CommercialOffer.ASSESSMENT
    assert canonical_offer_for_storage_code("full_analysis") is CommercialOffer.ASSESSMENT


def test_monitoring_variants_share_offer_but_keep_billing_cadence() -> None:
    assert canonical_offer_for_storage_code("monitoring_monthly") is CommercialOffer.MONITORING
    assert canonical_offer_for_storage_code("monitoring_annual") is CommercialOffer.MONITORING
    assert billing_variant_for_storage_code("monitoring_monthly") is BillingVariant.MONTHLY
    assert billing_variant_for_storage_code("monitoring_annual") is BillingVariant.ANNUAL


def test_validation_maps_to_canonical_offer_and_entitlement() -> None:
    assert canonical_offer_for_storage_code("validation_check") is CommercialOffer.VALIDATION
    assert Entitlement.VALIDATION_RUN in entitlements_for_storage_code("validation_check")


def test_monitoring_entitlements_are_explicit() -> None:
    entitlements = entitlements_for_storage_code("monitoring_monthly")
    assert Entitlement.MONITORING_SCHEDULE in entitlements
    assert Entitlement.MONITORING_HISTORY in entitlements
    assert Entitlement.ANALYTICS_FULL in entitlements


def test_free_score_is_not_a_paid_commercial_offer() -> None:
    assert canonical_offer_for_storage_code("data_health_score") is None
    assert entitlements_for_storage_code("data_health_score") == frozenset()


def test_unknown_product_code_fails_closed() -> None:
    assert canonical_offer_for_storage_code("unknown") is None
    assert billing_variant_for_storage_code("unknown") is None
    assert entitlements_for_storage_code("unknown") == frozenset()
