from __future__ import annotations

import json
import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from app.core.settings import settings
from app.db import SessionLocal
from app.lifecycle_models import LifecycleEmailOutbox, TenantLifecycleProfile
from app.models import Scan, Tenant, TenantProductEntitlement, TenantScanCredit
from app.operator_models import TenantOperatorAction
from app.security.csrf import CSRF_COOKIE_NAME, create_csrf_token, verify_csrf_token
from app.services.operator_commercial_service import (
    extend_assessment,
    grant_assessment,
    grant_validation,
    revoke_product,
)
from app.services.product_license_service import (
    PRODUCT_ASSESSMENT,
    PRODUCT_VALIDATION_CHECK,
    build_license_snapshot,
)

router = APIRouter(tags=["operator-admin"])
security = HTTPBasic()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


def require_operator(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    username_ok = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    password_ok = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def _check_csrf(request: Request, supplied: str) -> None:
    if not verify_csrf_token(settings.SECRET_KEY, request.cookies.get(CSRF_COOKIE_NAME), supplied):
        raise HTTPException(status_code=403, detail="Invalid CSRF token.")


def _redirect(message: str, *, error: bool = False) -> RedirectResponse:
    from urllib.parse import quote_plus

    key = "error" if error else "message"
    return RedirectResponse(url=f"/admin/operator?{key}={quote_plus(message)}", status_code=303)


def _operator_rows(db, query: str) -> list[dict]:
    tenants = db.scalars(select(Tenant).order_by(Tenant.created_at_utc.desc())).all()
    profiles = {row.tenant_id: row for row in db.scalars(select(TenantLifecycleProfile)).all()}
    actions = db.scalars(
        select(TenantOperatorAction).order_by(TenantOperatorAction.created_at_utc.desc())
    ).all()
    latest_action: dict[str, TenantOperatorAction] = {}
    order_refs: dict[str, list[str]] = {}
    for action in actions:
        latest_action.setdefault(action.tenant_id, action)
        if action.external_order_reference:
            order_refs.setdefault(action.tenant_id, []).append(action.external_order_reference)

    q = (query or "").strip().lower()
    rows: list[dict] = []
    for tenant in tenants:
        profile = profiles.get(tenant.tenant_id)
        searchable = " ".join(
            [
                tenant.tenant_id or "",
                tenant.environment_name or "",
                profile.primary_notification_email if profile else "",
                " ".join(order_refs.get(tenant.tenant_id, [])),
            ]
        ).lower()
        if q and q not in searchable:
            continue
        scan = db.scalar(
            select(Scan)
            .where(Scan.tenant_id == tenant.tenant_id)
            .order_by(Scan.generated_at_utc.desc(), Scan.id.desc())
            .limit(1)
        )
        snapshot = build_license_snapshot(db, tenant)
        rows.append(
            {
                "tenant_id": tenant.tenant_id,
                "environment_name": tenant.environment_name,
                "notification_email": profile.primary_notification_email if profile else "—",
                "preferred_language": profile.preferred_language.upper() if profile else "—",
                "latest_scan_id": scan.scan_id if scan else "—",
                "latest_scan_at": scan.generated_at_utc if scan else None,
                "assessment_active": snapshot["assessment_access_active"],
                "assessment_until": snapshot["product_access"].get("assessment_access_until"),
                "validation_active": snapshot["validation_access_active"],
                "validation_credits": db.query(TenantScanCredit).filter(
                    TenantScanCredit.tenant_id == tenant.tenant_id,
                    TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
                    TenantScanCredit.status == "available",
                ).count(),
                "latest_action": latest_action.get(tenant.tenant_id),
            }
        )
        if len(rows) >= 50:
            break
    return rows


@router.get("/admin/operator", response_class=HTMLResponse)
def operator_console(
    request: Request,
    q: str = Query(default=""),
    message: str = Query(default=""),
    error: str = Query(default=""),
    admin_username: str = Depends(require_operator),
):
    csrf_token = create_csrf_token(settings.SECRET_KEY)
    with SessionLocal() as db:
        rows = _operator_rows(db, q)
    response = templates.TemplateResponse(
        name="operator_console.html",
        context={
            "request": request,
            "rows": rows,
            "query": q,
            "message": message,
            "error": error,
            "csrf_token": csrf_token,
            "admin_username": admin_username,
        },
    )
    response.set_cookie(
        CSRF_COOKIE_NAME,
        csrf_token,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
    )
    return response


@router.post("/admin/operator/{tenant_id}/grant-assessment")
def operator_grant_assessment(
    request: Request,
    tenant_id: str,
    csrf_token: str = Form(...),
    sales_channel: str = Form("fiverr"),
    external_order_reference: str = Form(""),
    note: str = Form(""),
    admin_username: str = Depends(require_operator),
):
    _check_csrf(request, csrf_token)
    with SessionLocal() as db:
        try:
            result = grant_assessment(
                db,
                tenant_id=tenant_id,
                sales_channel=sales_channel,
                external_order_reference=external_order_reference,
                actor=admin_username,
                note=note,
            )
            db.commit()
            return _redirect(f"Assessment activated through {result['valid_until_utc']} for {tenant_id}.")
        except ValueError as exc:
            db.rollback()
            return _redirect(str(exc), error=True)


@router.post("/admin/operator/{tenant_id}/extend-assessment")
def operator_extend_assessment(
    request: Request,
    tenant_id: str,
    csrf_token: str = Form(...),
    sales_channel: str = Form("fiverr"),
    external_order_reference: str = Form(""),
    note: str = Form(""),
    admin_username: str = Depends(require_operator),
):
    _check_csrf(request, csrf_token)
    with SessionLocal() as db:
        try:
            result = extend_assessment(
                db,
                tenant_id=tenant_id,
                sales_channel=sales_channel,
                external_order_reference=external_order_reference,
                actor=admin_username,
                note=note,
            )
            db.commit()
            return _redirect(f"Assessment extended through {result['valid_until_utc']} for {tenant_id}.")
        except ValueError as exc:
            db.rollback()
            return _redirect(str(exc), error=True)


@router.post("/admin/operator/{tenant_id}/grant-validation")
def operator_grant_validation(
    request: Request,
    tenant_id: str,
    csrf_token: str = Form(...),
    sales_channel: str = Form("fiverr"),
    external_order_reference: str = Form(""),
    note: str = Form(""),
    admin_username: str = Depends(require_operator),
):
    _check_csrf(request, csrf_token)
    with SessionLocal() as db:
        try:
            result = grant_validation(
                db,
                tenant_id=tenant_id,
                sales_channel=sales_channel,
                external_order_reference=external_order_reference,
                actor=admin_username,
                note=note,
            )
            db.commit()
            return _redirect(f"Validation scan enabled for {tenant_id}. Credit {result['credit_id']}.")
        except ValueError as exc:
            db.rollback()
            return _redirect(str(exc), error=True)


@router.post("/admin/operator/{tenant_id}/revoke")
def operator_revoke(
    request: Request,
    tenant_id: str,
    csrf_token: str = Form(...),
    product_code: str = Form(...),
    reason: str = Form(...),
    admin_username: str = Depends(require_operator),
):
    _check_csrf(request, csrf_token)
    with SessionLocal() as db:
        try:
            result = revoke_product(
                db,
                tenant_id=tenant_id,
                product_code=product_code,
                actor=admin_username,
                reason=reason,
            )
            db.commit()
            return _redirect(f"{result['product_code']} revoked for {tenant_id}.")
        except ValueError as exc:
            db.rollback()
            return _redirect(str(exc), error=True)


@router.post("/admin/operator/{tenant_id}/resend-latest")
def operator_resend_latest(
    request: Request,
    tenant_id: str,
    csrf_token: str = Form(...),
    admin_username: str = Depends(require_operator),
):
    _check_csrf(request, csrf_token)
    from app.services.lifecycle_email_service import queue_lifecycle_email

    with SessionLocal() as db:
        profile = db.get(TenantLifecycleProfile, tenant_id)
        if profile is None:
            return _redirect("Tenant has no lifecycle notification profile.", error=True)
        latest = db.scalar(
            select(LifecycleEmailOutbox)
            .where(LifecycleEmailOutbox.tenant_id == tenant_id)
            .order_by(LifecycleEmailOutbox.created_at_utc.desc(), LifecycleEmailOutbox.id.desc())
            .limit(1)
        )
        if latest is None:
            return _redirect("No lifecycle email exists to resend.", error=True)
        payload = json.loads(latest.payload_json or "{}")
        row = queue_lifecycle_email(
            db,
            tenant_id=tenant_id,
            event_type=latest.event_type,
            payload=payload,
            dedupe_key=f"manual-resend:{latest.id}:{int(latest.created_at_utc.timestamp())}:{latest.attempts}",
        )
        if row is None:
            return _redirect("Lifecycle email is disabled for this tenant.", error=True)
        from app.services.admin_audit_service import log_admin_event

        log_admin_event(
            db,
            admin_username=admin_username,
            action="operator.lifecycle_email.resend",
            target_type="tenant",
            target_id=tenant_id,
            details={"source_outbox_id": latest.id, "event_type": latest.event_type, "new_outbox_id": row.id},
        )
        db.commit()
        return _redirect(f"Lifecycle email {latest.event_type} queued again for {tenant_id}.")
