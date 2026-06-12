from __future__ import annotations


def test_security_headers_are_set(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "frame-ancestors" in response.headers["Content-Security-Policy"]


def test_analytics_embed_keeps_business_central_frame_ancestor(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory()
    token_response = client.get("/analytics/get-token", headers=auth_header_factory(tenant))

    assert token_response.status_code == 200
    token = token_response.json()["token"]
    response = client.get(f"/analytics/embed?embed_token={token}", follow_redirects=False)

    assert response.status_code == 303
    assert "businesscentral.dynamics.com" in response.headers["Content-Security-Policy"]
