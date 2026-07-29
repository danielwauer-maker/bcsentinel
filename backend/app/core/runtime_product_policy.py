"""Runtime policy derived from the canonical BCSentinel product model.

The policy intentionally keeps legacy access flags as a compatibility boundary.
Canonical offers and entitlements become an additional prerequisite for paid
runtime capabilities, so this adoption step cannot grant broader access than
before.
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

    def to_snapshot(self) -> dict[str, Any]:
        return {
            "commercial_offers": [offer.value for offer in self.active_offers],
            "experience_mode": self.experience_mode.value,
            "entitlements": sorted(entitlement.value for entitlement in self.entitlements),
            "access_state": self.access_state.value,
            "compatibility_source": "product_license_service",
            "runtime_policy": "canonical_with_legacy_guard",
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
