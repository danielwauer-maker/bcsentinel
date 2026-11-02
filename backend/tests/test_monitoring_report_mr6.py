from datetime import datetime, timezone

from app.main import app
from app.schemas.monitoring_report import MonitoringCoverage, MonitoringReport
from app.services.monitoring_report_pdf_service import render_monitoring_report_pdf


def _report() -> MonitoringReport:
    now = datetime(2026, 11, 2, tzinfo=timezone.utc)
    return MonitoringReport(
        tenant_id="ten_test",
        company_name="Contoso GmbH",
        environment_name="PROD",
        current_scan_id="S3",
        previous_scan_id="S2",
        baseline_scan_id="S1",
        current_data_health_score=79,
        previous_data_health_score=75,
        baseline_data_health_score=68,
        score_delta_previous=4,
        score_delta_baseline=11,
        current_findings_count=18,
        previous_findings_count=20,
        findings_delta_previous=-2,
        current_affected_records=161200,
        previous_affected_records=180000,
        affected_records_delta_previous=-18800,
        current_business_impact_eur=104800,
        previous_business_impact_eur=120000,
        business_impact_delta_previous_eur=-15200,
        business_impact_delta_baseline_eur=-81630,
        current_critical_findings=2,
        current_high_findings=5,
        management_interpretation=["Positive trend."],
        coverage=MonitoringCoverage(
            period_start_utc=now,
            period_end_utc=now,
            scans_in_period=3,
            latest_scan_at_utc=now,
            baseline_scan_at_utc=now,
            freshness_hours=1,
            data_freshness="current",
        ),
    )


def test_mr6_monitoring_routes_are_registered_under_reports_namespace():
    paths = {route.path for route in app.routes}
    assert "/reports/monitoring/{scan_id}" in paths
    assert "/reports/monitoring/{scan_id}/html" in paths
    assert "/reports/monitoring/{scan_id}/pdf" in paths
    assert "/reports/monitoring/{scan_id}/share-link" in paths
    assert "/reports/monitoring/{scan_id}/html/shared" in paths
    assert "/reports/monitoring/{scan_id}/pdf/shared" in paths


def test_mr6_pdf_renderer_produces_four_page_pdf_document():
    payload = render_monitoring_report_pdf(_report())
    assert payload.startswith(b"%PDF-1.4")
    assert b"/Count 4" in payload
    assert b"BCSentinel Monitoring" in payload
