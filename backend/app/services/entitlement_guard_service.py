from __future__ import annotations

from fastapi import HTTPException

from app.models import Tenant
from app.services.billing_service import resolve_effective_license
from app.services.entitlement_service import resolve_features
from app.services.product_license_service import build_product_access_snapshot, resolve_product_features


def get_tenant_features(db, tenant: Tenant) -> set[str]:
    plan, license_status = resolve_effective_license(db, tenant)
    access = build_product_access_snapshot(db, tenant)
    if (
        plan == "premium"
        and not access["monitoring_active"]
        and not access["full_analysis_access_active"]
        and not access["validation_check_access_active"]
    ):
        plan = "free"
        license_status = "expired"
    return set(resolve_features(plan, license_status)).union(resolve_product_features(db, tenant))


def require_tenant_feature(db, tenant: Tenant, feature: str) -> None:
    features = get_tenant_features(db, tenant)
    if feature not in features:
        raise HTTPException(status_code=403, detail=f"Feature '{feature}' is not available for this tenant.")
