"""Authenticated, company-scoped source of truth for the Lovable report renderer.

Never expose the Business Central API token to web clients. Existing report
builders remain authoritative for entitlement checks and data visibility.
"""
from __future__ import annotations

from typing import Literal

import hashlib
import json

from fastapi import APIRouter, Header, HTTPException, Query, Response
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db import SessionLocal
from app.models import Scan, Tenant
from app.routers.membership_admin import _tenant_user_principal
from app.services.free_health_report_service import build_free_health_report
from app.services.quick_assessment_access_service import build_quick_assessment_access_snapshot
from app.services.quick_assessment_report_service import build_quick_assessment_report
from app.services.executive_report_v2_service import build_executive_report
from app.services.product_license_service import build_product_access_snapshot
from app.services.validation_report_service import build_validation_report
from app.services.monitoring_report_service import build_monitoring_report
from app.services.tenant_access_service import enforce_tenant_is_active
from app.services.scan_company_service import canonical_company_id
from app.services.full_report_render_service import build_full_render_vm
from app.report_archive_models import ReportArchive
from app.services.report_archive_service import verify_scoped_session

router = APIRouter(prefix="/account/reports", tags=["reports"])
ReportVariant = Literal["free", "quick", "full", "validation", "monitoring"]
CONTRACT_VERSION = "bcsentinel-render-bridge-v1"


class ReportCurrencyContext(BaseModel):
    source_currency: str = "EUR"
    company_lcy_code: str
    report_currency: str
    model_currency_provenance: str = "eur_model"
    conversion_status: str = "not_required"
    fx_snapshot_id: str | None = None


class ReportRenderEnvelope(BaseModel):
    contract_version: str = CONTRACT_VERSION
    source: Literal["live"] = "live"
    status: Literal["ready"] = "ready"
    variant: ReportVariant
    tenant_id: str
    company_id: str
    scan_id: str
    language: str
    currency: ReportCurrencyContext
    report: dict
    render_vm: dict | None = None


def _require_company_scan(db, tenant_id: str, scan_id: str, company_id: str) -> Scan:
    # A scan must be explicitly bound at upload time to a BC Company GUID.
    # Legacy tenant-only scans MUST NOT be guessed into a company.
    scan = db.scalar(select(Scan).where(Scan.scan_id == scan_id, Scan.tenant_id == tenant_id))
    if scan is None:
        raise HTTPException(status_code=404, detail="Report not found.")
    if not scan.bc_company_id or not scan.lcy_code:
        raise HTTPException(status_code=409, detail="Scan has no verified BC company and local currency binding.")
    try:
        requested_company_id = canonical_company_id(company_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Report not found.") from None
    if scan.bc_company_id != requested_company_id:
        raise HTTPException(status_code=404, detail="Report not found.")
    return scan


def _assert_comparable_history(db, tenant_id: str, company_id: str, lcy_code: str, scan_ids: list[str]) -> None:
    for history_scan_id in set(scan_ids):
        if history_scan_id:
            previous = _require_company_scan(db, tenant_id, history_scan_id, company_id)
            if previous.lcy_code != lcy_code:
                raise HTTPException(status_code=409, detail="Report historical company currency is not comparable.")


def _build_authorized_report(db, tenant: Tenant, scan_id: str, variant: ReportVariant):
    if variant == "free":
        from app.services.product_license_service import is_original_free_scan
        if not is_original_free_scan(db, tenant.tenant_id, scan_id):
            raise HTTPException(status_code=404, detail="Free Report not found.")
        return build_free_health_report(db, tenant, scan_id)
    if variant == "quick":
        from app.core.settings import settings
        if not settings.QUICK_ASSESSMENT_ENABLED:
            raise HTTPException(status_code=404, detail="Quick Assessment is not available.")
        access = build_quick_assessment_access_snapshot(db, tenant)
        if not access["can_view_quick_assessment"]:
            raise HTTPException(status_code=402, detail="Quick Assessment access required.")
        return build_quick_assessment_report(db, tenant, scan_id)
    access = build_product_access_snapshot(db, tenant)
    if variant == "full":
        # Validation-only rights must never unlock the initial Full Assessment.
        if not access["premium_active"]:
            raise HTTPException(status_code=402, detail="Full Assessment access required.")
        return build_executive_report(db, tenant, scan_id)
    if variant == "validation":
        if not access["premium_active"]:
            raise HTTPException(status_code=402, detail="Premium access required for Validation report.")
        return build_validation_report(db, tenant, scan_id)
    if variant == "monitoring":
        if not access["monitoring_active"]:
            raise HTTPException(status_code=402, detail="Monitoring access required.")
        return build_monitoring_report(db, tenant, scan_id)
    raise HTTPException(status_code=404, detail="Unsupported report.")


@router.get("/{variant}/{scan_id}", response_model=ReportRenderEnvelope)
def read_report_for_renderer(
    variant: ReportVariant,
    scan_id: str,
    response: Response,
    company_id: str = Query(min_length=32, max_length=64),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> ReportRenderEnvelope:
    # The 15-minute tenant-user token is scoped to an ACTIVE membership and its
    # role/status binding. An account-level token and BC API token are rejected.
    if response is not None:
        response.headers["Cache-Control"] = "no-store, private"
        response.headers["Pragma"] = "no-cache"
    # A report-scoped bearer is accepted only for the exact Full scan/company
    # for which BC previously obtained a one-time grant. Other variants still
    # require the independent account membership authentication.
    scoped_tenant_id = verify_scoped_session(
        authorization, scan_id=scan_id, company_id=company_id, variant=variant
    ) if variant == "full" else None
    if scoped_tenant_id is None:
        _, tenant_id, _ = _tenant_user_principal(authorization)
    else:
        tenant_id = scoped_tenant_id

    with SessionLocal() as db:
        enforce_tenant_is_active(db, tenant_id)
        scan = _require_company_scan(db, tenant_id, scan_id, company_id)
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
        if tenant is None:
            raise HTTPException(status_code=404, detail="Report not found.")
        if scoped_tenant_id is not None:
            if not build_product_access_snapshot(db, tenant)["premium_active"]:
                raise HTTPException(status_code=403, detail="Premium report access expired.")
            archived = db.scalar(select(ReportArchive).where(
                ReportArchive.tenant_id == tenant_id,
                ReportArchive.company_id == scan.bc_company_id,
                ReportArchive.scan_id == scan_id,
                ReportArchive.variant == "full",
            ))
            if archived is None:
                raise HTTPException(status_code=404, detail="Report not found.")
            if hashlib.sha256(archived.payload_json.encode("utf-8")).hexdigest() != archived.sha256:
                raise HTTPException(status_code=409, detail="Report archive integrity check failed.")
            return ReportRenderEnvelope.model_validate(json.loads(archived.payload_json))

        # Existing financial models explicitly store EUR-derived estimates.
        # We refuse to relabel them as company LCY until an immutable,
        # verified conversion snapshot is available to every historic scan.
        if variant in ("full", "validation", "monitoring") and scan.lcy_code.upper() != "EUR":
            raise HTTPException(status_code=409, detail="Verified financial currency conversion unavailable.")

        report = _build_authorized_report(db, tenant, scan_id, variant)
        # Only Full currently has an evidenced v6 renderer projection. The
        # other report types retain their existing safe, raw stage contracts.
        render_vm = build_full_render_vm(db, tenant, scan) if variant == "full" else None
        if variant == "validation":
            _assert_comparable_history(
                db, tenant_id, company_id, scan.lcy_code,
                [report.baseline_scan_id, report.validation_scan_id],
            )
        if variant == "monitoring":
            _assert_comparable_history(
                db, tenant_id, company_id, scan.lcy_code,
                [point.scan_id for point in report.trend_points] + [report.baseline_scan_id, report.current_scan_id],
            )
        data = report.model_dump(mode="json")
        return ReportRenderEnvelope(
            variant=variant,
            tenant_id=tenant_id,
            company_id=scan.bc_company_id,
            scan_id=scan_id,
            language=report.language,
            currency=ReportCurrencyContext(
                company_lcy_code=scan.lcy_code.upper(),
                report_currency="EUR",
            ),
            report=data,
            render_vm=render_vm,
        )

