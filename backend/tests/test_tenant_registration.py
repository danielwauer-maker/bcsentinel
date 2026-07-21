from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from app.db import SessionLocal
from app.models import DashboardUser, DashboardUserTenantMembership, Tenant
from app.security.token_hash import verify_api_token


def _registration_payload(**overrides):
    payload = {
        "entra_tenant_id": "11111111-1111-1111-1111-111111111111",
        "environment_name": "Production",
        "environment_type": "production",
        "company_id": "22222222-2222-2222-2222-222222222222",
        "company_name": "CRONUS DE",
        "app_version": "1.0.0",
        "contact_email": "pilot.customer@example.com",
    }
    payload.update(overrides)
    return payload


def test_tenant_registration_requires_invite_when_configured(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")

    response = client.post(
        "/tenant/register",
        json=_registration_payload(),
    )

    assert response.status_code == 403


def test_tenant_registration_with_valid_invite_requires_contact_email(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")

    response = client.post(
        "/tenant/register",
        headers={"X-Registration-Invite": "pilot-secret"},
        json=_registration_payload(contact_email=None),
    )

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_REGISTRATION_PAYLOAD"


def test_tenant_registration_with_valid_invite_returns_token_but_stores_only_hash(
    client, settings_state, monkeypatch
):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    delivery_calls = []

    def fake_delivery(db, *, tenant, user, invite_token):
        delivery_calls.append((tenant.tenant_id, user.email, bool(invite_token)))
        return False, "SMTP delivery mocked for registration test."

    monkeypatch.setattr(
        "app.services.dashboard_invite_service._send_dashboard_invite_email",
        fake_delivery,
    )
    monkeypatch.setattr(
        "app.services.dashboard_invite_service.smtplib.SMTP",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("External SMTP must not be used in tests.")),
    )

    response = client.post(
        "/tenant/register",
        headers={"X-Registration-Invite": "pilot-secret"},
        json=_registration_payload(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"].startswith("ten_")
    assert body["api_token"].startswith("tok_")
    assert body["dashboard_invite_email"] == "pilot.customer@example.com"
    assert body["dashboard_invite_sent"] is False
    assert body["dashboard_invite_error"] == "SMTP delivery mocked for registration test."
    assert len(delivery_calls) == 1
    assert delivery_calls[0][1:] == ("pilot.customer@example.com", True)

    with SessionLocal() as db:
        tenant = db.query(Tenant).filter(Tenant.tenant_id == body["tenant_id"]).one()
        assert tenant.api_token is None
        assert tenant.api_token_hash
        assert tenant.contact_email == "pilot.customer@example.com"
        membership = db.scalar(
            select(DashboardUserTenantMembership).where(
                DashboardUserTenantMembership.tenant_id == tenant.tenant_id
            )
        )
        assert membership is not None
        user = db.get(DashboardUser, membership.dashboard_user_id)
        assert user is not None
        assert user.email == "pilot.customer@example.com"
        assert user.password_hash is None
        assert user.invite_token_hash
        assert user.invite_mail_status == "failed"


def test_tenant_registration_stores_optional_contact_email(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")

    response = client.post(
        "/tenant/register",
        headers={"X-Registration-Invite": "pilot-secret"},
        json=_registration_payload(contact_email=" Pilot.Customer@Example.COM "),
    )

    assert response.status_code == 200
    body = response.json()

    with SessionLocal() as db:
        tenant = db.query(Tenant).filter(Tenant.tenant_id == body["tenant_id"]).one()
        assert tenant.contact_email == "pilot.customer@example.com"
        memberships = db.scalars(
            select(DashboardUserTenantMembership).where(
                DashboardUserTenantMembership.tenant_id == tenant.tenant_id
            )
        ).all()
        assert len(memberships) == 1
        assert db.get(DashboardUser, memberships[0].dashboard_user_id).email == "pilot.customer@example.com"


def test_tenant_registration_rejects_invalid_contact_email(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")

    response = client.post(
        "/tenant/register",
        headers={"X-Registration-Invite": "pilot-secret"},
        json=_registration_payload(contact_email="not-valid"),
    )

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_REGISTRATION_PAYLOAD"


def test_tenant_registration_reuses_dashboard_email_for_other_tenant(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")

    first = client.post(
        "/tenant/register",
        headers={"X-Registration-Invite": "pilot-secret"},
        json=_registration_payload(contact_email="shared@example.com"),
    )
    assert first.status_code == 200

    second = client.post(
        "/tenant/register",
        headers={"X-Registration-Invite": "pilot-secret"},
        json=_registration_payload(
            contact_email="shared@example.com",
            company_id="33333333-3333-3333-3333-333333333333",
            company_name="OTHER",
        ),
    )

    assert second.status_code == 200
    assert second.json()["existing_dashboard_user"] is True
    assert second.json()["membership_created"] is True
    assert second.json()["dashboard_access_count"] == 2
    assert second.json()["dashboard_user_id"] == first.json()["dashboard_user_id"]

    with SessionLocal() as db:
        assert db.query(DashboardUser).count() == 1
        assert db.query(DashboardUserTenantMembership).count() == 2


def test_tenant_registration_rate_limit_returns_429(client, settings_state):
    settings_state(
        TENANT_REGISTRATION_INVITE_CODE="pilot-secret",
        TENANT_REGISTRATION_RATE_LIMIT_ATTEMPTS=2,
        TENANT_REGISTRATION_RATE_LIMIT_WINDOW_SECONDS=300,
    )

    payload = _registration_payload()
    headers = {"X-Registration-Invite": "wrong"}

    assert client.post("/tenant/register", headers=headers, json=payload).status_code == 403
    assert client.post("/tenant/register", headers=headers, json=payload).status_code == 403
    assert client.post("/tenant/register", headers=headers, json=payload).status_code == 429


def test_registration_validation_and_identity_errors_use_stable_codes(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")
    missing_field = _registration_payload()
    missing_field.pop("environment_name")
    validation = client.post(
        "/tenant/register",
        headers={"X-Registration-Invite": "pilot-secret"},
        json=missing_field,
    )
    assert validation.status_code == 422
    assert validation.json()["code"] == "INVALID_REGISTRATION_PAYLOAD"
    assert validation.json()["message_de"]

    identity_conflict = client.post(
        "/tenant/register",
        headers={"X-Registration-Invite": "pilot-secret"},
        json=_registration_payload(existing_tenant_id="ten_untrusted"),
    )
    assert identity_conflict.status_code == 409
    assert identity_conflict.json()["code"] == "REGISTRATION_IDENTITY_CONFLICT"


def test_unexpected_registration_error_is_structured_without_traceback(client, settings_state, monkeypatch):
    import app.main as app_main

    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")

    def fail_registration(*args, **kwargs):
        raise RuntimeError("synthetic sensitive diagnostic")

    monkeypatch.setattr(app_main, "upsert_tenant_registration", fail_registration)
    response = client.post(
        "/tenant/register",
        headers={"X-Registration-Invite": "pilot-secret"},
        json=_registration_payload(),
    )
    assert response.status_code == 500
    assert response.json()["code"] == "REGISTRATION_UNEXPECTED_ERROR"
    assert "synthetic" not in response.text


def test_legacy_plaintext_token_is_migrated_after_successful_auth(client, product_access_factory):
    tenant_id = "ten_legacy_test"
    api_token = "tok_legacy_test_secret"
    with SessionLocal() as db:
        db.add(
            Tenant(
                tenant_id=tenant_id,
                api_token=api_token,
                api_token_hash=None,
                environment_name="legacy",
                app_version="1.0.0",
                created_at_utc=datetime.now(timezone.utc),
                last_seen_at_utc=datetime.now(timezone.utc),
                current_plan="free",
                license_status="trial",
            )
        )
        db.commit()

    product_access_factory(tenant_id=tenant_id)

    response = client.get("/analytics/get-token", headers={"X-Tenant-Id": tenant_id, "X-Api-Token": api_token})

    assert response.status_code == 200
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
        assert tenant is not None
        assert tenant.api_token is None
        assert tenant.api_token_hash
        assert verify_api_token(api_token, tenant.api_token_hash)
