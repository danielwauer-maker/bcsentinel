from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Scan, ScanIssueRecord, Tenant
from app.schemas.free_health_report import FreeHealthReport, FreeRiskArea, FreeSeveritySummary
from app.services.localization_service import tenant_language


MODULES = [
    ("Finance", "finance_score"),
    ("Sales", "sales_score"),
    ("Purchasing", "purchasing_score"),
    ("Inventory", "inventory_score"),
    ("CRM", "crm_score"),
    ("Manufacturing", "manufacturing_score"),
    ("Service", "service_score"),
    ("Jobs", "jobs_score"),
    ("HR", "hr_score"),
    ("System", "system_score"),
]


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

    issues = list(db.scalars(select(ScanIssueRecord).where(ScanIssueRecord.scan_id == scan.scan_id)).all())
    by_category: dict[str, dict[str, int | str]] = {}
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    severity_rank = {"low": 0, "medium": 1, "high": 2}

    for issue in issues:
        severity = str(issue.severity or "low").lower()
        if severity not in severity_counts:
            severity = "low"
        severity_counts[severity] += 1
        category = _category(issue.category, issue.code)
        bucket = by_category.setdefault(category, {"issues": 0, "affected": 0, "severity": "low"})
        bucket["issues"] = int(bucket["issues"]) + 1
        bucket["affected"] = int(bucket["affected"]) + max(0, _safe_int(issue.affected_count))
        if severity_rank[severity] > severity_rank[str(bucket["severity"])]:
            bucket["severity"] = severity

    risk_areas: list[FreeRiskArea] = []
    for name, score_attr in MODULES:
        score = max(0, min(100, _safe_int(getattr(scan, score_attr, 100), 100)))
        bucket = by_category.get(name, {"issues": 0, "affected": 0, "severity": "low"})
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

    score = max(0, min(100, _safe_int(scan.data_score)))
    affected_records = sum(max(0, _safe_int(issue.affected_count)) for issue in issues)
    band = _impact_band(_safe_float(scan.estimated_loss_eur), language)

    if language == "de":
        summary = (
            f"Der BCSentinel Health Check bewertet die Datenqualität mit {score}/100. "
            f"Es wurden {max(0, _safe_int(scan.issues_count))} Auffälligkeiten in {len(risk_areas)} Risikobereichen erkannt. "
            "Der Free Health Check zeigt bewusst nur aggregierte Ergebnisse."
        )
        upgrade_message = (
            "Das Assessment schaltet für 7 Tage die konkreten Findings, Ursachen, finanziellen Modellwerte, "
            "Prioritäten und Handlungsempfehlungen dieses bereits abgeschlossenen Scans frei."
        )
    else:
        summary = (
            f"The BCSentinel Health Check rates data quality at {score}/100. "
            f"It identified {max(0, _safe_int(scan.issues_count))} issues across {len(risk_areas)} risk areas. "
            "The Free Health Check intentionally contains aggregate results only."
        )
        upgrade_message = (
            "Assessment unlocks the concrete findings, root causes, modeled financial values, priorities and "
            "recommendations from this already completed scan for 7 days."
        )

    return FreeHealthReport(
        report_id=f"free-{scan.scan_id}",
        tenant_id=tenant.tenant_id,
        language=language,
        scan_id=scan.scan_id,
        generated_at_utc=datetime.now(timezone.utc),
        scan_generated_at_utc=scan.generated_at_utc,
        company_label=tenant.tenant_id,
        environment_label=tenant.environment_name,
        data_health_score=score,
        score_status=_status(score, language),
        checks_count=max(0, _safe_int(scan.checks_count)),
        issues_count=max(0, _safe_int(scan.issues_count)),
        affected_records=affected_records,
        total_records=max(0, _safe_int(scan.total_records)),
        severity=FreeSeveritySummary(**severity_counts),
        risk_areas=risk_areas,
        impact_band=band,
        summary=summary,
        upgrade_message=upgrade_message,
    )
