from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.db import SessionLocal
from app.models import Scan, ScanIssueRecord, TenantScanCredit
from app.services.product_license_service import (
    PRODUCT_ASSESSMENT,
    PRODUCT_VALIDATION_CHECK,
    grant_product_entitlement,
)


def _grant(tenant_id: str, product_code: str) -> None:
    with SessionLocal() as db:
        grant_product_entitlement(
            db,
            tenant_id=tenant_id,
            product_code=product_code,
            source="f2-test",
            valid_until_utc=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.commit()


def test_assessment_route_is_canonical_alias_without_breaking_executive(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    _grant(tenant["tenant_id"], PRODUCT_ASSESSMENT)
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="f2-assessment-1")
    headers = auth_header_factory(tenant)

    assessment = client.get("/reports/assessment/f2-assessment-1", headers=headers)
    executive = client.get("/reports/executive/f2-assessment-1", headers=headers)

    assert assessment.status_code == 200, assessment.text
    assert executive.status_code == 200, executive.text
    assert assessment.json()["report_variant"] == "assessment"
    assert executive.json()["report_variant"] == "executive"
    assert assessment.json()["scan_id"] == executive.json()["scan_id"]

    html = client.get("/reports/assessment/f2-assessment-1/html", headers=headers)
    pdf = client.get("/reports/assessment/f2-assessment-1/pdf", headers=headers)
    assert html.status_code == 200
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert "bcsentinel-assessment-report-f2-assessment-1.pdf" in pdf.headers["content-disposition"]


def test_validation_requires_validation_access_not_assessment_only(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    _grant(tenant["tenant_id"], PRODUCT_ASSESSMENT)
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="f2-base-access")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="f2-validation-access")

    response = client.get(
        "/reports/validation/f2-validation-access",
        headers=auth_header_factory(tenant),
    )
    assert response.status_code == 402
    assert "validation" in response.json()["detail"].lower()


def test_validation_report_compares_real_validation_credit_scan_to_prior_baseline(
    client, tenant_factory, auth_header_factory, scan_factory, settings_state
):
    settings_state(APP_BASE_URL="https://app.bcsentinel.com")
    tenant = tenant_factory(plan="free", license_status="active")
    tenant_id = tenant["tenant_id"]
    headers = auth_header_factory(tenant)

    scan_factory(tenant_id=tenant_id, scan_id="f2-baseline")
    scan_factory(tenant_id=tenant_id, scan_id="f2-validation")

    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        baseline = db.query(Scan).filter(Scan.scan_id == "f2-baseline").one()
        validation = db.query(Scan).filter(Scan.scan_id == "f2-validation").one()
        baseline.generated_at_utc = now - timedelta(days=2)
        validation.generated_at_utc = now - timedelta(days=1)
        baseline.data_score = 62
        baseline.issues_count = 4
        baseline.estimated_loss_eur = 50000.0
        validation.data_score = 79
        validation.issues_count = 3
        validation.estimated_loss_eur = 28000.0

        db.query(ScanIssueRecord).filter(ScanIssueRecord.scan_id.in_(["f2-baseline", "f2-validation"])).delete(synchronize_session=False)
        db.add_all(
            [
                ScanIssueRecord(
                    scan_id="f2-baseline", code="RESOLVED", category="Finance", title="Resolved issue",
                    severity="high", affected_count=20, premium_only=False,
                    recommendation_preview="Fix resolved", estimated_impact_eur=12000.0,
                ),
                ScanIssueRecord(
                    scan_id="f2-baseline", code="IMPROVED", category="CRM", title="Improved issue",
                    severity="high", affected_count=30, premium_only=False,
                    recommendation_preview="Fix improved", estimated_impact_eur=15000.0,
                ),
                ScanIssueRecord(
                    scan_id="f2-validation", code="IMPROVED", category="CRM", title="Improved issue",
                    severity="medium", affected_count=10, premium_only=False,
                    recommendation_preview="Fix improved", estimated_impact_eur=6000.0,
                ),
                ScanIssueRecord(
                    scan_id="f2-baseline", code="REGRESSED", category="Inventory", title="Regressed issue",
                    severity="medium", affected_count=4, premium_only=False,
                    recommendation_preview="Fix regressed", estimated_impact_eur=2000.0,
                ),
                ScanIssueRecord(
                    scan_id="f2-validation", code="REGRESSED", category="Inventory", title="Regressed issue",
                    severity="high", affected_count=9, premium_only=False,
                    recommendation_preview="Fix regressed", estimated_impact_eur=5500.0,
                ),
                ScanIssueRecord(
                    scan_id="f2-validation", code="NEW", category="Sales", title="New issue",
                    severity="medium", affected_count=3, premium_only=False,
                    recommendation_preview="Fix new", estimated_impact_eur=4500.0,
                ),
            ]
        )
        db.add(
            TenantScanCredit(
                tenant_id=tenant_id,
                product_code=PRODUCT_VALIDATION_CHECK,
                status="consumed",
                source="f2-test",
                source_purchase_id=None,
                consumed_scan_id="f2-validation",
                created_at_utc=now - timedelta(days=1),
                consumed_at_utc=now - timedelta(days=1),
            )
        )
        grant_product_entitlement(
            db,
            tenant_id=tenant_id,
            product_code=PRODUCT_VALIDATION_CHECK,
            source="f2-test",
            valid_until_utc=now + timedelta(days=7),
        )
        db.commit()

    response = client.get("/reports/validation/f2-validation", headers=headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["contract_version"] == "validation-report-v1"
    assert payload["baseline_scan_id"] == "f2-baseline"
    assert payload["validation_scan_id"] == "f2-validation"
    assert payload["baseline_score"] == 62
    assert payload["validation_score"] == 79
    assert payload["score_delta"] == 17
    assert payload["resolved_count"] == 1
    assert payload["improved_count"] == 1
    assert payload["regressed_count"] == 1
    assert payload["new_count"] == 1
    assert payload["estimated_exposure_reduction_eur"] == 22000.0

    html = client.get("/reports/validation/f2-validation/html", headers=headers)
    pdf = client.get("/reports/validation/f2-validation/pdf", headers=headers)
    assert html.status_code == 200
    assert "Validation Report" in html.text
    assert "Resolved issue" in html.text
    assert "New issue" in html.text
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF-1.4")

    link = client.post(
        "/reports/validation/f2-validation/share-link",
        headers=headers,
        json={"report_type": "html"},
    )
    assert link.status_code == 200, link.text
    url = link.json()["url"]
    assert url.startswith("https://app.bcsentinel.com/reports/validation/f2-validation/html/shared?token=")
    assert "api_token" not in url.lower()
    shared = client.get(url)
    assert shared.status_code == 200
    assert "Regressed issue" in shared.text


def test_non_validation_scan_cannot_be_presented_as_validation_report(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    _grant(tenant["tenant_id"], PRODUCT_VALIDATION_CHECK)
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="f2-normal-scan")

    response = client.get(
        "/reports/validation/f2-normal-scan",
        headers=auth_header_factory(tenant),
    )
    assert response.status_code == 404
    assert "not a completed" in response.json()["detail"].lower()
