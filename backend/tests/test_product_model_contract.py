from app.core.product_model import (
    BillingVariant,
    CommercialOffer,
    Entitlement,
    billing_variant_for_storage_code,
    canonical_offer_for_storage_code,
    entitlements_for_storage_code,
    product_contract_for_storage_code,
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


def test_storage_codes_expose_canonical_contract_metadata() -> None:
    assessment = product_contract_for_storage_code("full_analysis")
    assessment_legacy = product_contract_for_storage_code("assessment")
    validation = product_contract_for_storage_code("validation_check")
    monitoring_monthly = product_contract_for_storage_code("monitoring_monthly")
    monitoring_annual = product_contract_for_storage_code("monitoring_annual")
    free = product_contract_for_storage_code("data_health_score")

    assert assessment["commercial_offer_id"] == "assessment"
    assert assessment_legacy["commercial_offer_id"] == "assessment"
    assert assessment["experience_mode"] == "assessment"
    assert "report.executive" in assessment["entitlement_ids"]

    assert validation["commercial_offer_id"] == "validation"
    assert validation["billing_variant"] == "one_time"
    assert "validation.run" in validation["entitlement_ids"]

    assert monitoring_monthly["commercial_offer_id"] == "monitoring"
    assert monitoring_monthly["billing_variant"] == "monthly"
    assert monitoring_annual["commercial_offer_id"] == "monitoring"
    assert monitoring_annual["billing_variant"] == "annual"
    assert monitoring_monthly["entitlement_ids"] == monitoring_annual["entitlement_ids"]

    assert free["commercial_offer_id"] is None
    assert free["experience_mode"] == "free"
    assert free["entitlement_ids"] == []


def test_premium_is_not_a_canonical_offer() -> None:
    premium = product_contract_for_storage_code("premium")
    assert premium["commercial_offer_id"] is None
    assert premium["entitlement_ids"] == []
    assert premium["experience_mode"] == "locked"
    assert premium["access_state"] == "locked"
