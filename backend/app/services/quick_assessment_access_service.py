from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from app.models import Tenant, TenantProductEntitlement
from app.services.product_license_service import build_product_access_snapshot

PRODUCT_QUICK_ASSESSMENT = "quick_assessment"

QUICK_ASSESSMENT_FEATURES = {
    "quick_assessment",
    "quick_assessment_findings",
}


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _iso(value: datetime | None) -> str | None:
    normalized = _as_utc(value)
    if normalized is None:
        return None
    return normalized.isoformat().replace("+00:00", "Z")


def _active_quick_entitlements(db, tenant_id: str) -> list[TenantProductEntitlement]:
    now = datetime.now(timezone.utc)
    rows = db.scalars(
        select(TenantProductEntitlement).where(
            TenantProductEntitlement.tenant_id == tenant_id,
            TenantProductEntitlement.product_code == PRODUCT_QUICK_ASSESSMENT,
            TenantProductEntitlement.status == "active",
        )
    ).all()
    return [
        row
        for row in rows
        if row.valid_until_utc is None or (_as_utc(row.valid_until_utc) or now) >= now
    ]


def build_quick_assessment_access_snapshot(db, tenant: Tenant) -> dict[str, Any]:
    """Resolve the Quick Assessment layer without granting Full Assessment rights.

    A dedicated Quick Assessment entitlement exposes only Quick-specific capability
    flags. Higher product tiers imply the ability to consume Quick-level views, but
    Quick itself never grants deep-scan credits, full issue detail, executive-report
    access, dashboard detail or recommendations.
    """
    quick_entitlements = _active_quick_entitlements(db, tenant.tenant_id)
    quick_entitlement_active = bool(quick_entitlements)

    finite_until_values = [
        _as_utc(row.valid_until_utc)
        for row in quick_entitlements
        if row.valid_until_utc is not None
    ]
    quick_access_until = max(finite_until_values) if finite_until_values else None

    full_access = build_product_access_snapshot(db, tenant)
    higher_tier_active = bool(
        full_access["assessment_access_active"]
        or full_access["validation_access_active"]
        or full_access["monitoring_active"]
    )
    effective_access = quick_entitlement_active or higher_tier_active

    return {
        "quick_assessment_entitlement_active": quick_entitlement_active,
        "quick_assessment_access_active": effective_access,
        "quick_assessment_access_until": _iso(quick_access_until),
        "can_view_quick_assessment": effective_access,
        "can_view_quick_findings": effective_access,
    }


def resolve_quick_assessment_features(db, tenant: Tenant) -> set[str]:
    access = build_quick_assessment_access_snapshot(db, tenant)
    if not access["can_view_quick_assessment"]:
        return set()
    return set(QUICK_ASSESSMENT_FEATURES)
