from __future__ import annotations

from app.db import SessionLocal
from app.models import TenantProductEntitlement
from app.services.product_license_service import grant_product_entitlement
from app.services.quick_assessment_access_service import PRODUCT_QUICK_ASSESSMENT


def _grant_quick(tenant_id: str) -> None:
    with SessionLocal() as db:
        grant_product_entitlement(
            db,
            tenant_id=tenant_id,
            product_code=PRODUCT_QUICK_ASSESSMENT,
            source="f8b-test",
            valid_until_utc=None,
        )
        db.commit()


def test_quick_report_requires_quick_or_higher_access(client, tenant_factory, auth_header_factory, scan_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="f8b-free-blocked")

    response = client.get(
        "/reports/quick-assessment/f8b-free-blocked",
        headers=auth_header_factory(tenant),
    )

    assert response.status_code == 402
    assert "quick assessment" in response.json()["detail"].lower()


def test_quick_report_json_html_pdf_and_share_link_are_limited_and_secure(
    client,
    tenant_factory,
    auth_header_factory,
    scan_factory,
    settings_state,
):
    settings_state(APP_BASE_URL="https://app.bcsentinel.com")
    tenant = tenant_factory(plan="free", license_status="active")
    tenant_id = tenant["tenant_id"]
    scan_factory(tenant_id=tenant_id, scan_id="f8b-quick-report")
    _grant_quick(tenant_id)
    headers = auth_header_factory(tenant)

    response = client.get("/reports/quick-assessment/f8b-quick-report", headers=headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["contract_version"] == "quick-assessment-report-v1"
    assert payload["report_variant"] == "quick_assessment"
    assert payload["scan_id"] == "f8b-quick-report"
    assert payload["modules_analyzed"] >= 0
    assert set(payload["severity"]) == {"critical", "high", "medium", "low", "info"}
    assert len(payload["findings"]) == 1
    assert payload["findings"][0]["title"] == "Issue"
    assert payload["findings"][0]["rank"] == 1
    assert payload["findings"][0]["impact_band"] in {"Low", "Moderate", "High", "Very high", "Niedrig", "Moderat", "Hoch", "Sehr hoch"}
    assert payload["recommended_next_actions"] == []
    assert "impact_band" in payload

    serialized = response.text.lower()
    for forbidden in [
        "estimated_loss_eur",
        "potential_saving_eur",
        "estimated_impact_eur",
        "issue_1",
        "recommendation_preview",
        "fix it",
        "root_cause",
        "record_no",
    ]:
        assert forbidden not in serialized

    html = client.get("/reports/quick-assessment/f8b-quick-report/html", headers=headers)
    assert html.status_code == 200
    assert "Quick Assessment" in html.text
    assert "Issue" in html.text
    assert "ISSUE_1" not in html.text
    assert "Fix it" not in html.text
    assert "10.00 EUR" not in html.text

    pdf = client.get("/reports/quick-assessment/f8b-quick-report/pdf", headers=headers)
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content.startswith(b"%PDF-1.4")
    assert b"QUICK ASSESSMENT" in pdf.content
    assert b"ISSUE_1" not in pdf.content
    assert b"Fix it" not in pdf.content
    assert "bcsentinel-quick-assessment-f8b-quick-report.pdf" in pdf.headers["content-disposition"]

    link = client.post(
        "/reports/quick-assessment/f8b-quick-report/share-link",
        headers=headers,
        json={"report_type": "html"},
    )
    assert link.status_code == 200, link.text
    url = link.json()["url"]
    assert url.startswith("https://app.bcsentinel.com/reports/quick-assessment/f8b-quick-report/html/shared?token=")
    assert "api_token" not in url.lower()
    assert tenant["api_token"] not in url

    shared = client.get(url)
    assert shared.status_code == 200
    assert "Quick Assessment" in shared.text
    assert "Issue" in shared.text
    assert "ISSUE_1" not in shared.text


def test_quick_share_link_rechecks_live_entitlement(client, tenant_factory, auth_header_factory, scan_factory, settings_state):
    settings_state(APP_BASE_URL="https://app.bcsentinel.com")
    tenant = tenant_factory(plan="free", license_status="active")
    tenant_id = tenant["tenant_id"]
    scan_factory(tenant_id=tenant_id, scan_id="f8b-share-revoked")
    _grant_quick(tenant_id)
    headers = auth_header_factory(tenant)

    link = client.post(
        "/reports/quick-assessment/f8b-share-revoked/share-link",
        headers=headers,
        json={"report_type": "html"},
    )
    assert link.status_code == 200
    url = link.json()["url"]

    with SessionLocal() as db:
        entitlement = db.query(TenantProductEntitlement).filter(
            TenantProductEntitlement.tenant_id == tenant_id,
            TenantProductEntitlement.product_code == PRODUCT_QUICK_ASSESSMENT,
        ).one()
        entitlement.status = "revoked"
        db.commit()

    shared = client.get(url)
    assert shared.status_code == 403
    assert "no longer active" in shared.json()["detail"].lower()


def test_quick_share_token_is_bound_to_report_type(client, tenant_factory, auth_header_factory, scan_factory, settings_state):
    settings_state(APP_BASE_URL="https://app.bcsentinel.com")
    tenant = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="f8b-token-binding")
    _grant_quick(tenant["tenant_id"])

    link = client.post(
        "/reports/quick-assessment/f8b-token-binding/share-link",
        headers=auth_header_factory(tenant),
        json={"report_type": "html"},
    )
    assert link.status_code == 200
    token = link.json()["url"].split("token=", 1)[1]

    wrong_surface = client.get(
        f"/reports/quick-assessment/f8b-token-binding/pdf/shared?token={token}"
    )
    assert wrong_surface.status_code == 403
    assert "invalid report share token" in wrong_surface.json()["detail"].lower()
