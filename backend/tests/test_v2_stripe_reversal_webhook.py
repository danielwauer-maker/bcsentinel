"""Verified Stripe reversal webhooks, retries and tenant-safe v2 revocation."""
from __future__ import annotations

from app.core.settings import settings
from app.db import SessionLocal
from app.models import Tenant, TenantProductPurchase, TenantScanCredit
from app.services.product_license_service import (
    PRODUCT_ACCESS_RENEWAL_VALIDATION,
    PRODUCT_FULL_ASSESSMENT_V2,
    build_product_access_snapshot,
    grant_v2_access_purchase,
    record_product_purchase,
)


def _seed_paid(tenant_id: str, code: str, intent: str):
    with SessionLocal() as db:
        purchase = record_product_purchase(
            db, tenant_id=tenant_id, product_code=code, provider="stripe",
            provider_checkout_session_id="cs_" + intent,
            provider_payment_intent_id=intent, status="paid",
            currency="EUR", amount_total=129.0 if code == PRODUCT_ACCESS_RENEWAL_VALIDATION else 249.0,
        )
        grant_v2_access_purchase(db, tenant_id=tenant_id,
                                 product_code=code, purchase_id=purchase.id)
        db.commit()


def _send_event(client, monkeypatch, *, event_id: str, event_type: str, intent: str):
    event = {
        "id": event_id,
        "type": event_type,
        "created": 1780000000,
        "data": {"object": {"id": "ch_" + intent,
                            "payment_intent": intent}},
    }
    monkeypatch.setattr("app.routers.billing.stripe.Webhook.construct_event",
                        lambda *args, **kwargs: event)
    return client.post("/billing/webhook",
                       content=b'{"stripe":"signed-fixture"}',
                       headers={"Stripe-Signature": "verified-test-signature"})


def test_signed_refund_revokes_v2_grant_and_duplicate_is_idempotent(
    client, monkeypatch, tenant_factory,
):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_test")
    tenant = tenant_factory()
    other = tenant_factory()
    _seed_paid(tenant["tenant_id"], PRODUCT_FULL_ASSESSMENT_V2, "pi_v2_signed_refund")
    _seed_paid(other["tenant_id"], PRODUCT_FULL_ASSESSMENT_V2, "pi_v2_other_safe")
    assert _send_event(client, monkeypatch, event_id="evt_v2_signed_refund",
                       event_type="charge.refunded",
                       intent="pi_v2_signed_refund").status_code == 200
    repeat = _send_event(client, monkeypatch, event_id="evt_v2_signed_refund",
                         event_type="charge.refunded", intent="pi_v2_signed_refund")
    assert repeat.status_code == 200
    assert repeat.json()["status"] == "duplicate"
    with SessionLocal() as db:
        paid = db.query(Tenant).filter_by(tenant_id=tenant["tenant_id"]).one()
        unaffected = db.query(Tenant).filter_by(tenant_id=other["tenant_id"]).one()
        assert not build_product_access_snapshot(db, paid)["premium_active"]
        assert build_product_access_snapshot(db, paid)["v2_payment_hold"]
        assert build_product_access_snapshot(db, unaffected)["premium_active"]


def test_out_of_order_signed_refund_retries_until_purchase_exists(
    client, monkeypatch, tenant_factory,
):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_test")
    tenant_id = tenant_factory()["tenant_id"]
    first = _send_event(client, monkeypatch, event_id="evt_v2_early_refund",
                        event_type="charge.refunded", intent="pi_v2_early_refund")
    assert first.status_code == 503  # Stripe retries: never acknowledge unknown reversal.
    _seed_paid(tenant_id, PRODUCT_ACCESS_RENEWAL_VALIDATION, "pi_v2_early_refund")
    second = _send_event(client, monkeypatch, event_id="evt_v2_early_refund",
                         event_type="charge.refunded", intent="pi_v2_early_refund")
    assert second.status_code == 200, second.text
    with SessionLocal() as db:
        purchase = db.query(TenantProductPurchase).filter_by(
            provider_payment_intent_id="pi_v2_early_refund"
        ).one()
        credit = db.query(TenantScanCredit).filter_by(source_purchase_id=purchase.id).one()
        assert purchase.status == "refunded"
        assert credit.status == "revoked"
        assert not build_product_access_snapshot(
            db, db.query(Tenant).filter_by(tenant_id=tenant_id).one()
        )["premium_active"]
