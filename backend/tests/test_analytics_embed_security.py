from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.settings import settings
from app.routers.analytics import ANALYTICS_EMBED_TOKEN_TYPE
from app.security.token import ALGORITHM, create_token
from app.db import SessionLocal
from app.models import TenantProductEntitlement
from app.services.access_control_service import TOKEN_AUDIENCE


def _grant_dashboard_access(tenant_id: str) -> None:
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(
            TenantProductEntitlement(
                tenant_id=tenant_id,
                product_code="full_analysis",
                status="active",
                source="analytics_test",
                valid_until_utc=now + timedelta(days=7),
                created_at_utc=now,
                updated_at_utc=now,
            )
        )
        db.commit()


def test_analytics_get_token_returns_short_lived_embed_token(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory()
    _grant_dashboard_access(tenant["tenant_id"])

    response = client.get(
        "/analytics/get-token?company=CRONUS&environment=BC%20Cloud&tenant_id="
        + tenant["tenant_id"],
        headers=auth_header_factory(tenant),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == ANALYTICS_EMBED_TOKEN_TYPE
    assert body["expires_in_seconds"] == 300

    payload = jwt.decode(body["token"], settings.SECRET_KEY, algorithms=[ALGORITHM], audience=TOKEN_AUDIENCE)
    assert payload["type"] == ANALYTICS_EMBED_TOKEN_TYPE
    assert payload["scope"] == "analytics:embed"
    assert payload["tenant_id"] == tenant["tenant_id"]
    assert payload["company"] == "CRONUS"

    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    ttl_seconds = (expires_at - datetime.now(timezone.utc)).total_seconds()
    assert 0 < ttl_seconds <= 300
    assert "api_token" not in body["token"].lower()


def test_analytics_embed_token_sets_cookie_and_redirects_without_token_in_location(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory()
    _grant_dashboard_access(tenant["tenant_id"])
    token_response = client.get("/analytics/get-token", headers=auth_header_factory(tenant))
    embed_token = token_response.json()["token"]

    response = client.get(f"/analytics/embed?embed_token={embed_token}", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/analytics/embed"
    assert "token=" not in response.headers["location"].lower()
    assert "bcs_at=" in response.headers["set-cookie"]
    assert "httponly" in response.headers["set-cookie"].lower()


def test_analytics_data_rejects_generic_non_embed_token(client, tenant_factory):
    tenant = tenant_factory()
    generic_token = create_token({"tenant_id": tenant["tenant_id"], "scope": "generic"})

    response = client.get(f"/analytics/embed/data?embed_token={generic_token}")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid analytics embed token."


def _analytics_embed_token(client, tenant, auth_header_factory):
    _grant_dashboard_access(tenant["tenant_id"])
    token_response = client.get("/analytics/get-token", headers=auth_header_factory(tenant))
    assert token_response.status_code == 200
    return token_response.json()["token"]


def test_dev_demo_mode_returns_demo_payload_without_scans(client, tenant_factory, auth_header_factory, monkeypatch):
    monkeypatch.setattr(settings, "ENV", "dev")
    monkeypatch.setattr(settings, "ANALYTICS_DEMO_MODE", True)
    tenant = tenant_factory()
    embed_token = _analytics_embed_token(client, tenant, auth_header_factory)

    response = client.get("/analytics/embed/data", params={"embed_token": embed_token})

    assert response.status_code == 200
    body = response.json()
    assert body["is_demo"] is True
    assert body["data_source"] == "demo_preview"
    assert "Demo Preview" in body["subtitle"]
    assert body["selected_scan_id"] == "demo_preview_scan"
    assert body["free_insights"]["top_findings"]


def test_demo_mode_disabled_uses_fallback_without_scans(client, tenant_factory, auth_header_factory, monkeypatch):
    monkeypatch.setattr(settings, "ENV", "dev")
    monkeypatch.setattr(settings, "ANALYTICS_DEMO_MODE", False)
    tenant = tenant_factory()
    embed_token = _analytics_embed_token(client, tenant, auth_header_factory)

    response = client.get("/analytics/embed/data", params={"embed_token": embed_token})

    assert response.status_code == 200
    body = response.json()
    assert body.get("is_demo") is not True
    assert body["selected_scan_id"] is None
    assert body["recent_scans"] == []


def test_prod_demo_mode_flag_uses_fallback_without_scans(client, tenant_factory, auth_header_factory, monkeypatch):
    monkeypatch.setattr(settings, "ENV", "prod")
    monkeypatch.setattr(settings, "ANALYTICS_DEMO_MODE", True)
    tenant = tenant_factory()
    embed_token = _analytics_embed_token(client, tenant, auth_header_factory)

    response = client.get("/analytics/embed/data", params={"embed_token": embed_token})

    assert response.status_code == 200
    body = response.json()
    assert body.get("is_demo") is not True
    assert body["selected_scan_id"] is None
    assert body["recent_scans"] == []


def test_real_scan_takes_precedence_over_demo_mode(
    client,
    tenant_factory,
    auth_header_factory,
    scan_factory,
    monkeypatch,
):
    monkeypatch.setattr(settings, "ENV", "dev")
    monkeypatch.setattr(settings, "ANALYTICS_DEMO_MODE", True)
    tenant = tenant_factory()
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="real_scan_demo_precedence")
    embed_token = _analytics_embed_token(client, tenant, auth_header_factory)

    response = client.get("/analytics/embed/data", params={"embed_token": embed_token})

    assert response.status_code == 200
    body = response.json()
    assert body.get("is_demo") is not True
    assert body["selected_scan_id"] == "real_scan_demo_precedence"
    assert body["kpis"]["health_score"] == 80
