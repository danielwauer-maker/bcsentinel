from __future__ import annotations

import html
import textwrap
from datetime import datetime, timezone
from io import BytesIO

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Scan, ScanIssueRecord, Tenant, TenantScanCredit
from app.schemas.report import (
    ExecutiveReport,
    ReportCategoryImpact,
    ReportCategoryScore,
    ReportFinding,
    ReportKpi,
    ReportPriorityItem,
)
from app.services.impact_service import normalize_stored_commercials
from app.services.localization_service import tenant_language
from app.services.product_license_service import PRODUCT_VALIDATION_CHECK
from app.services.quick_finding_selection_service import normalize_severity


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

MASTER_DATA_MODULES = {"CRM", "Purchasing", "Inventory", "Sales"}
FINANCIAL_CATEGORIES = {"Finance", "Sales", "Purchasing", "Inventory"}
SEVERITY_WEIGHT = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
SEVERITY_RANK = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


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


def _money(value: float, language: str = "en") -> str:
    amount = round(max(0.0, _safe_float(value)), 2)
    if language == "de":
        return f"{amount:,.2f} EUR".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"EUR {amount:,.2f}"


def _number(value: int, language: str = "en") -> str:
    text = f"{max(0, _safe_int(value)):,}"
    return text.replace(",", ".") if language == "de" else text


def score_status(score: int, language: str = "en") -> str:
    if score < 60:
        return "Kritisch" if language == "de" else "Critical"
    if score < 75:
        return "Braucht Aufmerksamkeit" if language == "de" else "Needs attention"
    if score < 85:
        return "Stabil mit Risiken" if language == "de" else "Stable with risks"
    if score < 95:
        return "Gut" if language == "de" else "Good"
    return "Exzellent" if language == "de" else "Excellent"


def _normalize_category(category: str | None, code: str) -> str:
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


def _recommendation(issue: ScanIssueRecord, language: str = "en") -> str:
    preview = str(issue.recommendation_preview or "").strip()
    if preview:
        return preview
    category = _normalize_category(issue.category, issue.code)
    if language == "de":
        return {
            "Finance": "Buchungs- und Abstimmungssetup sowie die betroffenen Datensätze fachlich prüfen.",
            "Inventory": "Artikel-, Lager- und Bewertungsdaten im betroffenen Bereich prüfen und bereinigen.",
            "CRM": "Kunden- und Kontaktstammdaten im betroffenen Bereich vervollständigen und bereinigen.",
            "Purchasing": "Lieferanten- und Einkaufsstammdaten sowie das Prozesssetup prüfen.",
            "Sales": "Verkaufsstammdaten und Prozesssetup für die betroffenen Datensätze prüfen.",
        }.get(category, "Betroffene Datensätze und das zugehörige Business-Central-Setup fachlich prüfen.")
    return {
        "Finance": "Review posting and reconciliation setup together with the affected records.",
        "Inventory": "Review and remediate item, inventory and valuation data in the affected area.",
        "CRM": "Complete and remediate customer and contact master data in the affected area.",
        "Purchasing": "Review vendor and purchasing master data together with process setup.",
        "Sales": "Review sales master data and process setup for the affected records.",
    }.get(category, "Review the affected records and the related Business Central setup.")


def _finding(rank: int, issue: ScanIssueRecord, language: str = "en") -> ReportFinding:
    return ReportFinding(
        rank=rank,
        code=issue.code,
        title=issue.title,
        category=_normalize_category(issue.category, issue.code),
        severity=normalize_severity(issue.severity),
        affected_count=max(0, _safe_int(issue.affected_count)),
        estimated_impact_eur=round(max(0.0, _safe_float(issue.estimated_impact_eur)), 2),
        recommendation=_recommendation(issue, language),
    )


def _sorted_issues(issues: list[ScanIssueRecord]) -> list[ScanIssueRecord]:
    return sorted(
        issues,
        key=lambda issue: (
            -max(0.0, _safe_float(issue.estimated_impact_eur)),
            SEVERITY_WEIGHT[normalize_severity(issue.severity)],
            -max(0, _safe_int(issue.affected_count)),
            str(issue.code or ""),
        ),
    )


def _category_scores(scan: Scan, findings: list[ReportFinding], language: str = "en") -> list[ReportCategoryScore]:
    by_category: dict[str, dict[str, int]] = {}
    for finding in findings:
        bucket = by_category.setdefault(finding.category, {"issues": 0, "affected": 0})
        bucket["issues"] += 1
        bucket["affected"] += finding.affected_count

    rows: list[ReportCategoryScore] = []
    for name, attr in MODULES:
        score = max(0, min(100, _safe_int(getattr(scan, attr, 100), 100)))
        bucket = by_category.get(name, {"issues": 0, "affected": 0})
        if score < 100 or bucket["issues"] > 0:
            rows.append(
                ReportCategoryScore(
                    name=name,
                    score=score,
                    status=score_status(score, language),
                    issue_count=bucket["issues"],
                    affected_count=bucket["affected"],
                )
            )
    return sorted(rows, key=lambda row: (row.score, -row.affected_count, row.name))


def _business_area_impact(scan: Scan, findings: list[ReportFinding]) -> list[ReportCategoryImpact]:
    score_by_area = {name: max(0, min(100, _safe_int(getattr(scan, attr, 100), 100))) for name, attr in MODULES}
    buckets: dict[str, dict[str, object]] = {}
    total_impact = sum(max(0.0, finding.estimated_impact_eur) for finding in findings)
    for finding in findings:
        bucket = buckets.setdefault(
            finding.category,
            {"issues": 0, "affected": 0, "impact": 0.0, "highest_severity": "info"},
        )
        bucket["issues"] = int(bucket["issues"]) + 1
        bucket["affected"] = int(bucket["affected"]) + finding.affected_count
        bucket["impact"] = float(bucket["impact"]) + max(0.0, finding.estimated_impact_eur)
        current = str(bucket["highest_severity"])
        if SEVERITY_RANK[finding.severity] > SEVERITY_RANK[current]:
            bucket["highest_severity"] = finding.severity

    rows: list[ReportCategoryImpact] = []
    for name, _ in MODULES:
        bucket = buckets.get(name)
        if bucket is None:
            continue
        impact = round(float(bucket["impact"]), 2)
        share = round((impact / total_impact) * 100.0, 1) if total_impact > 0 else 0.0
        rows.append(
            ReportCategoryImpact(
                name=name,
                score=score_by_area[name],
                issue_count=int(bucket["issues"]),
                affected_count=int(bucket["affected"]),
                estimated_impact_eur=impact,
                impact_share_percent=share,
                highest_severity=str(bucket["highest_severity"]),
            )
        )
    return sorted(rows, key=lambda row: (-row.estimated_impact_eur, row.score, row.name))


def _build_summary(
    scan: Scan,
    estimated_loss_eur: float,
    potential_saving_eur: float,
    critical_count: int,
    high_count: int,
    language: str = "en",
) -> str:
    score = max(0, min(100, _safe_int(scan.data_score)))
    if language == "de":
        return (
            f"Der Full Assessment Scan zeigt einen Data Health Score von {score}/100. "
            f"Der modellierte jährliche Business Impact beträgt {_money(estimated_loss_eur, language)}; "
            f"das modellierte Verbesserungspotenzial beträgt {_money(potential_saving_eur, language)}. "
            f"Im vollständigen Finding-Bestand liegen {critical_count} kritische und {high_count} hohe Findings vor."
        )
    return (
        f"The Full Assessment scan shows a Data Health Score of {score}/100. "
        f"Modeled annual business impact is {_money(estimated_loss_eur, language)} and modeled improvement potential is "
        f"{_money(potential_saving_eur, language)}. The complete finding set contains {critical_count} critical and "
        f"{high_count} high-severity findings."
    )


def _priority_matrix(findings: list[ReportFinding], language: str = "en") -> list[ReportPriorityItem]:
    groups: list[tuple[str, list[ReportFinding]]] = [
        (
            "P1",
            [f for f in findings if f.severity == "critical" or f.estimated_impact_eur >= 100_000],
        ),
        (
            "P2",
            [
                f
                for f in findings
                if f.severity == "high" or 25_000 <= f.estimated_impact_eur < 100_000
            ],
        ),
    ]
    used_codes = {f.code for _, rows in groups for f in rows}
    groups.append(("P3", [f for f in findings if f.code not in used_codes]))

    rows: list[ReportPriorityItem] = []
    for priority, grouped in groups:
        if not grouped:
            continue
        impact_total = round(sum(f.estimated_impact_eur for f in grouped), 2)
        first = grouped[0]
        if language == "de":
            focus = {
                "P1": "Kritische / sehr hohe Business-Priorität",
                "P2": "Hohe Business-Priorität",
                "P3": "Weitere priorisierte Bereinigung",
            }[priority]
            recommendation = first.recommendation
            impact = f"{len(grouped)} Findings · {_money(impact_total, language)} modellierter Impact"
        else:
            focus = {
                "P1": "Critical / very-high business priority",
                "P2": "High business priority",
                "P3": "Remaining prioritized remediation",
            }[priority]
            recommendation = first.recommendation
            impact = f"{len(grouped)} findings · {_money(impact_total, language)} modeled impact"
        rows.append(
            ReportPriorityItem(
                priority=priority,
                focus=focus,
                impact=impact,
                recommendation=recommendation,
                finding_codes=[f.code for f in grouped],
                effort=None,
            )
        )
    return rows


def _recommended_actions(findings: list[ReportFinding], language: str) -> list[str]:
    actions: list[str] = []
    seen: set[str] = set()
    for finding in findings:
        action = finding.recommendation.strip()
        if not action or action in seen:
            continue
        seen.add(action)
        actions.append(action)
        if len(actions) == 5:
            break
    if actions:
        return actions
    return [
        "Keine konkrete Bereinigungsmaßnahme erforderlich; Ergebnis fachlich verifizieren."
        if language == "de"
        else "No specific remediation action is required; verify the result with the business owner."
    ]


def _validation_baseline_eligible(db: Session, tenant: Tenant, scan: Scan) -> bool:
    validation_credit = db.scalar(
        select(TenantScanCredit).where(
            TenantScanCredit.tenant_id == tenant.tenant_id,
            TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
            TenantScanCredit.status == "consumed",
            TenantScanCredit.consumed_scan_id == scan.scan_id,
        )
    )
    return validation_credit is None


def build_executive_report(db: Session, tenant: Tenant, scan_id: str) -> ExecutiveReport:
    language = tenant_language(tenant)
    scan = db.scalar(select(Scan).where(Scan.scan_id == scan_id))
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found.")
    if scan.tenant_id != tenant.tenant_id:
        raise HTTPException(status_code=403, detail="Scan does not belong to authenticated tenant.")

    issues = db.scalars(select(ScanIssueRecord).where(ScanIssueRecord.scan_id == scan.scan_id)).all()
    findings = [_finding(index + 1, issue, language) for index, issue in enumerate(_sorted_issues(list(issues)))]
    affected_records = sum(finding.affected_count for finding in findings)

    commercials = normalize_stored_commercials(
        total_records=_safe_int(scan.total_records),
        estimated_loss_eur=_safe_float(scan.estimated_loss_eur),
        potential_saving_eur=_safe_float(scan.potential_saving_eur),
        estimated_premium_price_monthly=_safe_float(scan.estimated_premium_price_monthly),
    )
    estimated_loss = float(commercials["estimated_loss_eur"])
    potential_saving = float(commercials["potential_saving_eur"])

    critical = [finding for finding in findings if finding.severity == "critical"]
    high = [finding for finding in findings if finding.severity == "high"]
    # Compatibility-only projection; no priority or effort inference depends on it.
    quick_wins = [finding for finding in findings if finding.severity in {"medium", "low"} and finding.affected_count > 0][:5]
    financial = [finding for finding in findings if finding.category in FINANCIAL_CATEGORIES][:8]
    category_scores = _category_scores(scan, findings, language)
    master_data = [row for row in category_scores if row.name in MASTER_DATA_MODULES]
    area_impact = _business_area_impact(scan, findings)
    baseline_eligible = _validation_baseline_eligible(db, tenant, scan)

    if language == "de":
        next_steps = [
            "P1-Findings zuerst fachlich prüfen und die zugehörigen Empfehlungen umsetzen.",
            "Danach P2- und P3-Findings anhand der modellierten Business-Priorität bearbeiten.",
            "Nach der Bereinigung einen Validation Scan starten, um Score, Findings, betroffene Datensätze und modellierten Impact gegen diese Baseline zu vergleichen.",
        ]
    else:
        next_steps = [
            "Review P1 findings first and implement the associated recommendations.",
            "Then address P2 and P3 findings using modeled business priority.",
            "After remediation, run Validation to compare score, findings, affected records and modeled impact against this baseline.",
        ]

    return ExecutiveReport(
        report_id=f"exec-{scan.scan_id}",
        tenant_id=tenant.tenant_id,
        language=language,
        scan_id=scan.scan_id,
        generated_at_utc=datetime.now(timezone.utc),
        scan_generated_at_utc=scan.generated_at_utc,
        company_label=tenant.tenant_id,
        environment_label=tenant.environment_name,
        executive_summary=_build_summary(scan, estimated_loss, potential_saving, len(critical), len(high), language),
        data_health_score=max(0, min(100, _safe_int(scan.data_score))),
        score_status=score_status(_safe_int(scan.data_score), language),
        total_records=max(0, _safe_int(scan.total_records)),
        checks_count=max(0, _safe_int(scan.checks_count)),
        issues_count=max(0, _safe_int(scan.issues_count)),
        affected_records=max(0, affected_records),
        estimated_loss_eur=estimated_loss,
        potential_saving_eur=potential_saving,
        validation_baseline_eligible=baseline_eligible,
        validation_baseline_scan_id=scan.scan_id,
        headline=scan.summary_headline,
        rating=scan.summary_rating,
        kpis=[
            ReportKpi(
                label="Data Health Score",
                value=f"{max(0, min(100, _safe_int(scan.data_score)))}/100",
                note=score_status(_safe_int(scan.data_score), language),
            ),
            ReportKpi(
                label="Geschätzter Business Impact" if language == "de" else "Estimated Business Impact",
                value=_money(estimated_loss, language),
                note="Modellierter Jahreswert" if language == "de" else "Modeled annual value",
            ),
            ReportKpi(
                label="Potenzielle Einsparung" if language == "de" else "Potential Saving",
                value=_money(potential_saving, language),
                note="Modelliertes Verbesserungspotenzial" if language == "de" else "Modeled improvement potential",
            ),
            ReportKpi(
                label="Analysierte Datensätze" if language == "de" else "Records Analyzed",
                value=_number(scan.total_records, language),
                note=f"{_safe_int(scan.issues_count)} Findings",
            ),
        ],
        all_findings=findings,
        top_risks=findings[:10],
        quick_wins=quick_wins,
        critical_findings=critical,
        data_quality=category_scores,
        business_area_impact=area_impact,
        master_data_quality=master_data,
        financial_risks=financial,
        recommended_actions=_recommended_actions(findings, language),
        priority_matrix=_priority_matrix(findings, language),
        next_steps=next_steps,
    )


def render_executive_report_pdf(report: ExecutiveReport) -> bytes:
    language = getattr(report, "language", "en")
    lines = [
        "BCSentinel Full Assessment",
        f"Scan: {report.scan_id}",
        f"Environment: {report.environment_label}",
        f"Generated: {report.generated_at_utc.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "Executive Summary" if language == "en" else "Management-Zusammenfassung",
        report.executive_summary,
        "",
        f"Data Health Score: {report.data_health_score}/100 ({report.score_status})",
        f"Business Impact: {_money(report.estimated_loss_eur, language)}",
        f"{'Potential Saving' if language == 'en' else 'Potenzielle Einsparung'}: {_money(report.potential_saving_eur, language)}",
        f"{'Records analyzed' if language == 'en' else 'Analysierte Datensätze'}: {_number(report.total_records, language)}",
        "",
        "Top 10 Risks" if language == "en" else "Top-10-Risiken",
    ]
    for finding in report.top_risks:
        lines.append(
            f"{finding.rank}. {finding.title} | {finding.category} | {finding.severity.upper()} | "
            f"{_number(finding.affected_count, language)} {'records' if language == 'en' else 'Datensätze'} | "
            f"{_money(finding.estimated_impact_eur, language)}"
        )
    lines.extend(["", "Validation baseline", f"Baseline scan: {report.validation_baseline_scan_id}"])
    lines.extend(["", "Recommended Next Steps" if language == "en" else "Empfohlene nächste Schritte"])
    lines.extend(f"- {step}" for step in report.next_steps)
    return _simple_pdf(lines)


def _simple_pdf(lines: list[str]) -> bytes:
    wrapped: list[str] = []
    for line in lines:
        if not line:
            wrapped.append("")
            continue
        wrapped.extend(textwrap.wrap(line, width=92) or [""])

    pages = [wrapped[index : index + 44] for index in range(0, len(wrapped), 44)] or [[]]
    objects: list[bytes] = []

    def add_object(content: bytes) -> int:
        objects.append(content)
        return len(objects)

    font_obj = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    page_refs = []
    for page_lines in pages:
        stream_lines = ["BT", "/F1 10 Tf", "50 790 Td", "14 TL"]
        for index, line in enumerate(page_lines):
            safe = html.escape(line, quote=False).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            if index == 0:
                stream_lines.append(f"({safe}) Tj")
            else:
                stream_lines.append(f"T* ({safe}) Tj")
        stream_lines.append("ET")
        stream = "\n".join(stream_lines).encode("latin-1", errors="replace")
        content_obj = add_object(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")
        page_obj = add_object(
            b"<< /Type /Page /Parent 0 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 "
            + str(font_obj).encode("ascii")
            + b" 0 R >> >> /Contents "
            + str(content_obj).encode("ascii")
            + b" 0 R >>"
        )
        page_refs.append(page_obj)

    kids = b" ".join(str(ref).encode("ascii") + b" 0 R" for ref in page_refs)
    pages_obj = add_object(b"<< /Type /Pages /Kids [" + kids + b"] /Count " + str(len(page_refs)).encode("ascii") + b" >>")
    catalog_obj = add_object(b"<< /Type /Catalog /Pages " + str(pages_obj).encode("ascii") + b" 0 R >>")

    fixed_objects = [
        content.replace(b"/Parent 0 0 R", b"/Parent " + str(pages_obj).encode("ascii") + b" 0 R")
        for content in objects
    ]

    buffer = BytesIO()
    buffer.write(b"%PDF-1.4\n")
    offsets = [0]
    for index, content in enumerate(fixed_objects, start=1):
        offsets.append(buffer.tell())
        buffer.write(f"{index} 0 obj\n".encode("ascii"))
        buffer.write(content)
        buffer.write(b"\nendobj\n")
    xref = buffer.tell()
    buffer.write(f"xref\n0 {len(fixed_objects) + 1}\n".encode("ascii"))
    buffer.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        buffer.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    buffer.write(
        f"trailer\n<< /Size {len(fixed_objects) + 1} /Root {catalog_obj} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    return buffer.getvalue()
