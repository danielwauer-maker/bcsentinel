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


def _start_deep_scan(client, tenant: dict[str, str], run_id: str):
    return client.post(
        "/scan/start",
        headers=_headers(tenant),
        json={
            "tenant_id": tenant["tenant_id"],
            "run_id": run_id,
            "scan_mode": "deep",
            "total_modules": 10,
            "company_name": "F1 Free Tenant",
            "environment_name": "BC Cloud",
        },
    )


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

    first_scan = _start_deep_scan(client, tenant, "F1-FREE-0001")
    assert first_scan.status_code == 200, first_scan.text
    assert first_scan.json()["credit_consumed"] is True

    after_first_scan = client.get("/license/status", headers=headers)
    assert after_first_scan.status_code == 200, after_first_scan.text
    after = after_first_scan.json()

    assert after["scan_credits_available"] == 0
    assert after["can_run_deep_scan"] is False
    assert after["can_view_dashboard"] is False
    assert after["can_view_issue_details"] is False

    second_scan = _start_deep_scan(client, tenant, "F1-FREE-0002")
    assert second_scan.status_code == 402, second_scan.text
    assert "scan credit or active monitoring subscription" in second_scan.json()["detail"].lower()


def test_failed_initial_free_scan_restores_only_free_entry_credit(client):
    tenant = _register_free_tenant(client)
    headers = _headers(tenant)

    first_scan = _start_deep_scan(client, tenant, "F1-FREE-FAIL-0001")
    assert first_scan.status_code == 200, first_scan.text

    consumed = client.get("/license/status", headers=headers)
    assert consumed.status_code == 200, consumed.text
    assert consumed.json()["scan_credits_available"] == 0

    failed = client.post(
        "/scan/status/update",
        headers=headers,
        json={
            "tenant_id": tenant["tenant_id"],
            "run_id": "F1-FREE-FAIL-0001",
            "scan_mode": "deep",
            "status": "failed",
            "progress_percent": 25,
            "current_module": "System",
            "current_step": "Technical failure",
            "event_message": "Initial Free Entry scan failed",
            "event_level": "error",
            "total_modules": 10,
            "completed_modules": 2,
            "failed_modules": 1,
            "error_code": "F1_TEST_FAILURE",
            "error_message": "Synthetic initial Free Entry failure",
        },
    )
    assert failed.status_code == 200, failed.text

    restored = client.get("/license/status", headers=headers)
    assert restored.status_code == 200, restored.text
    restored_status = restored.json()
    assert restored_status["scan_credits_available"] == 1
    assert restored_status["can_run_deep_scan"] is True
    assert restored_status["assessment_access_active"] is False
    assert restored_status["validation_access_active"] is False
    assert restored_status["can_view_issue_details"] is False

    retry = _start_deep_scan(client, tenant, "F1-FREE-RETRY-0002")
    assert retry.status_code == 200, retry.text
    assert retry.json()["credit_consumed"] is True
