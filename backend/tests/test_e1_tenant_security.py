from __future__ import annotations

from datetime import datetime, timezone

from app.db import SessionLocal
from app.models import Tenant
from app.remediation_models import RemediationActionRead
from app.security.token_hash import hash_api_token
from app.services.product_license_service import PRODUCT_ASSESSMENT, grant_product_entitlement
from app.services.scan_status_service import create_or_get_scan_run
from app.services.tenant_access_service import set_tenant_status


def _grant_assessment(tenant_id: str) -> None:
    with SessionLocal() as db:
        grant_product_entitlement(
            db,
            tenant_id=tenant_id,
            product_code=PRODUCT_ASSESSMENT,
            source="e1_test",
        )
        db.commit()


def _set_status(tenant_id: str, status: str) -> None:
    with SessionLocal() as db:
        set_tenant_status(
            db,
            tenant_id=tenant_id,
            status=status,
            reason="E1 test",
            updated_by="pytest",
        )
        db.commit()


def _create_action(tenant_id: str, action_id: str) -> None:
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(
            RemediationActionRead(
                action_id=action_id,
                tenant_id=tenant_id,
                company_id="CRONUS",
                finding_key="CUSTOMERS_MISSING_EMAIL",
                title="Complete customer email data",
                description="E1 isolation fixture",
                status="open",
                priority="high",
                source="e1_test",
                created_at_utc=now,
                updated_at_utc=now,
                synced_at_utc=now,
            )
        )
        db.commit()


def test_unknown_tenant_and_wrong_token_have_same_failure(client, tenant_factory):
    tenant = tenant_factory()
    wrong_token = client.get(
        "/license/status",
        headers={"X-Tenant-Id": tenant["tenant_id"], "X-Api-Token": "wrong-token"},
    )
    unknown_tenant = client.get(
        "/license/status",
        headers={"X-Tenant-Id": "ten_does_not_exist", "X-Api-Token": "wrong-token"},
    )

    assert wrong_token.status_code == 403
    assert unknown_tenant.status_code == 403
    assert wrong_token.json()["detail"] == "Invalid tenant credentials."
    assert unknown_tenant.json()["detail"] == wrong_token.json()["detail"]


def test_short_lived_dashboard_session_authenticates_without_raw_api_token(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory()
    exchange = client.post("/auth/session", headers=auth_header_factory(tenant))

    assert exchange.status_code == 200
    body = exchange.json()
    assert body["tenant_id"] == tenant["tenant_id"]
    assert body["token_type"] == "Bearer"
    assert body["expires_in_seconds"] == 900
    assert body["scope"] == "tenant:dashboard"
    assert body["role"] == "dashboard_runtime"
    assert body["tenant_status"] == "active"
    assert tenant["api_token"] not in body["session_token"]

    status_response = client.get(
        "/license/status",
        headers={"Authorization": f"Bearer {body['session_token']}"},
    )
    assert status_response.status_code == 200
    assert status_response.json()["tenant_id"] == tenant["tenant_id"]
    assert status_response.json()["tenant_status"] == "active"


def test_dashboard_session_is_revoked_by_api_token_rotation(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory()
    exchange = client.post("/auth/session", headers=auth_header_factory(tenant))
    session_token = exchange.json()["session_token"]

    with SessionLocal() as db:
        row = db.query(Tenant).filter(Tenant.tenant_id == tenant["tenant_id"]).one()
        row.api_token_hash = hash_api_token("rotated-api-token")
        row.api_token = None
        db.commit()

    response = client.get(
        "/license/status",
        headers={"Authorization": f"Bearer {session_token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid tenant credentials."


def test_suspended_tenant_blocks_valid_machine_and_browser_credentials_before_entitlements(
    client,
    tenant_factory,
    auth_header_factory,
    scan_factory,
):
    tenant = tenant_factory()
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_e1_suspended")
    _grant_assessment(tenant["tenant_id"])

    exchange = client.post("/auth/session", headers=auth_header_factory(tenant))
    assert exchange.status_code == 200
    session_token = exchange.json()["session_token"]
    _set_status(tenant["tenant_id"], "suspended")

    machine_response = client.get("/license/status", headers=auth_header_factory(tenant))
    browser_response = client.get(
        "/reports/executive/scan_e1_suspended",
        headers={"Authorization": f"Bearer {session_token}"},
    )

    assert machine_response.status_code == 403
    assert browser_response.status_code == 403
    assert machine_response.json()["detail"] == "Tenant access is not active."
    assert browser_response.json()["detail"] == "Tenant access is not active."


def test_authentication_never_implies_paid_entitlement(
    client,
    tenant_factory,
    auth_header_factory,
    scan_factory,
):
    tenant = tenant_factory()
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_e1_entitlement")

    authenticated = client.get("/license/status", headers=auth_header_factory(tenant))
    locked_report = client.get(
        "/reports/executive/scan_e1_entitlement",
        headers=auth_header_factory(tenant),
    )

    assert authenticated.status_code == 200
    assert authenticated.json()["product_access"]["can_view_executive_report"] is False
    assert locked_report.status_code == 402

    _grant_assessment(tenant["tenant_id"])
    unlocked_report = client.get(
        "/reports/executive/scan_e1_entitlement",
        headers=auth_header_factory(tenant),
    )
    assert unlocked_report.status_code == 200


def test_report_resource_existence_is_masked_across_tenants(
    client,
    tenant_factory,
    auth_header_factory,
    scan_factory,
):
    owner = tenant_factory()
    other = tenant_factory()
    scan_factory(tenant_id=owner["tenant_id"], scan_id="scan_e1_private")
    _grant_assessment(other["tenant_id"])

    foreign = client.get(
        "/reports/executive/scan_e1_private",
        headers=auth_header_factory(other),
    )
    missing = client.get(
        "/reports/executive/scan_e1_missing",
        headers=auth_header_factory(other),
    )

    assert foreign.status_code == 404
    assert missing.status_code == 404
    assert foreign.json()["detail"] == "Report not found."
    assert missing.json()["detail"] == foreign.json()["detail"]


def test_remediation_detail_and_list_do_not_cross_tenant_boundary(
    client,
    tenant_factory,
    auth_header_factory,
):
    owner = tenant_factory()
    other = tenant_factory()
    _create_action(owner["tenant_id"], "action_e1_private")

    detail = client.get(
        "/remediation/actions/action_e1_private",
        headers=auth_header_factory(other),
    )
    listing = client.get(
        "/remediation/actions",
        headers=auth_header_factory(other),
    )

    assert detail.status_code == 404
    assert listing.status_code == 200
    assert all(item["action_id"] != "action_e1_private" for item in listing.json()["items"])


def test_scan_status_is_scoped_to_authenticated_tenant(
    client,
    tenant_factory,
    auth_header_factory,
):
    owner = tenant_factory()
    other = tenant_factory()
    with SessionLocal() as db:
        create_or_get_scan_run(
            db,
            run_id="run_e1_private",
            tenant_id=owner["tenant_id"],
            status="running",
        )
        db.commit()

    response = client.get(
        "/scan/status/run_e1_private",
        headers=auth_header_factory(other),
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Scan status not found."


def test_payload_tenant_mismatch_is_authorization_failure_and_preserves_data(
    client,
    tenant_factory,
    auth_header_factory,
    scan_factory,
):
    owner = tenant_factory()
    other = tenant_factory()
    scan_factory(tenant_id=other["tenant_id"], scan_id="scan_e1_other")

    response = client.post(
        "/scan/reconcile",
        headers=auth_header_factory(owner),
        json={"tenant_id": other["tenant_id"], "scan_ids": []},
    )

    assert response.status_code == 403
    with SessionLocal() as db:
        from app.models import Scan

        assert db.query(Scan).filter(Scan.scan_id == "scan_e1_other").one_or_none() is not None


def test_shared_report_link_is_invalidated_when_tenant_is_suspended(
    client,
    tenant_factory,
    auth_header_factory,
    scan_factory,
    settings_state,
):
    settings_state(APP_BASE_URL="https://app.bcsentinel.com")
    tenant = tenant_factory()
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_e1_shared")
    _grant_assessment(tenant["tenant_id"])

    link_response = client.post(
        "/reports/executive/scan_e1_shared/share-link",
        headers=auth_header_factory(tenant),
        json={"report_type": "html"},
    )
    assert link_response.status_code == 200
    share_url = link_response.json()["url"]

    _set_status(tenant["tenant_id"], "deactivated")
    shared_response = client.get(share_url)
    assert shared_response.status_code == 403
    assert shared_response.json()["detail"] == "Tenant access is not active."
