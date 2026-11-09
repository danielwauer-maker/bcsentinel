"""Verified Stripe reversals: the revoked v2 purchase must stay inaccessible."""
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


def _paid_purchase(db, tenant_id, *, product, session, intent):
    purchase = record_product_purchase(
        db, tenant_id=tenant_id, product_code=product,
        provider="stripe", provider_checkout_session_id=session,
        provider_payment_intent_id=intent,
        status="paid", currency="EUR", amount_total=249.0,
    )
    grant_v2_access_purchase(
        db, tenant_id=tenant_id, product_code=product,
        purchase_id=purchase.id,
    )
    db.commit()
    return purchase.id


def _signed(client, monkeypatch, *, event_id, event_type, data):
    event = {"id": event_id, "type": event_type, "created": 1710000000,
             "data": {"object": data}}
    monkeypatch.setattr(
        "app.routers.billing.stripe.Webhook.construct_event",
        lambda *args, **kwargs: event,
    )
    return client.post(
        "/billing/webhook", headers={"Stripe-Signature": "sig_test"},
        content=b'{"verified_event":true}',
    )


def test_signed_refund_revokes_v2_full_and_replay_cannot_resurrect(
    client, tenant_factory, monkeypatch, settings_state,
):
    tenant_id = tenant_factory()["tenant_id"]
    settings_state(STRIPE_SECRET_KEY="sk_test", STRIPE_WEBHOOK_SECRET="whsec_test")
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    with SessionLocal() as db:
        _paid_purchase(db, tenant_id, product=PRODUCT_FULL_ASSESSMENT_V2,
                       session="cs_signed_refund", intent="pi_signed_refund")
    refund = _signed(
        client, monkeypatch, event_id="evt_signed_refund",
        event_type="charge.refunded",
        data={"id": "ch_signed_refund", "payment_intent": "pi_signed_refund"},
    )
    assert refund.status_code == 200, refund.text
    assert refund.json()["processed"] is True
    replay = _signed(
        client, monkeypatch, event_id="evt_signed_refund",
        event_type="charge.refunded",
        data={"id": "ch_signed_refund", "payment_intent": "pi_signed_refund"},
    )
    assert replay.status_code == 200
    assert replay.json()["status"] == "duplicate"
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_id).one()
        purchase = db.query(TenantProductPurchase).filter_by(
            provider_payment_intent_id="pi_signed_refund",
        ).one()
        assert purchase.status == "refunded"
        snap = build_product_access_snapshot(db, tenant)
        assert snap["v2_payment_hold"]
        assert not snap["premium_active"]


def test_signed_dispute_revokes_unspent_validation_credit(
    client, tenant_factory, monkeypatch, settings_state,
):
    tenant_id = tenant_factory()["tenant_id"]
    settings_state(STRIPE_SECRET_KEY="sk_test", STRIPE_WEBHOOK_SECRET="whsec_test")
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    with SessionLocal() as db:
        purchase_id = _paid_purchase(
            db, tenant_id, product=PRODUCT_ACCESS_RENEWAL_VALIDATION,
            session="cs_signed_dispute", intent="pi_signed_dispute",
        )
    response = _signed(
        client, monkeypatch, event_id="evt_signed_dispute",
        event_type="charge.dispute.created",
        data={"id": "dp_signed_dispute", "payment_intent": "pi_signed_dispute"},
    )
    assert response.status_code == 200, response.text
    with SessionLocal() as db:
        credit = db.query(TenantScanCredit).filter_by(source_purchase_id=purchase_id).one()
        assert credit.status == "revoked"
        purchase = db.query(TenantProductPurchase).filter_by(id=purchase_id).one()
        assert purchase.status == "disputed"


def test_unknown_reversal_retries_instead_of_misassigning_to_tenant(
    client, monkeypatch, settings_state,
):
    settings_state(STRIPE_SECRET_KEY="sk_test", STRIPE_WEBHOOK_SECRET="whsec_test")
    response = _signed(
        client, monkeypatch, event_id="evt_unknown_stripe_charge",
        event_type="charge.refunded",
        data={"id": "ch_unknown", "payment_intent": "pi_unknown"},
    )
    assert response.status_code == 503
