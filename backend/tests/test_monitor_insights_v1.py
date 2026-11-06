from __future__ import annotations

from app.db import SessionLocal
from app.services.product_license_service import grant_product_entitlement
from app.services.quick_assessment_access_service import PRODUCT_QUICK_ASSESSMENT


def test_free_scan_monitor_uses_report_scoped_metrics_without_paid_details(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="monitor-insights-free-01")
    response = client.get(
        "/reports/monitor-insights-free-01/monitor-insights",
        headers=auth_header_factory(tenant),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["tier"] == "free-health"
    assert isinstance(body["score"], int)
    assert isinstance(body["findings"], int)
    assert isinstance(body["risk_areas"], list)
    for forbidden in (
        "top_findings", "impact_eur", "impact_delta_eur", "potential_saving_eur",
        "trend", "all_findings", "module_scores", "root_causes", "recommendations"
    ):
        assert forbidden not in body
    for area in body["risk_areas"]:
        assert "score" not in area
        assert "title" not in area
        assert "code" not in area


def test_quick_scan_monitor_limits_findings_and_excludes_euro_amounts(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="monitor-insights-quick-01")
    with SessionLocal() as db:
        grant_product_entitlement(
            db, tenant_id=tenant["tenant_id"],
            product_code=PRODUCT_QUICK_ASSESSMENT, source="monitor-insights-test",
        )
        db.commit()
    response = client.get(
        "/reports/monitor-insights-quick-01/monitor-insights",
        headers=auth_header_factory(tenant),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["tier"] == "quick-assessment"
    assert len(body["top_findings"]) <= 5
    assert "impact_eur" not in body
    assert "potential_saving_eur" not in body
    for finding in body["top_findings"]:
        assert "impact_eur" not in finding
        assert "code" not in finding
        assert "recommendation" not in finding


def test_monitor_insights_rejects_other_tenants_scan(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant_one = tenant_factory(plan="free", license_status="active")
    tenant_two = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant_one["tenant_id"], scan_id="monitor-insights-private-01")
    response = client.get(
        "/reports/monitor-insights-private-01/monitor-insights",
        headers=auth_header_factory(tenant_two),
    )
    assert response.status_code == 404
