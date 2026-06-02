from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.db import SessionLocal
from app.security.tenant import load_authenticated_tenant, require_tenant_headers
from app.services.billing_service import resolve_effective_license
from app.services.entitlement_service import resolve_features
from app.services.entitlement_guard_service import get_tenant_features
from app.services.product_license_service import build_license_snapshot

router = APIRouter(tags=["license"])


class LicenseStatusResponse(BaseModel):
    tenant_id: str
    plan: str
    license_status: str
    features: list[str]
    active_products: list[str] = []
    scan_credits_available: int = 0
    monitoring_active: bool = False
    products: list[dict] = []


@router.get("/license/status", response_model=LicenseStatusResponse)
def get_license_status(
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
) -> LicenseStatusResponse:
    header_tenant_id, header_api_token = tenant_auth

    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, header_tenant_id, header_api_token)
        normalized_plan, normalized_license_status = resolve_effective_license(db, tenant)
        features = sorted(get_tenant_features(db, tenant))
        snapshot = build_license_snapshot(db, tenant)

        return LicenseStatusResponse(
            tenant_id=tenant.tenant_id,
            plan=normalized_plan,
            license_status=normalized_license_status,
            features=features,
            active_products=snapshot["active_products"],
            scan_credits_available=snapshot["scan_credits_available"],
            monitoring_active=snapshot["monitoring_active"],
            products=snapshot["products"],
        )
