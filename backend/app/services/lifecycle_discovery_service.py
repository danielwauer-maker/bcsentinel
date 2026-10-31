from __future__ import annotations

from sqlalchemy import select

from app.lifecycle_models import TenantLifecycleProfile
from app.models import Scan, ScanRunStatus
from app.services.lifecycle_email_service import queue_scan_completed, queue_scan_failed


def discover_scan_lifecycle_events(db, *, limit: int = 250) -> dict[str, int]:
    tenant_ids = set(db.scalars(select(TenantLifecycleProfile.tenant_id)).all())
    if not tenant_ids:
        return {"completed": 0, "failed": 0}

    rows = db.scalars(
        select(ScanRunStatus)
        .where(
            ScanRunStatus.tenant_id.in_(tenant_ids),
            ScanRunStatus.status.in_(["completed", "failed"]),
        )
        .order_by(ScanRunStatus.updated_at_utc.desc(), ScanRunStatus.id.desc())
        .limit(max(1, min(limit, 1000)))
    ).all()

    completed = failed = 0
    for run in rows:
        if run.status == "completed":
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
    return {"completed": completed, "failed": failed}
