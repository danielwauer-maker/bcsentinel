from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ScanIssueRecord
from app.schemas.quick_assessment_report import QuickFinding

MAX_QUICK_FINDINGS = 5
SEVERITY_WEIGHT = {"high": 0, "medium": 1, "low": 2}


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


def _risk_area(issue: ScanIssueRecord) -> str:
    raw = str(issue.category or "").strip().lower()
    code = str(issue.code or "").upper()
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
    if code.startswith(("CUSTOMER", "CUSTOMERS")):
        return "CRM"
    if code.startswith(("VENDOR", "VENDORS", "PURCHASE", "PURCH")):
        return "Purchasing"
    if code.startswith(("ITEM", "ITEMS", "INVENTORY", "WAREHOUSE", "VALUE")):
        return "Inventory"
    if code.startswith(("SALE", "SALES")):
        return "Sales"
    if "LEDGER" in code or code.startswith(("GL_", "G_L_")):
        return "Finance"
    return "System"


def _next_action(area: str, language: str) -> str:
    if language == "de":
        return {
            "Finance": "Buchungs- und Abstimmungssetup gezielt prüfen und betroffene Datenverantwortliche einbeziehen.",
            "Sales": "Verkaufsstammdaten und Prozesssetup für die betroffenen Datensätze priorisiert prüfen.",
            "Purchasing": "Lieferanten- und Einkaufssetup für die betroffenen Datensätze priorisiert prüfen.",
            "Inventory": "Artikel-, Lager- und Bewertungssetup für die betroffenen Datensätze priorisiert prüfen.",
            "CRM": "Kunden- und Kontaktstammdaten für die betroffenen Datensätze priorisiert vervollständigen.",
            "Manufacturing": "Fertigungsstammdaten und Prozesssetup für den betroffenen Bereich gezielt prüfen.",
            "Service": "Service-Stammdaten und Prozesssetup für den betroffenen Bereich gezielt prüfen.",
            "Jobs": "Projekt-/Job-Stammdaten und Prozesssetup für den betroffenen Bereich gezielt prüfen.",
            "HR": "HR-Stammdaten und zugehöriges Setup für den betroffenen Bereich gezielt prüfen.",
            "System": "Betroffene Datensätze und das zugrunde liegende Business-Central-Setup gezielt prüfen.",
        }.get(area, "Betroffene Datensätze und das zugrunde liegende Business-Central-Setup gezielt prüfen.")
    return {
        "Finance": "Review posting and reconciliation setup and involve the accountable data owners.",
        "Sales": "Prioritize sales master data and process setup for the affected records.",
        "Purchasing": "Prioritize vendor and purchasing setup for the affected records.",
        "Inventory": "Prioritize item, inventory and costing setup for the affected records.",
        "CRM": "Prioritize completion of customer and contact master data for the affected records.",
        "Manufacturing": "Review manufacturing master data and process setup for the affected area.",
        "Service": "Review service master data and process setup for the affected area.",
        "Jobs": "Review job/project master data and process setup for the affected area.",
        "HR": "Review HR master data and related setup for the affected area.",
        "System": "Review the affected records and the underlying Business Central setup.",
    }.get(area, "Review the affected records and the underlying Business Central setup.")


def _priority_key(issue: ScanIssueRecord) -> tuple[float, int, int, str]:
    """Match Full Assessment business priority without exposing its sensitive inputs."""
    severity = str(issue.severity or "low").lower()
    return (
        -_safe_float(issue.estimated_impact_eur),
        SEVERITY_WEIGHT.get(severity, 9),
        -_safe_int(issue.affected_count),
        str(issue.code or ""),
    )


def select_quick_findings(db: Session, *, scan_id: str, language: str) -> list[QuickFinding]:
    """Return at most five Quick-safe findings for a scan.

    Exact modeled impact, issue codes, recommendation previews, root-cause data
    and record detail are used neither as output fields nor copied into the
    Quick contract. Modeled impact is used only as an internal ranking signal.
    """
    issues = list(
        db.scalars(
            select(ScanIssueRecord).where(ScanIssueRecord.scan_id == scan_id)
        ).all()
    )
    prioritized = sorted(issues, key=_priority_key)[:MAX_QUICK_FINDINGS]

    findings: list[QuickFinding] = []
    for rank, issue in enumerate(prioritized, start=1):
        area = _risk_area(issue)
        findings.append(
            QuickFinding(
                rank=rank,
                title=str(issue.title or "Data quality finding").strip() or "Data quality finding",
                severity=str(issue.severity or "low").lower(),
                affected_count=max(0, _safe_int(issue.affected_count)),
                risk_area=area,
                next_action=_next_action(area, language),
            )
        )
    return findings
