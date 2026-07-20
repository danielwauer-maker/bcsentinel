from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal
from app.models import CreditLedgerEntry, Scan, ScanIssueRecord, ScanRunEvent, ScanRunStatus, TenantScanCredit
from app.services.product_license_service import grant_scan_credit
from app.services.scan_status_service import (
    InvalidScanTransitionError,
    ScanLeaseConflictError,
    ScanResultIncompleteError,
    claim_scan_run,
    create_or_get_scan_run,
    mark_scan_result_persisted,
    recover_stale_runs,
    update_scan_progress,
    utc_now,
)


def _create_run(tenant_id: str, run_id: str, *, total_modules: int = 2) -> tuple[str, str]:
    with SessionLocal() as db:
        run = create_or_get_scan_run(db, run_id=run_id, tenant_id=tenant_id, total_modules=total_modules)
        token, correlation = run.lease_token, run.correlation_id
        db.commit()
    assert token and correlation
    return token, correlation


def _claim(tenant_id: str, run_id: str, token: str, worker: str = "bc-worker") -> None:
    with SessionLocal() as db:
        claim_scan_run(db, run_id=run_id, tenant_id=tenant_id, lease_token=token, worker_id=worker)
        db.commit()


def _persist_complete_result(db, tenant_id: str, run_id: str, *, issues: int = 1) -> ScanRunStatus:
    scan = db.query(Scan).filter_by(scan_id=run_id).one_or_none()
    if scan is None:
        scan = Scan(
            scan_id=run_id,
            tenant_id=tenant_id,
            scan_type="deep",
            generated_at_utc=utc_now(),
            data_score=90,
            checks_count=12,
            issues_count=issues,
            premium_available=True,
            summary_headline="Scan result ready",
            summary_rating="Good",
        )
        db.add(scan)
        db.flush()
    for index in range(issues):
        db.add(ScanIssueRecord(scan_id=run_id, code=f"ISSUE_{index}", title="Issue", severity="medium", affected_count=1, premium_only=False))
    db.flush()
    run = db.query(ScanRunStatus).filter_by(run_id=run_id).one()
    mark_scan_result_persisted(db, run)
    return run


def _grant(tenant_id: str) -> None:
    with SessionLocal() as db:
        grant_scan_credit(db, tenant_id=tenant_id, product_code="full_analysis", source="test_explicit")
        db.commit()


def _start(client, tenant, run_id: str):
    return client.post(
        "/scan/start",
        headers={"X-Tenant-Id": tenant["tenant_id"], "X-Api-Token": tenant["api_token"]},
        json={"tenant_id": tenant["tenant_id"], "run_id": run_id, "client_request_id": str(uuid4()), "scan_mode": "assessment", "total_modules": 2},
    )


def test_successful_scan_claim_and_complete_is_terminal(tenant_factory):
    tenant = tenant_factory()
    token, _ = _create_run(tenant["tenant_id"], "P0C_SUCCESS")
    _claim(tenant["tenant_id"], "P0C_SUCCESS", token)
    with SessionLocal() as db:
        run = _persist_complete_result(db, tenant["tenant_id"], "P0C_SUCCESS")
        run = update_scan_progress(db, run_id=run.run_id, status="completed", lease_token=token, worker_id="bc-worker", result_is_persisted=True)
        db.commit()
        assert run.status == "completed" and run.completed_at_utc and run.lease_owner is None


@pytest.mark.parametrize("code", ["validation_error", "unexpected_exception"])
def test_processing_errors_end_failed_and_are_non_retrying(tenant_factory, code):
    tenant = tenant_factory()
    token, _ = _create_run(tenant["tenant_id"], f"P0C_FAIL_{code}")
    _claim(tenant["tenant_id"], f"P0C_FAIL_{code}", token)
    with SessionLocal() as db:
        run = update_scan_progress(db, run_id=f"P0C_FAIL_{code}", status="failed", error_code=code, error_message="Customer-safe failure", lease_token=token, worker_id="bc-worker", event_message="Scan failed")
        db.commit()
        assert run.status == "failed" and run.failed_at_utc and run.next_retry_at_utc is None


def test_stale_running_is_requeued_with_backoff_and_same_run(tenant_factory, settings_state):
    settings_state(SCAN_STALLED_AFTER_SECONDS=10, SCAN_RETRY_BACKOFF_SECONDS=7, SCAN_MAX_ATTEMPTS=3)
    tenant = tenant_factory()
    token, _ = _create_run(tenant["tenant_id"], "P0C_STALE_RUNNING")
    _claim(tenant["tenant_id"], "P0C_STALE_RUNNING", token)
    with SessionLocal() as db:
        run = db.query(ScanRunStatus).filter_by(run_id="P0C_STALE_RUNNING").one()
        run.heartbeat_at_utc = utc_now() - timedelta(minutes=5)
        run.lease_expires_at_utc = utc_now() - timedelta(seconds=1)
        db.commit()
    with SessionLocal() as db:
        outcome = recover_stale_runs(db)
        db.commit()
        run = db.query(ScanRunStatus).filter_by(run_id="P0C_STALE_RUNNING").one()
        assert outcome["requeued"] == 1
        assert run.status == "queued" and run.retry_count == 1 and run.next_retry_at_utc
        assert run.lease_token != token


def test_stale_queued_expires_instead_of_blocking_scheduler(tenant_factory, settings_state):
    settings_state(SCAN_QUEUED_TIMEOUT_SECONDS=10)
    tenant = tenant_factory()
    _create_run(tenant["tenant_id"], "P0C_STALE_QUEUED")
    with SessionLocal() as db:
        run = db.query(ScanRunStatus).filter_by(run_id="P0C_STALE_QUEUED").one()
        run.updated_at_utc = utc_now() - timedelta(minutes=5)
        run.created_at_utc = run.updated_at_utc
        db.commit()
    with SessionLocal() as db:
        assert recover_stale_runs(db)["expired"] == 1
        db.commit()
        run = db.query(ScanRunStatus).filter_by(run_id="P0C_STALE_QUEUED").one()
        assert run.status == "expired" and run.error_code == "queue_timeout"


def test_valid_lease_prevents_second_worker(tenant_factory):
    tenant = tenant_factory()
    token, _ = _create_run(tenant["tenant_id"], "P0C_VALID_LEASE")
    _claim(tenant["tenant_id"], "P0C_VALID_LEASE", token, "worker-a")
    with SessionLocal() as db, pytest.raises(ScanLeaseConflictError):
        claim_scan_run(db, run_id="P0C_VALID_LEASE", tenant_id=tenant["tenant_id"], lease_token=token, worker_id="worker-b")


def test_parallel_workers_claim_exactly_once(tenant_factory):
    tenant = tenant_factory()
    token, _ = _create_run(tenant["tenant_id"], "P0C_PARALLEL_CLAIM")

    def attempt(worker: str) -> str:
        try:
            with SessionLocal() as db:
                claim_scan_run(db, run_id="P0C_PARALLEL_CLAIM", tenant_id=tenant["tenant_id"], lease_token=token, worker_id=worker)
                db.commit()
            return "claimed"
        except ScanLeaseConflictError:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, ["worker-a", "worker-b"]))
    assert sorted(results) == ["claimed", "conflict"]


def test_old_worker_cannot_write_after_recovery_rotates_token(tenant_factory, settings_state):
    settings_state(SCAN_STALLED_AFTER_SECONDS=10)
    tenant = tenant_factory()
    old_token, _ = _create_run(tenant["tenant_id"], "P0C_LATE_WORKER")
    _claim(tenant["tenant_id"], "P0C_LATE_WORKER", old_token)
    with SessionLocal() as db:
        run = db.query(ScanRunStatus).filter_by(run_id="P0C_LATE_WORKER").one()
        run.heartbeat_at_utc = utc_now() - timedelta(minutes=5)
        run.lease_expires_at_utc = utc_now() - timedelta(minutes=1)
        db.commit()
    with SessionLocal() as db:
        recover_stale_runs(db)
        db.commit()
    with SessionLocal() as db, pytest.raises(ScanLeaseConflictError):
        update_scan_progress(db, run_id="P0C_LATE_WORKER", status="running", lease_token=old_token, worker_id="bc-worker")
    with SessionLocal() as db:
        assert db.query(ScanRunEvent).filter_by(run_id="P0C_LATE_WORKER", event_type="scan_retry_scheduled").count() == 1


def test_heartbeat_extends_lease(tenant_factory, settings_state):
    settings_state(SCAN_LEASE_SECONDS=60)
    tenant = tenant_factory()
    token, _ = _create_run(tenant["tenant_id"], "P0C_HEARTBEAT")
    _claim(tenant["tenant_id"], "P0C_HEARTBEAT", token)
    with SessionLocal() as db:
        before = db.query(ScanRunStatus).filter_by(run_id="P0C_HEARTBEAT").one().lease_expires_at_utc
        run = update_scan_progress(db, run_id="P0C_HEARTBEAT", status="running", lease_token=token, worker_id="bc-worker", progress_percent=25, event_message="Heartbeat")
        db.commit()
        assert run.heartbeat_at_utc and run.lease_expires_at_utc >= before


def test_recovery_is_idempotent(tenant_factory, settings_state):
    settings_state(SCAN_QUEUED_TIMEOUT_SECONDS=10)
    tenant = tenant_factory()
    _create_run(tenant["tenant_id"], "P0C_RECOVERY_IDEMPOTENT")
    with SessionLocal() as db:
        run = db.query(ScanRunStatus).filter_by(run_id="P0C_RECOVERY_IDEMPOTENT").one()
        run.updated_at_utc = utc_now() - timedelta(hours=1)
        db.commit()
    with SessionLocal() as db:
        first = recover_stale_runs(db)
        db.commit()
    with SessionLocal() as db:
        second = recover_stale_runs(db)
        db.commit()
        assert first["expired"] == 1 and second["expired"] == 0
        assert db.query(ScanRunEvent).filter_by(run_id="P0C_RECOVERY_IDEMPOTENT", event_type="scan_expired").count() == 1


def test_max_attempts_terminally_fail_without_another_retry(tenant_factory, settings_state):
    settings_state(SCAN_STALLED_AFTER_SECONDS=10, SCAN_MAX_ATTEMPTS=2)
    tenant = tenant_factory()
    token, _ = _create_run(tenant["tenant_id"], "P0C_MAX_ATTEMPTS")
    _claim(tenant["tenant_id"], "P0C_MAX_ATTEMPTS", token)
    with SessionLocal() as db:
        run = db.query(ScanRunStatus).filter_by(run_id="P0C_MAX_ATTEMPTS").one()
        run.execution_attempt = 2
        run.heartbeat_at_utc = utc_now() - timedelta(hours=1)
        run.lease_expires_at_utc = utc_now() - timedelta(hours=1)
        db.commit()
    with SessionLocal() as db:
        assert recover_stale_runs(db)["failed"] == 1
        db.commit()
        run = db.query(ScanRunStatus).filter_by(run_id="P0C_MAX_ATTEMPTS").one()
        assert run.status == "failed" and run.error_code == "max_attempts_exceeded"


def test_non_retryable_failed_run_cannot_be_claimed(tenant_factory):
    tenant = tenant_factory()
    token, _ = _create_run(tenant["tenant_id"], "P0C_NON_RETRY")
    _claim(tenant["tenant_id"], "P0C_NON_RETRY", token)
    with SessionLocal() as db:
        update_scan_progress(db, run_id="P0C_NON_RETRY", status="failed", lease_token=token, worker_id="bc-worker", error_code="invalid_configuration")
        db.commit()
    with SessionLocal() as db, pytest.raises(InvalidScanTransitionError):
        claim_scan_run(db, run_id="P0C_NON_RETRY", tenant_id=tenant["tenant_id"], lease_token=token, worker_id="bc-worker")


def test_retry_keeps_same_scan_and_does_not_consume_another_credit(client, tenant_factory, settings_state):
    settings_state(SCAN_STALLED_AFTER_SECONDS=10)
    tenant = tenant_factory()
    _grant(tenant["tenant_id"])
    response = _start(client, tenant, "P0C_CREDIT_STABLE")
    assert response.status_code == 200
    token = response.json()["execution_token"]
    _claim(tenant["tenant_id"], "P0C_CREDIT_STABLE", token)
    with SessionLocal() as db:
        run = db.query(ScanRunStatus).filter_by(run_id="P0C_CREDIT_STABLE").one()
        run.heartbeat_at_utc = utc_now() - timedelta(hours=1)
        run.lease_expires_at_utc = utc_now() - timedelta(hours=1)
        db.commit()
    with SessionLocal() as db:
        recover_stale_runs(db)
        db.commit()
        assert db.query(ScanRunStatus).filter_by(run_id="P0C_CREDIT_STABLE").count() == 1
        assert db.query(TenantScanCredit).filter_by(tenant_id=tenant["tenant_id"], status="consumed").count() == 1
        assert db.query(CreditLedgerEntry).filter_by(tenant_id=tenant["tenant_id"], operation_type="SCAN_CONSUMED").count() == 1


def test_partial_result_cannot_complete(tenant_factory):
    tenant = tenant_factory()
    token, _ = _create_run(tenant["tenant_id"], "P0C_PARTIAL")
    _claim(tenant["tenant_id"], "P0C_PARTIAL", token)
    with SessionLocal() as db, pytest.raises(ScanResultIncompleteError):
        update_scan_progress(db, run_id="P0C_PARTIAL", status="completed", lease_token=token, worker_id="bc-worker")


def test_duplicate_findings_are_rejected_by_database(tenant_factory):
    tenant = tenant_factory()
    with SessionLocal() as db:
        db.add(Scan(scan_id="P0C_DUP_FINDING", tenant_id=tenant["tenant_id"], scan_type="deep", generated_at_utc=utc_now(), data_score=1, checks_count=1, issues_count=2, premium_available=True, summary_headline="x", summary_rating="y"))
        db.flush()
        db.add_all([
            ScanIssueRecord(scan_id="P0C_DUP_FINDING", code="DUP", title="A", severity="low", affected_count=1, premium_only=False),
            ScanIssueRecord(scan_id="P0C_DUP_FINDING", code="DUP", title="B", severity="low", affected_count=1, premium_only=False),
        ])
        with pytest.raises(IntegrityError):
            db.commit()


def test_report_or_postprocessing_failure_does_not_reopen_completed_core(tenant_factory):
    tenant = tenant_factory()
    token, _ = _create_run(tenant["tenant_id"], "P0C_POSTPROCESS")
    _claim(tenant["tenant_id"], "P0C_POSTPROCESS", token)
    with SessionLocal() as db:
        run = _persist_complete_result(db, tenant["tenant_id"], "P0C_POSTPROCESS", issues=0)
        update_scan_progress(db, run_id=run.run_id, status="completed", lease_token=token, worker_id="bc-worker", result_is_persisted=True)
        db.commit()
    with pytest.raises(RuntimeError, match="report failed"):
        raise RuntimeError("report failed")
    with SessionLocal() as db:
        assert db.query(ScanRunStatus).filter_by(run_id="P0C_POSTPROCESS").one().status == "completed"


def test_completed_without_mandatory_result_is_repaired_to_failed(tenant_factory):
    tenant = tenant_factory()
    _create_run(tenant["tenant_id"], "P0C_BAD_COMPLETED")
    with SessionLocal() as db:
        run = db.query(ScanRunStatus).filter_by(run_id="P0C_BAD_COMPLETED").one()
        run.status = "completed"
        run.completed_at_utc = utc_now()
        db.commit()
    with SessionLocal() as db:
        assert recover_stale_runs(db)["failed"] == 1
        db.commit()
        assert db.query(ScanRunStatus).filter_by(run_id="P0C_BAD_COMPLETED").one().error_code == "inconsistent_completed_result"


def test_status_polling_returns_terminal_failure(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory()
    token, _ = _create_run(tenant["tenant_id"], "P0C_BC_POLL")
    _claim(tenant["tenant_id"], "P0C_BC_POLL", token)
    with SessionLocal() as db:
        update_scan_progress(db, run_id="P0C_BC_POLL", status="failed", lease_token=token, worker_id="bc-worker", error_code="scan_exception")
        db.commit()
    response = client.get("/scan/status/P0C_BC_POLL", headers=auth_header_factory(tenant))
    assert response.status_code == 200
    assert response.json()["status"] == "failed" and response.json()["terminal"] is True


def test_multiple_recovery_instances_do_not_process_same_run_twice(tenant_factory, settings_state):
    settings_state(SCAN_QUEUED_TIMEOUT_SECONDS=10)
    tenant = tenant_factory()
    _create_run(tenant["tenant_id"], "P0C_MULTI_RECOVERY")
    with SessionLocal() as db:
        run = db.query(ScanRunStatus).filter_by(run_id="P0C_MULTI_RECOVERY").one()
        run.updated_at_utc = utc_now() - timedelta(hours=1)
        db.commit()

    def recover() -> int:
        with SessionLocal() as db:
            changed = recover_stale_runs(db)["expired"]
            db.commit()
            return changed

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: recover(), range(2)))
    assert sum(results) == 1
    with SessionLocal() as db:
        assert db.query(ScanRunEvent).filter_by(run_id="P0C_MULTI_RECOVERY", event_type="scan_expired").count() == 1
