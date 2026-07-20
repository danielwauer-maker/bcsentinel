from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select

from app.db import SessionLocal
from app.models import DashboardUser, DashboardUserTenantMembership, Tenant
from app.security.token_hash import hash_api_token
from app.security.url_policy import UnsafeUrlError, normalize_service_base_url


INVITE_HEADERS = {"X-Registration-Invite": "pilot-secret"}


def registration_payload(**overrides):
    payload = {
        "entra_tenant_id": "11111111-1111-1111-1111-111111111111",
        "environment_name": "Production",
        "environment_type": "production",
        "company_id": "22222222-2222-2222-2222-222222222222",
        "company_name": "CRONUS DE",
        "app_version": "1.0.2.6",
        "preferred_language": "de",
        "contact_email": "owner@example.com",
    }
    payload.update(overrides)
    return payload


def register(client, payload=None, headers=None):
    return client.post(
        "/tenant/register",
        headers=headers or INVITE_HEADERS,
        json=payload or registration_payload(),
    )


def test_production_http_is_rejected():
    with pytest.raises(UnsafeUrlError, match="HTTPS is required"):
        normalize_service_base_url("http://api.bcsentinel.com", environment="prod")


def test_production_https_is_accepted():
    assert (
        normalize_service_base_url(" HTTPS://API.BCSENTINEL.COM/ ", environment="prod")
        == "https://api.bcsentinel.com"
    )


def test_backend_rejects_plain_http_request_in_production(client, settings_state):
    settings_state(ENV="prod")
    response = client.get("http://testserver/health", headers={"X-Forwarded-Proto": "http"})
    assert response.status_code == 400
    assert "HTTPS is required" in response.json()["detail"]


def test_backend_accepts_https_request_in_production(client, settings_state):
    settings_state(ENV="prod")
    response = client.get("https://testserver/health")
    assert response.status_code == 200


def test_localhost_http_is_allowed_only_outside_production():
    assert normalize_service_base_url("http://localhost:8000", environment="dev") == "http://localhost:8000"
    assert normalize_service_base_url("http://127.0.0.1:8000", environment="test") == "http://127.0.0.1:8000"
    with pytest.raises(UnsafeUrlError):
        normalize_service_base_url("http://localhost:8000", environment="production")


@pytest.mark.parametrize(
    "url",
    [
        "http://10.0.0.1:8000",
        "http://192.168.1.10",
        "http://devbox.local",
        "https://user:secret@api.bcsentinel.com",
        "https://api.bcsentinel.com?api_token=secret",
        "javascript:alert(1)",
        "https://api.bcsentinel.com bad",
    ],
)
def test_external_or_malformed_urls_are_rejected(url):
    with pytest.raises(UnsafeUrlError):
        normalize_service_base_url(url, environment="dev")


def test_first_registration_creates_stable_identity(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    response = register(client)
    assert response.status_code == 200
    body = response.json()
    assert body["registration_status"] == "created"
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == body["tenant_id"]))
        assert tenant is not None
        assert tenant.registration_identity_key
        assert tenant.entra_tenant_id == "11111111-1111-1111-1111-111111111111"
        assert tenant.bc_environment_name == "Production"
        assert tenant.bc_environment_type == "production"
        assert tenant.bc_company_id == "22222222-2222-2222-2222-222222222222"


def test_identical_registration_is_idempotent_and_does_not_resend_invite(client, settings_state, monkeypatch):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    send_count = 0

    def fake_send(*_args, **_kwargs):
        nonlocal send_count
        send_count += 1
        return True, None

    monkeypatch.setattr("app.services.dashboard_invite_service._send_dashboard_invite_email", fake_send)
    first = register(client)
    second = register(client)
    assert first.status_code == second.status_code == 200
    assert first.json()["tenant_id"] == second.json()["tenant_id"]
    assert first.json()["api_token"] == second.json()["api_token"]
    assert second.json()["registration_status"] == "existing"
    assert send_count == 1
    with SessionLocal() as db:
        assert db.scalar(select(func.count(Tenant.id))) == 1
        assert db.scalar(select(func.count(DashboardUser.id))) == 1


def test_retry_after_response_loss_returns_same_context(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    committed_response = register(client)
    retry_response = register(client)
    assert committed_response.status_code == retry_response.status_code == 200
    assert committed_response.json()["tenant_id"] == retry_response.json()["tenant_id"]
    assert committed_response.json()["api_token"] == retry_response.json()["api_token"]


def test_parallel_identical_registration_has_one_tenant_and_user(client, settings_state):
    settings_state(
        TENANT_REGISTRATION_INVITE_CODE="pilot-secret",
        TENANT_REGISTRATION_RATE_LIMIT_ATTEMPTS=20,
    )
    with ThreadPoolExecutor(max_workers=4) as executor:
        responses = list(executor.map(lambda _: register(client), range(4)))
    assert {response.status_code for response in responses} == {200}
    assert len({response.json()["tenant_id"] for response in responses}) == 1
    assert len({response.json()["api_token"] for response in responses}) == 1
    with SessionLocal() as db:
        assert db.scalar(select(func.count(Tenant.id))) == 1
        assert db.scalar(select(func.count(DashboardUser.id))) == 1


def test_contact_email_change_reassigns_membership_without_mutating_existing_login(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    first = register(client)
    second = register(client, registration_payload(contact_email="new-owner@example.com"))
    assert second.status_code == 200
    assert second.json()["tenant_id"] == first.json()["tenant_id"]
    with SessionLocal() as db:
        assert db.scalar(select(func.count(Tenant.id))) == 1
        users = db.scalars(select(DashboardUser).order_by(DashboardUser.id)).all()
        assert [user.email for user in users] == ["owner@example.com", "new-owner@example.com"]
        memberships = db.scalars(
            select(DashboardUserTenantMembership).order_by(DashboardUserTenantMembership.id)
        ).all()
        assert len(memberships) == 2
        assert memberships[0].dashboard_user_id == users[0].id
        assert memberships[0].is_active is False
        assert memberships[1].dashboard_user_id == users[1].id
        assert memberships[1].is_active is True


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("company_id", "33333333-3333-3333-3333-333333333333"),
        ("environment_name", "Sandbox-A"),
        ("entra_tenant_id", "44444444-4444-4444-4444-444444444444"),
    ],
)
def test_identity_dimensions_create_distinct_registration(client, settings_state, field, value):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    first = register(client)
    second_payload = registration_payload(contact_email=f"{field}@example.com", **{field: value})
    if field == "environment_name":
        second_payload["environment_type"] = "sandbox"
    second = register(client, second_payload)
    assert first.status_code == second.status_code == 200
    assert first.json()["tenant_id"] != second.json()["tenant_id"]


def test_portal_account_is_not_duplicated_and_resend_is_explicit(client, settings_state, monkeypatch):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    send_count = 0

    def fake_send(*_args, **_kwargs):
        nonlocal send_count
        send_count += 1
        return True, None

    monkeypatch.setattr("app.services.dashboard_invite_service._send_dashboard_invite_email", fake_send)
    first = register(client)
    register(client)
    body = first.json()
    resend = client.post(
        "/tenant/dashboard-invite/resend",
        headers={"X-Tenant-Id": body["tenant_id"], "X-Api-Token": body["api_token"]},
        json={"contact_email": "owner@example.com"},
    )
    assert resend.status_code == 200
    assert send_count == 2


def test_dashboard_token_requires_exact_registered_context(client, settings_state, product_access_factory):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    registration = register(client).json()
    headers = {"X-Tenant-Id": registration["tenant_id"], "X-Api-Token": registration["api_token"]}
    product_access_factory(tenant_id=registration["tenant_id"])
    valid_params = {
        "tenant_id": registration["tenant_id"],
        "company": "CRONUS DE",
        "company_id": "22222222-2222-2222-2222-222222222222",
        "environment": "Production",
        "environment_type": "production",
        "entra_tenant_id": "11111111-1111-1111-1111-111111111111",
    }
    assert client.get("/analytics/get-token", headers=headers, params=valid_params).status_code == 200
    wrong_params = {**valid_params, "company_id": "33333333-3333-3333-3333-333333333333"}
    assert client.get("/analytics/get-token", headers=headers, params=wrong_params).status_code == 403


def test_legacy_tenant_can_be_authenticated_and_bound_without_new_tenant(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    legacy_id = "ten_legacy_bind"
    legacy_token = "tok_legacy_bind"
    with SessionLocal() as db:
        now = datetime.now(timezone.utc)
        db.add(
            Tenant(
                tenant_id=legacy_id,
                api_token=None,
                api_token_hash=hash_api_token(legacy_token),
                environment_name="legacy",
                app_version="1.0.0",
                created_at_utc=now,
                last_seen_at_utc=now,
                current_plan="free",
                license_status="trial",
            )
        )
        db.commit()
    headers = {
        **INVITE_HEADERS,
        "X-Tenant-Id": legacy_id,
        "X-Api-Token": legacy_token,
    }
    response = register(client, registration_payload(existing_tenant_id=legacy_id), headers=headers)
    assert response.status_code == 200
    assert response.json()["tenant_id"] == legacy_id
    assert response.json()["registration_status"] == "bound_legacy"
    with SessionLocal() as db:
        assert db.scalar(select(func.count(Tenant.id))) == 1
