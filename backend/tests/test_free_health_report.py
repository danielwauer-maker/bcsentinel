from __future__ import annotations

from datetime import datetime, timezone

from app.db import SessionLocal
from app.models import Scan, ScanIssueRecord, ScanRunStatus


def test_free_health_report_json_html_pdf_are_available_without_paid_access(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_free_report_1")
    with SessionLocal() as db:
        scan = db.query(Scan).filter(Scan.scan_id == "scan_free_report_1").one()
        scan.data_score = 68
        scan.checks_count = 199
        scan.issues_count = 4
        scan.total_records = 2500
        scan.estimated_loss_eur = 42000.0
        scan.potential_saving_eur = 21000.0
        scan.finance_score = 58
        scan.crm_score = 66
        scan.service_score = 92
        scan.enabled_modules = "System,Finance,CRM,Service"
        db.query(ScanIssueRecord).filter(ScanIssueRecord.scan_id == "scan_free_report_1").delete(synchronize_session=False)
        db.add(
            ScanRunStatus(
                run_id="scan_free_report_1",
                tenant_id=tenant["tenant_id"],
                company_name="Contoso GmbH",
                environment_name="PROD",
                scan_mode="deep",
                status="completed",
                progress_percent=100,
                total_modules=4,
                completed_modules=4,
                failed_modules=0,
                updated_at_utc=datetime.now(timezone.utc),
            )
        )
        db.add(
            ScanIssueRecord(
                scan_id="scan_free_report_1",
                code="CUSTOMERS_DUPLICATE",
                category="CRM",
                title="Duplicate customers",
                severity="critical",
                affected_count=24,
                premium_only=False,
                recommendation_preview="Review duplicate customer records.",
                estimated_impact_eur=10000.0,
            )
        )
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
                estimated_impact_eur=14000.0,
            )
        )
        db.add(
            ScanIssueRecord(
                scan_id="scan_free_report_1",
                code="SERVICE_INFORMATIONAL",
                category="Service",
                title="Service informational signal",
                severity="info",
                affected_count=3,
                premium_only=False,
                recommendation_preview="Review when convenient.",
                estimated_impact_eur=0.0,
            )
        )
        db.commit()

    response = client.get("/reports/free-health/scan_free_report_1", headers=auth_header_factory(tenant))
    assert response.status_code == 200
    payload = response.json()
    assert payload["contract_version"] == "free-health-report-v1"
    assert payload["report_variant"] == "free_health"
    assert payload["company_label"] == "Contoso GmbH"
    assert payload["data_health_score"] == 68
    assert payload["checks_count"] == 199
    assert payload["modules_analyzed"] == 4
    assert payload["impact_band"] == "High"
    assert payload["severity"] == {
        "critical": 1,
        "high": 1,
        "medium": 1,
        "low": 0,
        "info": 1,
    }
    crm_area = next(area for area in payload["risk_areas"] if area["name"] == "CRM")
    assert crm_area["highest_severity"] == "critical"

    serialized = response.text.lower()
    for forbidden in (
        "duplicate customers",
        "customers missing email",
        "ledger setup gap",
        "service informational signal",
        "customers_duplicate",
        "customers_missing_email",
        "gl_ledger_setup_gap",
        "service_informational",
        "10000",
        "18000",
        "14000",
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
    assert "CUSTOMERS_DUPLICATE" not in html.text
    assert "Duplicate customers" not in html.text
    assert "42,000" not in html.text
    assert "42000" not in html.text

    pdf = client.get("/reports/free-health/scan_free_report_1/pdf", headers=auth_header_factory(tenant))
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content.startswith(b"%PDF-1.4")


def test_free_health_report_uses_run_module_count_as_legacy_fallback(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_free_modules_fallback")
    with SessionLocal() as db:
        scan = db.query(Scan).filter(Scan.scan_id == "scan_free_modules_fallback").one()
        scan.enabled_modules = None
        db.add(
            ScanRunStatus(
                run_id="scan_free_modules_fallback",
                tenant_id=tenant["tenant_id"],
                company_name="Fallback Company GmbH",
                scan_mode="deep",
                status="completed",
                progress_percent=100,
                total_modules=10,
                completed_modules=10,
                failed_modules=0,
                updated_at_utc=datetime.now(timezone.utc),
            )
        )
        db.commit()

    response = client.get(
        "/reports/free-health/scan_free_modules_fallback",
        headers=auth_header_factory(tenant),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["company_label"] == "Fallback Company GmbH"
    assert payload["modules_analyzed"] == 10


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
