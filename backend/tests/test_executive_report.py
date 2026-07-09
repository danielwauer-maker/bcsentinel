from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.settings import settings
from app.db import SessionLocal
from app.models import Scan, ScanIssueRecord, TenantProductEntitlement
from app.routers.reports import REPORT_SHARE_ALGORITHM, REPORT_SHARE_TOKEN_TYPE


def _grant_report_access(tenant_id: str) -> None:
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(
            TenantProductEntitlement(
                tenant_id=tenant_id,
                product_code="full_analysis",
                status="active",
                source="test",
                valid_until_utc=now + timedelta(days=7),
                created_at_utc=now,
                updated_at_utc=now,
            )
        )
        db.commit()


def test_executive_report_json_html_and_pdf(client, tenant_factory, auth_header_factory, scan_factory):
    tenant = tenant_factory(plan="premium", license_status="active")
    _grant_report_access(tenant["tenant_id"])
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
    assert payload["scan_type"] == "Manual Scan"
    assert payload["checks_total"] == 165
    assert {bucket["key"] for bucket in payload["severity_distribution"]} == {
        "critical",
        "high",
        "medium",
        "low",
    }

    html_response = client.get("/reports/executive/scan_exec_1/html", headers=auth_header_factory(tenant))

    assert html_response.status_code == 200
    assert "BCSentinel Executive Report (Free)" in html_response.text
    assert "Data Health &Uuml;berblick" in html_response.text
    assert html_response.text.count('class="report-page') == 3
    assert "42.000,00 EUR" in html_response.text
    assert "Upgrade zu Full Analysis oder Monitoring" in html_response.text
    assert "Report Information" in html_response.text
    assert "Top 10 Risks" not in html_response.text
    assert "Quick Wins" not in html_response.text
    assert "Critical Findings" not in html_response.text
    assert "Priority Matrix" not in html_response.text

    pdf_response = client.get("/reports/executive/scan_exec_1/pdf", headers=auth_header_factory(tenant))

    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"
    assert pdf_response.content.startswith(b"%PDF-1.4")


def test_executive_report_free_html_pdf_share_link_does_not_require_paid_access(
    client,
    tenant_factory,
    auth_header_factory,
    scan_factory,
    settings_state,
):
    settings_state(APP_BASE_URL="https://app.bcsentinel.com")
    tenant = tenant_factory()
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_exec_free")

    json_response = client.get("/reports/executive/scan_exec_free", headers=auth_header_factory(tenant))
    html_response = client.get("/reports/executive/scan_exec_free/html", headers=auth_header_factory(tenant))
    pdf_response = client.get("/reports/executive/scan_exec_free/pdf", headers=auth_header_factory(tenant))
    share_link_response = client.post(
        "/reports/executive/scan_exec_free/share-link",
        headers=auth_header_factory(tenant),
        json={"report_type": "html"},
    )

    assert json_response.status_code == 402
    assert html_response.status_code == 200
    assert "BCSentinel Executive Report (Free)" in html_response.text
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"
    assert share_link_response.status_code == 200

    shared_html_response = client.get(share_link_response.json()["url"])

    assert shared_html_response.status_code == 200
    assert "BCSentinel Executive Report (Free)" in shared_html_response.text


def test_executive_report_enforces_tenant_isolation(client, tenant_factory, auth_header_factory, scan_factory):
    owner = tenant_factory()
    other = tenant_factory()
    scan_factory(tenant_id=owner["tenant_id"], scan_id="scan_exec_private")

    response = client.get("/reports/executive/scan_exec_private", headers=auth_header_factory(other))

    assert response.status_code == 403


def test_executive_report_direct_html_requires_tenant_headers(client, tenant_factory, scan_factory):
    tenant = tenant_factory(plan="premium", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_exec_headers")

    response = client.get("/reports/executive/scan_exec_headers/html")

    assert response.status_code == 401
    assert "Missing tenant authentication headers" in response.json()["detail"]


def test_executive_report_share_links_open_without_headers(
    client,
    tenant_factory,
    auth_header_factory,
    scan_factory,
    settings_state,
):
    settings_state(APP_BASE_URL="https://app.bcsentinel.com")
    tenant = tenant_factory(plan="premium", license_status="active")
    _grant_report_access(tenant["tenant_id"])
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_exec_shared")

    html_link_response = client.post(
        "/reports/executive/scan_exec_shared/share-link",
        headers=auth_header_factory(tenant),
        json={"report_type": "html"},
    )
    pdf_link_response = client.post(
        "/reports/executive/scan_exec_shared/share-link",
        headers=auth_header_factory(tenant),
        json={"report_type": "pdf"},
    )

    assert html_link_response.status_code == 200
    assert pdf_link_response.status_code == 200
    html_url = html_link_response.json()["url"]
    pdf_url = pdf_link_response.json()["url"]
    assert "X-Api-Token" not in html_url
    assert "api_token" not in html_url.lower()
    assert html_url.startswith("https://app.bcsentinel.com/reports/")
    assert pdf_url.startswith("https://app.bcsentinel.com/reports/")
    assert "localhost" not in html_url
    assert "localhost" not in pdf_url
    assert "/reports/executive/scan_exec_shared/html/shared?token=" in html_url
    assert "/reports/executive/scan_exec_shared/pdf/shared?token=" in pdf_url

    html_response = client.get(html_url)
    pdf_response = client.get(pdf_url)

    assert html_response.status_code == 200
    assert "BCSentinel Executive Report (Free)" in html_response.text
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"
    assert pdf_response.content.startswith(b"%PDF-1.4")


def test_executive_report_shared_token_is_bound_to_type_and_scan(
    client,
    tenant_factory,
    auth_header_factory,
    scan_factory,
):
    tenant = tenant_factory(plan="premium", license_status="active")
    _grant_report_access(tenant["tenant_id"])
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_exec_bound_1")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_exec_bound_2")

    link_response = client.post(
        "/reports/executive/scan_exec_bound_1/share-link",
        headers=auth_header_factory(tenant),
        json={"report_type": "html"},
    )
    token = link_response.json()["url"].split("token=", 1)[1]

    wrong_type_response = client.get(f"/reports/executive/scan_exec_bound_1/pdf/shared?token={token}")
    wrong_scan_response = client.get(f"/reports/executive/scan_exec_bound_2/html/shared?token={token}")

    assert wrong_type_response.status_code == 403
    assert wrong_scan_response.status_code == 403


def test_executive_report_shared_token_expires(client, tenant_factory, scan_factory):
    tenant = tenant_factory(plan="premium", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_exec_expired")
    expired_token = jwt.encode(
        {
            "type": REPORT_SHARE_TOKEN_TYPE,
            "tenant_id": tenant["tenant_id"],
            "scan_id": "scan_exec_expired",
            "report_type": "html",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.SECRET_KEY,
        algorithm=REPORT_SHARE_ALGORITHM,
    )

    response = client.get(f"/reports/executive/scan_exec_expired/html/shared?token={expired_token}")

    assert response.status_code == 403
