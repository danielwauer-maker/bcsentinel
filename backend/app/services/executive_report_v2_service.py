from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exception_snapshot_models import ScanExceptionSnapshot
from app.models import Tenant
from app.schemas.report import ExecutiveReport, ReportAppliedException
from app.services.executive_report_service import build_executive_report as build_base_executive_report


def build_executive_report(db: Session, tenant: Tenant, scan_id: str) -> ExecutiveReport:
    """Canonical X5 report builder used by JSON, HTML, PDF and Monitoring.

    D10 remains the analytical base. X5 adds immutable scan-time exception
    transparency without reading mutable current BC exception state.
    """
    report = build_base_executive_report(db, tenant, scan_id)
    rows = db.scalars(
        select(ScanExceptionSnapshot)
        .where(
            ScanExceptionSnapshot.scan_id == scan_id,
            ScanExceptionSnapshot.tenant_id == tenant.tenant_id,
        )
        .order_by(ScanExceptionSnapshot.issue_code, ScanExceptionSnapshot.source_exception_entry_no)
    ).all()
    applied = [
        ReportAppliedException(
            source_exception_entry_no=row.source_exception_entry_no,
            company_id=row.company_id,
            table_id=row.table_id,
            record_no=row.record_no,
            record_caption=row.record_caption,
            issue_code=row.issue_code,
            reason=row.reason,
            exception_created_by=row.exception_created_by,
            exception_created_at_utc=row.exception_created_at_utc,
            captured_at_utc=row.captured_at_utc,
        )
        for row in rows
    ]
    return report.model_copy(
        update={
            "exceptions_applied": bool(applied),
            "exception_count": len(applied),
            "applied_exceptions": applied,
        }
    )
