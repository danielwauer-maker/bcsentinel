from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db import SessionLocal
from app.exception_snapshot_models import ScanExceptionSnapshot, ScanExceptionSnapshotCapture
from app.models import Scan
from app.security.tenant import load_authenticated_tenant, require_tenant_headers

router = APIRouter(tags=["exception-transparency"])


class ExceptionSnapshotItem(BaseModel):
    source_exception_entry_no: int = Field(ge=1)
    table_id: int = Field(ge=1)
    record_system_id: str | None = Field(default=None, max_length=40)
    record_no: str | None = Field(default=None, max_length=50)
    record_caption: str | None = Field(default=None, max_length=150)
    issue_code: str = Field(min_length=1, max_length=80)
    reason: str = Field(min_length=1, max_length=2000)
    exception_created_by: str | None = Field(default=None, max_length=100)
    exception_created_at_utc: datetime | None = None


class ExceptionSnapshotRequest(BaseModel):
    company_id: str | None = Field(default=None, max_length=100)
    exceptions: list[ExceptionSnapshotItem] = Field(default_factory=list, max_length=5000)


def _machine_tenant(
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
    x_api_token: str | None = Header(default=None, alias="X-Api-Token"),
):
    # Exception snapshots are operational scan evidence and therefore writeable
    # only by the Business Central/machine credential path, never a dashboard
    # bearer session.
    if not x_tenant_id or not x_api_token:
        raise HTTPException(status_code=401, detail="Machine tenant credentials are required.")
    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, x_tenant_id.strip(), x_api_token)
        return tenant.tenant_id


@router.post("/scans/{scan_id}/exception-snapshot")
def replace_scan_exception_snapshot(
    scan_id: str,
    payload: ExceptionSnapshotRequest,
    tenant_id: str = Depends(_machine_tenant),
) -> dict:
    with SessionLocal() as db:
        scan = db.scalar(select(Scan).where(Scan.scan_id == scan_id, Scan.tenant_id == tenant_id))
        if scan is None:
            raise HTTPException(status_code=404, detail="Scan not found.")

        capture = db.scalar(
            select(ScanExceptionSnapshotCapture).where(
                ScanExceptionSnapshotCapture.scan_id == scan_id,
                ScanExceptionSnapshotCapture.tenant_id == tenant_id,
            )
        )
        legacy_rows = db.scalars(
            select(ScanExceptionSnapshot).where(
                ScanExceptionSnapshot.scan_id == scan_id,
                ScanExceptionSnapshot.tenant_id == tenant_id,
            )
        ).all()
        if capture is not None or legacy_rows:
            raise HTTPException(
                status_code=409,
                detail="Exception snapshot is immutable once captured for a scan.",
            )

        seen: set[int] = set()
        for item in payload.exceptions:
            if item.source_exception_entry_no in seen:
                raise HTTPException(status_code=422, detail="Duplicate source_exception_entry_no in snapshot payload.")
            seen.add(item.source_exception_entry_no)

        captured_at = datetime.now(timezone.utc)
        company_id = (payload.company_id or "").strip() or None
        db.add(
            ScanExceptionSnapshotCapture(
                scan_id=scan_id,
                tenant_id=tenant_id,
                company_id=company_id,
                exception_count=len(payload.exceptions),
                captured_at_utc=captured_at,
            )
        )
        for item in payload.exceptions:
            db.add(
                ScanExceptionSnapshot(
                    scan_id=scan_id,
                    tenant_id=tenant_id,
                    company_id=company_id,
                    source_exception_entry_no=item.source_exception_entry_no,
                    table_id=item.table_id,
                    record_system_id=(item.record_system_id or "").strip() or None,
                    record_no=(item.record_no or "").strip() or None,
                    record_caption=(item.record_caption or "").strip() or None,
                    issue_code=item.issue_code.strip(),
                    reason=item.reason.strip(),
                    exception_created_by=(item.exception_created_by or "").strip() or None,
                    exception_created_at_utc=item.exception_created_at_utc,
                    captured_at_utc=captured_at,
                )
            )
        db.commit()
        return {
            "scan_id": scan_id,
            "tenant_id": tenant_id,
            "captured_exception_count": len(payload.exceptions),
            "captured_at_utc": captured_at,
            "immutable": True,
        }


@router.get("/scans/{scan_id}/exceptions")
def read_scan_exceptions(
    scan_id: str,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
) -> dict:
    tenant_id, credential = tenant_auth
    with SessionLocal() as db:
        load_authenticated_tenant(db, tenant_id, credential)
        scan = db.scalar(select(Scan).where(Scan.scan_id == scan_id, Scan.tenant_id == tenant_id))
        if scan is None:
            raise HTTPException(status_code=404, detail="Scan not found.")
        capture = db.scalar(
            select(ScanExceptionSnapshotCapture).where(
                ScanExceptionSnapshotCapture.scan_id == scan_id,
                ScanExceptionSnapshotCapture.tenant_id == tenant_id,
            )
        )
        rows = db.scalars(
            select(ScanExceptionSnapshot)
            .where(ScanExceptionSnapshot.scan_id == scan_id, ScanExceptionSnapshot.tenant_id == tenant_id)
            .order_by(ScanExceptionSnapshot.issue_code, ScanExceptionSnapshot.source_exception_entry_no)
        ).all()
        snapshot_captured = capture is not None or bool(rows)
        return {
            "scan_id": scan_id,
            "tenant_id": tenant_id,
            "snapshot_captured": snapshot_captured,
            "captured_at_utc": capture.captured_at_utc if capture is not None else (rows[0].captured_at_utc if rows else None),
            "exception_count": capture.exception_count if capture is not None else len(rows),
            "exceptions_applied": bool(rows),
            "exceptions": [
                {
                    "source_exception_entry_no": row.source_exception_entry_no,
                    "company_id": row.company_id,
                    "table_id": row.table_id,
                    "record_no": row.record_no,
                    "record_caption": row.record_caption,
                    "issue_code": row.issue_code,
                    "reason": row.reason,
                    "exception_created_by": row.exception_created_by,
                    "exception_created_at_utc": row.exception_created_at_utc,
                    "captured_at_utc": row.captured_at_utc,
                }
                for row in rows
            ],
        }
