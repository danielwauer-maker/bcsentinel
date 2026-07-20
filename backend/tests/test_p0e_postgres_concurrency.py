from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Barrier
from uuid import uuid4

import pytest

from app.db import SessionLocal, engine
from app.models import CreditLedgerEntry, ScanRunEvent, ScanRunStatus, Subscription, TenantScanCredit
from app.services.product_license_service import grant_scan_credit
from app.services.scan_status_service import (
    ScanLeaseConflictError,
    claim_scan_run,
    create_or_get_scan_run,
    recover_stale_runs,
    update_scan_progress,
    utc_now,
)


pytestmark = pytest.mark.skipif(
    engine.dialect.name != "postgresql",
    reason="GL-EXT-P0E requires real PostgreSQL locking semantics.",
)


def _headers(tenant):
    return {"X-Tenant-Id": tenant["tenant_id"], "X-Api-Token": tenant["api_token"]}


def _start(client, tenant, *, mode: str, run_id: str):
    return client.post(
        "/scan/start",
        headers=_headers(tenant),
        json={
            "tenant_id": tenant["tenant_id"],
            "client_request_id": str(uuid4()),
            "run_id": run_id,
            "scan_mode": mode,
            "total_modules": 2,
            "company_name": "P0E Company",
            "environment_name": "P0E PostgreSQL",
        },
    )


def test_parallel_different_registrations_remain_isolated(client, settings_state):
    settings_state(
        TENANT_REGISTRATION_INVITE_CODE="p0e-invite",
        TENANT_REGISTRATION_RATE_LIMIT_ATTEMPTS=20,
    )

    def register(index: int):
        return client.post(
            "/tenant/register",
            headers={"X-Registration-Invite": "p0e-invite"},
            json={
                "entra_tenant_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "environment_name": "P0E PostgreSQL",
                "environment_type": "sandbox",
                "company_id": f"00000000-0000-0000-0000-{index:012d}",
                "company_name": f"P0E Company {index}",
                "app_version": "1.0.2.6",
                "preferred_language": "en",
                "contact_email": f"p0e-{index}@example.invalid",
            },
        )

    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = list(pool.map(register, range(4)))

    assert {response.status_code for response in responses} == {200}
    assert len({response.json()["tenant_id"] for response in responses}) == 4


def test_parallel_validation_starts_consume_one_validation_credit(client, tenant_factory):
    tenant = tenant_factory()
    with SessionLocal() as db:
        grant_scan_credit(db, tenant_id=tenant["tenant_id"], product_code="validation_check", source="p0e")
        db.commit()

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda n: _start(client, tenant, mode="validation", run_id=f"P0E_VALIDATION_{n}"), range(2)))

    assert sorted(response.status_code for response in responses) == [200, 402]
    with SessionLocal() as db:
        assert db.query(TenantScanCredit).filter_by(tenant_id=tenant["tenant_id"], status="consumed").count() == 1
        assert db.query(CreditLedgerEntry).filter_by(tenant_id=tenant["tenant_id"], operation_type="SCAN_CONSUMED").count() == 1


def test_parallel_monitoring_starts_do_not_consume_credit(client, tenant_factory):
    tenant = tenant_factory()
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(
            Subscription(
                tenant_id=tenant["tenant_id"],
                provider="p0e",
                provider_subscription_id=f"sub_{uuid4().hex}",
                status="active",
                plan_code="monitoring_monthly",
                currency="EUR",
                amount_monthly=149,
                current_period_start_utc=now - timedelta(days=1),
                current_period_end_utc=now + timedelta(days=30),
                cancel_at_period_end=False,
                created_at_utc=now,
                updated_at_utc=now,
            )
        )
        db.commit()

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda n: _start(client, tenant, mode="monitoring", run_id=f"P0E_MONITORING_{n}"), range(2)))

    assert [response.status_code for response in responses] == [200, 200]
    with SessionLocal() as db:
        assert db.query(CreditLedgerEntry).filter_by(tenant_id=tenant["tenant_id"], operation_type="SCAN_CONSUMED").count() == 0


def test_heartbeat_and_recovery_compete_without_lost_state(tenant_factory, settings_state):
    settings_state(SCAN_STALLED_AFTER_SECONDS=1, SCAN_RETRY_BACKOFF_SECONDS=1)
    tenant = tenant_factory()
    run_id = "P0E_HEARTBEAT_RECOVERY"
    with SessionLocal() as db:
        run = create_or_get_scan_run(db, run_id=run_id, tenant_id=tenant["tenant_id"], total_modules=2)
        token = run.lease_token
        claim_scan_run(db, run_id=run_id, tenant_id=tenant["tenant_id"], lease_token=token, worker_id="p0e-worker")
        run.heartbeat_at_utc = utc_now() - timedelta(minutes=5)
        run.lease_expires_at_utc = utc_now() - timedelta(seconds=1)
        db.commit()

    barrier = Barrier(2)

    def heartbeat():
        barrier.wait()
        try:
            with SessionLocal() as db:
                update_scan_progress(
                    db,
                    run_id=run_id,
                    status="running",
                    lease_token=token,
                    worker_id="p0e-worker",
                    progress_percent=50,
                    event_message="P0E heartbeat",
                )
                db.commit()
            return "heartbeat"
        except ScanLeaseConflictError:
            return "lease_lost"

    def recover():
        barrier.wait()
        with SessionLocal() as db:
            outcome = recover_stale_runs(db)
            db.commit()
            return outcome["requeued"]

    with ThreadPoolExecutor(max_workers=2) as pool:
        heartbeat_result = pool.submit(heartbeat)
        recovery_result = pool.submit(recover)
        outcomes = (heartbeat_result.result(), recovery_result.result())

    with SessionLocal() as db:
        run = db.query(ScanRunStatus).filter_by(run_id=run_id).one()
        recovery_events = db.query(ScanRunEvent).filter_by(run_id=run_id, event_type="scan_retry_scheduled").count()
        assert run.status in {"running", "queued"}
        assert recovery_events <= 1
        assert outcomes in {("heartbeat", 0), ("lease_lost", 1)}


def test_parallel_access_snapshot_refresh_is_tenant_bound(client, tenant_factory):
    tenant = tenant_factory()
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = list(pool.map(lambda _: client.get("/license/status", headers=_headers(tenant)), range(4)))

    assert {response.status_code for response in responses} == {200}
    snapshots = [response.json() for response in responses]
    assert {snapshot["tenant_id"] for snapshot in snapshots} == {tenant["tenant_id"]}
    assert {snapshot["snapshot_version"] for snapshot in snapshots} == {"p0d-v1"}


def test_parallel_token_issuance_after_expiry_is_denied(client, tenant_factory):
    tenant = tenant_factory()
    query = {
        "tenant_id": tenant["tenant_id"],
        "company_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "company": "P0E Company",
        "environment": "P0E PostgreSQL",
        "environment_type": "sandbox",
        "entra_tenant_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    }
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = list(pool.map(lambda _: client.get("/analytics/get-token", headers=_headers(tenant), params=query), range(4)))

    assert {response.status_code for response in responses} == {403}
