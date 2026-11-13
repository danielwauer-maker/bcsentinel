from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.assessment_scope_models import AssessmentScopeSnapshot
from app.core.settings import settings
from app.db import SessionLocal
from app.models import CreditLedgerEntry, Scan, ScanRunStatus, Tenant, TenantProductEntitlement, TenantScanCredit
from app.services.operator_commercial_service import cancel_fiverr_monitoring, grant_fiverr_monitoring, grant_fiverr_v2, revoke_fiverr_v2
from app.services.product_license_service import build_product_access_snapshot

COMPANY = "11111111-2222-3333-4444-555555555555"


@pytest.fixture
def v2_tenant(monkeypatch, tenant_factory, scan_factory):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    tenant = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="operator-v2-free")
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        row = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        row.bc_company_id = COMPANY
        scan = db.scalar(select(Scan).where(Scan.scan_id == "operator-v2-free"))
        scan.bc_company_id, scan.lcy_code = COMPANY, "EUR"
        db.add(ScanRunStatus(run_id=scan.scan_id, tenant_id=tenant["tenant_id"], scan_mode="deep",
                             status="completed", created_at_utc=now, updated_at_utc=now,
                             completed_at_utc=now, result_persisted_at_utc=now))
        db.add(TenantScanCredit(tenant_id=tenant["tenant_id"], product_code="free_entry", status="consumed",
                                source="legacy", consumed_scan_id=scan.scan_id, created_at_utc=now,
                                consumed_at_utc=now))
        db.add(AssessmentScopeSnapshot(scan_id=scan.scan_id, tenant_id=tenant["tenant_id"], version=1,
                                       state="confirmed", included_modules_count=1,
                                       created_at_utc=now, confirmed_at_utc=now))
        db.commit()
    return tenant["tenant_id"]


def grant(db, tenant, product, position):
    return grant_fiverr_v2(db, tenant_id=tenant, product_code=product, order_reference="order-1",
                           order_position=position, amount=249.0, actor="operator")


def test_free_to_full_grant_allows_subsequent_scope_confirmation(client, v2_tenant):
    from app.services.assessment_scope_service import get_or_create_auto_scope

    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == v2_tenant))
        headers = {"X-Tenant-Id": v2_tenant, "X-Api-Token": tenant.api_token}
        old_scope = db.scalar(select(AssessmentScopeSnapshot).where(AssessmentScopeSnapshot.scan_id == "operator-v2-free"))
        db.delete(old_scope)
        db.flush()
        scan = db.scalar(select(Scan).where(Scan.scan_id == "operator-v2-free"))
        scope = get_or_create_auto_scope(db, scan)
        assert scope.state == "auto"
        assert scope.included_modules_count > 0
        db.commit()
    url = "/scans/operator-v2-free/assessment-scope/confirm"
    assert client.post(url, headers=headers, json={"decisions": {}}).status_code == 403
    with SessionLocal() as db:
        action = grant(db, v2_tenant, "full_assessment_v2", "1")
        assert action.credit_id is None
        db.commit()
    response = client.post(url, headers=headers, json={"decisions": {}})
    assert response.status_code == 200, response.text
    assert response.json()["state"] == "confirmed"


def test_full_renewal_validation_idempotency_and_order_refund(v2_tenant):
    with SessionLocal() as db:
        before = datetime.now(timezone.utc)
        full = grant(db, v2_tenant, "full_assessment_v2", "1")
        expiry = db.get(TenantProductEntitlement, full.entitlement_id).valid_until_utc
        assert before + timedelta(days=14, seconds=-1) <= expiry.replace(tzinfo=timezone.utc) <= before + timedelta(days=14, seconds=5)
        assert full.credit_id is None
        db.commit()
        replay = grant(db, v2_tenant, "full_assessment_v2", "1")
        assert replay.id == full.id
        renewal = grant(db, v2_tenant, "access_renewal", "2")
        assert renewal.credit_id is None
        validation = grant(db, v2_tenant, "access_renewal_validation", "3")
        assert validation.credit_id is not None
        renewal_expiry = db.get(TenantProductEntitlement, renewal.entitlement_id).valid_until_utc
        validation_expiry = db.get(TenantProductEntitlement, validation.entitlement_id).valid_until_utc
        assert renewal_expiry - expiry == timedelta(days=14)
        assert validation_expiry - renewal_expiry == timedelta(days=14)
        db.commit()
        assert len(db.scalars(select(TenantScanCredit).where(TenantScanCredit.tenant_id == v2_tenant, TenantScanCredit.status == "available")).all()) == 1
        revoke_fiverr_v2(db, tenant_id=v2_tenant, order_reference="order-1", order_position="1", actor="operator")
        db.commit()
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == v2_tenant))
        assert build_product_access_snapshot(db, tenant)["premium_active"]
        assert db.get(TenantProductEntitlement, full.entitlement_id).status == "revoked"
        assert db.get(TenantProductEntitlement, renewal.entitlement_id).status == "active"
        assert db.get(TenantProductEntitlement, validation.entitlement_id).status == "active"
        assert revoke_fiverr_v2(db, tenant_id=v2_tenant, order_reference="order-1", order_position="1", actor="operator").action_type == "v2_purchase_revoke"
        revoke_fiverr_v2(db, tenant_id=v2_tenant, order_reference="order-1", order_position="3", actor="operator")
        db.commit()
        revoke_fiverr_v2(db, tenant_id=v2_tenant, order_reference="order-1", order_position="3", actor="operator")
        db.commit()
        assert db.get(TenantScanCredit, validation.credit_id).status == "revoked"
        assert len(db.scalars(select(CreditLedgerEntry).where(
            CreditLedgerEntry.credit_id == validation.credit_id,
            CreditLedgerEntry.operation_type == "PURCHASE_REVOKED",
        )).all()) == 1


def test_invalid_company_cannot_receive_full(v2_tenant):
    with SessionLocal() as db:
        db.scalar(select(Tenant).where(Tenant.tenant_id == v2_tenant)).bc_company_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        db.flush()
        with pytest.raises(ValueError, match="verified original Free scan"):
            grant(db, v2_tenant, "full_assessment_v2", "1")


def test_legacy_executive_endpoint_rejects_other_company(v2_tenant):
    from fastapi import HTTPException
    from app.routers.reports import _require_owned_scan

    with SessionLocal() as db:
        _require_owned_scan(db, v2_tenant, "operator-v2-free")
        scan = db.scalar(select(Scan).where(Scan.scan_id == "operator-v2-free"))
        scan.bc_company_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        db.flush()
        with pytest.raises(HTTPException) as exc:
            _require_owned_scan(db, v2_tenant, "operator-v2-free")
        assert exc.value.status_code == 404


def test_monitoring_survives_full_refund_and_ends_on_own_refund(v2_tenant):
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        grant(db, v2_tenant, "full_assessment_v2", "1")
        monitoring = grant_fiverr_monitoring(
            db, tenant_id=v2_tenant, product_code="monitoring_monthly", order_reference="order-1",
            order_position="2", amount=199.0, period_start=now - timedelta(minutes=1),
            period_end=now + timedelta(days=30), actor="operator",
        )
        db.commit()
        revoke_fiverr_v2(db, tenant_id=v2_tenant, order_reference="order-1", order_position="1", actor="operator")
        db.commit()
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == v2_tenant))
        assert build_product_access_snapshot(db, tenant)["monitoring_active"]
        assert monitoring.action_type == "v2_purchase_grant"
        cancellation = cancel_fiverr_monitoring(db, tenant_id=v2_tenant, order_reference="order-1", order_position="2", actor="operator")
        db.commit()
        assert cancel_fiverr_monitoring(db, tenant_id=v2_tenant, order_reference="order-1", order_position="2", actor="operator").id == cancellation.id
        assert build_product_access_snapshot(db, tenant)["monitoring_active"]
        revoke_fiverr_v2(db, tenant_id=v2_tenant, order_reference="order-1", order_position="2", actor="operator")
        db.commit()
        assert not build_product_access_snapshot(db, tenant)["monitoring_active"]
        assert build_product_access_snapshot(db, tenant)["free_access_permanent"]


def test_monitoring_future_and_expired_periods_cannot_grant_scans(v2_tenant):
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        grant_fiverr_monitoring(db, tenant_id=v2_tenant, product_code="monitoring_monthly",
                                order_reference="future", order_position="1", amount=199.0,
                                period_start=now + timedelta(days=1), period_end=now + timedelta(days=31), actor="operator")
        grant_fiverr_monitoring(db, tenant_id=v2_tenant, product_code="monitoring_monthly",
                                order_reference="expired", order_position="1", amount=199.0,
                                period_start=now - timedelta(days=31), period_end=now - timedelta(days=1), actor="operator")
        db.commit()
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == v2_tenant))
        access = build_product_access_snapshot(db, tenant)
        assert not access["monitoring_active"]
        assert not access["can_run_deep_scan"]


def test_full_pass_is_not_stacked_on_monitoring_end(v2_tenant):
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        grant_fiverr_monitoring(db, tenant_id=v2_tenant, product_code="monitoring_annual",
                                order_reference="monitoring", order_position="1", amount=1990.0,
                                period_start=now - timedelta(days=1), period_end=now + timedelta(days=300), actor="operator")
        full = grant(db, v2_tenant, "full_assessment_v2", "1")
        expiry = db.get(TenantProductEntitlement, full.entitlement_id).valid_until_utc
        assert now + timedelta(days=14, seconds=-1) <= expiry.replace(tzinfo=timezone.utc) <= now + timedelta(days=14, seconds=10)


def test_parallel_same_order_position_issues_once(v2_tenant):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from app.db import engine

    if engine.dialect.name != "postgresql":
        pytest.skip("Concurrency requires PostgreSQL")
    barrier = Barrier(2)

    def issue():
        with SessionLocal() as db:
            barrier.wait(timeout=10)
            action = grant(db, v2_tenant, "full_assessment_v2", "1")
            db.commit()
            return action.id

    with ThreadPoolExecutor(max_workers=2) as pool:
        ids = list(pool.map(lambda _: issue(), range(2)))
    assert ids[0] == ids[1]
    with SessionLocal() as db:
        assert len(db.scalars(select(TenantProductEntitlement).where(
            TenantProductEntitlement.tenant_id == v2_tenant,
            TenantProductEntitlement.product_code == "full_assessment_v2",
        )).all()) == 1


def test_consumed_validation_credit_and_scan_survive_refund(v2_tenant, scan_factory):
    scan_factory(tenant_id=v2_tenant, scan_id="operator-v2-validation")
    with SessionLocal() as db:
        grant(db, v2_tenant, "full_assessment_v2", "1")
        validation = grant(db, v2_tenant, "access_renewal_validation", "2")
        credit = db.get(TenantScanCredit, validation.credit_id)
        credit.status = "consumed"
        credit.consumed_at_utc = datetime.now(timezone.utc)
        credit.consumed_scan_id = "operator-v2-validation"
        db.commit()
        revoke_fiverr_v2(db, tenant_id=v2_tenant, order_reference="order-1", order_position="2", actor="operator")
        db.commit()
        assert credit.status == "consumed"
        assert db.scalar(select(Scan).where(Scan.scan_id == "operator-v2-validation")) is not None
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == v2_tenant))
        assert build_product_access_snapshot(db, tenant)["free_access_permanent"]
        assert build_product_access_snapshot(db, tenant)["premium_active"]


def test_http_grant_requires_authentication_and_csrf(client, v2_tenant, tenant_factory):
    import base64

    url = f"/admin/operator/{v2_tenant}/v2/grant"
    payload = {"product_code": "full_assessment_v2", "order_reference": "http-order",
               "order_position": "1", "amount_eur": "249.00"}
    token = base64.b64encode(b"admin-test:admin-password-for-tests-123").decode("ascii")
    headers = {"Authorization": f"Basic {token}"}
    assert client.get("/admin/operator", headers=headers).status_code == 200
    csrf = client.cookies.get("bcs_csrf")
    assert client.post(url, data={**payload, "csrf_token": csrf}).status_code == 401
    assert client.post(url, data={**payload, "csrf_token": "invalid"}, headers=headers).status_code == 403
    response = client.post(url, data={**payload, "csrf_token": csrf}, headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()["credit_id"] is None
    replay = client.post(url, data={**payload, "csrf_token": csrf}, headers=headers)
    assert replay.status_code == 200
    assert replay.json()["action_id"] == response.json()["action_id"]
    other = tenant_factory(plan="free", license_status="active")
    foreign = client.post(f"/admin/operator/{other['tenant_id']}/v2/grant",
                          data={**payload, "csrf_token": csrf}, headers=headers)
    assert foreign.status_code == 409
    invalid = client.post(url, data={**payload, "order_position": "2", "product_code": "unsupported", "csrf_token": csrf}, headers=headers)
    assert invalid.status_code == 409
    revoke_url = f"/admin/operator/{v2_tenant}/v2/revoke"
    revoke_data = {"order_reference": "http-order", "order_position": "1", "reason": "Refund confirmed", "csrf_token": csrf}
    assert client.post(revoke_url, data=revoke_data, headers=headers).status_code == 200
    assert client.post(revoke_url, data=revoke_data, headers=headers).status_code == 200
    assert client.post(url, data={**payload, "csrf_token": csrf}, headers=headers).status_code == 409


def test_refunding_first_of_two_stacked_purchases_does_not_retain_refunded_days(v2_tenant):
    with SessionLocal() as db:
        before = datetime.now(timezone.utc)
        grant(db, v2_tenant, "full_assessment_v2", "1")
        grant(db, v2_tenant, "access_renewal", "2")
        db.commit()
        revoke_fiverr_v2(db, tenant_id=v2_tenant, order_reference="order-1", order_position="1", actor="operator")
        db.commit()
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == v2_tenant))
        snapshot = build_product_access_snapshot(db, tenant)
        expiry = datetime.fromisoformat(snapshot["premium_access_until"].replace("Z", "+00:00"))
        assert before + timedelta(days=14, seconds=-1) <= expiry <= before + timedelta(days=14, seconds=10)


def test_refund_after_ten_days_preserves_full_renewal_duration(v2_tenant, monkeypatch):
    clock = datetime.now(timezone.utc)
    monkeypatch.setattr("app.services.product_license_service.utc_now", lambda: clock)
    with SessionLocal() as db:
        grant(db, v2_tenant, "full_assessment_v2", "1")
        renewal = grant(db, v2_tenant, "access_renewal", "2")
        db.commit()
        clock += timedelta(days=10)
        revoke_fiverr_v2(db, tenant_id=v2_tenant, order_reference="order-1", order_position="1", actor="operator")
        db.commit()
        assert db.get(TenantProductEntitlement, renewal.entitlement_id).valid_until_utc.replace(tzinfo=timezone.utc) == clock + timedelta(days=14)


def test_refund_before_grant_blocks_replay(v2_tenant):
    with SessionLocal() as db:
        revoked = revoke_fiverr_v2(db, tenant_id=v2_tenant, order_reference="order-1", order_position="1", actor="operator")
        db.commit()
        assert revoke_fiverr_v2(db, tenant_id=v2_tenant, order_reference="order-1", order_position="1", actor="operator").id == revoked.id
        with pytest.raises(ValueError, match="already been reversed"):
            grant(db, v2_tenant, "full_assessment_v2", "1")
        assert not db.scalars(select(TenantProductEntitlement).where(
            TenantProductEntitlement.tenant_id == v2_tenant,
            TenantProductEntitlement.product_code == "full_assessment_v2",
        )).all()
