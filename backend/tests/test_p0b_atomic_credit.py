from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.db import SessionLocal
from app.models import CreditLedgerEntry, Scan, ScanRunStatus, ScanStartRequest, Subscription, Tenant, TenantScanCredit
from app.services.atomic_scan_start_service import accept_scan_start
from app.services.product_license_service import grant_scan_credit


def _grant(tenant_id: str, product: str, count: int = 1) -> None:
    with SessionLocal() as db:
        for _ in range(count):
            grant_scan_credit(db, tenant_id=tenant_id, product_code=product, source="test_explicit")
        db.commit()


def _monitoring(tenant_id: str, *, expired: bool = False) -> None:
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(Subscription(
            tenant_id=tenant_id, provider="test", provider_subscription_id=f"sub_{uuid4().hex}",
            status="active", plan_code="monitoring_monthly", currency="EUR", amount_monthly=149,
            current_period_start_utc=now - timedelta(days=2),
            current_period_end_utc=now - timedelta(days=1) if expired else now + timedelta(days=20),
            cancel_at_period_end=False, created_at_utc=now, updated_at_utc=now,
        ))
        db.commit()


def _start(client, tenant, *, request_id=None, run_id=None, mode="assessment", total_modules=3):
    return client.post(
        "/scan/start",
        headers={"X-Tenant-Id": tenant["tenant_id"], "X-Api-Token": tenant["api_token"]},
        json={
            "tenant_id": tenant["tenant_id"],
            "client_request_id": request_id or str(uuid4()),
            "run_id": run_id or f"RUN_{uuid4().hex[:20]}",
            "scan_mode": mode,
            "total_modules": total_modules,
            "company_name": "CRONUS",
            "environment_name": "Production",
        },
    )


def _counts(tenant_id: str):
    with SessionLocal() as db:
        return {
            "available": db.query(TenantScanCredit).filter_by(tenant_id=tenant_id, status="available").count(),
            "consumed": db.query(TenantScanCredit).filter_by(tenant_id=tenant_id, status="consumed").count(),
            "scans": db.query(Scan).filter_by(tenant_id=tenant_id).count(),
            "requests": db.query(ScanStartRequest).filter_by(tenant_id=tenant_id).count(),
            "consumption_ledger": db.query(CreditLedgerEntry).filter_by(tenant_id=tenant_id, operation_type="SCAN_CONSUMED").count(),
        }


def test_legacy_assessment_mode_consumes_exactly_one_validation_credit(client, tenant_factory):
    tenant = tenant_factory()
    _grant(tenant["tenant_id"], "validation_check")
    response = _start(client, tenant, mode="assessment")
    assert response.status_code == 200 and response.json()["credit_consumed"] is True
    assert _counts(tenant["tenant_id"])["consumed"] == 1


def test_validation_consumes_validation_not_assessment(client, tenant_factory):
    tenant = tenant_factory()
    with SessionLocal() as db:
        now = datetime.now(timezone.utc)
        db.add(TenantScanCredit(tenant_id=tenant["tenant_id"], product_code="full_analysis", status="available", source="legacy", created_at_utc=now))
        db.query(Tenant).filter_by(tenant_id=tenant["tenant_id"]).update({"free_assessment_used": True})
        db.commit()
    assert _start(client, tenant, mode="validation").status_code == 402
    _grant(tenant["tenant_id"], "validation_check")
    assert _start(client, tenant, mode="validation").status_code == 200
    with SessionLocal() as db:
        consumed = db.query(TenantScanCredit).filter_by(tenant_id=tenant["tenant_id"], status="consumed").one()
        assert consumed.product_code == "validation_check"


def test_monitoring_consumes_no_credit_and_expiry_blocks(client, tenant_factory):
    active = tenant_factory()
    _monitoring(active["tenant_id"])
    assert _start(client, active, mode="monitoring").status_code == 200
    assert _counts(active["tenant_id"])["consumption_ledger"] == 0
    expired = tenant_factory()
    _monitoring(expired["tenant_id"], expired=True)
    with SessionLocal() as db:
        db.query(Tenant).filter_by(tenant_id=expired["tenant_id"]).update({"free_assessment_used": True})
        db.commit()
    assert _start(client, expired, mode="monitoring").status_code == 402


def test_identical_retry_and_scheduler_retry_return_same_scan(client, tenant_factory):
    tenant = tenant_factory()
    _grant(tenant["tenant_id"], "validation_check")
    request_id, run_id = str(uuid4()), "RUN_RETRY_STABLE"
    first = _start(client, tenant, request_id=request_id, run_id=run_id)
    retry = _start(client, tenant, request_id=request_id, run_id=run_id)
    assert first.status_code == retry.status_code == 200
    assert retry.json()["idempotent_replay"] is True
    assert retry.json()["scan_id"] == first.json()["scan_id"]
    assert _counts(tenant["tenant_id"]) == {"available": 0, "consumed": 1, "scans": 1, "requests": 1, "consumption_ledger": 1}


def test_same_key_different_payload_is_conflict(client, tenant_factory):
    tenant = tenant_factory()
    _grant(tenant["tenant_id"], "validation_check")
    request_id = str(uuid4())
    assert _start(client, tenant, request_id=request_id, run_id="RUN_PAYLOAD_A").status_code == 200
    conflict = _start(client, tenant, request_id=request_id, run_id="RUN_PAYLOAD_B")
    assert conflict.status_code == 409
    assert conflict.json()["code"] == "SCAN_REQUEST_PAYLOAD_CONFLICT"
    assert _counts(tenant["tenant_id"])["consumed"] == 1


def test_same_scan_id_with_different_request_is_controlled_conflict_without_second_credit(client, tenant_factory):
    tenant = tenant_factory()
    _grant(tenant["tenant_id"], "validation_check", 2)
    run_id = "RUN_SCAN_ID_REUSE"
    first = _start(client, tenant, request_id=str(uuid4()), run_id=run_id)
    conflict = _start(client, tenant, request_id=str(uuid4()), run_id=run_id)

    assert first.status_code == 200
    assert conflict.status_code == 409
    assert conflict.json()["code"] == "SCAN_ID_REQUEST_CONFLICT"
    assert _counts(tenant["tenant_id"])["consumed"] == 1
    assert _counts(tenant["tenant_id"])["available"] == 1


def test_same_scan_id_in_another_tenant_is_not_adopted(client, tenant_factory):
    owner = tenant_factory()
    other = tenant_factory()
    _grant(owner["tenant_id"], "validation_check")
    _grant(other["tenant_id"], "validation_check")
    run_id = "RUN_CROSS_TENANT_COLLISION"

    assert _start(client, owner, run_id=run_id).status_code == 200
    conflict = _start(client, other, run_id=run_id)

    assert conflict.status_code == 409
    assert conflict.json()["code"] == "SCAN_ID_TENANT_CONFLICT"
    assert _counts(other["tenant_id"])["available"] == 1
    assert _counts(other["tenant_id"])["consumed"] == 0
    with SessionLocal() as db:
        assert db.query(ScanRunStatus).filter_by(tenant_id=other["tenant_id"]).count() == 0


def test_same_tenant_unbound_pending_scan_is_recovered_atomically(client, tenant_factory):
    tenant = tenant_factory()
    _grant(tenant["tenant_id"], "validation_check")
    run_id = "RUN_RECOVERABLE_ORPHAN"
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(
            Scan(
                scan_id=run_id,
                tenant_id=tenant["tenant_id"],
                scan_type="deep",
                generated_at_utc=now,
                data_score=0,
                checks_count=0,
                issues_count=0,
                premium_available=True,
                summary_headline="Deep scan queued",
                summary_rating="Pending",
                enabled_modules=None,
            )
        )
        db.commit()

    request_id = str(uuid4())
    accepted = _start(client, tenant, request_id=request_id, run_id=run_id)
    replay = _start(client, tenant, request_id=request_id, run_id=run_id)

    assert accepted.status_code == replay.status_code == 200
    assert replay.json()["idempotent_replay"] is True
    assert _counts(tenant["tenant_id"]) == {
        "available": 0,
        "consumed": 1,
        "scans": 1,
        "requests": 1,
        "consumption_ledger": 1,
    }


def test_completed_unbound_scan_is_not_recovered_or_charged(client, tenant_factory):
    tenant = tenant_factory()
    _grant(tenant["tenant_id"], "validation_check")
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(
            Scan(
                scan_id="RUN_NON_RECOVERABLE_ORPHAN",
                tenant_id=tenant["tenant_id"],
                scan_type="deep",
                generated_at_utc=now,
                data_score=80,
                checks_count=10,
                issues_count=2,
                premium_available=True,
                summary_headline="Completed scan",
                summary_rating="Good",
                enabled_modules=None,
            )
        )
        db.commit()

    conflict = _start(client, tenant, run_id="RUN_NON_RECOVERABLE_ORPHAN")
    assert conflict.status_code == 409
    assert conflict.json()["code"] == "SCAN_ID_CONFLICT"
    assert _counts(tenant["tenant_id"])["available"] == 1
    assert _counts(tenant["tenant_id"])["requests"] == 0
    with SessionLocal() as db:
        assert db.query(ScanRunStatus).filter_by(run_id="RUN_NON_RECOVERABLE_ORPHAN").count() == 0


def test_parallel_identical_requests_create_one_scan_and_ledger(client, tenant_factory):
    tenant = tenant_factory()
    _grant(tenant["tenant_id"], "validation_check")
    request_id = str(uuid4())
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = list(pool.map(lambda _: _start(client, tenant, request_id=request_id, run_id="RUN_PARALLEL_SAME"), range(4)))
    assert all(response.status_code == 200 for response in responses)
    counts = _counts(tenant["tenant_id"])
    assert counts["scans"] == counts["requests"] == counts["consumed"] == counts["consumption_ledger"] == 1


def test_parallel_different_requests_with_one_credit_allow_one(client, tenant_factory):
    tenant = tenant_factory()
    _grant(tenant["tenant_id"], "validation_check")
    with SessionLocal() as db:
        db.query(Tenant).filter_by(tenant_id=tenant["tenant_id"]).update({"free_assessment_used": True})
        db.commit()
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda n: _start(client, tenant, run_id=f"RUN_PARALLEL_{n}"), range(2)))
    assert sorted(response.status_code for response in responses) == [200, 402]
    counts = _counts(tenant["tenant_id"])
    assert counts["consumed"] == counts["scans"] == counts["consumption_ledger"] == 1


def test_request_scope_is_tenant_bound(client, tenant_factory):
    first, second = tenant_factory(), tenant_factory()
    _grant(first["tenant_id"], "validation_check")
    _grant(second["tenant_id"], "validation_check")
    shared = str(uuid4())
    a = _start(client, first, request_id=shared, run_id="RUN_TENANT_A")
    b = _start(client, second, request_id=shared, run_id="RUN_TENANT_B")
    assert a.status_code == b.status_code == 200
    assert a.json()["scan_id"] != b.json()["scan_id"]


def test_invalid_request_id_is_rejected_without_charge(client, tenant_factory):
    tenant = tenant_factory()
    _grant(tenant["tenant_id"], "validation_check")
    assert _start(client, tenant, request_id="not-a-guid").status_code == 422
    assert _counts(tenant["tenant_id"])["available"] == 1


def test_free_scan_is_once_per_tenant_and_idempotent(client, tenant_factory):
    tenant = tenant_factory()
    request_id = str(uuid4())
    assert _start(client, tenant, request_id=request_id, run_id="RUN_FREE_ONCE", mode="data_health_score").status_code == 200
    assert _start(client, tenant, request_id=request_id, run_id="RUN_FREE_ONCE", mode="data_health_score").status_code == 200
    assert _start(client, tenant, run_id="RUN_FREE_TWICE", mode="data_health_score").status_code == 402


def test_transaction_rolls_back_credit_scan_request_and_ledger(monkeypatch, tenant_factory):
    tenant_info = tenant_factory()
    _grant(tenant_info["tenant_id"], "validation_check")
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_info["tenant_id"]).one()
        monkeypatch.setattr("app.services.atomic_scan_start_service.create_or_get_scan_run", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("queue unavailable")))
        with pytest.raises(RuntimeError, match="queue unavailable"):
            accept_scan_start(db, tenant=tenant, client_request_id=str(uuid4()), run_id="RUN_ROLLBACK", scan_mode="assessment", total_modules=1, company_name=None, environment_name=None)
    counts = _counts(tenant_info["tenant_id"])
    assert counts["available"] == 1 and counts["consumed"] == counts["scans"] == counts["requests"] == counts["consumption_ledger"] == 0


def test_new_request_ids_create_new_scans_when_credits_exist(client, tenant_factory):
    tenant = tenant_factory()
    _grant(tenant["tenant_id"], "validation_check", 2)
    assert _start(client, tenant, run_id="RUN_NEW_1").status_code == 200
    assert _start(client, tenant, run_id="RUN_NEW_2").status_code == 200
    assert _counts(tenant["tenant_id"])["consumed"] == 2
