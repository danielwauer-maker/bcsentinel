from __future__ import annotations

from app.db import SessionLocal
from app.models import Scan, ScanIssueRecord


def test_executive_report_json_html_and_pdf(client, tenant_factory, auth_header_factory, scan_factory):
    tenant = tenant_factory(plan="premium", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_exec_1")
    with SessionLocal() as db:
        scan = db.query(Scan).filter(Scan.scan_id == "scan_exec_1").one()
        scan.data_score = 67
        scan.issues_count = 3
        scan.total_records = 2500
        scan.estimated_loss_eur = 42000.0
        scan.potential_saving_eur = 21000.0
        scan.finance_score = 58
        scan.crm_score = 66
        db.add(
            ScanIssueRecord(
                scan_id="scan_exec_1",
                code="CUSTOMERS_MISSING_EMAIL",
                category="CRM",
                title="Customers missing email",
                severity="high",
                affected_count=120,
                premium_only=False,
                recommendation_preview="Complete customer communication data.",
                estimated_impact_eur=18000.0,
            )
        )
        db.add(
            ScanIssueRecord(
                scan_id="scan_exec_1",
                code="GL_LEDGER_SETUP_GAP",
                category="Finance",
                title="Ledger setup gap",
                severity="medium",
                affected_count=15,
                premium_only=False,
                recommendation_preview="Review posting setup before month-end.",
                estimated_impact_eur=24000.0,
            )
        )
        db.commit()

    json_response = client.get("/reports/executive/scan_exec_1", headers=auth_header_factory(tenant))

    assert json_response.status_code == 200
    payload = json_response.json()
    assert payload["data_health_score"] == 67
    assert payload["estimated_loss_eur"] == 42000.0
    assert len(payload["top_risks"]) >= 3
    assert payload["top_risks"][0]["title"] == "Ledger setup gap"
    assert payload["critical_findings"][0]["title"] == "Customers missing email"

    html_response = client.get("/reports/executive/scan_exec_1/html", headers=auth_header_factory(tenant))

    assert html_response.status_code == 200
    assert "BCSentinel Executive Management Report" in html_response.text
    assert "Top 10 Risks" in html_response.text
    assert "42.000,00 EUR" in html_response.text

    pdf_response = client.get("/reports/executive/scan_exec_1/pdf", headers=auth_header_factory(tenant))

    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"
    assert pdf_response.content.startswith(b"%PDF-1.4")


def test_executive_report_enforces_tenant_isolation(client, tenant_factory, auth_header_factory, scan_factory):
    owner = tenant_factory()
    other = tenant_factory()
    scan_factory(tenant_id=owner["tenant_id"], scan_id="scan_exec_private")

    response = client.get("/reports/executive/scan_exec_private", headers=auth_header_factory(other))

    assert response.status_code == 403
