from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.db import SessionLocal
from app.models import DashboardUser, DashboardUserTenantMembership, Tenant
from app.security.token import create_token, verify_token
from app.security.token_hash import hash_api_token
from app.services.access_control_service import TOKEN_AUDIENCE


INVITE_HEADERS = {"X-Registration-Invite": "pilot-secret"}
PASSWORD = "a-secure-dashboard-password"


def _payload(*, company_id: str, environment_name: str = "Production", environment_type: str = "production", email: str = "shared@example.com"):
    return {
        "entra_tenant_id": "11111111-1111-1111-1111-111111111111",
        "environment_name": environment_name,
        "environment_type": environment_type,
        "company_id": company_id,
        "company_name": f"Company {company_id[:4]}",
        "app_version": "1.0.2.7",
        "contact_email": email,
    }


def _register(client, *, company_id: str, environment_name: str = "Production", environment_type: str = "production", email: str = "shared@example.com"):
    response = client.post(
        "/tenant/register",
        headers=INVITE_HEADERS,
        json=_payload(
            company_id=company_id,
            environment_name=environment_name,
            environment_type=environment_type,
            email=email,
        ),
    )
    assert response.status_code == 200, response.text
    return response.json()


def _activate_user(user_id: int) -> None:
    with SessionLocal() as db:
        user = db.get(DashboardUser, user_id)
        user.status = "active"
        user.password_hash = hash_api_token(PASSWORD)
        user.must_change_password = False
        user.updated_at_utc = datetime.now(timezone.utc)
        db.commit()


def _login(client, email: str = "shared@example.com"):
    return client.post("/dashboard/login", json={"email": email, "password": PASSWORD})


def test_same_user_can_access_production_sandbox_and_second_company(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    production = _register(client, company_id="22222222-2222-2222-2222-222222222222")
    with SessionLocal() as db:
        initial_user = db.get(DashboardUser, production["dashboard_user_id"])
        initial_invited_at = initial_user.last_invited_at_utc
        initial_invite_hash = initial_user.invite_token_hash
    sandbox = _register(
        client,
        company_id="22222222-2222-2222-2222-222222222222",
        environment_name="BCSentinel-Pilot",
        environment_type="sandbox",
    )
    second_company = _register(client, company_id="33333333-3333-3333-3333-333333333333")

    assert {production["dashboard_user_id"], sandbox["dashboard_user_id"], second_company["dashboard_user_id"]} == {production["dashboard_user_id"]}
    assert production["existing_dashboard_user"] is False
    assert sandbox["existing_dashboard_user"] is True
    assert second_company["dashboard_access_count"] == 3
    assert sandbox["dashboard_invite_sent"] is False

    with SessionLocal() as db:
        assert db.query(DashboardUser).count() == 1
        assert db.query(DashboardUserTenantMembership).count() == 3
        reused_user = db.get(DashboardUser, production["dashboard_user_id"])
        assert reused_user.last_invited_at_utc == initial_invited_at
        assert reused_user.invite_token_hash == initial_invite_hash


def test_registration_is_case_insensitive_and_idempotent_without_duplicate_membership(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    first = _register(client, company_id="22222222-2222-2222-2222-222222222222", email="Shared@Example.COM")
    repeated = _register(client, company_id="22222222-2222-2222-2222-222222222222", email=" shared@example.com ")

    assert repeated["tenant_id"] == first["tenant_id"]
    assert repeated["dashboard_user_id"] == first["dashboard_user_id"]
    assert repeated["membership_id"] == first["membership_id"]
    assert repeated["membership_created"] is False
    assert repeated["dashboard_access_count"] == 1
    with SessionLocal() as db:
        assert db.query(DashboardUser).count() == 1
        assert db.query(DashboardUserTenantMembership).count() == 1


def test_disabled_user_and_membership_are_not_silently_reactivated(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    registered = _register(client, company_id="22222222-2222-2222-2222-222222222222")
    with SessionLocal() as db:
        user = db.get(DashboardUser, registered["dashboard_user_id"])
        user.status = "disabled"
        db.commit()
    disabled_user = client.post("/tenant/register", headers=INVITE_HEADERS, json=_payload(company_id="22222222-2222-2222-2222-222222222222"))
    assert disabled_user.status_code == 403
    assert disabled_user.json()["code"] == "DASHBOARD_USER_DISABLED"

    with SessionLocal() as db:
        user = db.get(DashboardUser, registered["dashboard_user_id"])
        user.status = "active"
        membership = db.get(DashboardUserTenantMembership, registered["membership_id"])
        membership.is_active = False
        db.commit()
    disabled_membership = client.post("/tenant/register", headers=INVITE_HEADERS, json=_payload(company_id="22222222-2222-2222-2222-222222222222"))
    assert disabled_membership.status_code == 403
    assert disabled_membership.json()["code"] == "TENANT_MEMBERSHIP_DISABLED"


def test_login_lists_only_authorized_tenants_and_switch_rotates_active_context(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    first = _register(client, company_id="22222222-2222-2222-2222-222222222222")
    second = _register(client, company_id="33333333-3333-3333-3333-333333333333")
    foreign = _register(client, company_id="44444444-4444-4444-4444-444444444444", email="foreign@example.com")
    _activate_user(first["dashboard_user_id"])

    login = _login(client)
    assert login.status_code == 200
    assert login.json()["tenant_count"] == 2
    assert {item["tenant_id"] for item in login.json()["tenants"]} == {first["tenant_id"], second["tenant_id"]}
    assert foreign["tenant_id"] not in {item["tenant_id"] for item in login.json()["tenants"]}

    switched = client.post("/dashboard/tenant/switch", json={"tenant_id": second["tenant_id"]})
    assert switched.status_code == 200
    assert switched.json()["active_tenant_id"] == second["tenant_id"]
    payload = verify_token(switched.json()["session_token"], audience="bcsentinel-dashboard")
    assert payload["user_id"] == first["dashboard_user_id"]
    assert payload["active_tenant_id"] == second["tenant_id"]

    tenant_list = client.get("/dashboard/tenants")
    assert tenant_list.status_code == 200
    assert tenant_list.json()["active_tenant_id"] == second["tenant_id"]

    forbidden_switch = client.post("/dashboard/tenant/switch", json={"tenant_id": foreign["tenant_id"]})
    assert forbidden_switch.status_code == 403
    assert forbidden_switch.json()["detail"]["code"] == "TENANT_ACCESS_FORBIDDEN"
    forbidden_direct = client.get(f"/dashboard/tenant/{foreign['tenant_id']}")
    assert forbidden_direct.status_code == 403


def test_manipulated_session_cannot_open_unassigned_tenant(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    owner = _register(client, company_id="22222222-2222-2222-2222-222222222222")
    foreign = _register(client, company_id="33333333-3333-3333-3333-333333333333", email="foreign@example.com")
    _activate_user(owner["dashboard_user_id"])
    forged = create_token(
        {
            "type": "dashboard_session",
            "scope": "dashboard:user",
            "aud": "bcsentinel-dashboard",
            "user_id": owner["dashboard_user_id"],
            "active_tenant_id": foreign["tenant_id"],
            "membership_id": foreign["membership_id"],
        }
    )
    response = client.get("/dashboard/tenants", headers={"Authorization": f"Bearer {forged}"})
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "TENANT_ACCESS_FORBIDDEN"


def test_one_tenant_is_selected_automatically_and_logout_clears_session(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    registered = _register(client, company_id="22222222-2222-2222-2222-222222222222")
    _activate_user(registered["dashboard_user_id"])
    login = _login(client, email="SHARED@example.com")
    assert login.status_code == 200
    assert login.json()["tenant_count"] == 1
    assert login.json()["active_tenant_id"] == registered["tenant_id"]
    assert client.post("/dashboard/logout").status_code == 200
    assert client.get("/dashboard/tenants").status_code == 401


def test_invite_activation_keeps_memberships_and_establishes_user_session(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    registered = _register(client, company_id="22222222-2222-2222-2222-222222222222")
    raw_invite = "invite-token-known-only-to-test"
    with SessionLocal() as db:
        user = db.get(DashboardUser, registered["dashboard_user_id"])
        user.invite_token_hash = hash_api_token(raw_invite)
        user.invite_expires_at_utc = datetime.now(timezone.utc) + timedelta(hours=1)
        db.commit()

    activation = client.post(
        "/dashboard/invite/activate",
        json={"email": "SHARED@example.com", "invite_token": raw_invite, "password": PASSWORD},
    )
    assert activation.status_code == 200
    assert activation.json()["tenant_count"] == 1
    assert client.get("/dashboard/tenants").status_code == 200


def test_analytics_token_is_bound_to_server_validated_active_membership(client, settings_state, product_access_factory):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    first = _register(client, company_id="22222222-2222-2222-2222-222222222222")
    second = _register(client, company_id="33333333-3333-3333-3333-333333333333")
    product_access_factory(tenant_id=first["tenant_id"])
    product_access_factory(tenant_id=second["tenant_id"])
    _activate_user(first["dashboard_user_id"])
    assert _login(client).status_code == 200
    assert client.post("/dashboard/tenant/switch", json={"tenant_id": second["tenant_id"]}).status_code == 200

    response = client.post("/dashboard/analytics-token", json={})
    assert response.status_code == 200
    token_payload = verify_token(response.json()["token"], audience=TOKEN_AUDIENCE)
    assert token_payload["tenant_id"] == second["tenant_id"]
    assert token_payload["company_id"]


def test_dashboard_portal_has_responsive_tenant_selection(client):
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert 'name="viewport"' in response.text
    assert 'id="tenant-select"' in response.text
    assert "@media (max-width: 480px)" in response.text
