from __future__ import annotations

from datetime import timedelta, timezone

from sqlalchemy import select

from app.lifecycle_models import TenantLifecycleProfile
from app.models import Scan, ScanRunStatus, TenantScanCredit
from app.services.lifecycle_email_service import (
    EVENT_SCAN_STARTED,
    EVENT_VALIDATION_EXPIRING,
    queue_lifecycle_email,
    queue_scan_completed,
    queue_scan_failed,
    utc_now,
)
from app.services.product_license_service import PRODUCT_VALIDATION_CHECK


def _normalize_utc(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def discover_scan_lifecycle_events(db, *, limit: int = 250) -> dict[str, int]:
    tenant_ids = set(db.scalars(select(TenantLifecycleProfile.tenant_id)).all())
    if not tenant_ids:
        return {"started": 0, "completed": 0, "failed": 0, "validation_expiring": 0}

    rows = db.scalars(
        select(ScanRunStatus)
        .where(
            ScanRunStatus.tenant_id.in_(tenant_ids),
            ScanRunStatus.status.in_(["preparing", "running", "completed", "failed"]),
        )
        .order_by(ScanRunStatus.updated_at_utc.desc(), ScanRunStatus.id.desc())
        .limit(max(1, min(limit, 1000)))
    ).all()

    started = completed = failed = validation_expiring = 0
    for run in rows:
        if run.status in {"preparing", "running"}:
            queue_lifecycle_email(
                db,
                tenant_id=run.tenant_id,
                event_type=EVENT_SCAN_STARTED,
                payload={"scan_id": run.run_id},
                dedupe_key=f"{EVENT_SCAN_STARTED}:{run.tenant_id}:{run.run_id}",
            )
            started += 1
        elif run.status == "completed":
            scan = db.scalar(
                select(Scan).where(
                    Scan.scan_id == run.run_id,
                    Scan.tenant_id == run.tenant_id,
                )
            )
            if scan is None or int(scan.checks_count or 0) <= 0:
                continue
            queue_scan_completed(
                db,
                tenant_id=run.tenant_id,
                scan_id=run.run_id,
                data_score=int(scan.data_score or 0),
            )
            completed += 1
        elif run.status == "failed":
            queue_scan_failed(
                db,
                tenant_id=run.tenant_id,
                scan_id=run.run_id,
                error_message=run.error_message,
            )
            failed += 1

    validation_credits = db.scalars(
        select(TenantScanCredit).where(
            TenantScanCredit.tenant_id.in_(tenant_ids),
            TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
            TenantScanCredit.status == "consumed",
            TenantScanCredit.consumed_at_utc.is_not(None),
            TenantScanCredit.consumed_scan_id.is_not(None),
        )
    ).all()
    for credit in validation_credits:
        consumed_at = _normalize_utc(credit.consumed_at_utc)
        if consumed_at is None:
            continue
        valid_until = consumed_at + timedelta(days=7)
        warning_at = valid_until - timedelta(hours=48)
        queue_lifecycle_email(
            db,
            tenant_id=credit.tenant_id,
            event_type=EVENT_VALIDATION_EXPIRING,
            payload={
                "scan_id": credit.consumed_scan_id or "",
                "valid_until_utc": valid_until.isoformat().replace("+00:00", "Z"),
            },
            dedupe_key=f"{EVENT_VALIDATION_EXPIRING}:credit:{credit.id}",
            scheduled_at_utc=max(warning_at, utc_now()),
        )
        validation_expiring += 1

    return {
        "started": started,
        "completed": completed,
        "failed": failed,
        "validation_expiring": validation_expiring,
    }
