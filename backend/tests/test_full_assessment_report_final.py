from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.db import SessionLocal
from app.models import Scan, ScanIssueRecord
from app.services.product_license_service import PRODUCT_ASSESSMENT, grant_product_entitlement


def _grant_assessment(tenant_id: str) -> None:
    with SessionLocal() as db:
        grant_product_entitlement(
            db,
            tenant_id=tenant_id,
            product_code=PRODUCT_ASSESSMENT,
            source="full-report-final-test",
            valid_until_utc=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.commit()


def test_full_assessment_html_and_pdf_include_complete_customer_delivery_sections(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    tenant_id = tenant["tenant_id"]
    _grant_assessment(tenant_id)
    scan_factory(tenant_id=tenant_id, scan_id="full-report-final")

    with SessionLocal() as db:
        scan = db.query(Scan).filter(Scan.scan_id == "full-report-final").one()
        scan.data_score = 71
        scan.total_records = 125_000
        scan.checks_count = 199
        scan.issues_count = 12
        scan.estimated_loss_eur = 84_000.0
        scan.potential_saving_eur = 42_000.0
        db.query(ScanIssueRecord).filter(ScanIssueRecord.scan_id == "full-report-final").delete()
        for index in range(1, 13):
            db.add(
                ScanIssueRecord(
                    scan_id="full-report-final",
                    code=f"FULL_{index:02d}",
                    category="Finance" if index % 2 else "CRM",
                    title=f"Full finding {index}",
                    severity="high" if index <= 3 else "medium",
                    affected_count=index * 3,
                    premium_only=False,
                    recommendation_preview=f"Remediate finding {index} using verified Business Central data.",
                    estimated_impact_eur=float(13_000 - index * 500),
                )
            )
        db.commit()

    headers = auth_header_factory(tenant)
    html = client.get("/reports/assessment/full-report-final/html", headers=headers)
    assert html.status_code == 200, html.text
    for marker in [
        "Full Assessment Report",
        "Scan Scope &amp; Coverage",
        "Business Area Impact",
        "Detailed Findings",
        "Full finding 12",
        "Remediation Roadmap / Next Steps",
        "Methodology &amp; Limitations",
        "Clean Data – Higher Impact",
    ]:
        assert marker in html.text

    pdf = client.get("/reports/assessment/full-report-final/pdf", headers=headers)
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content.startswith(b"%PDF-1.4")
    for marker in [
        b"Full Assessment Report",
        b"Scan Scope & Coverage",
        b"Detailed Findings",
        b"Full finding 12",
        b"Remediation Roadmap",
        b"Methodology & Limitations",
    ]:
        assert marker in pdf.content


def test_full_assessment_does_not_infer_unsupported_root_cause(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    tenant_id = tenant["tenant_id"]
    _grant_assessment(tenant_id)
    scan_factory(tenant_id=tenant_id, scan_id="full-report-root-cause")

    html = client.get(
        "/reports/assessment/full-report-root-cause/html",
        headers=auth_header_factory(tenant),
    )
    assert html.status_code == 200
    assert "unsupported root cause is inferred" in html.text
