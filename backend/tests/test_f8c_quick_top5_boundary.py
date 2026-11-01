from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.db import SessionLocal
from app.models import Scan, ScanIssueRecord
from app.schemas.quick_assessment_report import QuickAssessmentReport, QuickFinding, QuickSeveritySummary
from app.services.product_license_service import grant_product_entitlement
from app.services.quick_assessment_access_service import PRODUCT_QUICK_ASSESSMENT


def _grant_quick(tenant_id: str) -> None:
    with SessionLocal() as db:
        grant_product_entitlement(
            db,
            tenant_id=tenant_id,
            product_code=PRODUCT_QUICK_ASSESSMENT,
            source="f8c-test",
            valid_until_utc=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.commit()


def _seed_ranked_findings(scan_id: str) -> None:
    rows = [
        ("TOP_HIGH", "Top high", "Finance", "high", 40, 5000.0, "secret recommendation 1"),
        ("TOP_MEDIUM", "Top medium", "CRM", "medium", 80, 5000.0, "secret recommendation 2"),
        ("THIRD", "Third finding", "Inventory", "low", 100, 4000.0, "secret recommendation 3"),
        ("FOURTH", "Fourth finding", "Purchasing", "high", 20, 3000.0, "secret recommendation 4"),
        ("FIFTH", "Fifth finding", "Sales", "medium", 15, 2000.0, "secret recommendation 5"),
        ("SIXTH_SECRET", "Sixth hidden finding", "System", "high", 200, 1000.0, "secret recommendation 6"),
        ("SEVENTH_SECRET", "Seventh hidden finding", "System", "high", 300, 900.0, "secret recommendation 7"),
    ]
    with SessionLocal() as db:
        scan = db.query(Scan).filter(Scan.scan_id == scan_id).one()
        db.query(ScanIssueRecord).filter(ScanIssueRecord.scan_id == scan_id).delete(synchronize_session=False)
        scan.issues_count = len(rows)
        scan.estimated_loss_eur = sum(row[5] for row in rows)
        for code, title, category, severity, affected, impact, recommendation in rows:
            db.add(
                ScanIssueRecord(
                    scan_id=scan_id,
                    code=code,
                    title=title,
                    category=category,
                    severity=severity,
                    affected_count=affected,
                    premium_only=False,
                    recommendation_preview=recommendation,
                    estimated_impact_eur=impact,
                )
            )
        db.commit()


def test_quick_report_returns_exactly_top_five_in_deterministic_business_priority(
    client, tenant_factory, auth_header_factory, scan_factory, settings_state
):
    settings_state(APP_BASE_URL="https://app.bcsentinel.com")
    tenant = tenant_factory(plan="free", license_status="active")
    tenant_id = tenant["tenant_id"]
    scan_id = "f8c-top5"
    scan_factory(tenant_id=tenant_id, scan_id=scan_id)
    _seed_ranked_findings(scan_id)
    _grant_quick(tenant_id)
    headers = auth_header_factory(tenant)

    response = client.get(f"/reports/quick-assessment/{scan_id}", headers=headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    findings = payload["findings"]

    assert len(findings) == 5
    assert [row["rank"] for row in findings] == [1, 2, 3, 4, 5]
    assert [row["title"] for row in findings] == [
        "Top high",
        "Top medium",
        "Third finding",
        "Fourth finding",
        "Fifth finding",
    ]
    # Equal modeled impact is resolved by severity, matching Full Assessment priority semantics.
    assert findings[0]["severity"] == "high"
    assert findings[1]["severity"] == "medium"

    serialized = response.text.lower()
    for forbidden in [
        "sixth hidden finding",
        "seventh hidden finding",
        "sixth_secret",
        "seventh_secret",
        "top_high",
        "top_medium",
        "secret recommendation",
        "estimated_impact_eur",
        "estimated_loss_eur",
        "potential_saving_eur",
    ]:
        assert forbidden not in serialized

    html = client.get(f"/reports/quick-assessment/{scan_id}/html", headers=headers)
    pdf = client.get(f"/reports/quick-assessment/{scan_id}/pdf", headers=headers)
    assert html.status_code == 200
    assert pdf.status_code == 200
    assert "Top high" in html.text
    assert "Fifth finding" in html.text
    assert "Sixth hidden finding" not in html.text
    assert "SIXTH_SECRET" not in html.text
    assert "secret recommendation" not in html.text
    assert b"Top high" in pdf.content
    assert b"Sixth hidden finding" not in pdf.content
    assert b"SIXTH_SECRET" not in pdf.content

    share = client.post(
        f"/reports/quick-assessment/{scan_id}/share-link",
        headers=headers,
        json={"report_type": "html"},
    )
    assert share.status_code == 200
    shared = client.get(share.json()["url"])
    assert shared.status_code == 200
    assert "Fifth finding" in shared.text
    assert "Sixth hidden finding" not in shared.text


def test_quick_report_schema_rejects_more_than_five_findings():
    findings = [
        QuickFinding(
            rank=min(index, 5),
            title=f"Finding {index}",
            severity="medium",
            affected_count=index,
            risk_area="System",
            next_action="Review affected setup.",
        )
        for index in range(1, 7)
    ]

    with pytest.raises(ValidationError):
        QuickAssessmentReport(
            report_id="quick-schema-limit",
            tenant_id="tenant",
            scan_id="scan",
            generated_at_utc=datetime.now(timezone.utc),
            scan_generated_at_utc=datetime.now(timezone.utc),
            company_label="Company",
            environment_label="Sandbox",
            data_health_score=80,
            score_status="Stable with risks",
            severity=QuickSeveritySummary(high=1, medium=4, low=1),
            impact_band="High",
            management_interpretation="Test",
            findings=findings,
            upgrade_message="Upgrade",
        )
