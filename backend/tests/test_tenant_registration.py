from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Tenant
from app.security.token_hash import verify_api_token


def test_tenant_registration_requires_invite_when_configured(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")

    response = client.post(
        "/tenant/register",
        json={"environment_name": "BC Cloud", "app_version": "1.0.0"},
    )

    assert response.status_code == 403


def test_tenant_registration_with_valid_invite_returns_token_but_stores_only_hash(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")

    response = client.post(
        "/tenant/register",
        headers={"X-Registration-Invite": "pilot-secret"},
        json={"environment_name": "BC Cloud", "app_version": "1.0.0"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"].startswith("ten_")
    assert body["api_token"].startswith("tok_")

    with SessionLocal() as db:
        tenant = db.query(Tenant).filter(Tenant.tenant_id == body["tenant_id"]).one()
        assert tenant.api_token is None
        assert tenant.api_token_hash


def test_tenant_registration_rate_limit_returns_429(client, settings_state):
    settings_state(
        TENANT_REGISTRATION_INVITE_CODE="pilot-secret",
        TENANT_REGISTRATION_RATE_LIMIT_ATTEMPTS=2,
        TENANT_REGISTRATION_RATE_LIMIT_WINDOW_SECONDS=300,
    )

    payload = {"environment_name": "BC Cloud", "app_version": "1.0.0"}
    headers = {"X-Registration-Invite": "wrong"}

    assert client.post("/tenant/register", headers=headers, json=payload).status_code == 403
    assert client.post("/tenant/register", headers=headers, json=payload).status_code == 403
    assert client.post("/tenant/register", headers=headers, json=payload).status_code == 429


def test_legacy_plaintext_token_is_migrated_after_successful_auth(client):
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

    response = client.get("/analytics/get-token", headers={"X-Tenant-Id": tenant_id, "X-Api-Token": api_token})

    assert response.status_code == 200
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
        assert tenant is not None
        assert tenant.api_token is None
        assert tenant.api_token_hash
        assert verify_api_token(api_token, tenant.api_token_hash)
