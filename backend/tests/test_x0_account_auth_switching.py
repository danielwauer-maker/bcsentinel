from __future__ import annotations

from app.db import SessionLocal
from app.routers import account_auth
from app.security.oidc import VerifiedOIDCIdentity
from app.services.account_membership_service import (
    get_or_create_user_identity,
    upsert_tenant_membership,
)


def _mock_identity() -> VerifiedOIDCIdentity:
    return VerifiedOIDCIdentity(
        provider="test-oidc",
        subject="subject-123",
        email="multi@example.com",
        display_name="Multi Tenant User",
    )


def _seed_memberships(tenant_a: dict, tenant_b: dict | None = None) -> None:
    with SessionLocal() as db:
        user = get_or_create_user_identity(
            db,
            provider="test-oidc",
            provider_subject="subject-123",
            email="multi@example.com",
            display_name="Multi Tenant User",
        )
        upsert_tenant_membership(
            db,
            user_identity_id=user.id,
            tenant_id=tenant_a["tenant_id"],
            role="ADMIN",
            status="active",
        )
        if tenant_b is not None:
            upsert_tenant_membership(
                db,
                user_identity_id=user.id,
                tenant_id=tenant_b["tenant_id"],
                role="VIEWER",
                status="active",
            )
        db.commit()


def test_account_login_lists_multiple_tenants_and_requires_selection(client, monkeypatch, tenant_factory):
    tenant_a = tenant_factory(plan="free")
    tenant_b = tenant_factory(plan="premium", license_status="active")
    _seed_memberships(tenant_a, tenant_b)
    monkeypatch.setattr(account_auth, "verify_oidc_bearer_token", lambda token: _mock_identity())

    login = client.post("/auth/account/session", headers={"Authorization": "Bearer external-token"})
    assert login.status_code == 200
    payload = login.json()
    assert payload["tenant_count"] == 2
    assert payload["requires_tenant_selection"] is True
    assert payload["auto_select_tenant_id"] is None

    account_token = payload["session_token"]
    tenants = client.get(
        "/auth/account/tenants",
        headers={"Authorization": f"Bearer {account_token}"},
    )
    assert tenants.status_code == 200
    rows = {row["tenant_id"]: row for row in tenants.json()["tenants"]}
    assert rows[tenant_a["tenant_id"]]["role"] == "ADMIN"
    assert rows[tenant_b["tenant_id"]]["role"] == "VIEWER"


def test_single_membership_can_be_auto_selected(client, monkeypatch, tenant_factory):
    tenant = tenant_factory()
    _seed_memberships(tenant)
    monkeypatch.setattr(account_auth, "verify_oidc_bearer_token", lambda token: _mock_identity())

    login = client.post("/auth/account/session", headers={"Authorization": "Bearer external-token"})
    assert login.status_code == 200
    assert login.json()["tenant_count"] == 1
    assert login.json()["requires_tenant_selection"] is False
    assert login.json()["auto_select_tenant_id"] == tenant["tenant_id"]


def test_tenant_switch_mints_tenant_bound_session_and_blocks_cross_tenant_use(client, monkeypatch, tenant_factory):
    tenant_a = tenant_factory()
    tenant_b = tenant_factory()
    _seed_memberships(tenant_a, tenant_b)
    monkeypatch.setattr(account_auth, "verify_oidc_bearer_token", lambda token: _mock_identity())

    login = client.post("/auth/account/session", headers={"Authorization": "Bearer external-token"})
    account_token = login.json()["session_token"]
    switched = client.post(
        "/auth/account/tenant-session",
        json={"tenant_id": tenant_a["tenant_id"]},
        headers={"Authorization": f"Bearer {account_token}"},
    )
    assert switched.status_code == 200
    tenant_token = switched.json()["session_token"]
    assert switched.json()["role"] == "ADMIN"

    own_status = client.get(
        "/billing/subscription/status",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert own_status.status_code == 200
    assert own_status.json()["tenant_id"] == tenant_a["tenant_id"]

    wrong_scope = client.get(
        "/billing/subscription/status",
        headers={
            "Authorization": f"Bearer {tenant_token}",
            "X-Tenant-Id": tenant_b["tenant_id"],
        },
    )
    assert wrong_scope.status_code == 403


def test_membership_role_change_invalidates_existing_tenant_session(client, monkeypatch, tenant_factory):
    tenant = tenant_factory()
    _seed_memberships(tenant)
    monkeypatch.setattr(account_auth, "verify_oidc_bearer_token", lambda token: _mock_identity())

    login = client.post("/auth/account/session", headers={"Authorization": "Bearer external-token"})
    account_token = login.json()["session_token"]
    switched = client.post(
        "/auth/account/tenant-session",
        json={"tenant_id": tenant["tenant_id"]},
        headers={"Authorization": f"Bearer {account_token}"},
    )
    tenant_token = switched.json()["session_token"]

    with SessionLocal() as db:
        user = get_or_create_user_identity(
            db,
            provider="test-oidc",
            provider_subject="subject-123",
            email="multi@example.com",
        )
        upsert_tenant_membership(
            db,
            user_identity_id=user.id,
            tenant_id=tenant["tenant_id"],
            role="VIEWER",
            status="active",
        )
        db.commit()

    stale_session = client.get(
        "/billing/subscription/status",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert stale_session.status_code == 403


def test_existing_machine_to_dashboard_session_endpoint_is_reachable(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory()
    response = client.post("/auth/session", headers=auth_header_factory(tenant))
    assert response.status_code == 200
    assert response.json()["tenant_id"] == tenant["tenant_id"]
    assert response.json()["scope"] == "tenant:dashboard"
