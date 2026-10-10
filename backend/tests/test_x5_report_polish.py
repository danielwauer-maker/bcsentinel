from __future__ import annotations

from datetime import datetime, timezone

from app.db import SessionLocal
from app.exception_snapshot_models import ScanExceptionSnapshot
from app.models import Tenant
from app.services.executive_report_pdf_service import render_executive_report_pdf
from app.services.executive_report_v2_service import build_executive_report
from app.services.product_license_service import PRODUCT_ASSESSMENT, grant_product_entitlement


def test_report_uses_immutable_exception_snapshot(tenant_factory, scan_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_x5_exception")
    with SessionLocal() as db:
        grant_product_entitlement(db, tenant_id=tenant["tenant_id"], product_code=PRODUCT_ASSESSMENT, source="x5-test")
        db.add(
            ScanExceptionSnapshot(
                scan_id="scan_x5_exception",
                tenant_id=tenant["tenant_id"],
                company_id="CRONUS DE",
                source_exception_entry_no=44,
                table_id=18,
                record_system_id=None,
                record_no="10000",
                record_caption="Demo Customer",
                issue_code="DUPLICATE_CUSTOMERS",
                reason="Approved separate invoice recipient",
                exception_created_by="BC ADMIN",
                exception_created_at_utc=datetime.now(timezone.utc),
                captured_at_utc=datetime.now(timezone.utc),
            )
        )
        db.commit()
        tenant_row = db.query(Tenant).filter(Tenant.tenant_id == tenant["tenant_id"]).one()
        report = build_executive_report(db, tenant_row, "scan_x5_exception")

    payload = report.model_dump()
    assert payload["exceptions_applied"] is True
    assert payload["exception_count"] == 1
    assert payload["applied_exceptions"][0]["issue_code"] == "DUPLICATE_CUSTOMERS"
    assert "roi_eur" not in payload
    assert "estimated_premium_price_monthly" not in payload

    pdf = render_executive_report_pdf(report)
    assert pdf.startswith(b"%PDF-1.4")
    assert b"BCSentinel" in pdf
    assert len(pdf) > 1500
