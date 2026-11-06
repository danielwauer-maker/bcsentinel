from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exception_snapshot_models import ScanExceptionSnapshot
from app.models import Tenant, ScanIssueRecord
from app.schemas.report import ExecutiveReport, ReportAppliedException
from app.services.assessment_scope_service import get_latest_confirmed_scope, included_module_codes
from app.services.executive_report_service import build_executive_report as build_base_executive_report


CATEGORY_TO_MODULE = {
    "finance": "finance",
    "finanzen": "finance",
    "sales": "sales",
    "verkauf": "sales",
    "purchasing": "purchasing",
    "purchase": "purchasing",
    "einkauf": "purchasing",
    "inventory": "inventory",
    "lager": "inventory",
    "artikel": "inventory",
    "crm": "crm",
    "customer": "crm",
    "kunden": "crm",
    "manufacturing": "manufacturing",
    "fertigung": "manufacturing",
    "produktion": "manufacturing",
    "service": "service",
    "jobs": "jobs",
    "job": "jobs",
    "projects": "jobs",
    "projekte": "jobs",
    "hr": "hr",
    "personal": "hr",
    "system": "system",
    "setup": "system",
}


def _module_code(value: str | None) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in CATEGORY_TO_MODULE:
        return CATEGORY_TO_MODULE[normalized]
    # Do not use substring matching: an extension area called "Custom Finance
    # Workflow" must not silently become a supported BC Finance module.
    # Unknown/custom categories are deliberately outside the supported standard
    # scope. Falling back to System would incorrectly keep custom findings in a
    # confirmed Full Assessment because System is always included.
    return "unsupported"


def _apply_confirmed_scope(db: Session, report: ExecutiveReport) -> ExecutiveReport:
    scope = get_latest_confirmed_scope(db, report.scan_id)
    if scope is None:
        return report

    included = included_module_codes(scope)
    # Project against the ORIGINAL scan issue category. The base report may
    # normalize unknown extension categories into "System", which must not
    # accidentally include custom logic in the confirmed standard BC scope.
    raw_issues = db.scalars(select(ScanIssueRecord).where(ScanIssueRecord.scan_id == report.scan_id)).all()
    raw_by_code: dict[str, str | None] = {}
    for issue in raw_issues:
        if issue.code in raw_by_code:
            # Duplicate issue identifiers cannot be reliably bound to a scope.
            from fastapi import HTTPException
            raise HTTPException(status_code=409, detail="Ambiguous duplicate issue code in confirmed scope.")
        raw_by_code[issue.code] = issue.category
    findings = [
        item for item in report.all_findings
        if item.code in raw_by_code and _module_code(raw_by_code[item.code]) in included
    ]
    finding_codes = {item.code for item in findings}
    top_risks = [item for item in report.top_risks if item.code in finding_codes]
    quick_wins = [item for item in report.quick_wins if item.code in finding_codes]
    critical = [item for item in report.critical_findings if item.code in finding_codes]
    financial_risks = [item for item in report.financial_risks if item.code in finding_codes]
    data_quality = [item for item in report.data_quality if _module_code(item.name) in included]
    master_data_quality = [item for item in report.master_data_quality if _module_code(item.name) in included]
    # Area impact must be re-aggregated from the SAME accepted scoped findings.
    # Filtering only the original area rows would leave unsupported extension
    # amounts included in the System bucket and disagree with finding totals.
    area_groups: dict[str, list] = {}
    for finding in findings:
        area_groups.setdefault(finding.category, []).append(finding)
    scoped_total = sum(max(0.0, float(f.estimated_impact_eur or 0.0)) for f in findings)
    business_area_impact = []
    severity_order = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    for old_area in report.business_area_impact:
        group = area_groups.get(old_area.name, [])
        if not group or _module_code(old_area.name) not in included:
            continue
        area_impact = round(sum(max(0.0, float(f.estimated_impact_eur or 0.0)) for f in group), 2)
        business_area_impact.append(old_area.model_copy(update={
            "issue_count": len(group),
            "affected_count": sum(max(0, f.affected_count) for f in group),
            "estimated_impact_eur": area_impact,
            "impact_share_percent": round(area_impact / scoped_total * 100.0, 1) if scoped_total else 0.0,
            "highest_severity": max(
                (f.severity for f in group), key=lambda x: severity_order.get(x, -1)
            ),
        }))
    priorities = [
        item.model_copy(update={"finding_codes": [code for code in item.finding_codes if code in finding_codes]})
        for item in report.priority_matrix
        if not item.finding_codes or any(code in finding_codes for code in item.finding_codes)
    ]

    issues_count = len(findings)
    affected_records = sum(max(0, int(item.affected_count or 0)) for item in findings)
    scoped_loss = round(sum(max(0.0, float(item.estimated_impact_eur or 0.0)) for item in findings), 2)
    original_loss = max(0.0, float(report.estimated_loss_eur or 0.0))
    original_saving = max(0.0, float(report.potential_saving_eur or 0.0))
    if original_loss > 0:
        potential_saving = round(original_saving * min(1.0, scoped_loss / original_loss), 2)
    else:
        potential_saving = 0.0

    language = (report.language or "en").lower()
    if language.startswith("de"):
        summary = (
            f"Bestätigte Full-Assessment-Baseline: {scope.score_value}/100. "
            f"Der bestätigte Scope umfasst {scope.included_modules_count} unterstützte Business-Central-Standardbereiche. "
            "Drittanbieter-Extensions und kundenspezifische Geschäftslogik sind nicht Teil des Scores, sofern sie nicht ausdrücklich unterstützt werden."
        )
    else:
        summary = (
            f"Confirmed Full Assessment baseline: {scope.score_value}/100. "
            f"The confirmed scope includes {scope.included_modules_count} supported Business Central standard areas. "
            "Third-party extensions and custom business logic are outside the score unless explicitly supported."
        )

    return report.model_copy(
        update={
            "executive_summary": summary,
            "data_health_score": scope.score_value,
            "issues_count": issues_count,
            "affected_records": affected_records,
            "estimated_loss_eur": scoped_loss,
            "potential_saving_eur": potential_saving,
            "all_findings": findings,
            "top_risks": top_risks,
            "quick_wins": quick_wins,
            "critical_findings": critical,
            "financial_risks": financial_risks,
            "data_quality": data_quality,
            "master_data_quality": master_data_quality,
            "business_area_impact": business_area_impact,
            "priority_matrix": priorities,
        }
    )


def build_executive_report(db: Session, tenant: Tenant, scan_id: str) -> ExecutiveReport:
    """Canonical Full Assessment report with immutable exception and scope overlays."""
    report = build_base_executive_report(db, tenant, scan_id)
    report = _apply_confirmed_scope(db, report)
    rows = db.scalars(
        select(ScanExceptionSnapshot)
        .where(
            ScanExceptionSnapshot.scan_id == scan_id,
            ScanExceptionSnapshot.tenant_id == tenant.tenant_id,
        )
        .order_by(ScanExceptionSnapshot.issue_code, ScanExceptionSnapshot.source_exception_entry_no)
    ).all()
    applied = [
        ReportAppliedException(
            source_exception_entry_no=row.source_exception_entry_no,
            company_id=row.company_id,
            table_id=row.table_id,
            record_no=row.record_no,
            record_caption=row.record_caption,
            issue_code=row.issue_code,
            reason=row.reason,
            exception_created_by=row.exception_created_by,
            exception_created_at_utc=row.exception_created_at_utc,
            captured_at_utc=row.captured_at_utc,
        )
        for row in rows
    ]
    return report.model_copy(
        update={
            "exceptions_applied": bool(applied),
            "exception_count": len(applied),
            "applied_exceptions": applied,
        }
    )
