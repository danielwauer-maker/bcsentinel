from __future__ import annotations

import base64
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _admin_auth_header() -> dict[str, str]:
    token = base64.b64encode(b"admin-test:admin-password-for-tests-123").decode("ascii")
    return {"Authorization": f"Basic {token}"}


def test_reverse_proxy_auth_endpoint_requires_existing_admin_credentials(client):
    unauthenticated = client.get("/_internal/admin-auth")
    assert unauthenticated.status_code == 401
    assert unauthenticated.headers["www-authenticate"] == "Basic"

    authenticated = client.get("/_internal/admin-auth", headers=_admin_auth_header())
    assert authenticated.status_code == 204
    assert authenticated.content == b""


def test_nginx_proxy_contract_secures_prefix_assets_apis_and_websockets():
    config = (ROOT / "config" / "nginx" / "bcsentinel.conf").read_text(encoding="utf-8")

    # Each production and DEV vhost has an exact and a descendants location.
    assert config.count("location = /admin/ai-control-center {") == 4
    assert config.count("location ^~ /admin/ai-control-center/ {") == 4
    assert config.count("auth_request /_bcsentinel_internal/ai-control-center-admin-auth;") == 8
    assert config.count("proxy_pass http://127.0.0.1:8092/;") == 8
    assert config.count("proxy_set_header Authorization \"\";") >= 8
    assert config.count("proxy_set_header Upgrade $http_upgrade;") == 8
    assert config.count("proxy_set_header Connection $http_connection;") == 8
    assert "/etc/nginx/snippets/bcsentinel-ai-control-center-proxy-auth.conf" in config
    assert "internal;" in config
