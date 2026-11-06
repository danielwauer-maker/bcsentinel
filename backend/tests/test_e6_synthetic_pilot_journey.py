from __future__ import annotations

from app.db import SessionLocal
from app.routers import account_auth
from app.security.oidc import VerifiedOIDCIdentity
from app.services.account_membership_service import get_or_create_user_identity, upsert_tenant_membership


def _identity() -> VerifiedOIDCIdentity:
    return VerifiedOIDCIdentity(
        provider="test-oidc",
        subject="e6-subject",
        email="pilot.multi@example.com",
        display_name="E6 Pilot User",
    )


def _seed_memberships(tenant_a: dict, tenant_b: dict) -> None:
    with SessionLocal() as db:
        user = get_or_create_user_identity(
            db,
            provider="test-oidc",
            provider_subject="e6-subject",
            email="pilot.multi@example.com",
            display_name="E6 Pilot User",
        )
        upsert_tenant_membership(
            db,
            user_identity_id=user.id,
            tenant_id=tenant_a["tenant_id"],
            role="ADMIN",
            status="active",
        )
        upsert_tenant_membership(
            db,
            user_identity_id=user.id,
            tenant_id=tenant_b["tenant_id"],
            role="VIEWER",
            status="active",
        )
        db.commit()


def _tenant_session(client, account_token: str, tenant_id: str) -> tuple[str, dict]:
    response = client.post(
        "/auth/account/tenant-session",
        json={"tenant_id": tenant_id},
        headers={"Authorization": f"Bearer {account_token}"},
    )
    assert response.status_code == 200, response.text
    return response.json()["session_token"], response.json()


def test_synthetic_pilot_journey_keeps_two_tenants_isolated(
    client,
    monkeypatch,
    tenant_factory,
    scan_factory,
):
    # 1. Public pilot funnel enters the same backend used by the landing page.
    lead = client.post(
        "/public/pilot-interest",
        json={
            "contact_name": "E6 Pilot User",
            "contact_email": "pilot.multi@example.com",
            "company_name": "Synthetic Pilot GmbH",
            "bc_context": "cloud",
            "message": "Synthetic multi-tenant controlled-pilot journey.",
            "preferred_language": "de",
            "source_page": "controlled-pilot",
            "privacy_consent": True,
            "website": "",
        },
    )
    assert lead.status_code == 202, lead.text
    assert lead.json()["reference"].startswith("PILOT-")

    # 2. The same account belongs to two tenants with independent commercial /
    # product states. Legacy premium remains a compatibility alias for paid
    # monitoring rights; free stays restricted.
    tenant_a = tenant_factory(plan="free", license_status="trial", tenant_id="ten_e6_free")
    tenant_b = tenant_factory(plan="premium", license_status="active", tenant_id="ten_e6_monitoring")
    scan_factory(tenant_id=tenant_a["tenant_id"], scan_id="scan_e6_free")
    scan_factory(tenant_id=tenant_b["tenant_id"], scan_id="scan_e6_monitoring")
    _seed_memberships(tenant_a, tenant_b)
    monkeypatch.setattr(account_auth, "verify_oidc_bearer_token", lambda token: _identity())

    # 3. Account login requires explicit tenant selection.
    login = client.post("/auth/account/session", headers={"Authorization": "Bearer external-e6-token"})
    assert login.status_code == 200, login.text
    login_body = login.json()
    assert login_body["tenant_count"] == 2
    assert login_body["requires_tenant_selection"] is True
    account_token = login_body["session_token"]

    tenant_list = client.get(
        "/auth/account/tenants",
        headers={"Authorization": f"Bearer {account_token}"},
    )
    assert tenant_list.status_code == 200
    by_id = {item["tenant_id"]: item for item in tenant_list.json()["tenants"]}
    assert by_id[tenant_a["tenant_id"]]["role"] == "ADMIN"
    assert by_id[tenant_b["tenant_id"]]["role"] == "VIEWER"
    assert by_id[tenant_a["tenant_id"]]["current_plan"] == "free"
    assert by_id[tenant_b["tenant_id"]]["current_plan"] == "premium"

    # 4. Tenant A session is scoped only to A and can load its runtime dashboard.
    token_a, session_a = _tenant_session(client, account_token, tenant_a["tenant_id"])
    assert session_a["role"] == "ADMIN"
    headers_a = {"Authorization": f"Bearer {token_a}"}
    status_a = client.get("/billing/subscription/status", headers=headers_a)
    assert status_a.status_code == 200
    assert status_a.json()["tenant_id"] == tenant_a["tenant_id"]

    analytics_token_a = client.get("/analytics/get-token", headers=headers_a)
    assert analytics_token_a.status_code == 200, analytics_token_a.text
    dashboard_a = client.get(
        f"/analytics/embed/data?embed_token={analytics_token_a.json()['token']}&scan_id=scan_e6_free"
    )
    assert dashboard_a.status_code == 200, dashboard_a.text
    assert dashboard_a.json()["selected_scan_id"] == "scan_e6_free"

    # 5. Switching to B mints a new tenant-bound session; monitoring/report
    # content is loaded only from B.
    token_b, session_b = _tenant_session(client, account_token, tenant_b["tenant_id"])
    assert session_b["role"] == "VIEWER"
    headers_b = {"Authorization": f"Bearer {token_b}"}
    status_b = client.get("/billing/subscription/status", headers=headers_b)
    assert status_b.status_code == 200
    assert status_b.json()["tenant_id"] == tenant_b["tenant_id"]

    analytics_token_b = client.get("/analytics/get-token", headers=headers_b)
    assert analytics_token_b.status_code == 200, analytics_token_b.text
    dashboard_b = client.get(
        f"/analytics/embed/data?embed_token={analytics_token_b.json()['token']}&scan_id=scan_e6_monitoring"
    )
    assert dashboard_b.status_code == 200, dashboard_b.text
    assert dashboard_b.json()["selected_scan_id"] == "scan_e6_monitoring"
    assert dashboard_b.json()["product_access"]["monitoring_active"] is True

    executive = client.get("/reports/executive/scan_e6_monitoring", headers=headers_b)
    assert executive.status_code == 200, executive.text
    assert executive.json()["scan_id"] == "scan_e6_monitoring"

    monitoring = client.get("/reports/monitoring/scan_e6_monitoring", headers=headers_b)
    assert monitoring.status_code == 200, monitoring.text
    assert monitoring.json()["scan_id"] == "scan_e6_monitoring"

    # 6. A valid A session still cannot see B's report. Foreign/nonexistent
    # report IDs intentionally collapse to the same 404 boundary.
    foreign = client.get("/reports/executive/scan_e6_monitoring", headers=headers_a)
    assert foreign.status_code == 404

    wrong_header = client.get(
        "/billing/subscription/status",
        headers={"Authorization": f"Bearer {token_b}", "X-Tenant-Id": tenant_a["tenant_id"]},
    )
    assert wrong_header.status_code == 403
