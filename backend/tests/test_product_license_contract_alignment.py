from app.core.product_model import (
    BillingVariant,
    CommercialOffer,
    STORAGE_ASSESSMENT_LEGACY,
    STORAGE_DATA_HEALTH_SCORE,
    STORAGE_FULL_ANALYSIS,
    STORAGE_MONITORING_ANNUAL,
    STORAGE_MONITORING_MONTHLY,
    STORAGE_VALIDATION_CHECK,
    billing_variant_for_storage_code,
    canonical_offer_for_storage_code,
)
from app.services import product_license_service


def test_license_service_constants_match_product_model_storage_codes() -> None:
    assert product_license_service.PRODUCT_DATA_HEALTH_SCORE == STORAGE_DATA_HEALTH_SCORE
    assert product_license_service.PRODUCT_FULL_ANALYSIS == STORAGE_FULL_ANALYSIS
    assert product_license_service.PRODUCT_ASSESSMENT_LEGACY == STORAGE_ASSESSMENT_LEGACY
    assert product_license_service.PRODUCT_VALIDATION_CHECK == STORAGE_VALIDATION_CHECK
    assert product_license_service.PRODUCT_MONITORING_MONTHLY == STORAGE_MONITORING_MONTHLY
    assert product_license_service.PRODUCT_MONITORING_ANNUAL == STORAGE_MONITORING_ANNUAL


def test_license_service_normalization_preserves_existing_storage_contract() -> None:
    assert product_license_service.normalize_product_code("assessment") == STORAGE_FULL_ANALYSIS
    assert product_license_service.normalize_product_code("full_analysis") == STORAGE_FULL_ANALYSIS
    assert product_license_service.normalize_product_code("validation_check") == STORAGE_VALIDATION_CHECK
    assert product_license_service.normalize_product_code("monitoring_monthly") == STORAGE_MONITORING_MONTHLY
    assert product_license_service.normalize_product_code("monitoring_annual") == STORAGE_MONITORING_ANNUAL


def test_legacy_storage_codes_resolve_to_canonical_offers() -> None:
    assert canonical_offer_for_storage_code(product_license_service.PRODUCT_FULL_ANALYSIS) is CommercialOffer.ASSESSMENT
    assert canonical_offer_for_storage_code(product_license_service.PRODUCT_ASSESSMENT_LEGACY) is CommercialOffer.ASSESSMENT
    assert canonical_offer_for_storage_code(product_license_service.PRODUCT_VALIDATION_CHECK) is CommercialOffer.VALIDATION
    assert canonical_offer_for_storage_code(product_license_service.PRODUCT_MONITORING_MONTHLY) is CommercialOffer.MONITORING
    assert canonical_offer_for_storage_code(product_license_service.PRODUCT_MONITORING_ANNUAL) is CommercialOffer.MONITORING


def test_monitoring_billing_variants_remain_distinct() -> None:
    assert billing_variant_for_storage_code(product_license_service.PRODUCT_MONITORING_MONTHLY) is BillingVariant.MONTHLY
    assert billing_variant_for_storage_code(product_license_service.PRODUCT_MONITORING_ANNUAL) is BillingVariant.ANNUAL
