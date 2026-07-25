"""Canonical BCSentinel product-model contract.

This module separates commercial offers, experience modes, entitlements and
access states. Existing storage codes remain supported through aliases so the
alignment can be rolled out without changing active customer rights.
"""

from __future__ import annotations

from enum import StrEnum


class CommercialOffer(StrEnum):
    ASSESSMENT = "assessment"
    VALIDATION = "validation"
    MONITORING = "monitoring"


class BillingVariant(StrEnum):
    ONE_TIME = "one_time"
    MONTHLY = "monthly"
    ANNUAL = "annual"


class ExperienceMode(StrEnum):
    FREE = "free"
    ASSESSMENT_RESULT = "assessment_result"
    VALIDATION_RESULT = "validation_result"
    MONITORING = "monitoring"
    LOCKED_PREVIEW = "locked_preview"


class AccessState(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    LOCKED = "locked"


class Entitlement(StrEnum):
    SCAN_CORE = "scan.core"
    FINDINGS_SUMMARY = "findings.summary"
    FINDINGS_FULL = "findings.full"
    REPORT_EXECUTIVE = "report.executive"
    VALIDATION_RUN = "validation.run"
    MONITORING_SCHEDULE = "monitoring.schedule"
    MONITORING_HISTORY = "monitoring.history"
    EXCEPTIONS_MANAGE = "exceptions.manage"
    ANALYTICS_FULL = "analytics.full"
    TENANT_MULTI_ACCESS = "tenant.multi_access"


# Existing persistent/API codes. These remain stable during ARCH-02A.
STORAGE_DATA_HEALTH_SCORE = "data_health_score"
STORAGE_FULL_ANALYSIS = "full_analysis"
STORAGE_ASSESSMENT_LEGACY = "assessment"
STORAGE_VALIDATION_CHECK = "validation_check"
STORAGE_MONITORING_MONTHLY = "monitoring_monthly"
STORAGE_MONITORING_ANNUAL = "monitoring_annual"


STORAGE_TO_OFFER: dict[str, CommercialOffer | None] = {
    STORAGE_DATA_HEALTH_SCORE: None,
    STORAGE_FULL_ANALYSIS: CommercialOffer.ASSESSMENT,
    STORAGE_ASSESSMENT_LEGACY: CommercialOffer.ASSESSMENT,
    STORAGE_VALIDATION_CHECK: CommercialOffer.VALIDATION,
    STORAGE_MONITORING_MONTHLY: CommercialOffer.MONITORING,
    STORAGE_MONITORING_ANNUAL: CommercialOffer.MONITORING,
}

STORAGE_TO_BILLING_VARIANT: dict[str, BillingVariant] = {
    STORAGE_DATA_HEALTH_SCORE: BillingVariant.ONE_TIME,
    STORAGE_FULL_ANALYSIS: BillingVariant.ONE_TIME,
    STORAGE_ASSESSMENT_LEGACY: BillingVariant.ONE_TIME,
    STORAGE_VALIDATION_CHECK: BillingVariant.ONE_TIME,
    STORAGE_MONITORING_MONTHLY: BillingVariant.MONTHLY,
    STORAGE_MONITORING_ANNUAL: BillingVariant.ANNUAL,
}

OFFER_DISPLAY_NAMES: dict[CommercialOffer, str] = {
    CommercialOffer.ASSESSMENT: "BCSentinel Assessment",
    CommercialOffer.VALIDATION: "BCSentinel Validation",
    CommercialOffer.MONITORING: "BCSentinel Monitoring",
}

OFFER_ENTITLEMENTS: dict[CommercialOffer, frozenset[Entitlement]] = {
    CommercialOffer.ASSESSMENT: frozenset(
        {
            Entitlement.SCAN_CORE,
            Entitlement.FINDINGS_SUMMARY,
            Entitlement.FINDINGS_FULL,
            Entitlement.REPORT_EXECUTIVE,
        }
    ),
    CommercialOffer.VALIDATION: frozenset(
        {
            Entitlement.SCAN_CORE,
            Entitlement.FINDINGS_SUMMARY,
            Entitlement.FINDINGS_FULL,
            Entitlement.REPORT_EXECUTIVE,
            Entitlement.VALIDATION_RUN,
        }
    ),
    CommercialOffer.MONITORING: frozenset(
        {
            Entitlement.SCAN_CORE,
            Entitlement.FINDINGS_SUMMARY,
            Entitlement.FINDINGS_FULL,
            Entitlement.REPORT_EXECUTIVE,
            Entitlement.MONITORING_SCHEDULE,
            Entitlement.MONITORING_HISTORY,
            Entitlement.EXCEPTIONS_MANAGE,
            Entitlement.ANALYTICS_FULL,
        }
    ),
}


def canonical_offer_for_storage_code(value: str | None) -> CommercialOffer | None:
    """Resolve an existing storage/API code to the canonical commercial offer."""

    normalized = (value or "").strip().lower()
    return STORAGE_TO_OFFER.get(normalized)


def billing_variant_for_storage_code(value: str | None) -> BillingVariant | None:
    """Resolve billing cadence without changing the persisted product code."""

    normalized = (value or "").strip().lower()
    return STORAGE_TO_BILLING_VARIANT.get(normalized)


def entitlements_for_storage_code(value: str | None) -> frozenset[Entitlement]:
    """Return canonical entitlements for a legacy or current product code."""

    offer = canonical_offer_for_storage_code(value)
    return OFFER_ENTITLEMENTS.get(offer, frozenset()) if offer is not None else frozenset()
