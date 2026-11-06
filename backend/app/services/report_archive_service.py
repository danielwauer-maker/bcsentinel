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
from app.models import Scan, Tenant
from app.report_archive_models import ReportAccessGrant, ReportArchive
from app.security.token import create_token, verify_token
from app.services.product_license_service import build_product_access_snapshot
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


def _has_paid_full_access(db, tenant: Tenant) -> bool:
    access = build_product_access_snapshot(db, tenant)
    return bool(access["can_view_executive_report"] and (
        access.get("assessment_access_active") or access.get("monitoring_active")
    ))


def archive_full_report(db, tenant: Tenant, scan: Scan) -> ReportArchive:
    """First authorized access seals the real scan evidence, never demo data."""
    existing = db.scalar(select(ReportArchive).where(
        ReportArchive.tenant_id == tenant.tenant_id,
        ReportArchive.company_id == scan.bc_company_id,
        ReportArchive.scan_id == scan.scan_id,
        ReportArchive.variant == "full",
    ))
    if existing is not None:
        return existing
    if not _has_paid_full_access(db, tenant):
        raise HTTPException(status_code=402, detail="Full Assessment entitlement required.")
    if scan.lcy_code != "EUR":
        raise HTTPException(status_code=409, detail="Only verified EUR scan evidence is supported.")
    raw = build_executive_report(db, tenant, scan.scan_id)
    vm = build_full_render_vm(db, tenant, scan)
    envelope = {
        "contract_version": "bcsentinel-render-bridge-v1",
        "source": "live",
        "status": "ready",
        "variant": "full",
        "tenant_id": tenant.tenant_id,
        "company_id": scan.bc_company_id,
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
        tenant_id=tenant.tenant_id, company_id=scan.bc_company_id,
        scan_id=scan.scan_id, variant="full",
        contract_version=envelope["contract_version"],
        payload_json=payload,
        sha256=hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        created_at_utc=_now(),
    )
    # A unique constraint prevents duplicate snapshots under concurrent requests.
    # Never modify an existing snapshot after creation.
    db.add(result)
    db.flush()
    return result


def issue_full_link(db, tenant: Tenant, scan: Scan, viewer_url: str) -> str:
    enforce_tenant_is_active(db, tenant.tenant_id)
    if not scan.bc_company_id or not scan.lcy_code:
        raise HTTPException(status_code=409, detail="Scan requires verified BC company and LCY.")
    scan.bc_company_id = canonical_company_id(scan.bc_company_id)
    archive_full_report(db, tenant, scan)
    raw_code = secrets.token_urlsafe(32)
    db.add(ReportAccessGrant(
        token_hash=hashlib.sha256(raw_code.encode()).hexdigest(),
        tenant_id=tenant.tenant_id, company_id=scan.bc_company_id,
        scan_id=scan.scan_id, variant="full",
        created_at_utc=_now(), expires_at_utc=_now() + timedelta(seconds=CODE_TTL_SECONDS),
    ))
    db.commit()
    # This one-use code is a sensitive capability. The viewer must strip it
    # immediately, before API fetches, and send Referrer-Policy: no-referrer.
    return f"{viewer_url}/report/live?{urlencode({'scanId': scan.scan_id, 'companyId': scan.bc_company_id, 'code': raw_code, 'lang': 'de'})}"


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
    archive = db.scalar(select(ReportArchive).where(
        ReportArchive.tenant_id == grant.tenant_id,
        ReportArchive.company_id == grant.company_id,
        ReportArchive.scan_id == grant.scan_id,
        ReportArchive.variant == grant.variant,
    ))
    if archive is None:
        db.rollback()
        raise HTTPException(status_code=403, detail="Report access unavailable.")
    session = create_token({
        "type": REPORT_TOKEN_TYPE, "scope": REPORT_SCOPE,
        "tenant_id": grant.tenant_id, "company_id": grant.company_id,
        "scan_id": grant.scan_id, "variant": "full",
    }, expires_delta=timedelta(minutes=SESSION_TTL_MINUTES))
    db.commit()
    return {
        "access_token": session, "token_type": "bearer",
        "tenant_id": grant.tenant_id, "company_id": grant.company_id,
        "scan_id": grant.scan_id, "report_variant": "full",
        "expires_at": (now + timedelta(minutes=SESSION_TTL_MINUTES)).isoformat(),
    }


def verify_scoped_session(authorization: str | None, *, scan_id: str, company_id: str, variant: str) -> str | None:
    scheme, sep, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not sep:
        return None
    payload = verify_token(token.strip())
    if not payload or payload.get("type") != REPORT_TOKEN_TYPE or payload.get("scope") != REPORT_SCOPE:
        return None
    if payload.get("scan_id") != scan_id or payload.get("variant") != variant:
        return None
    try:
        if canonical_company_id(str(payload.get("company_id") or "")) != canonical_company_id(company_id):
            return None
    except ValueError:
        return None
    return str(payload.get("tenant_id") or "") or None
