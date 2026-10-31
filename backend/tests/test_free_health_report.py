from __future__ import annotations

from app.db import SessionLocal
from app.models import Scan, ScanIssueRecord


def test_free_health_report_json_html_pdf_are_available_without_paid_access(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_free_report_1")
    with SessionLocal() as db:
        scan = db.query(Scan).filter(Scan.scan_id == "scan_free_report_1").one()
        scan.data_score = 68
        scan.checks_count = 199
        scan.issues_count = 2
        scan.total_records = 2500
        scan.estimated_loss_eur = 42000.0
        scan.potential_saving_eur = 21000.0
        scan.finance_score = 58
        scan.crm_score = 66
        db.query(ScanIssueRecord).filter(ScanIssueRecord.scan_id == "scan_free_report_1").delete(synchronize_session=False)
        db.add(
            ScanIssueRecord(
                scan_id="scan_free_report_1",
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
                scan_id="scan_free_report_1",
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

    response = client.get("/reports/free-health/scan_free_report_1", headers=auth_header_factory(tenant))
    assert response.status_code == 200
    payload = response.json()
    assert payload["contract_version"] == "free-health-report-v1"
    assert payload["report_variant"] == "free_health"
    assert payload["data_health_score"] == 68
    assert payload["checks_count"] == 199
    assert payload["impact_band"] == "High"
    assert payload["severity"] == {"high": 1, "medium": 1, "low": 0}

    serialized = response.text.lower()
    for forbidden in (
        "customers missing email",
        "ledger setup gap",
        "customers_missing_email",
        "gl_ledger_setup_gap",
        "18000",
        "24000",
        "42000",
        "21000",
        "recommendation_preview",
        "estimated_loss_eur",
        "potential_saving_eur",
        "top_risks",
        "critical_findings",
    ):
        assert forbidden not in serialized

    html = client.get("/reports/free-health/scan_free_report_1/html", headers=auth_header_factory(tenant))
    assert html.status_code == 200
    assert "Free Health Report" in html.text
    assert "CUSTOMERS_MISSING_EMAIL" not in html.text
    assert "Customers missing email" not in html.text
    assert "42,000" not in html.text
    assert "42000" not in html.text

    pdf = client.get("/reports/free-health/scan_free_report_1/pdf", headers=auth_header_factory(tenant))
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content.startswith(b"%PDF-1.4")


def test_free_health_report_share_link_is_available_to_free_tenant(
    client, tenant_factory, auth_header_factory, scan_factory, settings_state
):
    settings_state(APP_BASE_URL="https://app.bcsentinel.com")
    tenant = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_free_shared")

    link = client.post(
        "/reports/free-health/scan_free_shared/share-link",
        headers=auth_header_factory(tenant),
        json={"report_type": "html"},
    )
    assert link.status_code == 200
    url = link.json()["url"]
    assert url.startswith("https://app.bcsentinel.com/reports/free-health/")
    assert "api_token" not in url.lower()
    assert "X-Api-Token" not in url

    shared = client.get(url)
    assert shared.status_code == 200
    assert "Free Health Report" in shared.text


def test_free_health_report_enforces_tenant_isolation(
    client, tenant_factory, auth_header_factory, scan_factory
):
    owner = tenant_factory(plan="free", license_status="active")
    other = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=owner["tenant_id"], scan_id="scan_free_private")

    response = client.get("/reports/free-health/scan_free_private", headers=auth_header_factory(other))
    assert response.status_code == 404
    assert response.json()["detail"] == "Report not found."


def test_paid_executive_report_remains_locked_for_free_tenant(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_free_locked_exec")

    free_response = client.get(
        "/reports/free-health/scan_free_locked_exec",
        headers=auth_header_factory(tenant),
    )
    paid_response = client.get(
        "/reports/executive/scan_free_locked_exec",
        headers=auth_header_factory(tenant),
    )
    assert free_response.status_code == 200
    assert paid_response.status_code == 402
