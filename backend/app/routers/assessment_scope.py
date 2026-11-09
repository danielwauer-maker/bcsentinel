from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db import SessionLocal
from app.models import Scan, Tenant
from app.routers.membership_admin import _tenant_user_principal
from app.security.tenant import load_authenticated_tenant
from app.services.assessment_scope_service import confirm_scope, get_latest_scope, get_or_create_auto_scope, serialize_scope
from app.services.entitlement_guard_service import get_tenant_features

router = APIRouter(prefix="/scans", tags=["assessment-scope"])


class ConfirmScopeRequest(BaseModel):
    decisions: dict[str, str] = Field(default_factory=dict)


def _load_scan(db, scan_id: str, tenant_id: str) -> Scan:
    scan = db.scalar(select(Scan).where(Scan.scan_id == scan_id))
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found.")
    if scan.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Scan does not belong to authenticated tenant.")
    return scan


def _resolve_tenant(
    db,
    *,
    authorization: str | None,
    tenant_id_header: str | None,
    api_token_header: str | None,
) -> Tenant:
    if authorization:
        _, tenant_id, _ = _tenant_user_principal(authorization)
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
        if tenant is None:
            raise HTTPException(status_code=404, detail="Tenant not found.")
        return tenant

    if tenant_id_header and api_token_header:
        return load_authenticated_tenant(db, tenant_id_header, api_token_header)

    raise HTTPException(status_code=401, detail="Tenant authentication required.")


def _has_full_assessment(db, tenant: Tenant) -> bool:
    # Channel-neutral feature resolution: direct purchase, Fiverr/operator grant
    # and compatible paid access all expose the same Full Assessment capability.
    return "executive_report" in get_tenant_features(db, tenant)


@router.get("/{scan_id}/report-preflight")
def report_preflight(
    scan_id: str,
    authorization: str | None = Header(default=None, alias="Authorization"),
    tenant_id_header: str | None = Header(default=None, alias="X-Tenant-Id"),
    api_token_header: str | None = Header(default=None, alias="X-Api-Token"),
) -> dict:
    """Read-only evidence checklist. Does not create scopes, archives or grants.

    A successful preflight does NOT imply report rendering succeeded. The
    report endpoint remains the final authority for entitlement and integrity.
    """
    from app.core.settings import settings
    from app.models import TenantScanCredit
    from app.services.assessment_scope_service import get_latest_confirmed_scope
    from app.services.product_license_service import (
        PRODUCT_VALIDATION_CHECK, build_product_access_snapshot,
    )
    from app.services.validation_comparison_v2_service import choose_validation_references
    with SessionLocal() as db:
        tenant = _resolve_tenant(
            db, authorization=authorization,
            tenant_id_header=tenant_id_header,
            api_token_header=api_token_header,
        )
        scan = _load_scan(db, scan_id, tenant.tenant_id)
        access = build_product_access_snapshot(db, tenant)
        latest_scope = get_latest_scope(db, scan_id)
        confirmed = get_latest_confirmed_scope(db, scan_id)
        validation_credit = db.scalar(select(TenantScanCredit.id).where(
            TenantScanCredit.tenant_id == tenant.tenant_id,
            TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
            TenantScanCredit.status == "consumed",
            TenantScanCredit.consumed_scan_id == scan_id,
        ).limit(1))
        missing: list[str] = []
        if not scan.bc_company_id:
            missing.append("verified_company_missing")
        if str(scan.lcy_code or "").upper() != "EUR":
            missing.append("verified_eur_currency_missing")
        if latest_scope is None:
            missing.append("scope_snapshot_missing")
        if confirmed is None:
            missing.append("confirmed_scope_missing")
        if validation_credit is not None and not settings.ACCESS_MODEL_V2_ENABLED:
            missing.append("full_report_not_valid_for_validation_scan")
        if not access["premium_active"]:
            missing.append("premium_access_inactive")

        comparison = None
        if settings.ACCESS_MODEL_V2_ENABLED and latest_scope is not None:
            try:
                references = choose_validation_references(db, tenant, scan)
                comparison = {
                    "previous_scan_id": references.previous.scan_id,
                    "initial_baseline_scan_id": references.initial.scan_id,
                    "initial_baseline_scope_version": references.scope_version,
                }
            except HTTPException:
                # No automatic confirmation or guessed baseline: detailed
                # validation diagnostics belong to the report workflow.
                comparison = None

        return {
            "scan_id": scan_id,
            "preflight_only": True,
            "premium_active": bool(access["premium_active"]),
            "scope_state": latest_scope.state if latest_scope is not None else "missing",
            "confirmed_scope_version": confirmed.version if confirmed is not None else None,
            "company_bound": bool(scan.bc_company_id),
            "eur_currency_verified": str(scan.lcy_code or "").upper() == "EUR",
            "is_validation_credit_scan": validation_credit is not None,
            "missing_prerequisites": missing,
            "validation_comparison": comparison,
        }


@router.get("/{scan_id}/assessment-scope")
def assessment_scope(
    scan_id: str,
    authorization: str | None = Header(default=None, alias="Authorization"),
    tenant_id_header: str | None = Header(default=None, alias="X-Tenant-Id"),
    api_token_header: str | None = Header(default=None, alias="X-Api-Token"),
) -> dict:
    with SessionLocal() as db:
        tenant = _resolve_tenant(
            db,
            authorization=authorization,
            tenant_id_header=tenant_id_header,
            api_token_header=api_token_header,
        )
        scan = _load_scan(db, scan_id, tenant.tenant_id)
        scope = get_latest_scope(db, scan_id) or get_or_create_auto_scope(db, scan)
        # Free/Quick may consume the scope summary but never receive module-level
        # edit data. Full Assessment receives the module list for confirmation.
        return serialize_scope(scope, include_modules=_has_full_assessment(db, tenant))


@router.post("/{scan_id}/assessment-scope/confirm")
def confirm_assessment_scope(
    scan_id: str,
    payload: ConfirmScopeRequest,
    authorization: str | None = Header(default=None, alias="Authorization"),
    tenant_id_header: str | None = Header(default=None, alias="X-Tenant-Id"),
    api_token_header: str | None = Header(default=None, alias="X-Api-Token"),
) -> dict:
    with SessionLocal() as db:
        tenant = _resolve_tenant(
            db,
            authorization=authorization,
            tenant_id_header=tenant_id_header,
            api_token_header=api_token_header,
        )
        if not _has_full_assessment(db, tenant):
            raise HTTPException(status_code=403, detail="Scope confirmation requires an active Full Assessment.")
        scan = _load_scan(db, scan_id, tenant.tenant_id)
        from app.core.settings import settings
        if settings.ACCESS_MODEL_V2_ENABLED:
            # The original completed Free scan is the Full Assessment baseline.
            # Validation/Monitoring scans must not be relabelled as baselines.
            from app.services.product_license_service import is_original_free_scan
            from app.services.assessment_scope_service import get_latest_confirmed_scope
            if not is_original_free_scan(db, tenant.tenant_id, scan.scan_id):
                raise HTTPException(
                    status_code=409,
                    detail="Only the original completed Free scan can establish the Full baseline.",
                )
            if not scan.bc_company_id or str(scan.lcy_code or "").upper() != "EUR":
                raise HTTPException(
                    status_code=409,
                    detail="Full baseline requires verified BC company and EUR local currency.",
                )
            confirmed = get_latest_confirmed_scope(db, scan.scan_id)
            if confirmed is not None:
                # Do not allow later re-confirmations to rewrite the original
                # historical baseline used by Validation comparisons.
                if payload.decisions:
                    raise HTTPException(
                        status_code=409,
                        detail="Full Assessment baseline is already confirmed and immutable.",
                    )
                return serialize_scope(confirmed, include_modules=True)
        scope = confirm_scope(db, scan, payload.decisions)
        return serialize_scope(scope, include_modules=True)
