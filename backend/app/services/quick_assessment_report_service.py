from __future__ import annotations

from collections import Counter

from app.models import Tenant
from app.schemas.quick_assessment_report import (
    QuickAssessmentReport,
    QuickRiskArea,
    QuickSeveritySummary,
)
from app.services.free_health_report_service import build_free_health_report
from app.services.quick_finding_selection_service import select_quick_findings


_DE_AREA_LABELS = {
    "Finance": "Finanzen",
    "Sales": "Verkauf",
    "Purchasing": "Einkauf",
    "Inventory": "Artikel & Lager",
    "CRM": "CRM / Kunden",
    "Manufacturing": "Fertigung",
    "Service": "Service",
    "Jobs": "Projekte / Jobs",
    "HR": "Personal",
    "System": "System & Setup",
}


def _localized_area(area: str, *, de: bool) -> str:
    return _DE_AREA_LABELS.get(area, area) if de else area


def _management_interpretation(findings, *, de: bool) -> str:
    """Describe only observable patterns inside the Quick Top-5 disclosure."""
    count = len(findings)
    if count == 0:
        return (
            "Im Quick-Assessment wurden keine priorisierbaren Findings erkannt. Der Scan-Kontext bleibt als Ausgangspunkt für die weitere Datenqualitätsbewertung bestehen."
            if de
            else "No findings eligible for Quick prioritization were detected. The scan context remains available as the baseline for further data-health review."
        )

    areas = Counter(item.risk_area for item in findings)
    lead_area, lead_count = sorted(areas.items(), key=lambda row: (-row[1], row[0]))[0]
    severe_count = sum(item.severity in {"critical", "high"} for item in findings)
    high_impact_labels = {"Hoch", "Sehr hoch"} if de else {"High", "Very high"}
    high_impact_count = sum(item.impact_band in high_impact_labels for item in findings)
    area_label = _localized_area(lead_area, de=de)

    if de:
        concentration = (
            f"Die Prioritäten bündeln sich im Bereich {area_label}: {lead_count} von {count} Top-Findings liegen dort."
            if lead_count > 1
            else f"Die {count} Top-Findings verteilen sich auf mehrere Bereiche; {area_label} steht in der aktuellen Priorisierung an erster Stelle."
        )
        severity = (
            f" {severe_count} von {count} priorisierten Findings haben eine hohe oder kritische Severity."
            if severe_count
            else f" Keines der {count} priorisierten Findings hat eine hohe oder kritische Severity."
        )
        impact = (
            f" {high_impact_count} von {count} liegen gleichzeitig in einem hohen oder sehr hohen Impact-Band."
            if high_impact_count
            else f" Keines der {count} liegt in einem hohen oder sehr hohen Impact-Band."
        )
        return concentration + severity + impact + " Die dargestellte Reihenfolge folgt der modellierten Business-Priorität des Scans."

    concentration = (
        f"Priorities are concentrated in {area_label}: {lead_count} of the {count} Top findings are in this area."
        if lead_count > 1
        else f"The {count} Top findings span several areas; {area_label} currently leads the priority order."
    )
    severity = (
        f" {severe_count} of {count} prioritized findings have high or critical severity."
        if severe_count
        else f" None of the {count} prioritized findings has high or critical severity."
    )
    impact = (
        f" {high_impact_count} of {count} also fall into a high or very-high impact band."
        if high_impact_count
        else f" None of the {count} falls into a high or very-high impact band."
    )
    return concentration + severity + impact + " The displayed order follows the scan's modeled business priority."


def build_quick_assessment_report(db, tenant: Tenant, scan_id: str) -> QuickAssessmentReport:
    """Build the permanent Quick disclosure layer from the existing full scan.

    The returned schema remains structurally incapable of carrying Full-only
    data such as issue codes, exact EUR values, root causes or record drilldown.
    """
    free = build_free_health_report(db, tenant, scan_id)
    de = free.language == "de"
    findings = select_quick_findings(db, scan_id=scan_id, language=free.language)

    interpretation = _management_interpretation(findings, de=de)
    if de:
        upgrade = (
            "Das Full Assessment erweitert denselben Scan um die vollständige Finding-Liste, exakte modellierte "
            "Business-Impact-Werte, Ursachenanalyse, detaillierte Empfehlungen und eine priorisierte Bereinigungs-Roadmap."
        )
    else:
        upgrade = (
            "Full Assessment expands the same scan with the complete finding list, exact modeled business-impact "
            "values, root-cause analysis, detailed recommendations and a prioritized remediation roadmap."
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
        modules_analyzed=free.modules_analyzed,
        issues_count=free.issues_count,
        affected_records=free.affected_records,
        total_records=free.total_records,
        severity=QuickSeveritySummary(**free.severity.model_dump()),
        risk_areas=[QuickRiskArea(**row.model_dump()) for row in free.risk_areas],
        impact_band=free.impact_band,
        management_interpretation=interpretation,
        findings=findings,
        recommended_next_actions=[],
        upgrade_message=upgrade,
    )
