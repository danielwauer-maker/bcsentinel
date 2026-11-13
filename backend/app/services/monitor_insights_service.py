"""Entitlement-filtered scan monitor summary.

These projections reuse the exact report builders. Never serialize a full
scan or report model to a Free/Quick browser and then hide fields in CSS.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Tenant
from app.services.report_access_service import resolve_preferred_report_variant
from app.services.product_license_service import build_product_access_snapshot
from app.services.free_health_report_service import build_free_health_report
from app.services.quick_assessment_report_service import build_quick_assessment_report
from app.services.executive_report_v2_service import build_executive_report
from app.services.validation_report_service import build_validation_report
from app.services.monitoring_report_service import build_monitoring_report


def build_monitor_insights(db: Session, tenant: Tenant, scan_id: str) -> dict:
    variant = resolve_preferred_report_variant(db, tenant, scan_id=scan_id)
    access = build_product_access_snapshot(db, tenant)

    if variant == "free-health":
        report = build_free_health_report(db, tenant, scan_id)
        return {
            "tier": "free-health",
            "score": report.data_health_score,
            "score_label": report.score_status,
            "checks": report.checks_count,
            "findings": report.issues_count,
            "affected_records": report.affected_records,
            "total_records": report.total_records,
            "modules_analyzed": report.modules_analyzed,
            "impact_band": report.impact_band,
            "severity": report.severity.model_dump(),
            "risk_areas": [
                {"name": x.name, "findings": x.issue_count,
                 "severity": x.highest_severity, "affected_records": x.affected_records}
                for x in report.risk_areas
            ],
            # No detailed module score, exact EUR impact, finding titles or codes.
        }

    if variant == "quick-assessment":
        report = build_quick_assessment_report(db, tenant, scan_id)
        return {
            "tier": "quick-assessment",
            "score": report.data_health_score,
            "score_label": report.score_status,
            "checks": report.checks_count,
            "findings": report.issues_count,
            "affected_records": report.affected_records,
            "total_records": report.total_records,
            "modules_analyzed": report.modules_analyzed,
            "impact_band": report.impact_band,
            "severity": report.severity.model_dump(),
            "risk_areas": [
                {"name": x.name, "findings": x.issue_count,
                 "severity": x.highest_severity, "affected_records": x.affected_records}
                for x in report.risk_areas
            ],
            "top_findings": [
                {"rank": f.rank, "title": f.title, "severity": f.severity,
                 "risk_area": f.risk_area_label, "impact_band": f.impact_band}
                for f in report.findings[:5]
            ],
        }

    if variant == "validation":
        report = build_validation_report(db, tenant, scan_id)
        return {
            "tier": "validation",
            "score": report.validation_score,
            "baseline_score": report.baseline_score,
            "score_delta": report.score_delta,
            "findings": report.validation_issues_count,
            "findings_delta": report.issues_delta,
            "affected_records": report.validation_affected_records,
            "resolved": report.resolved_count,
            "improved": report.improved_count,
            "remaining": report.remaining_count,
            "regressed": report.regressed_count,
            "new": report.new_count,
            "impact_delta_eur": report.business_impact_delta_eur,
        }

    # Monitoring is a separate subscription, while the report access hierarchy
    # maps it to Full Assessment. The monitor may additionally show trend KPIs.
    if access.get("monitoring_active"):
        report = build_monitoring_report(db, tenant, scan_id)
        return {
            "tier": "monitoring",
            "score": report.current_data_health_score,
            "findings": report.current_findings_count,
            "affected_records": report.current_affected_records,
            "score_delta": report.score_delta_previous,
            "findings_delta": report.findings_delta_previous,
            "new": report.new_findings_count,
            "resolved": report.resolved_findings_count,
            "impact_eur": report.current_business_impact_eur,
            "trend": [
                {"score": point.data_health_score, "findings": point.findings_count}
                for point in report.trend_points[-12:]
            ],
        }

    report = build_executive_report(db, tenant, scan_id)
    return {
        "tier": "assessment",
        "score": report.data_health_score,
        "score_label": report.score_status,
        "checks": report.checks_count,
        "findings": report.issues_count,
        "affected_records": report.affected_records,
        "total_records": report.total_records,
        "impact_eur": report.estimated_loss_eur,
        "potential_saving_eur": report.potential_saving_eur,
        "top_findings": [
            {"rank": f.rank, "title": f.title, "severity": f.severity,
             "affected_records": f.affected_count, "impact_eur": f.estimated_impact_eur}
            for f in report.top_risks[:5]
        ],
        "risk_areas": [
            {"name": x.name, "score": x.score, "findings": x.issue_count,
             "affected_records": x.affected_count}
            for x in report.data_quality
        ],
    }
