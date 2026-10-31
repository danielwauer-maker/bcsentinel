from __future__ import annotations


def _register_free_tenant(client) -> dict[str, str]:
    response = client.post(
        "/tenant/register",
        json={
            "environment_name": "BC Cloud",
            "app_version": "1.0.2.26-test",
            "preferred_language": "de",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def _headers(tenant: dict[str, str]) -> dict[str, str]:
    return {
        "X-Tenant-Id": tenant["tenant_id"],
        "X-Api-Token": tenant["api_token"],
    }


def test_registered_free_tenant_gets_exactly_one_deep_scan_without_paid_access(client):
    tenant = _register_free_tenant(client)
    headers = _headers(tenant)

    initial_status = client.get("/license/status", headers=headers)
    assert initial_status.status_code == 200, initial_status.text
    initial = initial_status.json()

    assert initial["plan"] == "free"
    assert initial["scan_credits_available"] == 1
    assert initial["can_run_deep_scan"] is True
    assert initial["assessment_access_active"] is False
    assert initial["validation_access_active"] is False
    assert initial["monitoring_active"] is False
    assert initial["can_view_dashboard"] is False
    assert initial["can_view_issue_details"] is False

    first_scan = client.post(
        "/scan/start",
        headers=headers,
        json={
            "tenant_id": tenant["tenant_id"],
            "run_id": "F1-FREE-0001",
            "scan_mode": "deep",
            "total_modules": 10,
            "company_name": "F1 Free Tenant",
            "environment_name": "BC Cloud",
        },
    )
    assert first_scan.status_code == 200, first_scan.text
    assert first_scan.json()["credit_consumed"] is True

    after_first_scan = client.get("/license/status", headers=headers)
    assert after_first_scan.status_code == 200, after_first_scan.text
    after = after_first_scan.json()

    assert after["scan_credits_available"] == 0
    assert after["can_run_deep_scan"] is False
    assert after["can_view_dashboard"] is False
    assert after["can_view_issue_details"] is False

    second_scan = client.post(
        "/scan/start",
        headers=headers,
        json={
            "tenant_id": tenant["tenant_id"],
            "run_id": "F1-FREE-0002",
            "scan_mode": "deep",
            "total_modules": 10,
            "company_name": "F1 Free Tenant",
            "environment_name": "BC Cloud",
        },
    )
    assert second_scan.status_code == 402, second_scan.text
    assert "scan credit or active monitoring subscription" in second_scan.json()["detail"].lower()
