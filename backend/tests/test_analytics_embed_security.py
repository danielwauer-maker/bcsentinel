from __future__ import annotations

from datetime import datetime, timezone

from jose import jwt

from app.core.settings import settings
from app.routers.analytics import ANALYTICS_EMBED_TOKEN_TYPE
from app.security.token import ALGORITHM, create_token


def test_analytics_get_token_returns_short_lived_embed_token(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory()

    response = client.get(
        "/analytics/get-token?company=CRONUS&environment=BC%20Cloud&tenant_id="
        + tenant["tenant_id"],
        headers=auth_header_factory(tenant),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == ANALYTICS_EMBED_TOKEN_TYPE
    assert body["expires_in_seconds"] == 300

    payload = jwt.decode(body["token"], settings.SECRET_KEY, algorithms=[ALGORITHM])
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
