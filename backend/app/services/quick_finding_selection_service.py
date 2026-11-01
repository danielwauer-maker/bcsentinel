from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ScanIssueRecord
from app.schemas.quick_assessment_report import QuickFinding

MAX_QUICK_FINDINGS = 5
SEVERITY_WEIGHT = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


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


def normalize_severity(value: object) -> str:
    normalized = str(value or "").strip().lower()
    mapping = {
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
    return mapping.get(normalized, "info")


def quick_impact_band(value: object, language: str) -> str:
    """Return the safe non-monetary band used by Quick, never the exact amount."""
    impact = max(0.0, _safe_float(value))
    if impact < 5_000:
        return "Niedrig" if language == "de" else "Low"
    if impact < 25_000:
        return "Moderat" if language == "de" else "Moderate"
    if impact < 100_000:
        return "Hoch" if language == "de" else "High"
    return "Sehr hoch" if language == "de" else "Very high"


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


def _next_action(issue: ScanIssueRecord, area: str, language: str) -> str:
    """Create a deterministic Quick-safe action tied to this finding.

    The allowed finding title is used only as context. No recommendation preview,
    root-cause detail, issue code or record-level detail is copied from Full.
    """
    title = str(issue.title or "Data quality finding").strip() or "Data quality finding"
    if language == "de":
        area_action = {
            "Finance": "Buchungs- und Abstimmungssetup sowie die betroffenen Datensätze fachlich prüfen",
            "Sales": "Verkaufsstammdaten und Prozesssetup für die betroffenen Datensätze fachlich prüfen",
            "Purchasing": "Lieferanten-/Einkaufsstammdaten und Prozesssetup fachlich prüfen",
            "Inventory": "Artikel-, Lager- und Bewertungsdaten im betroffenen Bereich fachlich prüfen",
            "CRM": "Kunden-/Kontaktstammdaten im betroffenen Bereich fachlich prüfen",
            "Manufacturing": "Fertigungsstammdaten und Prozesssetup im betroffenen Bereich fachlich prüfen",
            "Service": "Service-Stammdaten und Prozesssetup im betroffenen Bereich fachlich prüfen",
            "Jobs": "Projekt-/Job-Stammdaten und Prozesssetup im betroffenen Bereich fachlich prüfen",
            "HR": "HR-Stammdaten und zugehöriges Setup im betroffenen Bereich fachlich prüfen",
            "System": "betroffene Datensätze und das zugrunde liegende Business-Central-Setup fachlich prüfen",
        }.get(area, "betroffene Datensätze und das zugrunde liegende Business-Central-Setup fachlich prüfen")
        return f'Finding „{title}“ priorisieren: {area_action}.'

    area_action = {
        "Finance": "review posting/reconciliation setup and the affected records",
        "Sales": "review sales master data and process setup for the affected records",
        "Purchasing": "review vendor/purchasing master data and process setup",
        "Inventory": "review item, inventory and costing data in the affected area",
        "CRM": "review customer/contact master data in the affected area",
        "Manufacturing": "review manufacturing master data and process setup in the affected area",
        "Service": "review service master data and process setup in the affected area",
        "Jobs": "review job/project master data and process setup in the affected area",
        "HR": "review HR master data and related setup in the affected area",
        "System": "review the affected records and the underlying Business Central setup",
    }.get(area, "review the affected records and the underlying Business Central setup")
    return f'Prioritize “{title}”: {area_action}.'


def _priority_key(issue: ScanIssueRecord) -> tuple[float, int, int, str]:
    """Match Full Assessment business priority without exposing its sensitive inputs."""
    severity = normalize_severity(issue.severity)
    return (
        -_safe_float(issue.estimated_impact_eur),
        SEVERITY_WEIGHT[severity],
        -_safe_int(issue.affected_count),
        str(issue.code or ""),
    )


def select_quick_findings(db: Session, *, scan_id: str, language: str) -> list[QuickFinding]:
    """Return at most five Quick-safe findings for a scan.

    Exact modeled impact, issue codes, recommendation previews, root-cause data
    and record detail are used neither as output fields nor copied into the
    Quick contract. Modeled impact is used only as an internal ranking signal
    and converted to a safe non-monetary impact band for disclosure.
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
                severity=normalize_severity(issue.severity),
                affected_count=max(0, _safe_int(issue.affected_count)),
                risk_area=area,
                impact_band=quick_impact_band(issue.estimated_impact_eur, language),
                next_action=_next_action(issue, area, language),
            )
        )
    return findings
