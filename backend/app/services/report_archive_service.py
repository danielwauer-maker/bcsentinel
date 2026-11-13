"""BC-native Full report archival and short-lived browser access.

The permanent BC API token never reaches a browser. A single-use random
capability is atomically consumed and exchanged for a narrowly scoped bearer.
No customer OIDC identity is needed for this BC-initiated workflow.
"""
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.core.settings import settings
from app.models import Scan, ScanRunStatus, Tenant, TenantScanCredit
from app.report_archive_models import ReportAccessGrant, ReportArchive
from app.security.token import create_token, verify_token
from app.services.product_license_service import (
    PRODUCT_VALIDATION_CHECK,
    build_product_access_snapshot,
    is_original_free_scan,
)
from app.services.assessment_scope_service import get_latest_confirmed_scope
from app.services.full_report_render_service import build_full_render_vm
from app.services.executive_report_v2_service import build_executive_report
from app.services.tenant_access_service import enforce_tenant_is_active
from app.services.scan_company_service import canonical_company_id

REPORT_SCOPE = "report:full:read"
REPORT_TOKEN_TYPE = "bc_full_report_access"
CODE_TTL_SECONDS = 60
SESSION_TTL_MINUTES = 10


def _now() -> datetime:
    return datetime.now(timezone.utc)


def has_paid_full_access(db, tenant: Tenant) -> bool:
    access = build_product_access_snapshot(db, tenant)
    if settings.ACCESS_MODEL_V2_ENABLED:
        return bool(access["premium_active"])
    return bool(access["can_view_executive_report"] and (access["assessment_access_active"] or access["monitoring_active"]))


def require_report_company(tenant: Tenant, scan: Scan) -> str:
    try:
        company = canonical_company_id(scan.bc_company_id)
        registered = canonical_company_id(tenant.bc_company_id) if (
            settings.ACCESS_MODEL_V2_ENABLED or str(tenant.bc_company_id or "").strip()
        ) else None
    except ValueError:
        raise HTTPException(status_code=409, detail="SCAN_COMPANY_NOT_VERIFIED") from None
    if registered is not None and registered != company:
        raise HTTPException(status_code=404, detail="Report not found.")
    return company


def full_scan_blocker(db, tenant: Tenant, scan: Scan, *, require_baseline: bool = True) -> str | None:
    run = db.scalar(select(ScanRunStatus).where(
        ScanRunStatus.tenant_id == tenant.tenant_id, ScanRunStatus.run_id == scan.scan_id,
    ))
    validation = db.scalar(select(TenantScanCredit.id).where(
        TenantScanCredit.tenant_id == tenant.tenant_id,
        TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
        TenantScanCredit.status == "consumed",
        TenantScanCredit.consumed_scan_id == scan.scan_id,
    ))
    if validation is not None or (run is not None and run.scan_mode == "monitoring"):
        return "WRONG_REPORT_VARIANT"
    if require_baseline and (
        run is None or run.status not in {"completed", "completed_with_warnings"}
        or run.result_persisted_at_utc is None
    ):
        return "SCAN_NOT_COMPLETED"
    if require_baseline and not is_original_free_scan(db, tenant.tenant_id, scan.scan_id):
        return "FULL_BASELINE_NOT_VERIFIED"
    return None


def archive_full_report(db, tenant: Tenant, scan: Scan, company_id: str) -> ReportArchive:
    """First authorized access seals the real scan evidence, never demo data."""
    archive_query = select(ReportArchive).where(
        ReportArchive.tenant_id == tenant.tenant_id,
        ReportArchive.company_id == company_id,
        ReportArchive.scan_id == scan.scan_id,
        ReportArchive.variant == "full",
    )
    existing = db.scalar(archive_query)
    blocker = full_scan_blocker(db, tenant, scan, require_baseline=settings.ACCESS_MODEL_V2_ENABLED or existing is None)
    if blocker is not None:
        raise HTTPException(status_code=409, detail=blocker)
    if existing is not None:
        return existing
    scope = get_latest_confirmed_scope(db, scan.scan_id)
    if (scope is None or scope.tenant_id != tenant.tenant_id
            or scope.confirmed_at_utc is None or scope.included_modules_count < 1):
        raise HTTPException(status_code=409, detail="ASSESSMENT_SCOPE_NOT_CONFIRMED")
    try:
        raw = build_executive_report(db, tenant, scan.scan_id)
        vm = build_full_render_vm(db, tenant, scan)
    except HTTPException as exc:
        if exc.status_code != 409:
            raise
        raise HTTPException(status_code=409, detail="REPORT_ARCHIVE_UNAVAILABLE") from exc
    envelope = {
        "contract_version": "bcsentinel-render-bridge-v1",
        "source": "live",
        "status": "ready",
        "variant": "full",
        "tenant_id": tenant.tenant_id,
        "company_id": company_id,
        "scan_id": scan.scan_id,
        "language": raw.language,
        "currency": {
            "source_currency": "EUR",
            "company_lcy_code": "EUR",
            "report_currency": "EUR",
            "model_currency_provenance": "eur_model",
            "conversion_status": "not_required",
            "fx_snapshot_id": None,
        },
        "report": raw.model_dump(mode="json"),
        "render_vm": vm,
    }
    payload = json.dumps(envelope, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    result = ReportArchive(
        tenant_id=tenant.tenant_id, company_id=company_id,
        scan_id=scan.scan_id, variant="full",
        contract_version=envelope["contract_version"],
        payload_json=payload,
        sha256=hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        created_at_utc=_now(),
    )
    # A unique constraint prevents duplicate snapshots under concurrent requests.
    # Never modify an existing snapshot after creation.
    try:
        with db.begin_nested():
            db.add(result)
            db.flush()
    except IntegrityError:
        existing = db.scalar(archive_query)
        if existing is None:
            raise
        return existing
    return result


REPORT_VARIANT_SCOPES = {
    "full": REPORT_SCOPE,
    "validation": "report:validation:read",
    "monitoring": "report:monitoring:read",
}


def archive_variant_report(db, tenant: Tenant, scan: Scan, company_id: str, variant: str) -> ReportArchive:
    """V2 immutable evidence archive for non-Full report families."""
    if variant not in {"validation", "monitoring"} or not settings.ACCESS_MODEL_V2_ENABLED:
        raise HTTPException(status_code=404, detail="Report variant unavailable.")
    access = build_product_access_snapshot(db, tenant)
    if not access["premium_active"] or (variant == "monitoring" and not access["monitoring_active"]):
        raise HTTPException(status_code=402, detail="FULL_ACCESS_INACTIVE")
    existing = db.scalar(select(ReportArchive).where(
        ReportArchive.tenant_id == tenant.tenant_id,
        ReportArchive.company_id == company_id,
        ReportArchive.scan_id == scan.scan_id,
        ReportArchive.variant == variant,
    ))
    if existing is not None:
        return existing
    from app.services.validation_report_service import build_validation_report
    from app.services.monitoring_report_service import build_monitoring_report
    from app.models import Scan as ScanModel, ScanRunStatus
    # Only completed and persisted scans are admissible as report evidence.
    def completed_persisted(scan_id: str) -> bool:
        return db.scalar(select(ScanRunStatus.id).where(
            ScanRunStatus.tenant_id == tenant.tenant_id,
            ScanRunStatus.run_id == scan_id,
            ScanRunStatus.status.in_(["completed", "completed_with_warnings"]),
            ScanRunStatus.result_persisted_at_utc.is_not(None),
        ).limit(1)) is not None

    if not completed_persisted(scan.scan_id):
        raise HTTPException(status_code=409, detail="SCAN_NOT_COMPLETED")
    if variant == "validation":
        report = build_validation_report(db, tenant, scan.scan_id)
        referenced = [
            report.baseline_scan_id,
            report.validation_scan_id,
            report.initial_baseline_scan_id,
        ]
    else:
        report = build_monitoring_report(db, tenant, scan.scan_id)
        referenced = [
            report.baseline_scan_id, report.current_scan_id,
            *(point.scan_id for point in report.trend_points),
        ]
    # A historical scan from another company or currency must never be
    # silently mixed into a Validation/Monitoring report.
    for scan_id in set(filter(None, referenced)):
        if not completed_persisted(scan_id):
            raise HTTPException(status_code=409, detail="REPORT_ARCHIVE_UNAVAILABLE")
        historical = db.scalar(select(ScanModel).where(
            ScanModel.tenant_id == tenant.tenant_id,
            ScanModel.scan_id == scan_id,
        ))
        try:
            historical_company = canonical_company_id(historical.bc_company_id) if historical else None
        except ValueError:
            historical_company = None
        if historical_company != company_id or str(historical.lcy_code or "").upper() != "EUR":
            raise HTTPException(status_code=409, detail="REPORT_ARCHIVE_UNAVAILABLE")
    envelope = {
        "contract_version": "bcsentinel-render-bridge-v1",
        "source": "live", "status": "ready", "variant": variant,
        "tenant_id": tenant.tenant_id, "company_id": company_id,
        "scan_id": scan.scan_id, "language": report.language,
        "currency": {
            "source_currency": "EUR", "company_lcy_code": "EUR",
            "report_currency": "EUR", "model_currency_provenance": "eur_model",
            "conversion_status": "not_required", "fx_snapshot_id": None,
        },
        "report": report.model_dump(mode="json"),
        # Strict frontend adapters may deliberately reject raw evidence until
        # the corresponding validated render_vm is available.
        "render_vm": None,
    }
    payload = json.dumps(envelope, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    archive = ReportArchive(
        tenant_id=tenant.tenant_id, company_id=company_id,
        scan_id=scan.scan_id, variant=variant,
        contract_version=envelope["contract_version"],
        payload_json=payload,
        sha256=hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        created_at_utc=_now(),
    )
    db.add(archive)
    db.flush()
    return archive


def issue_variant_link(db, tenant: Tenant, scan: Scan, viewer_url: str, variant: str) -> str:
    if variant == "full":
        return issue_full_link(db, tenant, scan, viewer_url)
    enforce_tenant_is_active(db, tenant.tenant_id)
    if variant not in {"validation", "monitoring"} or not settings.ACCESS_MODEL_V2_ENABLED:
        raise HTTPException(status_code=404, detail="Report variant unavailable.")
    company_id = require_report_company(tenant, scan)
    if str(scan.lcy_code or "").upper() != "EUR":
        raise HTTPException(status_code=409, detail="SCAN_CURRENCY_NOT_VERIFIED")
    try:
        archive_variant_report(db, tenant, scan, company_id, variant)
    except HTTPException as exc:
        if exc.status_code != 409 or exc.detail in {"SCAN_NOT_COMPLETED", "REPORT_ARCHIVE_UNAVAILABLE"}:
            raise
        raise HTTPException(status_code=409, detail="REPORT_ARCHIVE_UNAVAILABLE") from exc
    raw_code = secrets.token_urlsafe(32)
    db.add(ReportAccessGrant(
        token_hash=hashlib.sha256(raw_code.encode()).hexdigest(),
        tenant_id=tenant.tenant_id, company_id=company_id,
        scan_id=scan.scan_id, variant=variant,
        created_at_utc=_now(),
        expires_at_utc=_now() + timedelta(seconds=CODE_TTL_SECONDS),
    ))
    db.commit()
    return f"{viewer_url}/report/live?{urlencode({'scanId': scan.scan_id, 'companyId': company_id, 'variant': variant, 'code': raw_code, 'lang': 'de'})}"


def issue_full_link(db, tenant: Tenant, scan: Scan, viewer_url: str) -> str:
    enforce_tenant_is_active(db, tenant.tenant_id)
    if not has_paid_full_access(db, tenant):
        raise HTTPException(status_code=402, detail="FULL_ACCESS_INACTIVE")
    company_id = require_report_company(tenant, scan)
    if scan.lcy_code != "EUR":
        raise HTTPException(status_code=409, detail="SCAN_CURRENCY_NOT_VERIFIED")
    archive_full_report(db, tenant, scan, company_id)
    raw_code = secrets.token_urlsafe(32)
    db.add(ReportAccessGrant(
        token_hash=hashlib.sha256(raw_code.encode()).hexdigest(),
        tenant_id=tenant.tenant_id, company_id=company_id,
        scan_id=scan.scan_id, variant="full",
        created_at_utc=_now(), expires_at_utc=_now() + timedelta(seconds=CODE_TTL_SECONDS),
    ))
    db.commit()
    # This one-use code is a sensitive capability. The viewer must strip it
    # immediately, before API fetches, and send Referrer-Policy: no-referrer.
    return f"{viewer_url}/report/live?{urlencode({'scanId': scan.scan_id, 'companyId': company_id, 'code': raw_code, 'lang': 'de'})}"


def redeem_code(db, raw_code: str) -> dict:
    if len(raw_code) < 32 or len(raw_code) > 256:
        raise HTTPException(status_code=403, detail="Invalid or expired report link.")
    hashed = hashlib.sha256(raw_code.encode()).hexdigest()
    now = _now()
    # Atomic compare-and-set ensures two concurrent exchanges cannot reuse a code.
    result = db.execute(
        update(ReportAccessGrant).where(
            ReportAccessGrant.token_hash == hashed,
            ReportAccessGrant.consumed_at_utc.is_(None),
            ReportAccessGrant.expires_at_utc > now,
        ).values(consumed_at_utc=now)
    )
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(status_code=403, detail="Invalid or expired report link.")
    grant = db.scalar(select(ReportAccessGrant).where(ReportAccessGrant.token_hash == hashed))
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == grant.tenant_id))
    if tenant is None:
        db.rollback()
        raise HTTPException(status_code=403, detail="Report access unavailable.")
    enforce_tenant_is_active(db, tenant.tenant_id)
    if not has_paid_full_access(db, tenant):
        db.rollback()
        raise HTTPException(status_code=403, detail="Premium report access expired.")
    archive = db.scalar(select(ReportArchive).where(
        ReportArchive.tenant_id == grant.tenant_id,
        ReportArchive.company_id == grant.company_id,
        ReportArchive.scan_id == grant.scan_id,
        ReportArchive.variant == grant.variant,
    ))
    if archive is None:
        db.rollback()
        raise HTTPException(status_code=403, detail="Report access unavailable.")
    if grant.variant not in REPORT_VARIANT_SCOPES or (
        grant.variant != "full" and not settings.ACCESS_MODEL_V2_ENABLED
    ):
        db.rollback()
        raise HTTPException(status_code=403, detail="Report variant unavailable.")
    access = build_product_access_snapshot(db, tenant)
    if grant.variant == "monitoring" and not access["monitoring_active"]:
        db.rollback()
        raise HTTPException(status_code=403, detail="Monitoring access expired.")
    session = create_token({
        "type": REPORT_TOKEN_TYPE, "scope": REPORT_VARIANT_SCOPES[grant.variant],
        "tenant_id": grant.tenant_id, "company_id": grant.company_id,
        "scan_id": grant.scan_id, "variant": grant.variant,
    }, expires_delta=timedelta(minutes=SESSION_TTL_MINUTES))
    db.commit()
    return {
        "access_token": session, "token_type": "bearer",
        "tenant_id": grant.tenant_id, "company_id": grant.company_id,
        "scan_id": grant.scan_id, "report_variant": grant.variant,
        "expires_at": (now + timedelta(minutes=SESSION_TTL_MINUTES)).isoformat(),
    }


def verify_scoped_session(authorization: str | None, *, scan_id: str, company_id: str, variant: str) -> str | None:
    scheme, sep, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not sep:
        return None
    payload = verify_token(token.strip())
    expected_scope = REPORT_VARIANT_SCOPES.get(variant)
    if not expected_scope or (variant != "full" and not settings.ACCESS_MODEL_V2_ENABLED):
        return None
    if not payload or payload.get("type") != REPORT_TOKEN_TYPE or payload.get("scope") != expected_scope:
        return None
    if payload.get("scan_id") != scan_id or payload.get("variant") != variant:
        return None
    try:
        if canonical_company_id(str(payload.get("company_id") or "")) != canonical_company_id(company_id):
            return None
    except ValueError:
        return None
    return str(payload.get("tenant_id") or "") or None
