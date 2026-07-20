from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from app.db import SessionLocal
from app.models import CreditLedgerEntry, ScanRunStatus, TenantScanCredit
from app.services.product_license_service import grant_scan_credit
from app.services.scan_status_service import recover_stale_runs, utc_now


def _headers(tenant: dict[str, str]) -> dict[str, str]:
    return {"X-Tenant-Id": tenant["tenant_id"], "X-Api-Token": tenant["api_token"]}


def _grant_credit(tenant_id: str) -> None:
    with SessionLocal() as db:
        grant_scan_credit(db, tenant_id=tenant_id, product_code="full_analysis", source="fix04_test")
        db.commit()


def _start_payload(tenant_id: str, run_id: str, request_id: str) -> dict[str, object]:
    return {
        "tenant_id": tenant_id,
        "run_id": run_id,
        "client_request_id": request_id,
        "scan_mode": "assessment",
        "total_modules": 2,
        "company_name": "CRONUS",
        "environment_name": "sandbox",
    }


def _status_payload(tenant_id: str, run_id: str, token: str, worker_id: str, progress: int = 10) -> dict[str, object]:
    return {
        "tenant_id": tenant_id,
        "run_id": run_id,
        "scan_mode": "assessment",
        "status": "running",
        "progress_percent": progress,
        "current_module": "System",
        "current_step": "Running checks",
        "event_message": "Heartbeat",
        "total_modules": 2,
        "completed_modules": 0,
        "execution_token": token,
        "worker_id": worker_id,
    }


def _sync_payload(tenant_id: str, run_id: str, token: str, worker_id: str, correlation_id: str) -> dict[str, object]:
    return {
        "tenant_id": tenant_id,
        "scan_id": run_id,
        "scan_type": "deep",
        "generated_at_utc": utc_now().isoformat(),
        "data_score": 91,
        "checks_count": 12,
        "issues_count": 0,
        "headline": "Scan completed",
        "rating": "Good",
        "enabled_modules": ["System", "Finance"],
        "execution_token": token,
        "worker_id": worker_id,
        "correlation_id": correlation_id,
    }


def _accepted_start(client, tenant_factory, run_id: str):
    tenant = tenant_factory()
    _grant_credit(tenant["tenant_id"])
    request_id = str(uuid4())
    payload = _start_payload(tenant["tenant_id"], run_id, request_id)
    response = client.post("/scan/start", headers=_headers(tenant), json=payload)
    assert response.status_code == 200
    return tenant, request_id, payload, response.json()


def test_accepted_lease_survives_sequential_updates_replay_and_final_sync(client, tenant_factory):
    tenant, worker_id, start_payload, accepted = _accepted_start(client, tenant_factory, "FIX04_FULL_LIFECYCLE")
    token = accepted["execution_token"]
    assert accepted["worker_id"] == worker_id

    for progress in (1, 25, 75):
        response = client.post(
            "/scan/status/update",
            headers=_headers(tenant),
            json=_status_payload(tenant["tenant_id"], "FIX04_FULL_LIFECYCLE", token, worker_id, progress),
        )
        assert response.status_code == 200
        assert response.json()["execution_token"] == token

    replay = client.post("/scan/start", headers=_headers(tenant), json=start_payload)
    assert replay.status_code == 200
    assert replay.json()["idempotent_replay"] is True
    assert replay.json()["execution_token"] == token

    synced = client.post(
        "/scan/sync",
        headers=_headers(tenant),
        json=_sync_payload(tenant["tenant_id"], "FIX04_FULL_LIFECYCLE", token, worker_id, accepted["correlation_id"]),
    )
    assert synced.status_code == 200

    with SessionLocal() as db:
        run = db.query(ScanRunStatus).filter_by(run_id="FIX04_FULL_LIFECYCLE").one()
        assert run.status == "completed" and run.result_persisted_at_utc and run.completed_at_utc
        assert db.query(TenantScanCredit).filter_by(tenant_id=tenant["tenant_id"], status="consumed").count() == 1
        assert db.query(CreditLedgerEntry).filter_by(tenant_id=tenant["tenant_id"], operation_type="SCAN_CONSUMED").count() == 1


def test_old_heartbeat_does_not_rotate_a_still_valid_lease(client, tenant_factory, settings_state):
    settings_state(SCAN_STALLED_AFTER_SECONDS=10, SCAN_LEASE_SECONDS=3600)
    tenant, worker_id, _, accepted = _accepted_start(client, tenant_factory, "FIX04_LONG_MODULE")
    token = accepted["execution_token"]
    assert client.post(
        "/scan/status/update",
        headers=_headers(tenant),
        json=_status_payload(tenant["tenant_id"], "FIX04_LONG_MODULE", token, worker_id),
    ).status_code == 200

    with SessionLocal() as db:
        run = db.query(ScanRunStatus).filter_by(run_id="FIX04_LONG_MODULE").one()
        run.heartbeat_at_utc = utc_now() - timedelta(minutes=30)
        run.lease_expires_at_utc = utc_now() + timedelta(minutes=30)
        db.commit()
    with SessionLocal() as db:
        assert recover_stale_runs(db)["requeued"] == 0
        db.commit()
        run = db.query(ScanRunStatus).filter_by(run_id="FIX04_LONG_MODULE").one()
        assert run.status == "running" and run.lease_token == token


def test_structured_wrong_token_worker_and_expired_lease_conflicts(client, tenant_factory):
    tenant, worker_id, _, accepted = _accepted_start(client, tenant_factory, "FIX04_STRUCTURED_CONFLICTS")
    token = accepted["execution_token"]
    assert client.post(
        "/scan/status/update",
        headers=_headers(tenant),
        json=_status_payload(tenant["tenant_id"], "FIX04_STRUCTURED_CONFLICTS", token, worker_id),
    ).status_code == 200

    wrong_token = client.post(
        "/scan/status/update",
        headers=_headers(tenant),
        json=_status_payload(tenant["tenant_id"], "FIX04_STRUCTURED_CONFLICTS", str(uuid4()), worker_id),
    )
    assert wrong_token.status_code == 409 and wrong_token.json()["code"] == "scan_execution_token_stale"

    wrong_worker = client.post(
        "/scan/status/update",
        headers=_headers(tenant),
        json=_status_payload(tenant["tenant_id"], "FIX04_STRUCTURED_CONFLICTS", token, "another-worker"),
    )
    assert wrong_worker.status_code == 409 and wrong_worker.json()["code"] == "scan_worker_mismatch"

    wrong_sync = client.post(
        "/scan/sync",
        headers=_headers(tenant),
        json=_sync_payload(
            tenant["tenant_id"],
            "FIX04_STRUCTURED_CONFLICTS",
            str(uuid4()),
            worker_id,
            accepted["correlation_id"],
        ),
    )
    assert wrong_sync.status_code == 409 and wrong_sync.json()["code"] == "scan_execution_token_stale"

    with SessionLocal() as db:
        run = db.query(ScanRunStatus).filter_by(run_id="FIX04_STRUCTURED_CONFLICTS").one()
        run.lease_expires_at_utc = utc_now() - timedelta(seconds=1)
        db.commit()
    expired = client.post(
        "/scan/status/update",
        headers=_headers(tenant),
        json=_status_payload(tenant["tenant_id"], "FIX04_STRUCTURED_CONFLICTS", token, worker_id),
    )
    assert expired.status_code == 409 and expired.json()["code"] == "scan_execution_lease_expired"


def test_recovery_rotates_expired_lease_and_rejects_old_worker(client, tenant_factory, settings_state):
    settings_state(SCAN_STALLED_AFTER_SECONDS=1, SCAN_RETRY_BACKOFF_SECONDS=1)
    tenant, worker_id, _, accepted = _accepted_start(client, tenant_factory, "FIX04_ROTATED")
    old_token = accepted["execution_token"]
    assert client.post(
        "/scan/status/update",
        headers=_headers(tenant),
        json=_status_payload(tenant["tenant_id"], "FIX04_ROTATED", old_token, worker_id),
    ).status_code == 200
    with SessionLocal() as db:
        run = db.query(ScanRunStatus).filter_by(run_id="FIX04_ROTATED").one()
        run.heartbeat_at_utc = utc_now() - timedelta(minutes=5)
        run.lease_expires_at_utc = utc_now() - timedelta(seconds=1)
        db.commit()
    with SessionLocal() as db:
        assert recover_stale_runs(db)["requeued"] == 1
        db.commit()
        assert db.query(ScanRunStatus).filter_by(run_id="FIX04_ROTATED").one().lease_token != old_token

    rejected = client.post(
        "/scan/status/update",
        headers=_headers(tenant),
        json=_status_payload(tenant["tenant_id"], "FIX04_ROTATED", old_token, worker_id),
    )
    assert rejected.status_code == 409 and rejected.json()["code"] == "scan_execution_token_stale"


def test_other_tenant_cannot_adopt_run_even_with_leaked_execution_identity(client, tenant_factory):
    owner, worker_id, _, accepted = _accepted_start(client, tenant_factory, "FIX04_TENANT_BOUND")
    attacker = tenant_factory()
    response = client.post(
        "/scan/status/update",
        headers=_headers(attacker),
        json=_status_payload(attacker["tenant_id"], "FIX04_TENANT_BOUND", accepted["execution_token"], worker_id),
    )
    assert response.status_code == 409 and response.json()["code"] == "scan_execution_not_owned"
    with SessionLocal() as db:
        assert db.query(ScanRunStatus).filter_by(run_id="FIX04_TENANT_BOUND").one().tenant_id == owner["tenant_id"]


def test_same_start_replay_returns_rotated_current_lease_without_second_credit(client, tenant_factory, settings_state):
    settings_state(SCAN_STALLED_AFTER_SECONDS=1, SCAN_RETRY_BACKOFF_SECONDS=1)
    tenant, worker_id, start_payload, accepted = _accepted_start(client, tenant_factory, "FIX04_REPLAY_CURRENT")
    old_token = accepted["execution_token"]
    assert client.post(
        "/scan/status/update",
        headers=_headers(tenant),
        json=_status_payload(tenant["tenant_id"], "FIX04_REPLAY_CURRENT", old_token, worker_id),
    ).status_code == 200
    with SessionLocal() as db:
        run = db.query(ScanRunStatus).filter_by(run_id="FIX04_REPLAY_CURRENT").one()
        run.heartbeat_at_utc = utc_now() - timedelta(minutes=5)
        run.lease_expires_at_utc = utc_now() - timedelta(seconds=1)
        db.commit()
    with SessionLocal() as db:
        assert recover_stale_runs(db)["requeued"] == 1
        db.commit()
        current_token = db.query(ScanRunStatus).filter_by(run_id="FIX04_REPLAY_CURRENT").one().lease_token
    assert current_token and current_token != old_token

    replay = client.post("/scan/start", headers=_headers(tenant), json=start_payload)
    assert replay.status_code == 200
    assert replay.json()["idempotent_replay"] is True
    assert replay.json()["execution_token"] == current_token
    with SessionLocal() as db:
        assert db.query(TenantScanCredit).filter_by(tenant_id=tenant["tenant_id"], status="consumed").count() == 1
        assert db.query(CreditLedgerEntry).filter_by(tenant_id=tenant["tenant_id"], operation_type="SCAN_CONSUMED").count() == 1
