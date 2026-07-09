from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from app.db import SessionLocal
from app.security.tenant import load_authenticated_tenant, require_tenant_headers
from app.services.billing_service import resolve_effective_license
from app.services.entitlement_service import resolve_features
from app.services.entitlement_guard_service import get_tenant_features
from app.services.localization_service import update_tenant_language
from app.services.product_license_service import build_license_snapshot

router = APIRouter(tags=["license"])


class LicenseStatusResponse(BaseModel):
    tenant_id: str
    plan: str
    license_status: str
    legacy_plan: str | None = None
    legacy_license_status: str | None = None
    features: list[str]
    active_products: list[str] = []
    scan_credits_available: int = 0
    monitoring_active: bool = False
    product_access: dict = {}
    assessment_access_active: bool = False
    full_analysis_access_active: bool = False
    validation_access_active: bool = False
    validation_check_access_active: bool = False
    dashboard_access_until: str | None = None
    dashboard_access_until_bc: str | None = None
    issue_access_until: str | None = None
    issue_access_until_bc: str | None = None
    premium_access_until: str | None = None
    premium_access_until_bc: str | None = None
    product_access_until: str | None = None
    subscription_end: str | None = None
    subscription_end_bc: str | None = None
    subscription_end_utc: str | None = None
    monitoring_access_until: str | None = None
    monitoring_access_until_bc: str | None = None
    monitoring_period_end: str | None = None
    monitoring_period_end_bc: str | None = None
    can_run_deep_scan: bool = False
    can_run_data_health_score: bool = False
    has_completed_data_health_score: bool = False
    can_view_dashboard: bool = False
    can_view_issue_details: bool = False
    can_view_free_insights: bool = False
    can_view_issues: bool = False
    can_view_actions: bool = False
    can_view_reports: bool = False
    can_view_record_details: bool = False
    can_use_monitoring: bool = False
    record_count: int | None = None
    pricing_tier: str | None = None
    products: list[dict] = []


@router.get("/license/status", response_model=LicenseStatusResponse)
def get_license_status(
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
    x_preferred_language: str | None = Header(default=None, alias="X-Preferred-Language"),
) -> LicenseStatusResponse:
    header_tenant_id, header_api_token = tenant_auth

    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, header_tenant_id, header_api_token)
        if update_tenant_language(tenant, x_preferred_language):
            db.flush()
        features = sorted(get_tenant_features(db, tenant))
        snapshot = build_license_snapshot(db, tenant)
        normalized_plan, normalized_license_status = resolve_effective_license(db, tenant)
        if (
            normalized_plan == "premium"
            and not snapshot["monitoring_active"]
            and not snapshot["full_analysis_access_active"]
            and not snapshot["validation_check_access_active"]
        ):
            normalized_plan = "free"
            normalized_license_status = "expired"

        response = LicenseStatusResponse(
            tenant_id=tenant.tenant_id,
            plan=normalized_plan,
            license_status=normalized_license_status,
            legacy_plan=normalized_plan,
            legacy_license_status=normalized_license_status,
            features=features,
            active_products=snapshot["active_products"],
            scan_credits_available=snapshot["scan_credits_available"],
            monitoring_active=snapshot["monitoring_active"],
            product_access=snapshot["product_access"],
            assessment_access_active=snapshot["assessment_access_active"],
            full_analysis_access_active=snapshot["full_analysis_access_active"],
            validation_access_active=snapshot["validation_access_active"],
            validation_check_access_active=snapshot["validation_check_access_active"],
            dashboard_access_until=snapshot["dashboard_access_until"],
            dashboard_access_until_bc=snapshot["dashboard_access_until_bc"],
            issue_access_until=snapshot["issue_access_until"],
            issue_access_until_bc=snapshot["issue_access_until_bc"],
            premium_access_until=snapshot["premium_access_until"],
            premium_access_until_bc=snapshot["premium_access_until_bc"],
            product_access_until=snapshot["product_access_until"],
            subscription_end=snapshot["subscription_end"],
            subscription_end_bc=snapshot["subscription_end_bc"],
            subscription_end_utc=snapshot["subscription_end_utc"],
            monitoring_access_until=snapshot["monitoring_access_until"],
            monitoring_access_until_bc=snapshot["monitoring_access_until_bc"],
            monitoring_period_end=snapshot["monitoring_period_end"],
            monitoring_period_end_bc=snapshot["monitoring_period_end_bc"],
            can_run_deep_scan=snapshot["can_run_deep_scan"],
            can_run_data_health_score=snapshot["can_run_data_health_score"],
            has_completed_data_health_score=snapshot["has_completed_data_health_score"],
            can_view_dashboard=snapshot["can_view_dashboard"],
            can_view_issue_details=snapshot["can_view_issue_details"],
            can_view_free_insights=snapshot["can_view_free_insights"],
            can_view_issues=snapshot["can_view_issues"],
            can_view_actions=snapshot["can_view_actions"],
            can_view_reports=snapshot["can_view_reports"],
            can_view_record_details=snapshot["can_view_record_details"],
            can_use_monitoring=snapshot["can_use_monitoring"],
            record_count=snapshot["record_count"],
            pricing_tier=snapshot["pricing_tier"],
            products=snapshot["products"],
        )
        db.commit()
        return response
