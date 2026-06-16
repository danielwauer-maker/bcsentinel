import base64

from app.db import SessionLocal
from app.models import (
    AdminAuditEvent,
    ImpactSettingsConfig,
    IssueImpactConfig,
    LicensePricingConfig,
    ProductPricingConfig,
    ProductPricingMatrixConfig,
)
from app.services.product_pricing_service import (
    PRICING_TIER_BUSINESS,
    PRICING_TIER_ENTERPRISE,
    PRICING_TIER_PROFESSIONAL,
    PRICING_TIER_STARTER,
    PRODUCT_PRICING_DEFAULTS,
    calculate_pricing_tier,
    build_tier_pricing_payload,
    ensure_default_product_pricing,
    ensure_default_product_pricing_matrix,
    get_matrix_price,
    get_public_product_pricing_payload,
)
from app.services.pricing_service import get_public_pricing_payload


def _admin_auth_header() -> dict[str, str]:
    token = base64.b64encode(b"admin-test:admin-password-for-tests-123").decode("ascii")
    return {"Authorization": f"Basic {token}"}


def _admin_csrf(client, path: str = "/admin/config/license-pricing") -> dict[str, str]:
    response = client.get(path, headers=_admin_auth_header())
    assert response.status_code == 200
    token = client.cookies.get("bcs_csrf")
    assert token
    return {"csrf_token": token}


def test_public_pricing_uses_canonical_defaults_without_db_override(db_session):
    payload = get_public_pricing_payload(db_session, "premium")

    assert payload["source"] == "canonical"
    assert payload["base_price"] == 149.0
    assert payload["annual_fixed_price"] == 1788.0
    assert payload["step_price"] == 8.0


def test_public_pricing_uses_database_override_when_valid(db_session):
    db_session.add(
        LicensePricingConfig(
            plan_code="premium",
            display_name="Premium Plus",
            base_price_monthly=199.0,
            included_records=4000,
            additional_price_per_1000_records=12.0,
            is_active=True,
        )
    )
    db_session.commit()

    payload = get_public_pricing_payload(db_session, "premium")

    assert payload["source"] == "database"
    assert payload["display_name"] == "Premium Plus"
    assert payload["base_price"] == 199.0
    assert payload["annual_fixed_price"] == 2388.0


def test_public_pricing_falls_back_when_database_override_is_invalid(db_session):
    db_session.add(
        LicensePricingConfig(
            plan_code="premium",
            display_name="",
            base_price_monthly=-99.0,
            included_records=-1,
            additional_price_per_1000_records=-5.0,
            is_active=True,
        )
    )
    db_session.commit()

    payload = get_public_pricing_payload(db_session, "premium")

    assert payload["source"] == "canonical"
    assert payload["base_price"] == 149.0
    assert payload["step_price"] == 8.0
    assert payload["included_records"] == 2000


def test_public_loss_examples_config_uses_current_hourly_rate_and_issue_factors(client, db_session):
    hourly_rate = db_session.get(ImpactSettingsConfig, "default_hourly_rate_eur")
    if hourly_rate is None:
        hourly_rate = ImpactSettingsConfig(
            key="default_hourly_rate_eur",
            value_number=62.0,
            title="Default hourly rate (EUR)",
        )
        db_session.add(hourly_rate)
    else:
        hourly_rate.value_number = 62.0

    issue = db_session.get(IssueImpactConfig, "SALES_LINES_ZERO_PRICE")
    if issue is None:
        issue = IssueImpactConfig(
            code="SALES_LINES_ZERO_PRICE",
            title="Sales lines zero price",
            category="sales",
            minutes_per_occurrence=19.0,
            probability=0.8,
            frequency_per_year=9.0,
            is_active=True,
        )
        db_session.add(issue)
    else:
        issue.minutes_per_occurrence = 19.0
        issue.probability = 0.8
        issue.frequency_per_year = 9.0
        issue.is_active = True

    db_session.commit()

    response = client.get("/public/loss-examples-config")

    assert response.status_code == 200
    payload = response.json()
    assert payload["hourly_rate_eur"] == 62.0
    assert payload["issues"]["SALES_LINES_ZERO_PRICE"] == {
        "minutes_per_occurrence": 19.0,
        "probability": 0.8,
        "frequency_per_year": 9.0,
    }


def test_product_pricing_seed_creates_default_products(db_session):
    ensure_default_product_pricing(db_session)

    rows = db_session.query(ProductPricingConfig).order_by(ProductPricingConfig.product_key.asc()).all()
    by_key = {row.product_key: row for row in rows}

    assert set(by_key.keys()) == set(PRODUCT_PRICING_DEFAULTS.keys())
    assert by_key["data_health_score"].price_cents == 0
    assert by_key["full_analysis"].price_cents == 7900
    assert by_key["validation_check"].price_cents == 4900
    assert by_key["monitoring_monthly"].billing_interval == "month"
    assert by_key["monitoring_monthly"].price_cents == 14900
    assert by_key["monitoring_annual"].price_cents == 149000


def test_pricing_tier_calculation_boundaries():
    assert calculate_pricing_tier(0) == PRICING_TIER_STARTER
    assert calculate_pricing_tier(100000) == PRICING_TIER_STARTER
    assert calculate_pricing_tier(100001) == PRICING_TIER_PROFESSIONAL
    assert calculate_pricing_tier(250000) == PRICING_TIER_PROFESSIONAL
    assert calculate_pricing_tier(250001) == PRICING_TIER_BUSINESS
    assert calculate_pricing_tier(500000) == PRICING_TIER_BUSINESS
    assert calculate_pricing_tier(500001) == PRICING_TIER_ENTERPRISE


def test_product_pricing_matrix_defaults_by_tier(db_session):
    ensure_default_product_pricing_matrix(db_session)

    expected = {
        ("full_analysis", "starter"): 79.0,
        ("full_analysis", "professional"): 99.0,
        ("full_analysis", "business"): 129.0,
        ("validation_check", "starter"): 49.0,
        ("validation_check", "professional"): 79.0,
        ("validation_check", "business"): 99.0,
        ("monitoring_monthly", "starter"): 149.0,
        ("monitoring_monthly", "professional"): 199.0,
        ("monitoring_monthly", "business"): 299.0,
        ("monitoring_annual", "starter"): 1490.0,
        ("monitoring_annual", "professional"): 1990.0,
        ("monitoring_annual", "business"): 2990.0,
    }

    for (product_key, pricing_tier), amount_eur in expected.items():
        assert get_matrix_price(db_session, product_key, pricing_tier).amount_eur == amount_eur

    enterprise = get_matrix_price(db_session, "full_analysis", "enterprise")
    assert enterprise.contact_sales is True
    assert enterprise.amount_eur is None


def test_public_product_pricing_api_returns_active_database_prices(client, db_session):
    ensure_default_product_pricing(db_session)
    row = db_session.get(ProductPricingConfig, "full_analysis")
    row.price_cents = 8500
    db_session.commit()

    response = client.get("/pricing/public")

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "database"
    products = {row["product_key"]: row for row in payload["products"]}
    assert products["data_health_score"]["price_cents"] == 0
    assert products["full_analysis"]["price_cents"] == 7900
    assert products["full_analysis"]["price_eur"] == 79.0
    assert products["full_analysis"]["starting_at"] is True
    assert products["validation_check"]["price_eur"] == 49.0
    assert products["monitoring"]["price_eur"] == 149.0
    assert products["monitoring"]["billing_interval"] == "month"
    assert "stripe" not in response.text.lower()


def test_public_product_pricing_payload_filters_inactive_products(db_session):
    ensure_default_product_pricing_matrix(db_session)
    rows = db_session.query(ProductPricingMatrixConfig).filter_by(product_key="validation_check").all()
    assert rows
    for row in rows:
        row.is_active = False
    db_session.commit()

    payload = get_public_product_pricing_payload(db_session)

    product_keys = {row["product_key"] for row in payload["products"]}
    assert "validation_check" not in product_keys
    assert "full_analysis" in product_keys


def test_public_product_pricing_api_optionally_returns_matrix(client):
    response = client.get("/pricing/public?include_matrix=true")

    assert response.status_code == 200
    payload = response.json()
    assert payload["matrix"]
    matrix_rows = {(row["product_key"], row["pricing_tier"]): row for row in payload["matrix"]}
    assert matrix_rows[("monitoring_monthly", "professional")]["amount_eur"] == 199.0
    assert matrix_rows[("full_analysis", "enterprise")]["contact_sales"] is True


def test_dashboard_tier_pricing_payload_uses_record_count(db_session):
    payload = build_tier_pricing_payload(db_session, record_count=184327)

    assert payload["record_count"] == 184327
    assert payload["pricing_tier"] == "professional"
    assert payload["contact_sales"] is False
    assert payload["prices"]["full_analysis"]["amount_eur"] == 99.0
    assert payload["prices"]["validation_check"]["amount_eur"] == 79.0
    assert payload["prices"]["monitoring_monthly"]["amount_eur"] == 199.0
    assert payload["prices"]["monitoring_annual"]["amount_eur"] == 1990.0


def test_dashboard_tier_pricing_payload_marks_enterprise_contact_sales(db_session):
    payload = build_tier_pricing_payload(db_session, record_count=500001)

    assert payload["pricing_tier"] == "enterprise"
    assert payload["contact_sales"] is True
    assert payload["prices"]["full_analysis"]["contact_sales"] is True
    assert payload["prices"]["monitoring_monthly"]["amount_eur"] is None


def test_admin_product_pricing_update_changes_price_and_audits(client):
    response = client.post(
        "/admin/config/product-pricing/full_analysis",
        headers=_admin_auth_header(),
        data={
            **_admin_csrf(client),
            "display_name": "Full Analysis",
            "price_cents": "8800",
            "currency": "EUR",
            "billing_interval": "one_time",
            "is_active": "on",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    with SessionLocal() as db:
        row = db.get(ProductPricingConfig, "full_analysis")
        event = db.query(AdminAuditEvent).filter(AdminAuditEvent.action == "config.product_pricing.update").one()

    assert row.price_cents == 8800
    assert event.target_id == "full_analysis"


def test_admin_product_pricing_rejects_invalid_interval(client):
    response = client.post(
        "/admin/config/product-pricing/full_analysis",
        headers=_admin_auth_header(),
        data={
            **_admin_csrf(client),
            "display_name": "Full Analysis",
            "price_cents": "7900",
            "currency": "EUR",
            "billing_interval": "month",
            "is_active": "on",
        },
        follow_redirects=False,
    )

    assert response.status_code == 400


def test_admin_product_pricing_matrix_update_changes_price_and_audits(client):
    response = client.post(
        "/admin/config/product-pricing-matrix/full_analysis/professional",
        headers=_admin_auth_header(),
        data={
            **_admin_csrf(client),
            "max_records": "250000",
            "amount_cents": "10500",
            "currency": "EUR",
            "billing_interval": "one_time",
            "display_name_de": "Full Analysis",
            "display_name_en": "Full Analysis",
            "stripe_price_id": "price_full_analysis_professional",
            "is_active": "on",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    with SessionLocal() as db:
        row = db.query(ProductPricingMatrixConfig).filter_by(
            product_key="full_analysis",
            pricing_tier="professional",
        ).one()
        event = db.query(AdminAuditEvent).filter(AdminAuditEvent.action == "config.product_pricing_matrix.update").one()

    assert row.amount_cents == 10500
    assert row.stripe_price_id == "price_full_analysis_professional"
    assert event.target_id == "full_analysis:professional"
