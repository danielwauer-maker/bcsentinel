import base64

from app.db import SessionLocal
from app.models import AdminAuditEvent, ImpactSettingsConfig, IssueImpactConfig, LicensePricingConfig, ProductPricingConfig
from app.services.product_pricing_service import (
    PRODUCT_PRICING_DEFAULTS,
    ensure_default_product_pricing,
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


def test_product_pricing_seed_creates_tier_specific_default_products(db_session):
    ensure_default_product_pricing(db_session)

    rows = db_session.query(ProductPricingConfig).order_by(ProductPricingConfig.product_key.asc()).all()
    by_key = {row.product_key: row for row in rows}

    assert set(by_key.keys()) == set(PRODUCT_PRICING_DEFAULTS.keys())
    assert by_key["small__assessment"].price_cents == 24900
    assert by_key["small__validation_check"].price_cents == 12900
    assert by_key["small__monitoring_monthly"].billing_interval == "month"
    assert by_key["small__monitoring_annual"].price_cents == 199000
    assert by_key["enterprise__assessment"].price_cents == 119000


def test_public_product_pricing_api_returns_active_database_tier_prices(client, db_session):
    ensure_default_product_pricing(db_session)
    row = db_session.get(ProductPricingConfig, "small__assessment")
    assert row is not None
    row.price_cents = 25000
    db_session.commit()

    response = client.get("/pricing/public")

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "database"
    assert payload["pricing_model"] == "record_volume_tiers"
    products = {row["product_key"]: row for row in payload["products"]}
    assert products["assessment"]["price_cents"] == 25000
    assert products["assessment"]["price_eur"] == 250.0
    tiers = {row["code"]: row for row in payload["tiers"]}
    assert tiers["small"]["prices"]["assessment"]["price_cents"] == 25000
    assert "stripe_price_id" not in response.text.lower()
    assert "sk_" not in response.text.lower()


def test_public_product_pricing_payload_exposes_record_volume_tiers(db_session):
    ensure_default_product_pricing(db_session)

    payload = get_public_product_pricing_payload(db_session)

    tiers = {row["code"]: row for row in payload["tiers"]}
    assert tiers["small"]["prices"]["validation_check"]["price_cents"] == 12900
    assert tiers["medium"]["prices"]["monitoring_monthly"]["price_cents"] == 29900
    assert tiers["enterprise"]["prices"]["monitoring_annual"]["price_cents"] == 799000
    assert tiers["enterprise_plus"]["custom_quote"] is True
    assert tiers["enterprise_plus"]["prices"] == {}


def test_admin_product_pricing_update_changes_tier_price_and_audits(client):
    sku_key = "small__assessment"
    response = client.post(
        f"/admin/config/product-pricing/{sku_key}",
        headers=_admin_auth_header(),
        data={
            **_admin_csrf(client),
            "display_name": "Assessment · Small",
            "price_cents": "25000",
            "currency": "EUR",
            "billing_interval": "one_time",
            "is_active": "on",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    with SessionLocal() as db:
        row = db.get(ProductPricingConfig, sku_key)
        event = db.query(AdminAuditEvent).filter(AdminAuditEvent.action == "config.product_pricing.update").one()

    assert row is not None
    assert row.price_cents == 25000
    assert event.target_id == sku_key


def test_admin_product_pricing_rejects_invalid_interval(client):
    sku_key = "small__assessment"
    response = client.post(
        f"/admin/config/product-pricing/{sku_key}",
        headers=_admin_auth_header(),
        data={
            **_admin_csrf(client),
            "display_name": "Assessment · Small",
            "price_cents": "24900",
            "currency": "EUR",
            "billing_interval": "month",
            "is_active": "on",
        },
        follow_redirects=False,
    )

    assert response.status_code == 400
