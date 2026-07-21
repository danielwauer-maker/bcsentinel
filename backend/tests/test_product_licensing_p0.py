from types import SimpleNamespace
import base64
from datetime import datetime, timedelta, timezone

import pytest

from app.db import SessionLocal
from app.models import Subscription, Tenant, TenantProductEntitlement, TenantScanCredit


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
    ("product_code", "settings_key", "price_id", "expected_mode", "expected_product_code"),
    [
        ("assessment", "STRIPE_PRICE_ID_ASSESSMENT", "price_assessment", "payment", "full_analysis"),
        ("full_analysis", "STRIPE_PRICE_ID_ASSESSMENT", "price_full_analysis", "payment", "full_analysis"),
        ("validation_check", "STRIPE_PRICE_ID_VALIDATION_CHECK", "price_validation_check", "payment", "validation_check"),
        ("monitoring_monthly", "STRIPE_PRICE_ID_MONITORING_MONTHLY", "price_monitoring_monthly", "subscription", "monitoring_monthly"),
        ("monitoring_annual", "STRIPE_PRICE_ID_MONITORING_ANNUAL", "price_monitoring_annual", "subscription", "monitoring_annual"),
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
    expected_product_code,
):
    tenant = tenant_factory(plan="premium", license_status="active")
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
    assert response.json()["product_code"] == expected_product_code
    assert captured["mode"] == expected_mode
    assert captured["line_items"] == [{"price": price_id, "quantity": 1}]
    assert captured["metadata"]["product_code"] == expected_product_code


@pytest.mark.parametrize(
    ("product_code", "expected_product_code"),
    [("assessment", "full_analysis"), ("full_analysis", "full_analysis"), ("validation_check", "validation_check")],
)
def test_checkout_completed_fulfills_one_time_product_semantics(
    client,
    tenant_factory,
    product_code,
    expected_product_code,
):
    tenant = tenant_factory(plan="premium", license_status="active")

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
        credits = db.query(TenantScanCredit).filter(TenantScanCredit.tenant_id == tenant["tenant_id"]).all()
        stored_tenant = db.query(Tenant).filter_by(tenant_id=tenant["tenant_id"]).one()
        assert stored_tenant.premium_until_utc is not None
        if expected_product_code == "validation_check":
            assert len(credits) == 1
            assert credits[0].product_code == "validation_check"
            assert credits[0].status == "available"
        else:
            assert credits == []


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
    assert payload["validation_check_access_active"] is True
    assert payload["can_view_issues"] is True
    assert payload["can_view_actions"] is True
    assert payload["can_view_reports"] is True
    assert payload["can_view_record_details"] is True
    assert payload["dashboard_access_until"]
    assert "deep_scan" in payload["features"]
    assert "executive_report" in payload["features"]


def test_license_status_uses_exact_seven_day_premium_extension_for_one_time_products(
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
            "product_code": "full_analysis",
        },
        follow_redirects=False,
    )

    response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert response.status_code == 200
    payload = response.json()
    assert payload["dashboard_access_until"] == payload["issue_access_until"]
    assert payload["dashboard_access_until"] == payload["premium_access_until"]
    access_until = datetime.fromisoformat(payload["dashboard_access_until"].replace("Z", "+00:00"))
    remaining = access_until - datetime.now(timezone.utc)
    assert timedelta(days=6, hours=23) < remaining <= timedelta(days=7, minutes=1)
    assert payload["product_access"]["subscription_end"] == payload["dashboard_access_until"]


def test_expired_monitoring_period_is_not_active_even_when_provider_status_is_active(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="premium", license_status="active")
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(
            Subscription(
                tenant_id=tenant["tenant_id"],
                provider="stripe",
                provider_subscription_id="sub_expired_active",
                status="active",
                plan_code="monitoring_monthly",
                currency="EUR",
                amount_monthly=149.0,
                current_period_start_utc=now - timedelta(days=40),
                current_period_end_utc=now - timedelta(days=1),
                cancel_at_period_end=False,
                canceled_at_utc=None,
                created_at_utc=now - timedelta(days=40),
                updated_at_utc=now,
            )
        )
        db.commit()

    response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert response.status_code == 200
    payload = response.json()
    assert payload["plan"] == "free"
    assert payload["license_status"] == "expired"
    assert payload["monitoring_active"] is False
    assert payload["can_use_monitoring"] is False
    assert payload["can_run_deep_scan"] is False
    assert "monitoring_monthly" not in payload["active_products"]
    assert "analytics_full" not in payload["features"]
    assert "recommendations" not in payload["features"]


def test_active_monitoring_without_period_end_gets_fallback_access_end_dates(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="premium", license_status="active")
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(
            Subscription(
                tenant_id=tenant["tenant_id"],
                provider="stripe",
                provider_subscription_id="sub_missing_period_end",
                status="active",
                plan_code="monitoring_monthly",
                currency="EUR",
                amount_monthly=149.0,
                current_period_start_utc=now,
                current_period_end_utc=None,
                cancel_at_period_end=False,
                canceled_at_utc=None,
                created_at_utc=now,
                updated_at_utc=now,
            )
        )
        db.commit()

    response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert response.status_code == 200
    payload = response.json()
    assert payload["monitoring_active"] is True
    assert payload["dashboard_access_until"]
    assert payload["issue_access_until"]
    assert payload["premium_access_until"]
    assert payload["subscription_end"]
    assert payload["subscription_end_utc"]
    assert payload["monitoring_access_until"]
    assert payload["monitoring_period_end"]
    assert payload["dashboard_access_until"] == payload["issue_access_until"]
    assert payload["dashboard_access_until"] == payload["premium_access_until"]
    assert payload["dashboard_access_until_bc"]
    access_until = datetime.fromisoformat(payload["dashboard_access_until"].replace("Z", "+00:00"))
    assert access_until.hour == 23
    assert access_until.minute == 59


def test_legacy_premium_tenant_without_product_record_does_not_get_open_ended_monitoring(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="premium", license_status="active")

    response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert response.status_code == 200
    payload = response.json()
    assert payload["monitoring_active"] is False
    assert "monitoring_active" not in payload["features"]
    assert payload["can_run_deep_scan"] is False
    assert payload["can_view_dashboard"] is False
    assert payload["dashboard_access_until"] is None


def test_free_insights_are_available_after_scan_without_premium_details(
    client,
    tenant_factory,
    auth_header_factory,
    deep_scan_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    deep_scan_factory(tenant_id=tenant["tenant_id"], scan_id="RUN_FREE_INSIGHTS", total_records=120000)

    response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert response.status_code == 200
    payload = response.json()
    assert payload["can_view_free_insights"] is True
    assert payload["record_count"] == 120000
    assert payload["pricing_tier"] == "professional"
    assert payload["can_view_issues"] is False
    assert payload["can_view_actions"] is False
    assert payload["can_view_reports"] is False
    assert payload["can_view_record_details"] is False
    assert payload["premium_access_until"] is None


def test_data_health_score_start_without_credit_does_not_consume_credit(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")

    response = client.post(
        "/scan/start",
        headers=auth_header_factory(tenant),
        json={
            "tenant_id": tenant["tenant_id"],
            "run_id": "RUN_FREE_SCORE_START",
            "scan_mode": "data_health_score",
            "total_modules": 3,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "queued"
    assert payload["free_data_health_score"] is True
    assert payload["credit_consumed"] is False

    with SessionLocal() as db:
        credit_count = db.query(TenantScanCredit).filter(TenantScanCredit.tenant_id == tenant["tenant_id"]).count()
    assert credit_count == 0


def test_data_health_score_sync_without_credit_exposes_free_insights_and_locks_premium(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    payload = _deep_scan_payload(tenant["tenant_id"], "RUN_FREE_SCORE_SYNC")
    payload["scan_type"] = "data_health_score"

    response = client.post(
        "/scan/sync",
        headers=auth_header_factory(tenant),
        json=payload,
    )

    assert response.status_code == 200
    with SessionLocal() as db:
        credit_count = db.query(TenantScanCredit).filter(TenantScanCredit.tenant_id == tenant["tenant_id"]).count()
    assert credit_count == 0

    license_response = client.get("/license/status", headers=auth_header_factory(tenant))
    assert license_response.status_code == 200
    license_payload = license_response.json()
    assert license_payload["can_view_free_insights"] is True
    assert license_payload["can_run_data_health_score"] is False
    assert license_payload["has_completed_data_health_score"] is True
    assert license_payload["can_view_issues"] is False
    assert license_payload["can_view_actions"] is False
    assert license_payload["can_view_reports"] is False
    assert license_payload["can_view_record_details"] is False

    token_response = client.get("/analytics/get-token", headers=auth_header_factory(tenant))
    assert token_response.status_code == 403


def test_data_health_score_sync_updates_queued_placeholder_and_analytics_values(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    start_response = client.post(
        "/scan/start",
        headers=auth_header_factory(tenant),
        json={
            "tenant_id": tenant["tenant_id"],
            "run_id": "RUN_FREE_SCORE_PLACEHOLDER",
            "scan_mode": "data_health_score",
            "total_modules": 3,
        },
    )
    assert start_response.status_code == 200

    payload = _deep_scan_payload(tenant["tenant_id"], "RUN_FREE_SCORE_PLACEHOLDER")
    payload["scan_type"] = "data_health_score"
    payload["data_score"] = 47
    payload["checks_count"] = 202
    payload["issues_count"] = 95
    payload["module_scores"]["finance"] = 42
    payload["data_profile"]["total_records"] = 1234
    payload["execution_token"] = start_response.json()["execution_token"]
    payload["worker_id"] = start_response.json()["worker_id"]
    sync_response = client.post("/scan/sync", headers=auth_header_factory(tenant), json=payload)
    assert sync_response.status_code == 200

    token_response = client.get("/analytics/get-token", headers=auth_header_factory(tenant))
    assert token_response.status_code == 403


def test_free_dashboard_sections_are_server_locked_until_premium_access(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    payload = _deep_scan_payload(tenant["tenant_id"], "RUN_FREE_SECTION_LOCKS")
    payload["scan_type"] = "data_health_score"
    scan_response = client.post("/scan/sync", headers=auth_header_factory(tenant), json=payload)
    assert scan_response.status_code == 200

    token_response = client.get("/analytics/get-token", headers=auth_header_factory(tenant))
    assert token_response.status_code == 403


def test_premium_dashboard_sections_are_unlocked(
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
    scan_response = client.post(
        "/scan/sync",
        headers=auth_header_factory(tenant),
        json=_deep_scan_payload(tenant["tenant_id"], "RUN_PREMIUM_SECTIONS"),
    )
    assert scan_response.status_code == 200

    token_response = client.get("/analytics/get-token", headers=auth_header_factory(tenant))
    assert token_response.status_code == 200
    analytics_token = token_response.json()["token"]

    for section in ("issues", "actions", "reports"):
        response = client.get(f"/analytics/embed/{section}?embed_token={analytics_token}")
        assert response.status_code == 200
        assert response.json()["locked"] is False


def test_enterprise_free_insights_use_contact_sales_tenant_pricing(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    payload = _deep_scan_payload(tenant["tenant_id"], "RUN_ENTERPRISE_FREE_SCORE")
    payload["scan_type"] = "data_health_score"
    payload["data_profile"]["total_records"] = 500001

    response = client.post("/scan/sync", headers=auth_header_factory(tenant), json=payload)
    assert response.status_code == 200

    token_response = client.get("/analytics/get-token", headers=auth_header_factory(tenant))
    assert token_response.status_code == 403


@pytest.mark.parametrize(
    ("record_count", "expected_tier"),
    [
        (100000, "starter"),
        (250000, "professional"),
        (500000, "business"),
        (500001, "enterprise"),
    ],
)
def test_pricing_tier_calculation_from_latest_scan(
    client,
    tenant_factory,
    auth_header_factory,
    deep_scan_factory,
    record_count,
    expected_tier,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    deep_scan_factory(tenant_id=tenant["tenant_id"], scan_id=f"RUN_TIER_{record_count}", total_records=record_count)

    response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert response.status_code == 200
    assert response.json()["pricing_tier"] == expected_tier


def test_monitoring_grants_new_premium_flags(
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

    response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert response.status_code == 200
    payload = response.json()
    assert payload["can_use_monitoring"] is True
    assert payload["can_view_issues"] is True
    assert payload["can_view_actions"] is True
    assert payload["can_view_reports"] is True
    assert payload["can_view_record_details"] is True


def test_deep_scan_without_credit_or_monitoring_claims_initial_free_assessment(
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

    assert response.status_code == 200
    with SessionLocal() as db:
        assert db.query(Tenant).filter_by(tenant_id=tenant["tenant_id"]).one().free_assessment_used is True


def test_deep_scan_start_without_credit_or_monitoring_resolves_to_free_assessment(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")

    response = client.post(
        "/scan/start",
        headers=auth_header_factory(tenant),
        json={
            "tenant_id": tenant["tenant_id"],
            "run_id": "RUN_START_NO_CREDIT",
            "scan_mode": "deep",
            "total_modules": 3,
        },
    )

    assert response.status_code == 200
    assert response.json()["free_data_health_score"] is True
    assert response.json()["credit_consumed"] is False


def test_deep_scan_start_consumes_credit_and_creates_history_entry(
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

    response = client.post(
        "/scan/start",
        headers=auth_header_factory(tenant),
        json={
            "tenant_id": tenant["tenant_id"],
            "run_id": "RUN_START_WITH_CREDIT",
            "scan_mode": "deep",
            "total_modules": 3,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "queued"
    assert response.json()["credit_consumed"] is True

    history_response = client.get(f"/scan/history/{tenant['tenant_id']}", headers=auth_header_factory(tenant))
    assert history_response.status_code == 200
    assert history_response.json()["scans"][0]["scan_id"] == "RUN_START_WITH_CREDIT"

    sync_payload = _deep_scan_payload(tenant["tenant_id"], "RUN_START_WITH_CREDIT")
    sync_payload["execution_token"] = response.json()["execution_token"]
    sync_payload["worker_id"] = response.json()["worker_id"]
    sync_response = client.post(
        "/scan/sync",
        headers=auth_header_factory(tenant),
        json=sync_payload,
    )
    assert sync_response.status_code == 200

    with SessionLocal() as db:
        credits = db.query(TenantScanCredit).filter(TenantScanCredit.tenant_id == tenant["tenant_id"]).all()
        assert len(credits) == 1
        assert credits[0].status == "consumed"
        assert credits[0].consumed_scan_id == "RUN_START_WITH_CREDIT"


def test_full_analysis_unlocks_premium_but_does_not_authorize_another_scan(
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

    free_response = client.post(
        "/scan/sync",
        headers=auth_header_factory(tenant),
        json={**_deep_scan_payload(tenant["tenant_id"], "RUN_FREE_BEFORE_FULL"), "scan_type": "data_health_score"},
    )
    blocked_response = client.post(
        "/scan/sync",
        headers=auth_header_factory(tenant),
        json=_deep_scan_payload(tenant["tenant_id"], "RUN_AFTER_FULL"),
    )

    assert free_response.status_code == 200
    assert blocked_response.status_code == 402
    with SessionLocal() as db:
        credits = db.query(TenantScanCredit).filter(TenantScanCredit.tenant_id == tenant["tenant_id"]).all()
        assert credits == []

    license_response = client.get("/license/status", headers=auth_header_factory(tenant))
    assert license_response.status_code == 200
    license_payload = license_response.json()
    assert license_payload["scan_credits_available"] == 0
    assert license_payload["can_run_deep_scan"] is False
    assert license_payload["can_view_dashboard"] is True
    assert license_payload["can_view_issue_details"] is True
    assert license_payload["assessment_access_active"] is True
    assert license_payload["full_analysis_access_active"] is True
    assert license_payload["can_view_free_insights"] is True
    assert license_payload["can_view_issues"] is True


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
    assert payload["subscription"]["plan_label"] == "Full Analysis / Validation access"
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
        stored_tenant = db.query(Tenant).filter_by(tenant_id=tenant["tenant_id"]).one()
        stored_tenant.premium_until_utc = expired_at
        entitlement = (
            db.query(TenantProductEntitlement)
            .filter(TenantProductEntitlement.tenant_id == tenant["tenant_id"])
            .one()
        )
        entitlement.valid_until_utc = expired_at
        db.commit()

    license_response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert license_response.status_code == 200
    payload = license_response.json()
    assert payload["assessment_access_active"] is False
    assert payload["full_analysis_access_active"] is False
    assert payload["can_run_deep_scan"] is False
    assert payload["can_view_dashboard"] is False
    assert payload["can_view_issue_details"] is False
    assert payload["can_view_free_insights"] is True
    assert payload["can_view_issues"] is False


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

    assert response.status_code == 403

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
