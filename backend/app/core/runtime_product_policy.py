"""Runtime policy derived from the canonical BCSentinel product model.

The policy keeps legacy access flags as a compatibility boundary while exposing
structured consistency diagnostics. Drift detection is observational only: it
must never grant or revoke customer rights by itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.product_model import (
    AccessState,
    CommercialOffer,
    Entitlement,
    ExperienceMode,
    OFFER_ENTITLEMENTS,
)

RUNTIME_POLICY_VERSION = "arch-02c-v1"


@dataclass(frozen=True)
class RuntimePolicyDrift:
    code: str
    legacy_granted: bool
    canonical_granted: bool

    def to_snapshot(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "legacy_granted": self.legacy_granted,
            "canonical_granted": self.canonical_granted,
        }


@dataclass(frozen=True)
class RuntimeProductPolicy:
    active_offers: tuple[CommercialOffer, ...]
    experience_mode: ExperienceMode
    entitlements: frozenset[Entitlement]
    access_state: AccessState

    def has_offer(self, offer: CommercialOffer) -> bool:
        return offer in self.active_offers

    def has_entitlement(self, entitlement: Entitlement) -> bool:
        return entitlement in self.entitlements

    def to_snapshot(self, drift: tuple[RuntimePolicyDrift, ...] = ()) -> dict[str, Any]:
        return {
            "commercial_offers": [offer.value for offer in self.active_offers],
            "experience_mode": self.experience_mode.value,
            "entitlements": sorted(entitlement.value for entitlement in self.entitlements),
            "access_state": self.access_state.value,
            "compatibility_source": "product_license_service",
            "runtime_policy": "canonical_with_legacy_guard",
            "runtime_policy_version": RUNTIME_POLICY_VERSION,
            "consistency_status": "drift_detected" if drift else "consistent",
            "drift_count": len(drift),
            "drift_issues": [item.to_snapshot() for item in drift],
        }


def build_runtime_product_policy(access: dict[str, Any]) -> RuntimeProductPolicy:
    """Build the canonical runtime policy from the compatibility snapshot."""

    active_offers: list[CommercialOffer] = []
    if bool(access.get("assessment_access_active") or access.get("full_analysis_access_active")):
        active_offers.append(CommercialOffer.ASSESSMENT)
    if bool(access.get("validation_access_active") or access.get("validation_check_access_active")):
        active_offers.append(CommercialOffer.VALIDATION)
    if bool(access.get("monitoring_active")):
        active_offers.append(CommercialOffer.MONITORING)

    entitlement_values: set[Entitlement] = set()
    for offer in active_offers:
        entitlement_values.update(OFFER_ENTITLEMENTS[offer])

    free_access = bool(access.get("free_access_permanent") or access.get("has_completed_data_health_score"))
    if CommercialOffer.MONITORING in active_offers:
        experience_mode = ExperienceMode.MONITORING
    elif CommercialOffer.VALIDATION in active_offers:
        experience_mode = ExperienceMode.VALIDATION_RESULT
    elif CommercialOffer.ASSESSMENT in active_offers:
        experience_mode = ExperienceMode.ASSESSMENT_RESULT
    elif free_access:
        experience_mode = ExperienceMode.FREE
    else:
        experience_mode = ExperienceMode.LOCKED_PREVIEW

    access_state = AccessState.ACTIVE if bool(access.get("can_view_dashboard")) else AccessState.LOCKED

    return RuntimeProductPolicy(
        active_offers=tuple(active_offers),
        experience_mode=experience_mode,
        entitlements=frozenset(entitlement_values),
        access_state=access_state,
    )


def detect_runtime_policy_drift(
    access: dict[str, Any],
    policy: RuntimeProductPolicy,
) -> tuple[RuntimePolicyDrift, ...]:
    """Return mismatches between canonical rights and legacy runtime flags.

    Free-result access is intentionally excluded because findings summary and the
    free report are established free capabilities rather than paid entitlements.
    """

    checks = (
        (
            "paid_product_access",
            bool(access.get("premium_active")),
            bool(policy.active_offers),
        ),
        (
            "paid_deep_scan_access",
            bool(access.get("can_run_deep_scan")),
            policy.has_entitlement(Entitlement.SCAN_CORE),
        ),
        (
            "paid_findings_full_access",
            bool(access.get("can_view_issue_details")),
            policy.has_entitlement(Entitlement.FINDINGS_FULL),
        ),
        (
            "paid_executive_report_access",
            bool(access.get("can_view_executive_report")),
            policy.has_entitlement(Entitlement.REPORT_EXECUTIVE),
        ),
        (
            "monitoring_schedule_access",
            bool(access.get("can_use_monitoring")),
            policy.has_entitlement(Entitlement.MONITORING_SCHEDULE),
        ),
        (
            "monitoring_subscription_state",
            bool(access.get("monitoring_active")),
            policy.has_offer(CommercialOffer.MONITORING),
        ),
    )

    return tuple(
        RuntimePolicyDrift(
            code=code,
            legacy_granted=legacy_granted,
            canonical_granted=canonical_granted,
        )
        for code, legacy_granted, canonical_granted in checks
        if legacy_granted != canonical_granted
    )
