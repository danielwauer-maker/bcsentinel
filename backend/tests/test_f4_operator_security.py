from __future__ import annotations

import base64


def _admin_auth_header() -> dict[str, str]:
    token = base64.b64encode(b"admin-test:admin-password-for-tests-123").decode("ascii")
    return {"Authorization": f"Basic {token}"}


def test_operator_console_requires_admin_basic_auth(client):
    response = client.get("/admin/operator")
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Basic"


def test_operator_console_accepts_valid_admin_auth_and_issues_csrf(client):
    response = client.get("/admin/operator", headers=_admin_auth_header())
    assert response.status_code == 200
    assert "BCSentinel Operator Console" in response.text
    assert client.cookies.get("bcs_csrf")


def test_operator_write_rejects_missing_csrf(client, tenant_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    response = client.post(
        f"/admin/operator/{tenant['tenant_id']}/grant-assessment",
        headers=_admin_auth_header(),
        data={
            "sales_channel": "fiverr",
            "external_order_reference": "FIV-CSRF-001",
            "note": "should not execute",
        },
        follow_redirects=False,
    )
    assert response.status_code == 422 or response.status_code == 403


def test_operator_write_rejects_invalid_csrf(client, tenant_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    response = client.post(
        f"/admin/operator/{tenant['tenant_id']}/grant-assessment",
        headers=_admin_auth_header(),
        data={
            "csrf_token": "invalid",
            "sales_channel": "fiverr",
            "external_order_reference": "FIV-CSRF-002",
            "note": "should not execute",
        },
        follow_redirects=False,
    )
    assert response.status_code == 403
