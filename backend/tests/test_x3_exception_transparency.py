from __future__ import annotations

from app.main import app


def test_pre_pilot_account_and_commercial_routes_are_mounted():
    paths = {route.path for route in app.routes}
    assert "/auth/account/tenants" in paths
    assert "/auth/account/tenant-session" in paths
    assert "/account/tenant/commercials" in paths
    assert "/account/tenant/support-access" in paths


def test_exception_snapshot_is_machine_written_and_dashboard_readable(
    client,
    tenant_factory,
    deep_scan_factory,
    auth_header_factory,
):
    tenant = tenant_factory()
    deep_scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_exception_test")
    headers = auth_header_factory(tenant)

    payload = {
        "company_id": "CRONUS DE",
        "exceptions": [
            {
                "source_exception_entry_no": 17,
                "table_id": 18,
                "record_system_id": "11111111-1111-1111-1111-111111111111",
                "record_no": "10000",
                "record_caption": "Demo Customer",
                "issue_code": "DUPLICATE_CUSTOMERS",
                "reason": "Approved exception for separate invoice recipient",
                "exception_created_by": "BC ADMIN",
            }
        ],
    }

    write = client.post(
        "/scans/scan_exception_test/exception-snapshot",
        json=payload,
        headers=headers,
    )
    assert write.status_code == 200, write.text
    assert write.json()["captured_exception_count"] == 1
    assert write.json()["immutable"] is True

    read = client.get(
        "/scans/scan_exception_test/exceptions",
        headers=headers,
    )
    assert read.status_code == 200, read.text
    body = read.json()
    assert body["snapshot_captured"] is True
    assert body["exceptions_applied"] is True
    assert body["exception_count"] == 1
    assert body["exceptions"][0]["issue_code"] == "DUPLICATE_CUSTOMERS"
    assert body["exceptions"][0]["reason"] == "Approved exception for separate invoice recipient"

    second_write = client.post(
        "/scans/scan_exception_test/exception-snapshot",
        json=payload,
        headers=headers,
    )
    assert second_write.status_code == 409


def test_empty_exception_snapshot_is_captured_once_and_stays_immutable(
    client,
    tenant_factory,
    deep_scan_factory,
    auth_header_factory,
):
    tenant = tenant_factory()
    deep_scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_exception_empty")
    headers = auth_header_factory(tenant)

    write = client.post(
        "/scans/scan_exception_empty/exception-snapshot",
        json={"company_id": "CRONUS DE", "exceptions": []},
        headers=headers,
    )
    assert write.status_code == 200, write.text
    assert write.json()["captured_exception_count"] == 0
    assert write.json()["immutable"] is True

    read = client.get(
        "/scans/scan_exception_empty/exceptions",
        headers=headers,
    )
    assert read.status_code == 200, read.text
    body = read.json()
    assert body["snapshot_captured"] is True
    assert body["exceptions_applied"] is False
    assert body["exception_count"] == 0
    assert body["exceptions"] == []
    assert body["captured_at_utc"] is not None

    second_write = client.post(
        "/scans/scan_exception_empty/exception-snapshot",
        json={"company_id": "CRONUS DE", "exceptions": []},
        headers=headers,
    )
    assert second_write.status_code == 409


def test_exception_snapshot_write_rejects_bearer_only_dashboard_session(client):
    response = client.post(
        "/scans/unknown/exception-snapshot",
        json={"exceptions": []},
        headers={"Authorization": "Bearer not-a-machine-token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Machine tenant credentials are required."
