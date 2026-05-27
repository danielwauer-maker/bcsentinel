from __future__ import annotations

from datetime import timedelta

from app.models import ScanRunEvent, ScanRunStatus
from app.services.scan_status_service import (
    create_or_get_scan_run,
    mark_stalled_scans,
    update_scan_progress,
    utc_now,
)


def test_scan_status_initializes_as_queued(db_session, tenant_factory):
    tenant = tenant_factory()

    run = create_or_get_scan_run(
        db_session,
        run_id="run_status_1",
        tenant_id=tenant["tenant_id"],
        scan_mode="deep",
        total_modules=3,
    )
    db_session.commit()

    assert run.status == "queued"
    assert run.progress_percent == 0
    assert run.total_modules == 3
    assert run.heartbeat_at_utc is not None


def test_progress_update_sets_heartbeat(db_session, tenant_factory):
    tenant = tenant_factory()
    create_or_get_scan_run(db_session, run_id="run_status_2", tenant_id=tenant["tenant_id"])
    run = update_scan_progress(
        db_session,
        run_id="run_status_2",
        tenant_id=tenant["tenant_id"],
        status="running",
        progress_percent=40,
        current_module="Inventory",
        current_step="Checking item references",
        event_message="Inventory scan started",
        total_modules=5,
    )
    db_session.commit()

    assert run.status == "running"
    assert run.progress_percent == 40
    assert run.heartbeat_at_utc is not None
    assert db_session.query(ScanRunEvent).filter_by(run_id="run_status_2").count() >= 2


def test_completed_sets_completed_at(db_session, tenant_factory):
    tenant = tenant_factory()
    create_or_get_scan_run(db_session, run_id="run_status_3", tenant_id=tenant["tenant_id"], total_modules=2)

    run = update_scan_progress(
        db_session,
        run_id="run_status_3",
        tenant_id=tenant["tenant_id"],
        status="completed",
        progress_percent=90,
        total_modules=2,
        completed_modules=1,
        event_message="Scan completed",
    )
    db_session.commit()

    assert run.status == "completed"
    assert run.progress_percent == 100
    assert run.completed_at_utc is not None
    assert run.completed_modules == 2
    assert run.current_module == "All modules completed"
    assert run.current_step == "Scan completed"
    assert run.error_message is None
    assert run.warning_message is None


def test_completed_clears_warning_and_overrides_running_state(db_session, tenant_factory):
    tenant = tenant_factory()
    run = create_or_get_scan_run(db_session, run_id="run_status_completed_override", tenant_id=tenant["tenant_id"], total_modules=3)
    run.status = "queued"
    run.warning_message = "Scan status could not be refreshed from the backend."
    run.error_message = "Stale local error"

    run = update_scan_progress(
        db_session,
        run_id="run_status_completed_override",
        tenant_id=tenant["tenant_id"],
        status="completed",
        progress_percent=15,
        current_module="Completed",
        current_step="Final local step",
        total_modules=3,
        completed_modules=1,
        event_message="Scan completed",
    )
    db_session.commit()

    assert run.status == "completed"
    assert run.progress_percent == 100
    assert run.completed_modules == 3
    assert run.current_module == "All modules completed"
    assert run.current_step == "Scan completed"
    assert run.warning_message is None
    assert run.error_message is None


def test_failed_sets_failed_at_and_error(db_session, tenant_factory):
    tenant = tenant_factory()
    create_or_get_scan_run(db_session, run_id="run_status_4", tenant_id=tenant["tenant_id"])

    run = update_scan_progress(
        db_session,
        run_id="run_status_4",
        tenant_id=tenant["tenant_id"],
        status="failed",
        error_code="backend_error",
        error_message="Backend timeout",
        event_message="Scan failed",
        event_level="error",
    )
    db_session.commit()

    assert run.status == "failed"
    assert run.failed_at_utc is not None
    assert run.error_code == "backend_error"
    assert run.error_message == "Backend timeout"


def test_watchdog_marks_old_running_scan_as_stalled(db_session, tenant_factory, settings_state):
    settings_state(SCAN_STALLED_AFTER_SECONDS=180)
    tenant = tenant_factory()
    run = create_or_get_scan_run(db_session, run_id="run_status_5", tenant_id=tenant["tenant_id"], status="running")
    run.status = "running"
    run.heartbeat_at_utc = utc_now() - timedelta(seconds=300)
    db_session.commit()

    marked = mark_stalled_scans(db_session)
    db_session.commit()

    assert marked == 1
    assert run.status == "stalled"
    assert "heartbeat" in run.warning_message.lower()


def test_status_endpoint_returns_expected_structure(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory()
    response = client.post(
        "/scan/status/update",
        headers=auth_header_factory(tenant),
        json={
            "tenant_id": tenant["tenant_id"],
            "run_id": "run_status_6",
            "scan_mode": "deep",
            "status": "running",
            "progress_percent": 62,
            "current_module": "Inventory",
            "current_step": "Checking item references",
            "event_message": "Inventory scan started",
            "total_modules": 4,
            "completed_modules": 2,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["run_id"] == "run_status_6"
    assert payload["status"] == "running"
    assert payload["progress_percent"] == 62
    assert payload["modules"][0]["name"] == "Inventory"
    assert payload["recent_events"]

    status_response = client.get(
        "/scan/status/run_status_6",
        headers=auth_header_factory(tenant),
    )

    assert status_response.status_code == 200
    assert status_response.json()["current_step"] == "Checking item references"


def test_completed_status_endpoint_returns_terminal_shape(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory()
    response = client.post(
        "/scan/status/update",
        headers=auth_header_factory(tenant),
        json={
            "tenant_id": tenant["tenant_id"],
            "run_id": "run_status_completed_endpoint",
            "scan_mode": "deep",
            "status": "completed",
            "progress_percent": 60,
            "current_module": "Completed",
            "current_step": "Finalizing",
            "warning_message": "Stale warning",
            "error_message": "Stale error",
            "total_modules": 2,
            "completed_modules": 1,
            "event_message": "Scan completed",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["progress_percent"] == 100
    assert payload["current_module"] == "All modules completed"
    assert payload["current_step"] == "Scan completed"
    assert payload["completed_at"] is not None
    assert payload["warning_message"] is None
    assert payload["error_message"] is None


def test_events_redact_email_addresses(db_session, tenant_factory):
    tenant = tenant_factory()
    create_or_get_scan_run(db_session, run_id="run_status_7", tenant_id=tenant["tenant_id"])

    update_scan_progress(
        db_session,
        run_id="run_status_7",
        tenant_id=tenant["tenant_id"],
        status="running",
        event_message="Processed contact user@example.com",
    )
    db_session.commit()

    event = db_session.query(ScanRunEvent).filter(ScanRunEvent.message.like("Processed%")).one()
    assert "user@example.com" not in event.message
    assert "[redacted]" in event.message
