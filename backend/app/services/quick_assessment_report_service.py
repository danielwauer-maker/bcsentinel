from __future__ import annotations

from app.models import Tenant
from app.schemas.quick_assessment_report import (
    QuickAssessmentReport,
    QuickRiskArea,
    QuickSeveritySummary,
)
from app.services.free_health_report_service import build_free_health_report


def build_quick_assessment_report(db, tenant: Tenant, scan_id: str) -> QuickAssessmentReport:
    """Build the F8.2 Quick Assessment report shell from the existing scan.

    F8.2 intentionally does not select or expose findings. F8.3 owns the
    server-side Top-Finding boundary and will populate ``findings`` using the
    restricted QuickFinding contract. Until then, the report remains aggregate
    safe while JSON/HTML/PDF/share-link infrastructure can be accepted.
    """
    free = build_free_health_report(db, tenant, scan_id)
    de = free.language == "de"

    if de:
        interpretation = (
            f"Der Quick Assessment ordnet den bestehenden Data-Health-Scan mit {free.data_health_score}/100 ein. "
            f"{free.issues_count} Auffälligkeiten verteilen sich auf {len(free.risk_areas)} relevante Risikobereiche. "
            f"Das modellierte geschäftliche Auswirkungsniveau liegt im Band „{free.impact_band}“."
        )
        actions = [
            "Die priorisierten Risikobereiche nach Score und Schweregrad zuerst prüfen.",
            "Betroffene Geschäftsprozesse und Verantwortlichkeiten für die wichtigsten Datenprobleme festlegen.",
            "Für vollständige Ursachenanalyse, finanzielle Modellwerte und Bereinigungsplanung auf das Full Assessment erweitern.",
        ]
        upgrade = (
            "Das Full Assessment schaltet die vollständige Finding-Liste, Ursachenanalyse, exakten modellierten "
            "Business-Impact-Werte, Priorisierung und detaillierte Bereinigungsempfehlungen dieses Scans frei."
        )
    else:
        interpretation = (
            f"The Quick Assessment interprets the existing Data Health Scan at {free.data_health_score}/100. "
            f"{free.issues_count} issues are distributed across {len(free.risk_areas)} relevant risk areas. "
            f"The modeled business-impact level is in the “{free.impact_band}” band."
        )
        actions = [
            "Review the lowest-scoring and highest-severity risk areas first.",
            "Assign process ownership for the most material data-quality risks.",
            "Upgrade to Full Assessment for complete root-cause analysis, financial modeling and remediation planning.",
        ]
        upgrade = (
            "Full Assessment unlocks the complete finding list, root-cause context, exact modeled business-impact "
            "values, prioritization and detailed remediation recommendations for this scan."
        )

    return QuickAssessmentReport(
        report_id=f"quick-{free.scan_id}",
        tenant_id=free.tenant_id,
        language=free.language,
        scan_id=free.scan_id,
        generated_at_utc=free.generated_at_utc,
        scan_generated_at_utc=free.scan_generated_at_utc,
        company_label=free.company_label,
        environment_label=free.environment_label,
        data_health_score=free.data_health_score,
        score_status=free.score_status,
        checks_count=free.checks_count,
        issues_count=free.issues_count,
        affected_records=free.affected_records,
        total_records=free.total_records,
        severity=QuickSeveritySummary(**free.severity.model_dump()),
        risk_areas=[QuickRiskArea(**row.model_dump()) for row in free.risk_areas],
        impact_band=free.impact_band,
        management_interpretation=interpretation,
        findings=[],
        recommended_next_actions=actions,
        upgrade_message=upgrade,
    )
