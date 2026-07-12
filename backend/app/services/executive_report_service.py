from __future__ import annotations

import base64
import html
import logging
import math
import textwrap
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Scan, ScanIssueRecord, ScanRunStatus, Tenant
from app.schemas.report import (
    ExecutiveReport,
    ReportCategoryScore,
    ReportFinding,
    ReportKpi,
    ReportPriorityItem,
    ReportSeverityBucket,
)
from app.services.impact_service import normalize_stored_commercials
from app.services.localization_service import tenant_language


logger = logging.getLogger(__name__)


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

FREE_REPORT_MODULE_FALLBACKS = {
    "Inventory": 24,
    "Finance": 29,
    "Purchasing": 44,
    "Sales": 47,
    "Manufacturing": 61,
    "CRM": 75,
    "System": 79,
}
FREE_REPORT_MODULE_ORDER = ["Inventory", "Finance", "Purchasing", "Sales", "Manufacturing", "CRM", "System"]
FREE_REPORT_CHECKS_TOTAL = 165
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
FREE_REPORT_TEMPLATE = "executive_report.html"
FREE_REPORT_CSS = Path(__file__).resolve().parent.parent / "static" / "reports" / "executive-free-report.css"
FREE_REPORT_LOGO = Path(__file__).resolve().parent.parent / "static" / "img" / "bcsentinel-report-logo.png"
FREE_REPORT_FONT = Path(__file__).resolve().parent.parent / "static" / "fonts" / "InterVariable.woff2"
FREE_REPORT_FONT_STATIC = Path(__file__).resolve().parent.parent / "static" / "fonts" / "Inter-Regular.woff2"

MASTER_DATA_MODULES = {"CRM", "Purchasing", "Inventory", "Sales"}
FINANCIAL_CATEGORIES = {"Finance", "Sales", "Purchasing", "Inventory"}
SEVERITY_WEIGHT = {"critical": 0, "high": 1, "medium": 2, "low": 3}


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
    amount = round(_safe_float(value), 2)
    if language == "de":
        return f"{amount:,.2f} EUR".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"EUR {amount:,.2f}"


def _number(value: int, language: str = "en") -> str:
    text = f"{_safe_int(value):,}"
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


def scan_type_label(value: str | None, language: str = "de") -> str:
    raw = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    if language != "de":
        labels = {
            "manual": "Manual Scan",
            "manual_scan": "Manual Scan",
            "quick": "Manual Scan",
            "deep": "Manual Scan",
            "scheduled": "Scheduled Scan",
            "scheduled_scan": "Scheduled Scan",
            "monitoring": "Monitoring Scan",
            "monitoring_scan": "Monitoring Scan",
            "assessment": "Assessment",
            "data_health_score": "Data Quality Assessment",
        }
        return labels.get(raw, "Scan")
    labels = {
        "manual": "Manueller Scan",
        "manual_scan": "Manueller Scan",
        "quick": "Manueller Scan",
        "deep": "Manueller Scan",
        "scheduled": "Geplanter Scan",
        "scheduled_scan": "Geplanter Scan",
        "monitoring": "Monitoring-Scan",
        "monitoring_scan": "Monitoring-Scan",
        "assessment": "Assessment",
        "data_health_score": "Datenqualitätsbewertung",
    }
    return labels.get(raw, "Scan")


def environment_label(value: str | None, language: str = "de") -> str:
    text = str(value or "").strip()
    if not text or language != "de":
        return text
    labels = {
        "production": "Produktivumgebung",
        "prod": "Produktivumgebung",
        "sandbox": "Sandbox",
        "development": "Entwicklungsumgebung",
        "dev": "Entwicklungsumgebung",
        "test": "Testumgebung",
    }
    return labels.get(text.lower(), text)


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
        if category == "Finance":
            return "Priorisiere Abstimmung und Buchungs-Setup, um Reporting-Risiken zu reduzieren."
        if category == "Inventory":
            return "Bereinige Artikel- und Lager-Setup vor dem naechsten Planungs- oder Bewertungszyklus."
        if category == "CRM":
            return "Vervollstaendige Kundenstammdaten, bevor sie Abrechnung, Lieferung oder Service verzoegern."
        if category == "Purchasing":
            return "Vervollstaendige Lieferanten- und Einkaufs-Setup, um manuelle Nacharbeit zu reduzieren."
        return "Pruefe die betroffenen Datensaetze und schliesse die zugrunde liegende Business-Central-Setup-Luecke."
    if category == "Finance":
        return "Prioritize reconciliation and posting setup to reduce financial reporting risk."
    if category == "Inventory":
        return "Clean item and inventory setup before the next planning or costing cycle."
    if category == "CRM":
        return "Complete customer master data before it causes billing, delivery, or service delays."
    if category == "Purchasing":
        return "Complete vendor and purchasing setup to reduce manual rework."
    return "Review the affected records and close the underlying Business Central setup gap."


def _finding(rank: int, issue: ScanIssueRecord, language: str = "en") -> ReportFinding:
    severity = str(issue.severity or "low").lower()
    if severity not in SEVERITY_WEIGHT:
        severity = "low"
    return ReportFinding(
        rank=rank,
        code=issue.code,
        title=issue.title,
        category=_normalize_category(issue.category, issue.code),
        severity=severity,
        affected_count=max(0, _safe_int(issue.affected_count)),
        estimated_impact_eur=round(_safe_float(issue.estimated_impact_eur), 2),
        recommendation=_recommendation(issue, language),
    )


def _sorted_issues(issues: list[ScanIssueRecord]) -> list[ScanIssueRecord]:
    return sorted(
        issues,
        key=lambda issue: (
            -_safe_float(issue.estimated_impact_eur),
            SEVERITY_WEIGHT.get(str(issue.severity or "").lower(), 9),
            -_safe_int(issue.affected_count),
            issue.code,
        ),
    )


def _category_scores(scan: Scan, findings: list[ReportFinding], language: str = "en") -> list[ReportCategoryScore]:
    by_category: dict[str, dict[str, int]] = {}
    for finding in findings:
        bucket = by_category.setdefault(finding.category, {"issues": 0, "affected": 0})
        bucket["issues"] += 1
        bucket["affected"] += finding.affected_count

    rows = []
    attr_by_module = {name: attr for name, attr in MODULES}
    for name in FREE_REPORT_MODULE_ORDER:
        attr = attr_by_module[name]
        score = max(0, min(100, _safe_int(getattr(scan, attr, 100), 100)))
        bucket = by_category.get(name, {"issues": 0, "affected": 0})
        rows.append(
            ReportCategoryScore(
                name=name,
                score=score,
                status=score_status(score, language),
                issue_count=bucket["issues"],
                affected_count=bucket["affected"],
            )
        )
    return rows


def _severity_distribution(findings: list[ReportFinding], language: str = "en") -> list[ReportSeverityBucket]:
    labels = {
        "critical": "Kritisch" if language == "de" else "Critical",
        "high": "Hoch" if language == "de" else "High",
        "medium": "Mittel" if language == "de" else "Medium",
        "low": "Niedrig" if language == "de" else "Low",
    }
    counts = {key: 0 for key in labels}
    for finding in findings:
        key = finding.severity if finding.severity in counts else "low"
        counts[key] += 1

    total = sum(counts.values())
    return [
        ReportSeverityBucket(
            label=labels[key],
            key=key,
            count=counts[key],
            percentage=round((counts[key] / total) * 100, 1) if total else 0.0,
        )
        for key in ["critical", "high", "medium", "low"]
    ]


def _build_summary(scan: Scan, estimated_loss_eur: float, potential_saving_eur: float, critical_count: int, language: str = "en") -> str:
    score = _safe_int(scan.data_score)
    if language == "de":
        if critical_count > 0 or score < 75:
            return (
                f"Der aktuelle BCSentinel-Scan zeigt einen Data Health Score von {score}/100. "
                f"Das aktuelle Datenqualitaetsprofil erzeugt einen geschaetzten Jahresimpact von {_money(estimated_loss_eur, language)}. "
                "Management-Aufmerksamkeit wird empfohlen, weil die wichtigsten Findings in operativ relevanten Business-Central-Bereichen konzentriert sind."
            )
        return (
            f"Der aktuelle BCSentinel-Scan zeigt einen Data Health Score von {score}/100. "
            f"Die Datenqualitaet ist insgesamt stabil, aber der Scan zeigt weiterhin {_money(potential_saving_eur, language)} potenziellen jaehrlichen Verbesserungswert."
        )
    if critical_count > 0 or score < 75:
        return (
            f"The latest BCSentinel scan shows a Data Health Score of {score}/100. "
            f"The current data quality profile creates an estimated annual business impact of {_money(estimated_loss_eur, language)}. "
            f"Management attention is recommended because the highest-impact findings are concentrated in operationally relevant Business Central areas."
        )
    return (
        f"The latest BCSentinel scan shows a Data Health Score of {score}/100. "
        f"Data quality is broadly stable, but the scan still identifies {_money(potential_saving_eur, language)} in potential annual improvement value."
    )


def _priority_matrix(top_risks: list[ReportFinding], quick_wins: list[ReportFinding], language: str = "en") -> list[ReportPriorityItem]:
    first_risk = top_risks[0] if top_risks else None
    first_quick_win = quick_wins[0] if quick_wins else first_risk
    if language == "de":
        return [
            ReportPriorityItem(
                priority="P1",
                focus="Hoher Impact / niedriger Aufwand",
                impact="Sofortiger operativer Nutzen",
                effort="Niedrig",
                recommendation=first_quick_win.recommendation if first_quick_win else "Starte mit den groessten Stammdatenluecken.",
            ),
            ReportPriorityItem(
                priority="P2",
                focus="Hoher Impact / hoeherer Aufwand",
                impact="Spuerbare Risikoreduktion",
                effort="Mittel",
                recommendation=first_risk.recommendation if first_risk else "Benenne Verantwortliche fuer Finance, Lager und Kundenstammdaten.",
            ),
            ReportPriorityItem(
                priority="P3",
                focus="Governance und Praevention",
                impact="Nachhaltige Score-Verbesserung",
                effort="Mittel",
                recommendation="Definiere wiederkehrende Data-Quality-Verantwortung und wiederhole BCSentinel nach der Bereinigung.",
            ),
        ]
    return [
        ReportPriorityItem(
            priority="P1",
            focus="High impact / low effort",
            impact="Immediate operational value",
            effort="Low",
            recommendation=first_quick_win.recommendation if first_quick_win else "Start with the largest affected master-data gaps.",
        ),
        ReportPriorityItem(
            priority="P2",
            focus="High impact / higher effort",
            impact="Material risk reduction",
            effort="Medium",
            recommendation=first_risk.recommendation if first_risk else "Assign owners for finance, inventory, and customer data remediation.",
        ),
        ReportPriorityItem(
            priority="P3",
            focus="Governance and prevention",
            impact="Sustained score improvement",
            effort="Medium",
            recommendation="Define recurring data quality ownership and rerun BCSentinel after remediation.",
        ),
    ]


def build_executive_report(db: Session, tenant: Tenant, scan_id: str) -> ExecutiveReport:
    language = tenant_language(tenant)
    scan = db.scalar(select(Scan).where(Scan.scan_id == scan_id))
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found.")
    if scan.tenant_id != tenant.tenant_id:
        raise HTTPException(status_code=403, detail="Scan does not belong to authenticated tenant.")

    issues = db.scalars(select(ScanIssueRecord).where(ScanIssueRecord.scan_id == scan.scan_id)).all()
    scan_run = db.scalar(select(ScanRunStatus).where(ScanRunStatus.run_id == scan.scan_id))
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
    critical = [finding for finding in findings if finding.severity in {"critical", "high"}]
    quick_wins = [
        finding
        for finding in findings
        if finding.severity in {"low", "medium"} and finding.affected_count > 0
    ][:5]
    financial = [finding for finding in findings if finding.category in FINANCIAL_CATEGORIES][:8]
    category_scores = _category_scores(scan, findings, language)
    master_data = [row for row in category_scores if row.name in MASTER_DATA_MODULES]

    if language == "de":
        recommended_actions = [
            "Benenne je High-Impact-Finding-Kategorie eine verantwortliche Person.",
            "Loese die wichtigsten Quick Wins zuerst, um im naechsten Scan sichtbaren Fortschritt zu zeigen.",
            "Pruefe Finance-, Lager-, Kunden- und Lieferanten-Setup vor dem naechsten Reporting-Zyklus.",
            "Fuehre nach der Bereinigung einen Folgescan aus und vergleiche Score, betroffene Datensaetze und geschaetzten Impact.",
        ]
        next_steps = [
            "Besprich diesen Report im naechsten Management- oder Steering-Termin.",
            "Bestaetige Owner und Faelligkeit fuer jedes P1-Element.",
            "Starte mit den Top-10-Findings und validiere Korrekturen direkt in Business Central.",
            "Fuehre einen Folgescan aus und teile den Delta-Report intern.",
        ]
    else:
        recommended_actions = [
            "Assign one accountable owner per high-impact finding category.",
            "Resolve the top quick wins first to show visible progress in the next scan.",
            "Review finance, inventory, customer, and vendor setup before the next reporting cycle.",
            "Rerun BCSentinel after remediation and compare score, affected records, and estimated impact.",
        ]
        next_steps = [
            "Review this report in the next management or steering meeting.",
            "Confirm the remediation owner and due date for each P1 item.",
            "Start with the top 10 findings and validate fixes directly in Business Central.",
            "Run a follow-up scan and share the delta report internally.",
        ]

    return ExecutiveReport(
        report_id=f"exec-{scan.scan_id}",
        tenant_id=tenant.tenant_id,
        language=language,
        scan_id=scan.scan_id,
        scan_type=scan_type_label(scan.scan_type, language),
        generated_at_utc=datetime.now(timezone.utc),
        scan_generated_at_utc=scan.generated_at_utc,
        company_label=(scan_run.company_name or "") if scan_run else "",
        environment_label=environment_label(
            (scan_run.environment_name or tenant.environment_name or "") if scan_run else (tenant.environment_name or ""),
            language,
        ),
        app_version=str(tenant.app_version or "").strip(),
        executive_summary=_build_summary(scan, estimated_loss, potential_saving, len(critical), language),
        data_health_score=max(0, min(100, _safe_int(scan.data_score))),
        score_status=score_status(_safe_int(scan.data_score), language),
        total_records=max(0, _safe_int(scan.total_records)),
        checks_count=max(0, _safe_int(scan.checks_count)),
        checks_total=max(FREE_REPORT_CHECKS_TOTAL, _safe_int(scan.checks_count)),
        issues_count=max(0, _safe_int(scan.issues_count)),
        affected_records=max(0, affected_records),
        estimated_loss_eur=estimated_loss,
        potential_saving_eur=potential_saving,
        estimated_premium_price_monthly=float(commercials["estimated_premium_price_monthly"]),
        roi_eur=float(commercials["roi_eur"]),
        headline=scan.summary_headline,
        rating=scan.summary_rating,
        kpis=[
            ReportKpi(label="Data Health Score", value=f"{_safe_int(scan.data_score)}/100", note=score_status(_safe_int(scan.data_score), language)),
            ReportKpi(label="Geschaetzter Business Impact" if language == "de" else "Estimated Business Impact", value=_money(estimated_loss, language), note="Jahreswert" if language == "de" else "Annualized estimate"),
            ReportKpi(label="Potenzielle Einsparung" if language == "de" else "Potential Saving", value=_money(potential_saving, language), note="Realisierbares Verbesserungspotenzial" if language == "de" else "Recoverable improvement potential"),
            ReportKpi(label="Betroffene Datensaetze" if language == "de" else "Affected Records", value=_number(affected_records, language), note=f"Ueber {_safe_int(scan.issues_count)} Findings" if language == "de" else f"Across {_safe_int(scan.issues_count)} findings"),
        ],
        top_risks=findings[:10],
        quick_wins=quick_wins,
        critical_findings=critical[:10],
        data_quality=category_scores,
        severity_distribution=_severity_distribution(findings, language),
        master_data_quality=master_data,
        financial_risks=financial,
        recommended_actions=recommended_actions,
        priority_matrix=_priority_matrix(findings[:10], quick_wins, language),
        next_steps=next_steps,
    )


def render_executive_report_html(report: ExecutiveReport, *, inline_css: bool = False) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(("html", "xml")),
    )
    logo_data = ""
    if FREE_REPORT_LOGO.exists():
        logo_data = "data:image/png;base64," + base64.b64encode(FREE_REPORT_LOGO.read_bytes()).decode("ascii")
    rendered = env.get_template(FREE_REPORT_TEMPLATE).render(
        report=report,
        logo_data=logo_data,
        money=lambda value: _money(value, "de"),
        number=lambda value: _number(value, "de"),
    )
    if not inline_css:
        return rendered

    css = FREE_REPORT_CSS.read_text(encoding="utf-8")
    if FREE_REPORT_FONT.exists():
        font_data = "data:font/woff2;base64," + base64.b64encode(FREE_REPORT_FONT.read_bytes()).decode("ascii")
        css = css.replace("/static/fonts/InterVariable.woff2", font_data)
    if FREE_REPORT_FONT_STATIC.exists():
        static_font_data = "data:font/woff2;base64," + base64.b64encode(FREE_REPORT_FONT_STATIC.read_bytes()).decode("ascii")
        css = css.replace("/static/fonts/Inter-Regular.woff2", static_font_data)
    stylesheet_link = '<link rel="stylesheet" href="/static/reports/executive-free-report.css">'
    return rendered.replace(stylesheet_link, f"<style>\n{css}\n</style>")


def render_executive_report_pdf(report: ExecutiveReport) -> bytes:
    try:
        return _render_executive_report_html_pdf(report)
    except Exception:
        logger.exception(
            "HTML-to-PDF renderer unavailable; using emergency text fallback.",
            extra={"scan_id": report.scan_id, "report_id": report.report_id},
        )
        return _render_executive_report_pdf_fallback(report)


def _render_executive_report_html_pdf(report: ExecutiveReport) -> bytes:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright is not installed.") from exc

    document = render_executive_report_html(report, inline_css=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 794, "height": 1123}, device_scale_factor=1)
            page.set_content(document, wait_until="load")
            page.evaluate("document.fonts.ready")
            return page.pdf(
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
        finally:
            browser.close()


def _render_executive_report_pdf_fallback(report: ExecutiveReport) -> bytes:
    language = getattr(report, "language", "en")
    lines = [
        "BCSentinel Executive Report (Free)",
        "HTML-to-PDF renderer unavailable; using emergency Free Report text fallback.",
        f"Scan: {report.scan_id}",
        f"Environment: {report.environment_label}",
        f"Generated: {report.generated_at_utc.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "Executive Summary" if language == "en" else "Management-Zusammenfassung",
        report.executive_summary,
        "",
        f"Data Health Score: {report.data_health_score}/100 ({report.score_status})",
        f"{'Business Impact' if language == 'en' else 'Business Impact'}: {_money(report.estimated_loss_eur, language)}",
        f"{'Potential Saving' if language == 'en' else 'Potenzielle Einsparung'}: {_money(report.potential_saving_eur, language)}",
        f"{'Affected Records' if language == 'en' else 'Betroffene Datensaetze'}: {_number(report.affected_records, language)}",
        f"{'Checks' if language == 'en' else 'Pruefungen'}: {_number(report.checks_count, language)} / {_number(report.checks_total, language)}",
        "",
        "Free Report Scope" if language == "en" else "Free-Report-Umfang",
        (
            "This Free Report contains a management summary only. Detailed findings, affected records, "
            "and concrete recommendations are part of Full Analysis or Monitoring."
            if language == "en"
            else "Dieser Free-Report enthaelt nur eine Management-Zusammenfassung. Detailanalysen, betroffene Datensaetze und konkrete Handlungsempfehlungen sind Bestandteil von Full Analysis oder Monitoring."
        ),
    ]
    lines.extend(["", "Recommended Next Steps" if language == "en" else "Empfohlene naechste Schritte"])
    if language == "en":
        lines.extend(
            [
                "- Plan an upgrade to Full Analysis or Monitoring for detailed insights.",
                "- Review trends and alerts continuously with Monitoring.",
                "- Use the aggregated score, module overview, and severity distribution to align next steps.",
            ]
        )
    else:
        lines.extend(
            [
                "- Upgrade zu Full Analysis oder Monitoring fuer vollstaendige Einblicke planen.",
                "- Trends und Alerts mit Monitoring kontinuierlich verfolgen.",
                "- Aggregierten Score, Moduluebersicht und Severity-Verteilung fuer die naechsten Schritte nutzen.",
            ]
        )
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

    fixed_objects = []
    for content in objects:
        fixed_objects.append(content.replace(b"/Parent 0 0 R", b"/Parent " + str(pages_obj).encode("ascii") + b" 0 R"))

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
