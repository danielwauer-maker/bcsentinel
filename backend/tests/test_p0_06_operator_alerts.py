from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/evaluate_operator_alerts.py"
spec = importlib.util.spec_from_file_location("operator_alerts", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def healthy_snapshot():
    return {
        "api_ready": True,
        "database_ready": True,
        "worker_ready": True,
        "scheduler_ready": True,
        "failed_scans_15m": 0,
        "stuck_scans": 0,
        "recovery_failures_1h": 0,
        "oldest_queue_age_seconds": 0,
        "disk_used_percent": 50,
        "backup_age_hours": 2,
        "smtp_failures_1h": 0,
        "certificate_days_remaining": 90,
        "container_restarts_1h": 0,
    }


def test_healthy_snapshot_has_no_alerts():
    assert module.evaluate(healthy_snapshot()) == []


def test_critical_snapshot_maps_to_p0_runbooks():
    snapshot = healthy_snapshot()
    snapshot.update({
        "api_ready": False,
        "database_ready": False,
        "worker_ready": False,
        "scheduler_ready": False,
        "failed_scans_15m": 4,
        "stuck_scans": 1,
        "recovery_failures_1h": 1,
        "oldest_queue_age_seconds": 1200,
        "disk_used_percent": 95,
        "backup_age_hours": 72,
        "smtp_failures_1h": 7,
        "certificate_days_remaining": 5,
        "container_restarts_1h": 4,
    })
    alerts = module.evaluate(snapshot)
    codes = {alert.code for alert in alerts}
    assert {
        "API_NOT_READY", "DATABASE_NOT_READY", "WORKER_NOT_READY", "SCHEDULER_NOT_READY",
        "SCAN_FAILURE_SPIKE", "STUCK_SCAN", "RECOVERY_FAILURE", "QUEUE_BACKLOG",
        "DISK_CRITICAL", "BACKUP_TOO_OLD", "SMTP_FAILURE_SPIKE",
        "CERTIFICATE_CRITICAL", "CONTAINER_RESTART_LOOP",
    } <= codes
    assert all(alert.runbook.startswith("RB-") for alert in alerts)
    assert all(alert.severity == "P0" for alert in alerts)


def test_warning_thresholds_are_p1():
    snapshot = healthy_snapshot()
    snapshot.update({
        "failed_scans_15m": 1,
        "oldest_queue_age_seconds": 400,
        "disk_used_percent": 82,
        "backup_age_hours": 30,
        "smtp_failures_1h": 1,
        "certificate_days_remaining": 20,
        "container_restarts_1h": 1,
    })
    alerts = module.evaluate(snapshot)
    assert alerts
    assert all(alert.severity == "P1" for alert in alerts)
