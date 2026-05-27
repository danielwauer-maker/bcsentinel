from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models import ScanRunEvent, ScanRunModule, ScanRunStatus

ACTIVE_STATUSES = {"queued", "preparing", "running", "finalizing"}
TERMINAL_STATUSES = {"completed", "failed", "stalled", "cancelled"}
VALID_STATUSES = ACTIVE_STATUSES | TERMINAL_STATUSES
VALID_EVENT_LEVELS = {"info", "warning", "error"}
SENSITIVE_PATTERNS = [
    re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"),
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def as_aware_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def normalize_status(value: str | None) -> str:
    status = (value or "running").strip().lower()
    if status == "canceled":
        status = "cancelled"
    return status if status in VALID_STATUSES else "running"


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
) -> ScanRunStatus:
    now = utc_now()
    run = db.scalar(select(ScanRunStatus).where(ScanRunStatus.run_id == run_id))
    if run is not None:
        return run

    normalized_status = normalize_status(status)
    run = ScanRunStatus(
        run_id=run_id,
        tenant_id=tenant_id,
        scan_mode=(scan_mode or "deep")[:20],
        company_name=(company_name or "")[:120] or None,
        environment_name=(environment_name or "")[:100] or None,
        status=normalized_status,
        progress_percent=0,
        current_module="Queued" if normalized_status == "queued" else None,
        current_step="Waiting to start" if normalized_status == "queued" else None,
        started_at_utc=now if normalized_status not in {"queued", "preparing"} else None,
        updated_at_utc=now,
        heartbeat_at_utc=now,
        total_modules=max(0, int(total_modules or 0)),
        completed_modules=0,
        failed_modules=0,
    )
    db.add(run)
    db.flush()
    add_scan_event(db, run_id=run_id, level="info", module=run.current_module, step=run.current_step, message="Scan queued")
    return run


def add_scan_event(
    db: Session,
    *,
    run_id: str,
    level: str = "info",
    module: str | None = None,
    step: str | None = None,
    message: str | None = None,
) -> ScanRunEvent:
    event = ScanRunEvent(
        run_id=run_id,
        timestamp_utc=utc_now(),
        level=level if level in VALID_EVENT_LEVELS else "info",
        module=(module or "")[:80] or None,
        step=(step or "")[:160] or None,
        message=sanitize_event_message(message),
    )
    db.add(event)
    return event


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
    module = db.scalar(
        select(ScanRunModule).where(
            ScanRunModule.run_id == run_id,
            ScanRunModule.name == module_name[:80],
        )
    )
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
) -> ScanRunStatus:
    now = utc_now()
    run = db.scalar(select(ScanRunStatus).where(ScanRunStatus.run_id == run_id))
    if run is None:
        if not tenant_id:
            raise ValueError("tenant_id is required when creating scan progress.")
        run = create_or_get_scan_run(db, run_id=run_id, tenant_id=tenant_id, scan_mode=scan_mode, total_modules=total_modules or 0)

    normalized_status = normalize_status(status)
    run.status = normalized_status
    run.progress_percent = clamp_percent(progress_percent if progress_percent is not None else run.progress_percent)
    run.current_module = (current_module or run.current_module or "")[:80] or None
    run.current_step = (current_step or run.current_step or "")[:160] or None
    run.updated_at_utc = now
    run.heartbeat_at_utc = now
    if tenant_id:
        run.tenant_id = tenant_id
    if scan_mode:
        run.scan_mode = scan_mode[:20]
    if total_modules is not None:
        run.total_modules = max(0, int(total_modules or 0))
    if completed_modules is not None:
        run.completed_modules = max(0, int(completed_modules or 0))
    if failed_modules is not None:
        run.failed_modules = max(0, int(failed_modules or 0))
    if normalized_status in {"running", "finalizing"} and run.started_at_utc is None:
        run.started_at_utc = now
    if normalized_status == "completed":
        run.completed_at_utc = now
        run.progress_percent = 100
        run.current_module = "All modules completed"
        run.current_step = "Scan completed"
        run.error_code = None
        run.error_message = None
        run.warning_message = None
        run.estimated_remaining_seconds = None
        if run.total_modules > 0:
            run.completed_modules = run.total_modules
    elif normalized_status == "failed":
        run.failed_at_utc = now
        run.error_code = (error_code or "scan_failed")[:80]
        run.error_message = sanitize_event_message(error_message or "Scan failed.")
    elif warning_message:
        run.warning_message = sanitize_event_message(warning_message)
    if normalized_status != "completed":
        run.estimated_remaining_seconds = calculate_eta_seconds(
            run.started_at_utc,
            run.completed_modules,
            run.total_modules,
        )

    module_status = "completed" if normalized_status == "completed" else normalized_status
    upsert_module_progress(
        db,
        run_id=run_id,
        name=run.current_module,
        status=module_status,
        progress_percent=run.progress_percent,
        current_step=run.current_step,
    )

    if event_message:
        add_scan_event(
            db,
            run_id=run_id,
            level=event_level,
            module=run.current_module,
            step=run.current_step,
            message=event_message,
        )

    db.flush()
    return run


def mark_stalled_scans(db: Session) -> int:
    now = utc_now()
    cutoff = now - timedelta(seconds=max(1, int(settings.SCAN_STALLED_AFTER_SECONDS or 180)))
    query = select(ScanRunStatus).where(
        ScanRunStatus.status.in_(ACTIVE_STATUSES),
        ScanRunStatus.heartbeat_at_utc < cutoff,
    )
    marked = 0
    for run in db.scalars(query).all():
        run.status = "stalled"
        run.updated_at_utc = now
        run.warning_message = "No heartbeat was received within the configured threshold."
        add_scan_event(
            db,
            run_id=run.run_id,
            level="warning",
            module=run.current_module,
            step=run.current_step,
            message="Scan marked as stalled because no heartbeat was received.",
        )
        marked += 1
    if marked:
        db.flush()
    return marked


def serialize_scan_status(db: Session, run: ScanRunStatus) -> dict[str, object]:
    modules = db.scalars(
        select(ScanRunModule)
        .where(ScanRunModule.run_id == run.run_id)
        .order_by(ScanRunModule.id)
    ).all()
    events = db.scalars(
        select(ScanRunEvent)
        .where(ScanRunEvent.run_id == run.run_id)
        .order_by(ScanRunEvent.timestamp_utc.desc(), ScanRunEvent.id.desc())
        .limit(10)
    ).all()
    return {
        "run_id": run.run_id,
        "tenant_id": run.tenant_id,
        "company": run.company_name,
        "environment": run.environment_name,
        "scan_mode": run.scan_mode,
        "status": run.status,
        "progress_percent": run.progress_percent,
        "current_module": run.current_module,
        "current_step": run.current_step,
        "started_at": run.started_at_utc,
        "updated_at": run.updated_at_utc,
        "heartbeat_at": run.heartbeat_at_utc,
        "completed_at": run.completed_at_utc,
        "failed_at": run.failed_at_utc,
        "error_code": run.error_code,
        "error_message": run.error_message,
        "warning_message": run.warning_message,
        "estimated_remaining_seconds": run.estimated_remaining_seconds,
        "total_modules": run.total_modules,
        "completed_modules": run.completed_modules,
        "failed_modules": run.failed_modules,
        "modules": [
            {
                "name": module.name,
                "status": module.status,
                "progress_percent": module.progress_percent,
                "current_step": module.current_step,
                "started_at": module.started_at_utc,
                "completed_at": module.completed_at_utc,
            }
            for module in modules
        ],
        "recent_events": [
            {
                "timestamp": event.timestamp_utc,
                "level": event.level,
                "module": event.module,
                "step": event.step,
                "message": event.message,
            }
            for event in reversed(events)
        ],
    }
