from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models import Scan, ScanIssueRecord, ScanRunEvent, ScanRunModule, ScanRunStatus

logger = logging.getLogger(__name__)

ACTIVE_STATUSES = {"queued", "running"}
TERMINAL_STATUSES = {"completed", "completed_with_warnings", "failed", "cancelled", "expired"}
VALID_STATUSES = ACTIVE_STATUSES | TERMINAL_STATUSES
LEGACY_STATUS_ALIASES = {
    "preparing": "queued",
    "finalizing": "running",
    "stalled": "expired",
    "canceled": "cancelled",
}
ALLOWED_TRANSITIONS = {
    "queued": {"queued", "running", "failed", "cancelled", "expired"},
    "running": {"running", "completed", "completed_with_warnings", "failed", "cancelled", "expired"},
    "completed": {"completed"},
    "completed_with_warnings": {"completed_with_warnings"},
    "failed": {"failed"},
    "cancelled": {"cancelled"},
    "expired": {"expired"},
}
VALID_EVENT_LEVELS = {"info", "warning", "error"}
SENSITIVE_PATTERNS = [re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")]


class InvalidScanTransitionError(ValueError):
    pass


class ScanLeaseConflictError(ValueError):
    pass


class ScanResultIncompleteError(ValueError):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def as_aware_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def normalize_status(value: str | None, *, strict: bool = True) -> str:
    status = (value or "").strip().lower()
    status = LEGACY_STATUS_ALIASES.get(status, status)
    if status in VALID_STATUSES:
        return status
    if strict:
        raise InvalidScanTransitionError(f"Unsupported scan status: {value!r}.")
    return "queued"


def clamp_percent(value: int | None) -> int:
    try:
        percent = int(value or 0)
    except (TypeError, ValueError):
        percent = 0
    return max(0, min(100, percent))


def sanitize_event_message(message: str | None) -> str:
    sanitized = (message or "").strip()
    for pattern in SENSITIVE_PATTERNS:
        sanitized = pattern.sub("[redacted]", sanitized)
    return sanitized[:255] or "Scan progress updated"


def calculate_eta_seconds(started_at: datetime | None, completed_modules: int, total_modules: int) -> int | None:
    started_at = as_aware_utc(started_at)
    if not started_at or completed_modules <= 0 or total_modules <= completed_modules:
        return None
    elapsed = max(0, int((utc_now() - started_at).total_seconds()))
    if elapsed <= 0:
        return None
    return int((elapsed / completed_modules) * (total_modules - completed_modules))


def add_scan_event(
    db: Session,
    *,
    run_id: str,
    event_type: str = "scan_progress",
    level: str = "info",
    module: str | None = None,
    step: str | None = None,
    message: str | None = None,
    attempt: int | None = None,
    worker_id: str | None = None,
    correlation_id: str | None = None,
    metadata: dict[str, object] | None = None,
) -> ScanRunEvent:
    event = ScanRunEvent(
        run_id=run_id,
        timestamp_utc=utc_now(),
        event_type=(event_type or "scan_progress")[:40],
        level=level if level in VALID_EVENT_LEVELS else "info",
        module=(module or "")[:80] or None,
        step=(step or "")[:160] or None,
        message=sanitize_event_message(message),
        attempt=attempt,
        worker_id=(worker_id or "")[:80] or None,
        correlation_id=(correlation_id or "")[:50] or None,
        metadata_json=json.dumps(metadata, sort_keys=True, separators=(",", ":")) if metadata else None,
    )
    db.add(event)
    return event


def create_or_get_scan_run(
    db: Session,
    *,
    run_id: str,
    tenant_id: str,
    scan_mode: str = "deep",
    company_name: str | None = None,
    environment_name: str | None = None,
    total_modules: int = 0,
    status: str = "queued",
    correlation_id: str | None = None,
) -> ScanRunStatus:
    run = db.scalar(select(ScanRunStatus).where(ScanRunStatus.run_id == run_id))
    if run is not None:
        return run

    now = utc_now()
    normalized_status = normalize_status(status)
    run = ScanRunStatus(
        run_id=run_id,
        tenant_id=tenant_id,
        scan_mode=(scan_mode or "deep")[:20],
        company_name=(company_name or "")[:120] or None,
        environment_name=(environment_name or "")[:100] or None,
        status=normalized_status,
        created_at_utc=now,
        progress_percent=0,
        current_module="Queued" if normalized_status == "queued" else None,
        current_step="Waiting to start" if normalized_status == "queued" else None,
        started_at_utc=now if normalized_status == "running" else None,
        updated_at_utc=now,
        heartbeat_at_utc=None,
        total_modules=max(0, int(total_modules or 0)),
        completed_modules=0,
        failed_modules=0,
        lease_token=str(uuid4()),
        execution_attempt=0,
        retry_count=0,
        recovery_count=0,
        lifecycle_version=0,
        correlation_id=(correlation_id or str(uuid4()))[:50],
    )
    db.add(run)
    db.flush()
    add_scan_event(
        db,
        run_id=run_id,
        event_type="scan_queued",
        message="Scan queued",
        correlation_id=run.correlation_id,
    )
    add_scan_event(
        db,
        run_id=run.run_id,
        event_type="scan_started",
        message="Scan execution started",
        attempt=run.execution_attempt,
        worker_id=run.lease_owner,
        correlation_id=run.correlation_id,
    )
    return run


def _lease_is_valid(run: ScanRunStatus, now: datetime) -> bool:
    expires = as_aware_utc(run.lease_expires_at_utc)
    return bool(run.lease_owner and run.lease_token and expires and expires > now)


def _validate_worker_lease(
    run: ScanRunStatus,
    *,
    lease_token: str | None,
    worker_id: str | None,
    now: datetime,
) -> None:
    if not lease_token or lease_token != run.lease_token:
        raise ScanLeaseConflictError("The scan execution lease is no longer valid. Refresh the scan status before retrying.")
    if worker_id and run.lease_owner and worker_id != run.lease_owner:
        raise ScanLeaseConflictError("The scan is owned by another active worker.")
    if run.status == "running" and not _lease_is_valid(run, now):
        raise ScanLeaseConflictError("The scan execution lease has expired. Refresh the scan status to start controlled recovery.")


def claim_scan_run(
    db: Session,
    *,
    run_id: str,
    tenant_id: str,
    lease_token: str,
    worker_id: str,
    correlation_id: str | None = None,
) -> ScanRunStatus:
    now = utc_now()
    run = db.scalar(
        select(ScanRunStatus).where(ScanRunStatus.run_id == run_id, ScanRunStatus.tenant_id == tenant_id)
    )
    if run is None:
        raise ValueError("Scan run not found.")
    current = normalize_status(run.status)
    run.status = current

    if current == "running":
        _validate_worker_lease(run, lease_token=lease_token, worker_id=worker_id, now=now)
        run.heartbeat_at_utc = now
        run.lease_expires_at_utc = now + timedelta(seconds=max(10, int(settings.SCAN_LEASE_SECONDS)))
        run.updated_at_utc = now
        db.flush()
        return run
    if current != "queued":
        raise InvalidScanTransitionError(f"A {current} scan cannot be claimed.")
    if run.next_retry_at_utc and as_aware_utc(run.next_retry_at_utc) > now:
        raise ScanLeaseConflictError("The scan retry backoff has not elapsed yet.")
    if lease_token != run.lease_token:
        raise ScanLeaseConflictError("The scan execution token is no longer current. Retry the original scan start to refresh it.")

    version = run.lifecycle_version
    result = db.execute(
        update(ScanRunStatus)
        .where(
            ScanRunStatus.id == run.id,
            ScanRunStatus.status.in_(["queued", "preparing"]),
            ScanRunStatus.lifecycle_version == version,
            ScanRunStatus.lease_token == lease_token,
        )
        .values(
            status="running",
            lease_owner=worker_id[:80],
            lease_expires_at_utc=now + timedelta(seconds=max(10, int(settings.SCAN_LEASE_SECONDS))),
            heartbeat_at_utc=now,
            started_at_utc=run.started_at_utc or now,
            updated_at_utc=now,
            execution_attempt=ScanRunStatus.execution_attempt + 1,
            lifecycle_version=ScanRunStatus.lifecycle_version + 1,
            next_retry_at_utc=None,
            correlation_id=(correlation_id or run.correlation_id)[:50],
        )
    )
    if result.rowcount != 1:
        raise ScanLeaseConflictError("Another worker claimed this scan first.")
    db.flush()
    db.refresh(run)
    add_scan_event(
        db,
        run_id=run.run_id,
        event_type="scan_claimed",
        message="Scan execution claimed",
        attempt=run.execution_attempt,
        worker_id=run.lease_owner,
        correlation_id=run.correlation_id,
    )
    logger.info(
        "Scan claimed.",
        extra={"event": "scan_claimed", "scan_id": run.run_id, "tenant_id": run.tenant_id, "attempt": run.execution_attempt, "worker_id": run.lease_owner, "correlation_id": run.correlation_id},
    )
    return run


def upsert_module_progress(
    db: Session,
    *,
    run_id: str,
    name: str | None,
    status: str,
    progress_percent: int,
    current_step: str | None,
) -> None:
    module_name = (name or "").strip()
    if not module_name:
        return
    now = utc_now()
    module = db.scalar(select(ScanRunModule).where(ScanRunModule.run_id == run_id, ScanRunModule.name == module_name[:80]))
    if module is None:
        module = ScanRunModule(
            run_id=run_id,
            name=module_name[:80],
            status=status,
            progress_percent=progress_percent,
            current_step=(current_step or "")[:160] or None,
            started_at_utc=now if status in {"running", "completed"} else None,
            completed_at_utc=now if status == "completed" else None,
            updated_at_utc=now,
        )
        db.add(module)
        return
    module.status = status
    module.progress_percent = progress_percent
    module.current_step = (current_step or "")[:160] or None
    module.updated_at_utc = now
    if status == "running" and module.started_at_utc is None:
        module.started_at_utc = now
    if status == "completed" and module.completed_at_utc is None:
        module.completed_at_utc = now


def _ensure_transition(current: str, target: str) -> None:
    if target not in ALLOWED_TRANSITIONS[current]:
        raise InvalidScanTransitionError(f"Invalid scan status transition: {current} -> {target}.")


def _claim_recovery_mutation(db: Session, run: ScanRunStatus) -> bool:
    """Claim one recovery mutation even on databases without SKIP LOCKED support."""
    expected_version = int(run.lifecycle_version or 0)
    result = db.execute(
        update(ScanRunStatus)
        .where(
            ScanRunStatus.id == run.id,
            ScanRunStatus.status == run.status,
            ScanRunStatus.lifecycle_version == expected_version,
        )
        .values(lifecycle_version=expected_version + 1)
        .execution_options(synchronize_session=False)
    )
    if result.rowcount != 1:
        db.expire(run)
        return False
    run.lifecycle_version = expected_version + 1
    return True


def update_scan_progress(
    db: Session,
    *,
    run_id: str,
    tenant_id: str | None = None,
    status: str = "running",
    progress_percent: int | None = None,
    current_module: str | None = None,
    current_step: str | None = None,
    event_message: str | None = None,
    event_level: str = "info",
    scan_mode: str = "deep",
    total_modules: int | None = None,
    completed_modules: int | None = None,
    failed_modules: int | None = None,
    error_code: str | None = None,
    error_message: str | None = None,
    warning_message: str | None = None,
    lease_token: str | None = None,
    worker_id: str | None = None,
    correlation_id: str | None = None,
    allow_unleased: bool = False,
    result_is_persisted: bool = False,
) -> ScanRunStatus:
    now = utc_now()
    run = db.scalar(select(ScanRunStatus).where(ScanRunStatus.run_id == run_id))
    if run is None:
        if not tenant_id:
            raise ValueError("tenant_id is required when creating scan progress.")
        run = create_or_get_scan_run(db, run_id=run_id, tenant_id=tenant_id, scan_mode=scan_mode, total_modules=total_modules or 0, correlation_id=correlation_id)

    current = normalize_status(run.status)
    target = normalize_status(status)
    run.status = current
    if current == "queued" and target == "running" and not allow_unleased:
        run = claim_scan_run(
            db,
            run_id=run.run_id,
            tenant_id=run.tenant_id,
            lease_token=lease_token or "",
            worker_id=worker_id or "unknown-worker",
            correlation_id=correlation_id,
        )
        current = "running"
    elif not allow_unleased and (current == "running" or target in TERMINAL_STATUSES):
        _validate_worker_lease(run, lease_token=lease_token, worker_id=worker_id, now=now)

    _ensure_transition(current, target)
    if target in {"completed", "completed_with_warnings"} and not (result_is_persisted or run.result_persisted_at_utc):
        raise ScanResultIncompleteError("A scan can only complete after its mandatory result was stored consistently.")

    run.status = target
    run.progress_percent = clamp_percent(progress_percent if progress_percent is not None else run.progress_percent)
    run.current_module = (current_module or run.current_module or "")[:80] or None
    run.current_step = (current_step or run.current_step or "")[:160] or None
    run.updated_at_utc = now
    if tenant_id:
        run.tenant_id = tenant_id
    if scan_mode:
        run.scan_mode = scan_mode[:20]
    if correlation_id:
        run.correlation_id = correlation_id[:50]
    if total_modules is not None:
        run.total_modules = max(0, int(total_modules or 0))
    if completed_modules is not None:
        run.completed_modules = max(0, int(completed_modules or 0))
    if failed_modules is not None:
        run.failed_modules = max(0, int(failed_modules or 0))

    if target == "running":
        run.heartbeat_at_utc = now
        run.lease_expires_at_utc = now + timedelta(seconds=max(10, int(settings.SCAN_LEASE_SECONDS)))
        if run.started_at_utc is None:
            run.started_at_utc = now
        run.estimated_remaining_seconds = calculate_eta_seconds(run.started_at_utc, run.completed_modules, run.total_modules)
    elif target in {"completed", "completed_with_warnings"}:
        run.result_persisted_at_utc = run.result_persisted_at_utc or now
        run.completed_at_utc = now
        run.progress_percent = 100
        run.current_module = "All modules completed"
        run.current_step = "Scan completed" if target == "completed" else "Scan completed with warnings"
        run.error_code = None
        run.error_message = None
        if target == "completed":
            run.warning_message = None
        elif warning_message:
            run.warning_message = sanitize_event_message(warning_message)
        run.estimated_remaining_seconds = None
        if run.total_modules > 0:
            run.completed_modules = run.total_modules
        run.lease_owner = None
        run.lease_expires_at_utc = None
    elif target in {"failed", "cancelled", "expired"}:
        run.failed_at_utc = now
        run.error_code = (error_code or target)[:80]
        run.error_message = sanitize_event_message(error_message or f"Scan {target}.")
        run.estimated_remaining_seconds = None
        run.lease_owner = None
        run.lease_expires_at_utc = None
    elif warning_message:
        run.warning_message = sanitize_event_message(warning_message)

    run.lifecycle_version += 1
    module_status = "completed" if target in {"completed", "completed_with_warnings"} else target
    upsert_module_progress(db, run_id=run_id, name=run.current_module, status=module_status, progress_percent=run.progress_percent, current_step=run.current_step)
    if event_message:
        event_type = {
            "running": "scan_heartbeat",
            "completed": "scan_completed",
            "completed_with_warnings": "scan_completed",
            "failed": "scan_failed",
            "cancelled": "scan_cancelled",
            "expired": "scan_expired",
        }.get(target, "scan_progress")
        add_scan_event(
            db,
            run_id=run_id,
            event_type=event_type,
            level=event_level,
            module=run.current_module,
            step=run.current_step,
            message=event_message,
            attempt=run.execution_attempt,
            worker_id=worker_id or run.lease_owner,
            correlation_id=run.correlation_id,
        )
    db.flush()
    return run


def result_is_complete(db: Session, run: ScanRunStatus) -> bool:
    scan = db.scalar(select(Scan).where(Scan.scan_id == run.run_id, Scan.tenant_id == run.tenant_id))
    if scan is None or not (scan.summary_headline or "").strip() or not (scan.summary_rating or "").strip():
        return False
    if (scan.summary_rating or "").strip().lower() == "pending":
        return False
    issue_type_count = db.query(ScanIssueRecord).filter(ScanIssueRecord.scan_id == run.run_id).count()
    aggregate_issue_count = max(0, int(scan.issues_count or 0))
    findings_consistent = (aggregate_issue_count == 0 and issue_type_count == 0) or (
        aggregate_issue_count > 0 and issue_type_count > 0
    )
    return scan.checks_count >= 0 and scan.issues_count >= 0 and findings_consistent


def mark_scan_result_persisted(db: Session, run: ScanRunStatus) -> None:
    if not result_is_complete(db, run):
        raise ScanResultIncompleteError("The stored scan result is incomplete or inconsistent.")
    run.result_persisted_at_utc = utc_now()
    db.flush()


def recover_stale_runs(db: Session, *, batch_size: int | None = None) -> dict[str, int]:
    now = utc_now()
    heartbeat_cutoff = now - timedelta(seconds=max(10, int(settings.SCAN_STALLED_AFTER_SECONDS)))
    queued_cutoff = now - timedelta(seconds=max(10, int(settings.SCAN_QUEUED_TIMEOUT_SECONDS)))
    limit = max(1, min(int(batch_size or settings.SCAN_RECOVERY_BATCH_SIZE), 1000))
    candidates = db.scalars(
        select(ScanRunStatus)
        .where(
            or_(
                ScanRunStatus.status.in_(["queued", "preparing"]),
                ScanRunStatus.status.in_(["running", "finalizing", "stalled"]),
                (ScanRunStatus.status.in_(["completed", "completed_with_warnings"])) & (ScanRunStatus.result_persisted_at_utc.is_(None)),
            )
        )
        .order_by(ScanRunStatus.updated_at_utc.asc(), ScanRunStatus.id.asc())
        .limit(limit)
        .with_for_update(skip_locked=True)
    ).all()
    outcome = {"examined": 0, "requeued": 0, "failed": 0, "expired": 0, "repaired": 0}
    max_attempts = max(1, int(settings.SCAN_MAX_ATTEMPTS))
    for run in candidates:
        outcome["examined"] += 1
        current = normalize_status(run.status)
        run.status = current
        updated = as_aware_utc(run.updated_at_utc) or as_aware_utc(run.created_at_utc) or now
        heartbeat = as_aware_utc(run.heartbeat_at_utc)
        lease_expired = not run.lease_expires_at_utc or as_aware_utc(run.lease_expires_at_utc) <= now

        if current in {"completed", "completed_with_warnings"}:
            if result_is_complete(db, run):
                if not _claim_recovery_mutation(db, run):
                    continue
                run.result_persisted_at_utc = run.completed_at_utc or now
                outcome["repaired"] += 1
                continue
            if not _claim_recovery_mutation(db, run):
                continue
            run.status = "failed"
            run.failed_at_utc = now
            run.error_code = "inconsistent_completed_result"
            run.error_message = "The scan was marked completed without a consistent mandatory result."
            run.lease_owner = None
            run.lease_expires_at_utc = None
            add_scan_event(db, run_id=run.run_id, event_type="scan_failed", level="error", message=run.error_message, attempt=run.execution_attempt, correlation_id=run.correlation_id)
            outcome["failed"] += 1
            continue

        if run.result_persisted_at_utc and current in ACTIVE_STATUSES:
            if not _claim_recovery_mutation(db, run):
                continue
            run.status = "completed_with_warnings" if run.warning_message else "completed"
            run.completed_at_utc = now
            run.progress_percent = 100
            run.lease_owner = None
            run.lease_expires_at_utc = None
            add_scan_event(db, run_id=run.run_id, event_type="scan_recovered", message="Persisted scan result finalized during recovery", attempt=run.execution_attempt, correlation_id=run.correlation_id)
            outcome["repaired"] += 1
            continue

        if current == "queued":
            if run.next_retry_at_utc and as_aware_utc(run.next_retry_at_utc) > now:
                continue
            if updated > queued_cutoff:
                continue
            if not _claim_recovery_mutation(db, run):
                continue
            run.status = "expired"
            run.failed_at_utc = now
            run.error_code = "queue_timeout"
            run.error_message = "No worker claimed the scan within the configured queue deadline."
            run.lease_owner = None
            run.lease_expires_at_utc = None
            add_scan_event(db, run_id=run.run_id, event_type="scan_expired", level="warning", message=run.error_message, attempt=run.execution_attempt, correlation_id=run.correlation_id, metadata={"recovery_reason": "stale_queued"})
            outcome["expired"] += 1
            continue

        stale_running = lease_expired or not heartbeat or heartbeat <= heartbeat_cutoff
        max_runtime = settings.SCAN_MAX_RUNTIME_SECONDS
        if max_runtime and run.started_at_utc:
            stale_running = stale_running or as_aware_utc(run.started_at_utc) <= now - timedelta(seconds=max(1, int(max_runtime)))
        if not stale_running:
            continue

        if not _claim_recovery_mutation(db, run):
            continue

        previous_worker = run.lease_owner
        run.recovery_count += 1
        run.lease_owner = None
        run.lease_expires_at_utc = None
        run.heartbeat_at_utc = None
        add_scan_event(
            db,
            run_id=run.run_id,
            event_type="scan_lease_lost",
            level="warning",
            message="The scan worker lease or heartbeat expired",
            attempt=run.execution_attempt,
            worker_id=previous_worker,
            correlation_id=run.correlation_id,
            metadata={"recovery_reason": "lease_or_heartbeat_expired"},
        )
        if run.execution_attempt < max_attempts:
            run.retry_count += 1
            backoff = max(1, int(settings.SCAN_RETRY_BACKOFF_SECONDS)) * (2 ** max(0, run.retry_count - 1))
            run.status = "queued"
            run.next_retry_at_utc = now + timedelta(seconds=backoff)
            run.lease_token = str(uuid4())
            run.error_code = "worker_lease_lost"
            run.error_message = "The previous worker stopped heartbeating. The same scan can be retried after backoff."
            run.current_step = "Recovery retry scheduled"
            add_scan_event(db, run_id=run.run_id, event_type="scan_retry_scheduled", level="warning", message=run.error_message, attempt=run.execution_attempt, correlation_id=run.correlation_id, metadata={"recovery_reason": "lease_or_heartbeat_expired", "backoff_seconds": backoff})
            outcome["requeued"] += 1
        else:
            run.status = "failed"
            run.failed_at_utc = now
            run.next_retry_at_utc = None
            run.error_code = "max_attempts_exceeded"
            run.error_message = "The scan stopped after the maximum number of recovery attempts."
            add_scan_event(db, run_id=run.run_id, event_type="scan_failed", level="error", message=run.error_message, attempt=run.execution_attempt, correlation_id=run.correlation_id, metadata={"recovery_reason": "max_attempts_exceeded"})
            outcome["failed"] += 1
    if any(outcome[key] for key in ("requeued", "failed", "expired", "repaired")):
        db.flush()
        logger.warning("Scan recovery processed stale runs.", extra={"event": "scan_recovered", **outcome})
    return outcome


def mark_stalled_scans(db: Session) -> int:
    outcome = recover_stale_runs(db)
    return outcome["requeued"] + outcome["failed"] + outcome["expired"] + outcome["repaired"]


def serialize_scan_status(db: Session, run: ScanRunStatus, *, include_execution_token: bool = False) -> dict[str, object]:
    modules = db.scalars(select(ScanRunModule).where(ScanRunModule.run_id == run.run_id).order_by(ScanRunModule.id)).all()
    events = db.scalars(select(ScanRunEvent).where(ScanRunEvent.run_id == run.run_id).order_by(ScanRunEvent.timestamp_utc.desc(), ScanRunEvent.id.desc()).limit(10)).all()
    payload: dict[str, object] = {
        "run_id": run.run_id,
        "tenant_id": run.tenant_id,
        "company": run.company_name,
        "environment": run.environment_name,
        "scan_mode": run.scan_mode,
        "status": normalize_status(run.status),
        "progress_percent": run.progress_percent,
        "current_module": run.current_module,
        "current_step": run.current_step,
        "created_at": run.created_at_utc,
        "started_at": run.started_at_utc,
        "updated_at": run.updated_at_utc,
        "heartbeat_at": run.heartbeat_at_utc,
        "completed_at": run.completed_at_utc,
        "failed_at": run.failed_at_utc,
        "failure_code": run.error_code,
        "error_code": run.error_code,
        "error_message": run.error_message,
        "warning_message": run.warning_message,
        "estimated_remaining_seconds": run.estimated_remaining_seconds,
        "total_modules": run.total_modules,
        "completed_modules": run.completed_modules,
        "failed_modules": run.failed_modules,
        "execution_attempt": run.execution_attempt,
        "retry_count": run.retry_count,
        "next_retry_at": run.next_retry_at_utc,
        "lease_owner": run.lease_owner,
        "lease_expires_at": run.lease_expires_at_utc,
        "correlation_id": run.correlation_id,
        "recovery_count": run.recovery_count,
        "result_persisted_at": run.result_persisted_at_utc,
        "recovery_required": normalize_status(run.status) == "queued" and run.retry_count > 0,
        "terminal": normalize_status(run.status) in TERMINAL_STATUSES,
        "modules": [{"name": module.name, "status": module.status, "progress_percent": module.progress_percent, "current_step": module.current_step, "started_at": module.started_at_utc, "completed_at": module.completed_at_utc} for module in modules],
        "recent_events": [{"timestamp": event.timestamp_utc, "event_type": event.event_type, "level": event.level, "module": event.module, "step": event.step, "message": event.message, "attempt": event.attempt, "correlation_id": event.correlation_id} for event in reversed(events)],
    }
    if include_execution_token:
        payload["execution_token"] = run.lease_token
    return payload
