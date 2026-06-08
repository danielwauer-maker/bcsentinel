from types import SimpleNamespace
import base64
from datetime import datetime, timedelta, timezone

import pytest

from app.db import SessionLocal
from app.models import TenantProductEntitlement, TenantScanCredit


def _admin_auth_header() -> dict[str, str]:
    token = base64.b64encode(b"admin-test:admin-password-for-tests-123").decode("ascii")
    return {"Authorization": f"Basic {token}"}


def _admin_csrf(client, path: str) -> dict[str, str]:
    response = client.get(path, headers=_admin_auth_header())
    assert response.status_code == 200
    token = client.cookies.get("bcs_csrf")
    assert token
    return {"csrf_token": token}


def _deep_scan_payload(tenant_id: str, scan_id: str) -> dict:
    return {
        "tenant_id": tenant_id,
        "scan_id": scan_id,
        "scan_type": "deep",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "data_score": 88,
        "checks_count": 10,
        "issues_count": 1,
        "premium_available": True,
        "headline": "Smoke scan",
        "rating": "good",
        "data_profile": {
            "customers": 10,
            "vendors": 5,
            "items": 12,
            "total_records": 27,
        },
        "module_scores": {
            "system": 90,
            "finance": 85,
            "sales": 90,
            "purchasing": 90,
            "inventory": 90,
            "crm": 90,
            "manufacturing": 90,
            "service": 90,
            "jobs": 90,
            "hr": 90,
        },
        "issues": [
            {
                "code": "SMOKE_ISSUE",
                "category": "master_data",
                "title": "Smoke issue",
                "severity": "medium",
                "affected_count": 1,
                "premium_only": False,
                "recommendation_preview": "Review smoke issue.",
                "estimated_impact_eur": 100.0,
            }
        ],
    }


@pytest.mark.parametrize(
    ("product_code", "settings_key", "price_id", "expected_mode"),
    [
        ("assessment", "STRIPE_PRICE_ID_ASSESSMENT", "price_assessment", "payment"),
        ("validation_check", "STRIPE_PRICE_ID_VALIDATION_CHECK", "price_validation_check", "payment"),
        ("monitoring_monthly", "STRIPE_PRICE_ID_MONITORING_MONTHLY", "price_monitoring_monthly", "subscription"),
        ("monitoring_annual", "STRIPE_PRICE_ID_MONITORING_ANNUAL", "price_monitoring_annual", "subscription"),
    ],
)
def test_product_checkout_uses_expected_stripe_mode(
    client,
    tenant_factory,
    auth_header_factory,
    settings_state,
    monkeypatch,
    product_code,
    settings_key,
    price_id,
    expected_mode,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    settings_state(
        STRIPE_SECRET_KEY="sk_test",
        **{settings_key: price_id},
        APP_BASE_URL="https://app.example.com",
    )
    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(id=f"cs_{product_code}", url=f"https://stripe.example/{product_code}")

    monkeypatch.setattr("app.routers.billing.stripe.checkout.Session.create", fake_create)

    response = client.post(
        "/billing/checkout/session",
        headers=auth_header_factory(tenant),
        json={"tenant_id": tenant["tenant_id"], "product_code": product_code},
    )

    assert response.status_code == 200
    assert response.json()["product_code"] == product_code
    assert captured["mode"] == expected_mode
    assert captured["line_items"] == [{"price": price_id, "quantity": 1}]
    assert captured["metadata"]["product_code"] == product_code


@pytest.mark.parametrize("product_code", ["assessment", "validation_check"])
def test_checkout_completed_grants_scan_credit_for_one_time_product(
    client,
    tenant_factory,
    product_code,
):
    tenant = tenant_factory(plan="free", license_status="trial")

    response = client.post(
        "/billing/webhook",
        json={
            "provider": "manual",
            "event_id": "evt_assessment_paid",
            "event_type": "checkout.session.completed",
            "tenant_id": tenant["tenant_id"],
            "subscription": {
                "id": f"cs_manual_{product_code}",
                "product_code": product_code,
                "payment_status": "paid",
                "currency": "EUR",
                "amount_total": 79.0 if product_code == "assessment" else 49.0,
            },
        },
    )

    assert response.status_code == 200
    with SessionLocal() as db:
        credit = db.query(TenantScanCredit).filter(TenantScanCredit.tenant_id == tenant["tenant_id"]).one()
        assert credit.product_code == product_code
        assert credit.status == "available"


@pytest.mark.parametrize("product_code", ["monitoring_monthly", "monitoring_annual"])
def test_subscription_webhook_activates_monitoring_product(
    client,
    tenant_factory,
    auth_header_factory,
    product_code,
):
    tenant = tenant_factory(plan="free", license_status="trial")

    response = client.post(
        "/billing/webhook",
        json={
            "provider": "manual",
            "event_id": f"evt_{product_code}_active",
            "event_type": "subscription.updated",
            "tenant_id": tenant["tenant_id"],
            "subscription": {
                "id": f"sub_{product_code}",
                "product_code": product_code,
                "status": "active",
                "currency": "EUR",
                "amount_monthly": 99.0 if product_code == "monitoring_monthly" else 82.5,
            },
        },
    )
    license_response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert response.status_code == 200
    assert license_response.status_code == 200
    payload = license_response.json()
    assert payload["monitoring_active"] is True
    assert product_code in payload["active_products"]
    with SessionLocal() as db:
        entitlement = db.query(TenantProductEntitlement).filter(
            TenantProductEntitlement.tenant_id == tenant["tenant_id"],
            TenantProductEntitlement.product_code == product_code,
        ).one()
        assert entitlement.status == "active"


def test_license_status_exposes_scan_credits_and_product_entitlements(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    client.post(
        f"/admin/tenants/{tenant['tenant_id']}/product-grant",
        headers=_admin_auth_header(),
        data={
            **_admin_csrf(client, f"/admin/tenants/{tenant['tenant_id']}"),
            "product_code": "validation_check",
        },
        follow_redirects=False,
    )

    response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert response.status_code == 200
    payload = response.json()
    assert payload["scan_credits_available"] == 1
    assert payload["can_run_deep_scan"] is True
    assert payload["can_view_dashboard"] is True
    assert payload["can_view_issue_details"] is True
    assert payload["validation_access_active"] is True
    assert payload["dashboard_access_until"]
    assert "deep_scan" in payload["features"]
    assert "executive_report" in payload["features"]


def test_legacy_premium_tenant_still_gets_monitoring_features(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="premium", license_status="active")

    response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert response.status_code == 200
    payload = response.json()
    assert payload["monitoring_active"] is True
    assert "monitoring_active" in payload["features"]
    assert "billing_portal" in payload["features"]
    assert payload["can_run_deep_scan"] is True
    assert payload["can_view_dashboard"] is True


def test_deep_scan_without_credit_or_monitoring_is_blocked(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")

    response = client.post(
        "/scan/sync",
        headers=auth_header_factory(tenant),
        json=_deep_scan_payload(tenant["tenant_id"], "RUN_NO_CREDIT"),
    )

    assert response.status_code == 402
    assert "scan credit" in response.json()["detail"].lower()


def test_assessment_credit_allows_one_deep_scan_and_is_consumed(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    client.post(
        f"/admin/tenants/{tenant['tenant_id']}/product-grant",
        headers=_admin_auth_header(),
        data={
            **_admin_csrf(client, f"/admin/tenants/{tenant['tenant_id']}"),
            "product_code": "assessment",
        },
        follow_redirects=False,
    )

    first_response = client.post(
        "/scan/sync",
        headers=auth_header_factory(tenant),
        json=_deep_scan_payload(tenant["tenant_id"], "RUN_WITH_CREDIT"),
    )
    second_response = client.post(
        "/scan/sync",
        headers=auth_header_factory(tenant),
        json=_deep_scan_payload(tenant["tenant_id"], "RUN_AFTER_CREDIT"),
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 402
    with SessionLocal() as db:
        credits = db.query(TenantScanCredit).filter(TenantScanCredit.tenant_id == tenant["tenant_id"]).all()
        assert len(credits) == 1
        assert credits[0].status == "consumed"
        assert credits[0].consumed_scan_id == "RUN_WITH_CREDIT"

    license_response = client.get("/license/status", headers=auth_header_factory(tenant))
    assert license_response.status_code == 200
    license_payload = license_response.json()
    assert license_payload["scan_credits_available"] == 0
    assert license_payload["can_run_deep_scan"] is False
    assert license_payload["can_view_dashboard"] is True
    assert license_payload["can_view_issue_details"] is True
    assert license_payload["assessment_access_active"] is True


def test_assessment_dashboard_payload_separates_access_from_monitoring(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    client.post(
        f"/admin/tenants/{tenant['tenant_id']}/product-grant",
        headers=_admin_auth_header(),
        data={
            **_admin_csrf(client, f"/admin/tenants/{tenant['tenant_id']}"),
            "product_code": "assessment",
        },
        follow_redirects=False,
    )
    scan_response = client.post(
        "/scan/sync",
        headers=auth_header_factory(tenant),
        json=_deep_scan_payload(tenant["tenant_id"], "RUN_ASSESSMENT_DASHBOARD"),
    )
    assert scan_response.status_code == 200

    token_response = client.get("/analytics/get-token", headers=auth_header_factory(tenant))
    assert token_response.status_code == 200
    analytics_token = token_response.json()["token"]

    response = client.get(f"/analytics/embed/data?embed_token={analytics_token}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["visibility"]["is_premium"] is True
    assert payload["product_access"]["monitoring_active"] is False
    assert payload["subscription"]["plan_label"] == "Assessment / Validation access"
    assert payload["subscription"]["price_monthly"] == 0.0
    assert payload["subscription"]["annual_cost"] == 0.0
    assert payload["subscription"]["cta_label"] == "Start Monitoring"
    assert payload["subscription"]["cta_product_code"] == "monitoring_monthly"
    assert payload["last_updated"][2] == "."
    assert len(payload["last_updated"].split(" ")[1].split(":")) == 3


def test_monitoring_tenant_can_run_repeated_deep_scans_without_consuming_credits(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    client.post(
        f"/admin/tenants/{tenant['tenant_id']}/product-grant",
        headers=_admin_auth_header(),
        data={
            **_admin_csrf(client, f"/admin/tenants/{tenant['tenant_id']}"),
            "product_code": "monitoring_monthly",
        },
        follow_redirects=False,
    )

    first_response = client.post(
        "/scan/sync",
        headers=auth_header_factory(tenant),
        json=_deep_scan_payload(tenant["tenant_id"], "RUN_MONITORING_1"),
    )
    second_response = client.post(
        "/scan/sync",
        headers=auth_header_factory(tenant),
        json=_deep_scan_payload(tenant["tenant_id"], "RUN_MONITORING_2"),
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200


def test_consumed_assessment_access_expires_after_seven_days(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    client.post(
        f"/admin/tenants/{tenant['tenant_id']}/product-grant",
        headers=_admin_auth_header(),
        data={
            **_admin_csrf(client, f"/admin/tenants/{tenant['tenant_id']}"),
            "product_code": "assessment",
        },
        follow_redirects=False,
    )
    response = client.post(
        "/scan/sync",
        headers=auth_header_factory(tenant),
        json=_deep_scan_payload(tenant["tenant_id"], "RUN_EXPIRED_ACCESS"),
    )
    assert response.status_code == 200

    expired_at = datetime.now(timezone.utc) - timedelta(days=8)
    with SessionLocal() as db:
        credit = db.query(TenantScanCredit).filter(TenantScanCredit.tenant_id == tenant["tenant_id"]).one()
        credit.consumed_at_utc = expired_at
        db.commit()

    license_response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert license_response.status_code == 200
    payload = license_response.json()
    assert payload["assessment_access_active"] is False
    assert payload["can_run_deep_scan"] is False
    assert payload["can_view_dashboard"] is False
    assert payload["can_view_issue_details"] is False


def test_executive_report_requires_active_product_access(
    client,
    tenant_factory,
    auth_header_factory,
    scan_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="RUN_REPORT_LOCKED")

    response = client.get(
        "/reports/executive/RUN_REPORT_LOCKED",
        headers=auth_header_factory(tenant),
    )

    assert response.status_code == 402

    client.post(
        f"/admin/tenants/{tenant['tenant_id']}/product-grant",
        headers=_admin_auth_header(),
        data={
            **_admin_csrf(client, f"/admin/tenants/{tenant['tenant_id']}"),
            "product_code": "validation_check",
        },
        follow_redirects=False,
    )

    unlocked_response = client.get(
        "/reports/executive/RUN_REPORT_LOCKED",
        headers=auth_header_factory(tenant),
    )
    assert unlocked_response.status_code == 200
