from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Cookie, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.db import SessionLocal
from app.models import DashboardUser, DashboardUserTenantMembership, Tenant
from app.routers.analytics import _create_analytics_embed_token
from app.security.token import create_token, verify_token
from app.security.token_hash import hash_api_token, verify_api_token
from app.services.access_control_service import CAPABILITY_DASHBOARD, require_capability
from app.services.admin_audit_service import log_admin_event
from app.services.billing_service import utc_now
from app.services.dashboard_invite_service import normalize_dashboard_email
from app.services.localization_service import tenant_language


router = APIRouter()
TEMPLATES = Jinja2Templates(directory=Path(__file__).resolve().parents[1] / "templates")
DASHBOARD_SESSION_COOKIE = "bcs_dashboard_session"
DASHBOARD_SESSION_AUDIENCE = "bcsentinel-dashboard"
DASHBOARD_SESSION_TYPE = "dashboard_session"


class DashboardLoginRequest(BaseModel):
    email: str
    password: str


class DashboardInviteActivationRequest(BaseModel):
    email: str
    invite_token: str
    password: str


class DashboardTenantSwitchRequest(BaseModel):
    tenant_id: str


def _error(status_code: int, code: str, message: str, message_de: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message, "message_de": message_de, "details": {}},
    )


def _session_token(user: DashboardUser, membership: DashboardUserTenantMembership) -> str:
    return create_token(
        {
            "type": DASHBOARD_SESSION_TYPE,
            "scope": "dashboard:user",
            "aud": DASHBOARD_SESSION_AUDIENCE,
            "user_id": user.id,
            "active_tenant_id": membership.tenant_id,
            "membership_id": membership.id,
            "role": membership.role,
        },
        expires_delta=timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
    )


def _set_session_cookie(response: JSONResponse, token: str) -> None:
    response.set_cookie(
        key=DASHBOARD_SESSION_COOKIE,
        value=token,
        max_age=settings.TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.ENV.lower() == "prod",
        samesite="strict",
        path="/",
    )


def _extract_session_token(
    authorization: str | None,
    dashboard_session: str | None,
) -> str:
    if authorization:
        scheme, _, value = authorization.partition(" ")
        if scheme.lower() == "bearer" and value.strip():
            return value.strip()
    if dashboard_session:
        return dashboard_session
    raise _error(401, "DASHBOARD_SESSION_REQUIRED", "Dashboard sign-in is required.", "Eine Dashboard-Anmeldung ist erforderlich.")


def _load_session_context(
    db: Session,
    *,
    authorization: str | None,
    dashboard_session: str | None,
) -> tuple[DashboardUser, DashboardUserTenantMembership, Tenant]:
    token = _extract_session_token(authorization, dashboard_session)
    payload = verify_token(token, audience=DASHBOARD_SESSION_AUDIENCE)
    if payload is None or payload.get("type") != DASHBOARD_SESSION_TYPE or payload.get("scope") != "dashboard:user":
        raise _error(401, "DASHBOARD_SESSION_INVALID", "Dashboard session is invalid or expired.", "Die Dashboard-Sitzung ist ungültig oder abgelaufen.")

    try:
        user_id = int(payload.get("user_id"))
    except (TypeError, ValueError) as exc:
        raise _error(401, "DASHBOARD_SESSION_INVALID", "Dashboard session is invalid.", "Die Dashboard-Sitzung ist ungültig.") from exc
    active_tenant_id = str(payload.get("active_tenant_id") or "").strip()

    user = db.scalar(select(DashboardUser).where(DashboardUser.id == user_id))
    if user is None or user.status != "active":
        raise _error(403, "DASHBOARD_USER_DISABLED", "Dashboard user is disabled.", "Der Dashboard-Benutzer ist deaktiviert.")
    membership = db.scalar(
        select(DashboardUserTenantMembership).where(
            DashboardUserTenantMembership.dashboard_user_id == user.id,
            DashboardUserTenantMembership.tenant_id == active_tenant_id,
        )
    )
    if membership is None:
        raise _error(403, "TENANT_ACCESS_FORBIDDEN", "Tenant access is forbidden.", "Der Zugriff auf diesen Mandanten ist nicht erlaubt.")
    if not membership.is_active:
        raise _error(403, "TENANT_MEMBERSHIP_DISABLED", "Tenant membership is disabled.", "Die Mandantenzuordnung ist deaktiviert.")
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == membership.tenant_id))
    if tenant is None:
        raise _error(404, "TENANT_NOT_FOUND", "Tenant was not found.", "Der Mandant wurde nicht gefunden.")
    return user, membership, tenant


def _membership_payload(membership: DashboardUserTenantMembership, tenant: Tenant) -> dict[str, object]:
    return {
        "tenant_id": tenant.tenant_id,
        "membership_id": membership.id,
        "role": membership.role,
        "environment_name": tenant.bc_environment_name or tenant.environment_name,
        "environment_type": tenant.bc_environment_type or "unknown",
        "company_name": tenant.bc_company_name or "Business Central",
        "tenant_name": tenant.bc_company_name or tenant.bc_environment_name or tenant.environment_name,
        "last_selected_at_utc": membership.last_selected_at_utc.isoformat() if membership.last_selected_at_utc else None,
    }


def _active_memberships(db: Session, user_id: int) -> list[tuple[DashboardUserTenantMembership, Tenant]]:
    return list(
        db.execute(
            select(DashboardUserTenantMembership, Tenant)
            .join(Tenant, Tenant.tenant_id == DashboardUserTenantMembership.tenant_id)
            .where(
                DashboardUserTenantMembership.dashboard_user_id == user_id,
                DashboardUserTenantMembership.is_active.is_(True),
            )
            .order_by(
                DashboardUserTenantMembership.last_selected_at_utc.desc(),
                Tenant.bc_company_name,
                Tenant.bc_environment_name,
            )
        ).all()
    )


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
@router.get("/dashboard/invite", response_class=HTMLResponse, include_in_schema=False)
def dashboard_portal(request: Request, token: str | None = None):
    return TEMPLATES.TemplateResponse(
        request=request,
        name="dashboard_portal.html",
        context={"invite_token": token or ""},
    )


@router.post("/dashboard/invite/activate")
def activate_dashboard_invite(payload: DashboardInviteActivationRequest):
    if len(payload.password) < 12:
        raise _error(422, "INVALID_REGISTRATION_PAYLOAD", "Password must contain at least 12 characters.", "Das Kennwort muss mindestens 12 Zeichen enthalten.")
    normalized_email = normalize_dashboard_email(payload.email)
    with SessionLocal() as db:
        user = db.scalar(select(DashboardUser).where(DashboardUser.normalized_email == normalized_email))
        now = utc_now()
        expires_at = user.invite_expires_at_utc if user else None
        if expires_at is not None and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if (
            user is None
            or not verify_api_token(payload.invite_token, user.invite_token_hash)
            or expires_at is None
            or expires_at <= now
        ):
            raise _error(401, "DASHBOARD_INVITE_INVALID", "Dashboard invitation is invalid or expired.", "Die Dashboard-Einladung ist ungültig oder abgelaufen.")
        memberships = _active_memberships(db, user.id)
        if not memberships:
            raise _error(403, "TENANT_MEMBERSHIP_NOT_ALLOWED", "No active tenant membership is available.", "Es ist keine aktive Mandantenzuordnung vorhanden.")
        user.password_hash = hash_api_token(payload.password)
        user.status = "active"
        user.must_change_password = False
        user.invite_token_hash = None
        user.invite_expires_at_utc = None
        user.updated_at_utc = now
        membership = memberships[0][0]
        membership.last_selected_at_utc = now
        db.commit()
        session_token = _session_token(user, membership)
    response = JSONResponse({"status": "activated", "active_tenant_id": membership.tenant_id, "tenant_count": len(memberships), "session_token": session_token})
    _set_session_cookie(response, session_token)
    return response


@router.post("/dashboard/login")
def dashboard_login(payload: DashboardLoginRequest):
    normalized_email = normalize_dashboard_email(payload.email)
    with SessionLocal() as db:
        user = db.scalar(select(DashboardUser).where(DashboardUser.normalized_email == normalized_email))
        if user is None or user.status != "active" or not verify_api_token(payload.password, user.password_hash):
            raise _error(401, "DASHBOARD_LOGIN_FAILED", "Email or password is invalid.", "E-Mail-Adresse oder Kennwort ist ungültig.")
        memberships = _active_memberships(db, user.id)
        if not memberships:
            raise _error(403, "TENANT_MEMBERSHIP_NOT_ALLOWED", "No active tenant membership is available.", "Es ist keine aktive Mandantenzuordnung vorhanden.")
        membership = memberships[0][0]
        membership.last_selected_at_utc = utc_now()
        user.updated_at_utc = utc_now()
        db.commit()
        session_token = _session_token(user, membership)
        tenant_items = [_membership_payload(item, tenant) for item, tenant in memberships]
    response = JSONResponse({"session_token": session_token, "active_tenant_id": membership.tenant_id, "tenant_count": len(tenant_items), "tenants": tenant_items})
    _set_session_cookie(response, session_token)
    return response


@router.post("/dashboard/logout")
def dashboard_logout():
    response = JSONResponse({"status": "signed_out"})
    response.delete_cookie(DASHBOARD_SESSION_COOKIE, path="/")
    return response


@router.get("/dashboard/tenants")
def dashboard_tenants(
    authorization: str | None = Header(default=None, alias="Authorization"),
    dashboard_session: str | None = Cookie(default=None, alias=DASHBOARD_SESSION_COOKIE),
):
    with SessionLocal() as db:
        user, active_membership, _ = _load_session_context(db, authorization=authorization, dashboard_session=dashboard_session)
        memberships = _active_memberships(db, user.id)
        return {
            "active_tenant_id": active_membership.tenant_id,
            "tenant_count": len(memberships),
            "tenants": [_membership_payload(membership, tenant) for membership, tenant in memberships],
        }


@router.get("/dashboard/tenant/{tenant_id}")
def dashboard_tenant_detail(
    tenant_id: str,
    authorization: str | None = Header(default=None, alias="Authorization"),
    dashboard_session: str | None = Cookie(default=None, alias=DASHBOARD_SESSION_COOKIE),
):
    with SessionLocal() as db:
        user, _, _ = _load_session_context(db, authorization=authorization, dashboard_session=dashboard_session)
        row = db.execute(
            select(DashboardUserTenantMembership, Tenant)
            .join(Tenant, Tenant.tenant_id == DashboardUserTenantMembership.tenant_id)
            .where(
                DashboardUserTenantMembership.dashboard_user_id == user.id,
                DashboardUserTenantMembership.tenant_id == tenant_id,
                DashboardUserTenantMembership.is_active.is_(True),
            )
        ).first()
        if row is None:
            raise _error(403, "TENANT_ACCESS_FORBIDDEN", "Tenant access is forbidden.", "Der Zugriff auf diesen Mandanten ist nicht erlaubt.")
        return _membership_payload(row[0], row[1])


@router.post("/dashboard/tenant/switch")
def switch_dashboard_tenant(
    payload: DashboardTenantSwitchRequest,
    authorization: str | None = Header(default=None, alias="Authorization"),
    dashboard_session: str | None = Cookie(default=None, alias=DASHBOARD_SESSION_COOKIE),
):
    with SessionLocal() as db:
        user, _, _ = _load_session_context(db, authorization=authorization, dashboard_session=dashboard_session)
        membership = db.scalar(
            select(DashboardUserTenantMembership).where(
                DashboardUserTenantMembership.dashboard_user_id == user.id,
                DashboardUserTenantMembership.tenant_id == payload.tenant_id,
                DashboardUserTenantMembership.is_active.is_(True),
            )
        )
        if membership is None:
            raise _error(403, "TENANT_ACCESS_FORBIDDEN", "Tenant access is forbidden.", "Der Zugriff auf diesen Mandanten ist nicht erlaubt.")
        membership.last_selected_at_utc = utc_now()
        membership.updated_at_utc = utc_now()
        log_admin_event(
            db,
            admin_username=f"dashboard-user:{user.id}",
            action="dashboard_tenant_switched",
            target_type="tenant",
            target_id=membership.tenant_id,
            details={"membership_id": membership.id},
        )
        db.commit()
        session_token = _session_token(user, membership)
    response = JSONResponse({"status": "switched", "active_tenant_id": membership.tenant_id, "session_token": session_token})
    _set_session_cookie(response, session_token)
    return response


@router.post("/dashboard/analytics-token")
def dashboard_analytics_token(
    authorization: str | None = Header(default=None, alias="Authorization"),
    dashboard_session: str | None = Cookie(default=None, alias=DASHBOARD_SESSION_COOKIE),
):
    with SessionLocal() as db:
        _, _, tenant = _load_session_context(db, authorization=authorization, dashboard_session=dashboard_session)
        require_capability(db, tenant, CAPABILITY_DASHBOARD)
        token = _create_analytics_embed_token(
            company=tenant.bc_company_name or "Business Central",
            environment=tenant.bc_environment_name or tenant.environment_name,
            tenant_id=tenant.tenant_id,
            company_id=tenant.bc_company_id,
            language=tenant_language(tenant),
            scan_mode=None,
            bc_issue_launch_url=None,
        )
    return {"token": token, "tenant_id": tenant.tenant_id}
