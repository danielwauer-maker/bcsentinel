from __future__ import annotations

from datetime import timedelta

import pytest

from app.db import SessionLocal
from app.services.product_license_service import PRODUCT_MONITORING_MONTHLY, active_entitlement_product_codes, utc_now
from app.services.tenant_commercial_service import (
    calculate_effective_price,
    consume_override_use,
    create_commercial_override,
    get_active_commercial_override,
    grant_pilot_sponsorship,
)


def test_free_override_reduces_price_to_zero_and_disables_coupon_stacking_by_default(tenant_factory):
    tenant = tenant_factory()
    now = utc_now()
    with SessionLocal() as db:
        override = create_commercial_override(
            db,
            tenant_id=tenant["tenant_id"],
            product_code=PRODUCT_MONITORING_MONTHLY,
            override_type="free",
            value_number=0,
            valid_from_utc=now - timedelta(minutes=1),
            valid_until_utc=now + timedelta(days=30),
            actor="pytest",
            reason="Controlled pilot",
        )
        db.flush()
        override_id = override.id
        db.commit()
        result = calculate_effective_price(
            db,
            tenant_id=tenant["tenant_id"],
            product_code=PRODUCT_MONITORING_MONTHLY,
            list_price_cents=29_900,
        )

    assert result["effective_price_cents"] == 0
    assert result["price_source"] == "tenant_commercial_override"
    assert result["override_id"] == override_id
    assert result["promotion_code_allowed"] is False


def test_fixed_and_percent_overrides_compute_server_side_effective_price(tenant_factory):
    tenant_a = tenant_factory()
    tenant_b = tenant_factory()
    now = utc_now()
    with SessionLocal() as db:
        create_commercial_override(
            db,
            tenant_id=tenant_a["tenant_id"],
            product_code="assessment",
            override_type="fixed_price",
            value_number=99.0,
            valid_from_utc=now - timedelta(minutes=1),
            valid_until_utc=now + timedelta(days=10),
            actor="pytest",
        )
        create_commercial_override(
            db,
            tenant_id=tenant_b["tenant_id"],
            product_code="assessment",
            override_type="percent_discount",
            value_number=50.0,
            valid_from_utc=now - timedelta(minutes=1),
            valid_until_utc=now + timedelta(days=10),
            actor="pytest",
        )
        db.commit()
        fixed = calculate_effective_price(
            db,
            tenant_id=tenant_a["tenant_id"],
            product_code="assessment",
            list_price_cents=39_900,
        )
        percent = calculate_effective_price(
            db,
            tenant_id=tenant_b["tenant_id"],
            product_code="assessment",
            list_price_cents=39_900,
        )

    assert fixed["effective_price_cents"] == 9_900
    assert percent["effective_price_cents"] == 19_950


def test_overlapping_active_override_is_rejected(tenant_factory):
    tenant = tenant_factory()
    now = utc_now()
    with SessionLocal() as db:
        create_commercial_override(
            db,
            tenant_id=tenant["tenant_id"],
            product_code="assessment",
            override_type="fixed_price",
            value_number=100,
            valid_from_utc=now,
            valid_until_utc=now + timedelta(days=30),
            actor="pytest",
        )
        with pytest.raises(ValueError, match="overlaps"):
            create_commercial_override(
                db,
                tenant_id=tenant["tenant_id"],
                product_code="assessment",
                override_type="fixed_price",
                value_number=50,
                valid_from_utc=now + timedelta(days=1),
                valid_until_utc=now + timedelta(days=2),
                actor="pytest",
            )


def test_expired_override_does_not_apply(tenant_factory):
    tenant = tenant_factory()
    now = utc_now()
    with SessionLocal() as db:
        create_commercial_override(
            db,
            tenant_id=tenant["tenant_id"],
            product_code="assessment",
            override_type="free",
            value_number=0,
            valid_from_utc=now - timedelta(days=10),
            valid_until_utc=now - timedelta(days=1),
            actor="pytest",
        )
        db.commit()
        result = calculate_effective_price(
            db,
            tenant_id=tenant["tenant_id"],
            product_code="assessment",
            list_price_cents=24_900,
        )

    assert result["effective_price_cents"] == 24_900
    assert result["price_source"] == "list_price"


def test_override_max_uses_is_enforced(tenant_factory):
    tenant = tenant_factory()
    now = utc_now()
    with SessionLocal() as db:
        override = create_commercial_override(
            db,
            tenant_id=tenant["tenant_id"],
            product_code="validation_check",
            override_type="fixed_price",
            value_number=1,
            valid_from_utc=now - timedelta(minutes=1),
            valid_until_utc=now + timedelta(days=10),
            actor="pytest",
            max_uses=1,
        )
        db.flush()
        override_id = override.id
        db.commit()
        consume_override_use(db, override_id=override_id, actor="pytest")
        db.commit()
        assert get_active_commercial_override(
            db,
            tenant_id=tenant["tenant_id"],
            product_code="validation_check",
        ) is None


def test_pilot_sponsorship_grants_time_limited_entitlement_without_paid_subscription(tenant_factory):
    tenant = tenant_factory()
    now = utc_now()
    with SessionLocal() as db:
        sponsorship = grant_pilot_sponsorship(
            db,
            tenant_id=tenant["tenant_id"],
            product_code=PRODUCT_MONITORING_MONTHLY,
            valid_from_utc=now,
            valid_until_utc=now + timedelta(days=60),
            actor="pytest",
            reason="Pilot customer",
        )
        sponsorship_status = sponsorship.status
        db.commit()
        active_products = active_entitlement_product_codes(db, tenant["tenant_id"])

    assert sponsorship_status == "active"
    assert PRODUCT_MONITORING_MONTHLY in active_products
