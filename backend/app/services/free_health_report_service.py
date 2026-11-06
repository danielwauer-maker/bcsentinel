from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Scan, ScanIssueRecord, ScanRunStatus, Tenant
from app.schemas.free_health_report import FreeHealthReport, FreeRiskArea, FreeSeveritySummary
from app.services.assessment_scope_service import (
    get_or_create_auto_scope,
    included_module_codes,
    supported_issue_area,
)
from app.services.localization_service import tenant_language


MODULES = [
    ("Finance", "finance_score", "finance"),
    ("Sales", "sales_score", "sales"),
    ("Purchasing", "purchasing_score", "purchasing"),
    ("Inventory", "inventory_score", "inventory"),
    ("CRM", "crm_score", "crm"),
    ("Manufacturing", "manufacturing_score", "manufacturing"),
    ("Service", "service_score", "service"),
    ("Jobs", "jobs_score", "jobs"),
    ("HR", "hr_score", "hr"),
    ("System", "system_score", "system"),
]


SEVERITY_ORDER = {
    "info": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value or default)
    except (TypeError, ValueError):
        return default


def _status(score: int, language: str) -> str:
    if score < 60:
        return "Kritisch" if language == "de" else "Critical"
    if score < 75:
        return "Braucht Aufmerksamkeit" if language == "de" else "Needs attention"
    if score < 85:
        return "Stabil mit Risiken" if language == "de" else "Stable with risks"
    if score < 95:
        return "Gut" if language == "de" else "Good"
    return "Exzellent" if language == "de" else "Excellent"


def _category(category: str | None, code: str | None) -> str:
    raw = str(category or "").strip().lower()
    code_upper = str(code or "").upper()
    mapping = {
        "finance": "Finance",
        "sales": "Sales",
        "purchase": "Purchasing",
        "purchasing": "Purchasing",
        "inventory": "Inventory",
        "item": "Inventory",
        "crm": "CRM",
        "customer": "CRM",
        "vendor": "Purchasing",
        "manufacturing": "Manufacturing",
        "service": "Service",
        "jobs": "Jobs",
        "job": "Jobs",
        "hr": "HR",
        "system": "System",
    }
    if raw in mapping:
        return mapping[raw]
    if code_upper.startswith(("CUSTOMER", "CUSTOMERS")):
        return "CRM"
    if code_upper.startswith(("VENDOR", "VENDORS", "PURCHASE", "PURCH")):
        return "Purchasing"
    if code_upper.startswith(("ITEM", "ITEMS", "INVENTORY", "WAREHOUSE", "VALUE")):
        return "Inventory"
    if code_upper.startswith(("SALE", "SALES")):
        return "Sales"
    if "LEDGER" in code_upper or code_upper.startswith(("GL_", "G_L_")):
        return "Finance"
    return "System"


def _severity(value: object) -> str:
    raw = str(value or "").strip().lower()
    aliases = {
        "critical": "critical",
        "crit": "critical",
        "high": "high",
        "medium": "medium",
        "moderate": "medium",
        "warning": "medium",
        "low": "low",
        "info": "info",
        "informational": "info",
    }
    return aliases.get(raw, "info")


def _enabled_module_count(value: str | None) -> int:
    modules = {
        item.strip().lower()
        for item in str(value or "").split(",")
        if item.strip()
    }
    return len(modules)


def _impact_band(estimated_loss_eur: float, language: str) -> str:
    value = max(0.0, estimated_loss_eur)
    if value < 5_000:
        key = "Low"
    elif value < 25_000:
        key = "Moderate"
    elif value < 100_000:
        key = "High"
    else:
        key = "Very high"
    if language != "de":
        return key
    return {"Low": "Niedrig", "Moderate": "Moderat", "High": "Hoch", "Very high": "Sehr hoch"}[key]


def build_free_health_report(db: Session, tenant: Tenant, scan_id: str) -> FreeHealthReport:
    language = tenant_language(tenant)
    scan = db.scalar(select(Scan).where(Scan.scan_id == scan_id))
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found.")
    if scan.tenant_id != tenant.tenant_id:
        raise HTTPException(status_code=403, detail="Scan does not belong to authenticated tenant.")

    run = db.scalar(
        select(ScanRunStatus).where(
            ScanRunStatus.run_id == scan.scan_id,
            ScanRunStatus.tenant_id == tenant.tenant_id,
        )
    )
    company_label = str(run.company_name or "").strip() if run is not None else ""
    if not company_label:
        company_label = tenant.tenant_id

    scope = get_or_create_auto_scope(db, scan)
    active_scope = included_module_codes(scope)

    modules_analyzed = _enabled_module_count(scan.enabled_modules)
    if modules_analyzed == 0 and run is not None:
        modules_analyzed = max(
            0,
            _safe_int(run.completed_modules) or _safe_int(run.total_modules),
        )

    all_issues = list(db.scalars(select(ScanIssueRecord).where(ScanIssueRecord.scan_id == scan.scan_id)).all())
    issues = [issue for issue in all_issues if supported_issue_area(issue) in active_scope]
    by_category: dict[str, dict[str, int | str]] = {}
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}

    for issue in issues:
        severity = _severity(issue.severity)
        severity_counts[severity] += 1
        category = _category(issue.category, issue.code)
        bucket = by_category.setdefault(category, {"issues": 0, "affected": 0, "severity": "info"})
        bucket["issues"] = int(bucket["issues"]) + 1
        bucket["affected"] = int(bucket["affected"]) + max(0, _safe_int(issue.affected_count))
        if SEVERITY_ORDER[severity] > SEVERITY_ORDER[str(bucket["severity"])]:
            bucket["severity"] = severity

    risk_areas: list[FreeRiskArea] = []
    for name, score_attr, module_code in MODULES:
        if module_code not in active_scope:
            continue
        score = max(0, min(100, _safe_int(getattr(scan, score_attr, 100), 100)))
        bucket = by_category.get(name, {"issues": 0, "affected": 0, "severity": "info"})
        if score < 100 or int(bucket["issues"]) > 0:
            risk_areas.append(
                FreeRiskArea(
                    name=name,
                    score=score,
                    status=_status(score, language),
                    issue_count=int(bucket["issues"]),
                    affected_records=int(bucket["affected"]),
                    highest_severity=str(bucket["severity"]),
                )
            )
    risk_areas.sort(key=lambda row: (row.score, -row.issue_count, -row.affected_records, row.name))

    score = max(0, min(100, _safe_int(scope.score_value)))
    affected_records = sum(max(0, _safe_int(issue.affected_count)) for issue in issues)
    band = _impact_band(sum(max(0.0, _safe_float(issue.estimated_impact_eur)) for issue in issues), language)
    scoped_issue_count = len(issues)

    if language == "de":
        summary = (
            f"Der vorläufige BCSentinel Health Score liegt bei {score}/100. "
            f"Es wurden {scoped_issue_count} Auffälligkeiten in {len(risk_areas)} automatisch erkannten Standard-Risikobereichen berücksichtigt. "
            "Die Anwendbarkeit weiterer Standardmodule wurde noch nicht bestätigt; Drittanbieter-Extensions und kundenspezifische Logik sind nicht Teil des Scores."
        )
        upgrade_message = (
            "Das Full Assessment schaltet die vollständigen Findings frei und ermöglicht die Bestätigung des tatsächlichen Standard-Modul-Scopes. "
            "Eine daraus resultierende Score-Änderung ist eine Scope-Anpassung und noch keine gemessene Verbesserung."
        )
    else:
        summary = (
            f"The preliminary BCSentinel Health Score is {score}/100. "
            f"It includes {scoped_issue_count} issues across {len(risk_areas)} automatically detected standard risk areas. "
            "Applicability of further standard modules has not yet been confirmed; third-party extensions and custom business logic are outside the score."
        )
        upgrade_message = (
            "Full Assessment unlocks the complete findings and allows confirmation of the actual standard-module scope. "
            "Any score change caused by scope confirmation is a scope adjustment, not measured remediation."
        )

    return FreeHealthReport(
        report_id=f"free-{scan.scan_id}",
        tenant_id=tenant.tenant_id,
        language=language,
        scan_id=scan.scan_id,
        generated_at_utc=datetime.now(timezone.utc),
        scan_generated_at_utc=scan.generated_at_utc,
        company_label=company_label,
        environment_label=tenant.environment_name,
        data_health_score=score,
        score_status=_status(score, language),
        checks_count=max(0, _safe_int(scan.checks_count)),
        modules_analyzed=modules_analyzed,
        issues_count=scoped_issue_count,
        affected_records=affected_records,
        total_records=max(0, _safe_int(scan.total_records)),
        severity=FreeSeveritySummary(**severity_counts),
        risk_areas=risk_areas,
        impact_band=band,
        summary=summary,
        upgrade_message=upgrade_message,
    )
