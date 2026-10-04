from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.db import SessionLocal
from app.models import AdminAuditEvent, DashboardUser, DashboardUserTenantMembership
from app.security.token_hash import hash_api_token


INVITE_HEADERS = {"X-Registration-Invite": "pilot-secret"}
PASSWORD = "a-secure-dashboard-password"
NEW_PASSWORD = "a-new-secure-dashboard-password"


def _admin_auth_header() -> dict[str, str]:
    token = base64.b64encode(b"admin-test:admin-password-for-tests-123").decode("ascii")
    return {"Authorization": f"Basic {token}"}


def _admin_csrf(client, tenant_id: str) -> dict[str, str]:
    response = client.get(f"/admin/tenants/{tenant_id}", headers=_admin_auth_header())
    assert response.status_code == 200
    token = client.cookies.get("bcs_csrf")
    assert token
    return {"csrf_token": token}


def _register(client, settings_state, *, email: str = "pilot-owner@example.com") -> dict:
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    response = client.post(
        "/tenant/register",
        headers=INVITE_HEADERS,
        json={
            "entra_tenant_id": "11111111-1111-1111-1111-111111111111",
            "environment_name": "BCSentinel-Pilot",
            "environment_type": "sandbox",
            "company_id": "22222222-2222-2222-2222-222222222222",
            "company_name": "Pilot Company",
            "app_version": "1.0.2.25",
            "contact_email": email,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def _activate(user_id: int) -> None:
    with SessionLocal() as db:
        user = db.get(DashboardUser, user_id)
        assert user is not None
        user.status = "active"
        user.password_hash = hash_api_token(PASSWORD)
        user.must_change_password = False
        user.updated_at_utc = datetime.now(timezone.utc)
        db.commit()


def test_dashboard_login_persists_lockout_and_recovers_after_window(client, settings_state):
    registered = _register(client, settings_state)
    _activate(registered["dashboard_user_id"])
    settings_state(DASHBOARD_LOGIN_MAX_FAILURES=3, DASHBOARD_LOGIN_LOCK_MINUTES=15)

    for _ in range(3):
        response = client.post(
            "/dashboard/login",
            json={"email": "pilot-owner@example.com", "password": "wrong-password"},
        )
        assert response.status_code == 401

    locked = client.post(
        "/dashboard/login",
        json={"email": "pilot-owner@example.com", "password": PASSWORD},
    )
    assert locked.status_code == 429
    assert locked.json()["detail"]["code"] == "DASHBOARD_LOGIN_LOCKED"

    with SessionLocal() as db:
        user = db.get(DashboardUser, registered["dashboard_user_id"])
        assert user.locked_until_utc is not None
        user.locked_until_utc = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()

    recovered = client.post(
        "/dashboard/login",
        json={"email": "pilot-owner@example.com", "password": PASSWORD},
    )
    assert recovered.status_code == 200
    with SessionLocal() as db:
        user = db.get(DashboardUser, registered["dashboard_user_id"])
        assert user.failed_login_count == 0
        assert user.locked_until_utc is None


def test_password_reset_request_is_non_enumerating_and_token_is_one_time(
    client,
    settings_state,
    monkeypatch,
):
    registered = _register(client, settings_state)
    _activate(registered["dashboard_user_id"])
    settings_state(
        DASHBOARD_PASSWORD_RESET_EXPIRE_MINUTES=30,
        SMTP_HOST=None,
        SMTP_FROM_EMAIL=None,
    )
    raw_token = "known-reset-token"
    monkeypatch.setattr(
        "app.services.dashboard_invite_service.secrets.token_urlsafe",
        lambda _: raw_token,
    )

    unknown = client.post(
        "/dashboard/password-reset/request",
        json={"email": "missing@example.com"},
    )
    known = client.post(
        "/dashboard/password-reset/request",
        json={"email": "pilot-owner@example.com"},
    )
    assert unknown.status_code == 200
    assert known.status_code == 200
    assert unknown.json() == known.json() == {"status": "accepted"}

    with SessionLocal() as db:
        user = db.get(DashboardUser, registered["dashboard_user_id"])
        assert user.password_reset_token_hash
        assert user.password_reset_expires_at_utc

    confirmed = client.post(
        "/dashboard/password-reset/confirm",
        json={
            "email": "pilot-owner@example.com",
            "reset_token": raw_token,
            "password": NEW_PASSWORD,
        },
    )
    assert confirmed.status_code == 200

    replay = client.post(
        "/dashboard/password-reset/confirm",
        json={
            "email": "pilot-owner@example.com",
            "reset_token": raw_token,
            "password": NEW_PASSWORD,
        },
    )
    assert replay.status_code == 401

    assert client.post(
        "/dashboard/login",
        json={"email": "pilot-owner@example.com", "password": NEW_PASSWORD},
    ).status_code == 200


def test_admin_can_suspend_reactivate_and_revoke_invite_with_audit(
    client,
    settings_state,
):
    registered = _register(client, settings_state)
    _activate(registered["dashboard_user_id"])
    tenant_id = registered["tenant_id"]

    suspend = client.post(
        f"/admin/tenant/{tenant_id}/dashboard-access/suspend",
        headers=_admin_auth_header(),
        data=_admin_csrf(client, tenant_id),
        follow_redirects=False,
    )
    assert suspend.status_code == 303
    with SessionLocal() as db:
        membership = db.get(DashboardUserTenantMembership, registered["membership_id"])
        user = db.get(DashboardUser, registered["dashboard_user_id"])
        assert membership.is_active is False
        assert user.status == "disabled"

    reactivate = client.post(
        f"/admin/tenant/{tenant_id}/dashboard-access/reactivate",
        headers=_admin_auth_header(),
        data=_admin_csrf(client, tenant_id),
        follow_redirects=False,
    )
    assert reactivate.status_code == 303
    with SessionLocal() as db:
        membership = db.get(DashboardUserTenantMembership, registered["membership_id"])
        user = db.get(DashboardUser, registered["dashboard_user_id"])
        assert membership.is_active is True
        assert user.status == "active"
        user.invite_token_hash = hash_api_token("temporary-invite")
        user.invite_expires_at_utc = datetime.now(timezone.utc) + timedelta(days=1)
        db.commit()

    revoked = client.post(
        f"/admin/tenant/{tenant_id}/dashboard-access/revoke-invite",
        headers=_admin_auth_header(),
        data=_admin_csrf(client, tenant_id),
        follow_redirects=False,
    )
    assert revoked.status_code == 303

    with SessionLocal() as db:
        user = db.get(DashboardUser, registered["dashboard_user_id"])
        assert user.invite_token_hash is None
        assert user.invite_expires_at_utc is None
        actions = {
            row.action
            for row in db.scalars(
                select(AdminAuditEvent).where(AdminAuditEvent.target_id == tenant_id)
            ).all()
        }
    assert {
        "tenant.dashboard_access.suspend",
        "tenant.dashboard_access.reactivate",
        "tenant.dashboard_access.revoke-invite",
    } <= actions
