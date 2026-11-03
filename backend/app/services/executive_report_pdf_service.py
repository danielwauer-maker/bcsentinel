from __future__ import annotations

import textwrap
from io import BytesIO

from app.schemas.report import ExecutiveReport

PAGE_W = 595
PAGE_H = 842
NAVY = (20 / 255, 33 / 255, 61 / 255)
ORANGE = (255 / 255, 146 / 255, 31 / 255)
BLUE = (36 / 255, 107 / 255, 253 / 255)
INK = (23 / 255, 32 / 255, 51 / 255)
MUTED = (102 / 255, 112 / 255, 133 / 255)
LIGHT = (247 / 255, 249 / 255, 252 / 255)
LINE = (217 / 255, 222 / 255, 232 / 255)


def _money(value: float, language: str) -> str:
    value = float(value or 0.0)
    if language == "de":
        return f"{value:,.2f} EUR".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"EUR {value:,.2f}"


def _number(value: int, language: str) -> str:
    text = f"{max(0, int(value or 0)):,}"
    return text.replace(",", ".") if language == "de" else text


def _pdf_escape(value: str) -> str:
    return (
        str(value or "")
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .encode("latin-1", errors="replace")
        .decode("latin-1")
    )


def _text_commands(
    text: str,
    *,
    x: float,
    y: float,
    size: float = 10,
    bold: bool = False,
    color: tuple[float, float, float] = INK,
) -> list[str]:
    font = "F2" if bold else "F1"
    r, g, b = color
    return [
        "BT",
        f"/{font} {size:.1f} Tf",
        f"{r:.4f} {g:.4f} {b:.4f} rg",
        f"{x:.1f} {y:.1f} Td",
        f"({_pdf_escape(text)}) Tj",
        "ET",
    ]


def _wrap(value: str, width: int) -> list[str]:
    return textwrap.wrap(
        str(value or ""),
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [""]


def _rect(
    x: float,
    y: float,
    w: float,
    h: float,
    fill: tuple[float, float, float],
    stroke=None,
) -> list[str]:
    fr, fg, fb = fill
    result = [f"{fr:.4f} {fg:.4f} {fb:.4f} rg"]
    if stroke:
        sr, sg, sb = stroke
        result.extend([f"{sr:.4f} {sg:.4f} {sb:.4f} RG", f"{x} {y} {w} {h} re B"])
    else:
        result.append(f"{x} {y} {w} {h} re f")
    return result


def _report_title(report: ExecutiveReport) -> str:
    if report.report_variant == "assessment":
        return "Full Assessment Report"
    if report.report_variant == "monitoring":
        return "Monitoring Report"
    return "Executive Management Report"


def _page_header(report: ExecutiveReport, page_number: int) -> list[str]:
    commands = _rect(0, PAGE_H - 116, PAGE_W, 116, NAVY)
    commands += _rect(0, PAGE_H - 122, PAGE_W, 6, ORANGE)
    commands += _text_commands("BCSentinel", x=42, y=PAGE_H - 51, size=20, bold=True, color=(1, 1, 1))
    commands += _text_commands(
        _report_title(report),
        x=42,
        y=PAGE_H - 76,
        size=11,
        color=(0.88, 0.91, 0.96),
    )
    commands += _text_commands(
        f"Scan {report.scan_id}", x=42, y=PAGE_H - 98, size=8.5, color=(0.75, 0.81, 0.90)
    )
    commands += _text_commands(str(page_number), x=536, y=PAGE_H - 96, size=9, bold=True, color=(1, 1, 1))
    return commands


def _kpi_card(label: str, value: str, x: float, y: float, w: float = 164, h: float = 72) -> list[str]:
    commands = _rect(x, y, w, h, LIGHT, LINE)
    commands += _text_commands(label.upper(), x=x + 12, y=y + h - 19, size=7.5, bold=True, color=MUTED)
    commands += _text_commands(value, x=x + 12, y=y + 22, size=14, bold=True, color=INK)
    return commands


def _section_title(text: str, *, y: float) -> list[str]:
    return _text_commands(text, x=42, y=y, size=16, bold=True, color=NAVY)


def _build_summary_page(report: ExecutiveReport) -> list[str]:
    language = report.language
    page = _page_header(report, 1)
    page += _section_title("Executive Summary" if language == "en" else "Management-Zusammenfassung", y=688)
    y = 662
    for line in _wrap(report.executive_summary, 90)[:6]:
        page += _text_commands(line, x=42, y=y, size=9.5)
        y -= 14
    y -= 10
    page += _kpi_card("Data Health Score", f"{report.data_health_score}/100", 42, y - 72)
    page += _kpi_card("Business Impact", _money(report.estimated_loss_eur, language), 216, y - 72)
    page += _kpi_card("Potential Saving", _money(report.potential_saving_eur, language), 390, y - 72)
    y -= 106
    page += _section_title("Top Risks" if language == "en" else "Top-Risiken", y=y)
    y -= 24
    for finding in report.top_risks[:6]:
        page += _text_commands(f"{finding.rank}. {finding.title}", x=48, y=y, size=9, bold=True)
        y -= 13
        page += _text_commands(
            f"{finding.category} · {finding.severity.upper()} · {_number(finding.affected_count, language)} · {_money(finding.estimated_impact_eur, language)}",
            x=48,
            y=y,
            size=8,
            color=MUTED,
        )
        y -= 19
        if y < 94:
            break
    return page


def _build_scope_page(report: ExecutiveReport, page_number: int) -> list[str]:
    language = report.language
    page = _page_header(report, page_number)
    page += _section_title("Scan Scope & Coverage" if language == "en" else "Scan-Scope & Abdeckung", y=688)
    y = 653
    scope_rows = [
        ("Records analyzed" if language == "en" else "Analysierte Datensätze", _number(report.total_records, language)),
        ("Checks executed" if language == "en" else "Ausgeführte Checks", _number(report.checks_count, language)),
        ("Findings", _number(report.issues_count, language)),
        ("Affected records" if language == "en" else "Betroffene Datensätze", _number(report.affected_records, language)),
    ]
    for index, (label, value) in enumerate(scope_rows):
        x = 42 + (index % 2) * 260
        yy = y - (index // 2) * 62
        page += _rect(x, yy - 42, 246, 50, LIGHT, LINE)
        page += _text_commands(label, x=x + 12, y=yy - 11, size=7.7, bold=True, color=MUTED)
        page += _text_commands(value, x=x + 12, y=yy - 31, size=13, bold=True)
    y -= 135
    scope_note = (
        "Supported Microsoft Dynamics 365 Business Central standard areas in the confirmed scan scope are assessed. Third-party extensions and customer-specific business logic are excluded unless explicitly supported."
        if language == "en"
        else "Bewertet werden unterstützte Microsoft-Dynamics-365-Business-Central-Standardbereiche des bestätigten Scan-Scopes. Drittanbieter-Extensions und kundenspezifische Geschäftslogik sind ausgeschlossen, sofern sie nicht ausdrücklich unterstützt werden."
    )
    for line in _wrap(scope_note, 92):
        page += _text_commands(line, x=42, y=y, size=8.2, color=MUTED)
        y -= 12
    y -= 16
    page += _section_title("Business Area Impact" if language == "en" else "Business Impact nach Geschäftsbereich", y=y)
    y -= 23
    for item in report.business_area_impact[:8]:
        text = (
            f"{item.name}: {item.score}/100 · {item.issue_count} findings · {_number(item.affected_count, language)} affected · {_money(item.estimated_impact_eur, language)} · {item.impact_share_percent:.1f}%"
        )
        page += _text_commands(text, x=48, y=y, size=8.2)
        y -= 18
        if y < 250:
            break
    y -= 8
    page += _section_title("Priority Sequence" if language == "en" else "Prioritätsreihenfolge", y=y)
    y -= 25
    for item in report.priority_matrix:
        page += _text_commands(f"{item.priority} · {item.focus}", x=48, y=y, size=9, bold=True, color=BLUE)
        y -= 13
        for line in _wrap(f"{item.impact} · {item.recommendation}", 88)[:2]:
            page += _text_commands(line, x=48, y=y, size=8, color=MUTED)
            y -= 12
        y -= 7
        if y < 90:
            break
    return page


def _build_findings_pages(report: ExecutiveReport, start_page_number: int) -> list[list[str]]:
    language = report.language
    pages: list[list[str]] = []
    findings = list(report.all_findings)
    if not findings:
        page = _page_header(report, start_page_number)
        page += _section_title("Detailed Findings" if language == "en" else "Detaillierte Findings", y=688)
        page += _text_commands(
            "No findings in the confirmed assessment scope." if language == "en" else "Keine Findings im bestätigten Assessment-Scope.",
            x=42,
            y=650,
            size=9,
            color=MUTED,
        )
        return [page]

    page_number = start_page_number
    page = _page_header(report, page_number)
    page += _section_title("Detailed Findings" if language == "en" else "Detaillierte Findings", y=688)
    y = 653
    for finding in findings:
        rec_lines = _wrap(finding.recommendation, 84)[:3]
        needed = 62 + max(0, len(rec_lines) - 1) * 11
        if y - needed < 82:
            pages.append(page)
            page_number += 1
            page = _page_header(report, page_number)
            page += _section_title("Detailed Findings" if language == "en" else "Detaillierte Findings", y=688)
            y = 653
        page += _rect(42, y - needed + 8, 512, needed - 2, LIGHT, LINE)
        page += _text_commands(f"{finding.rank}. {finding.title}", x=54, y=y - 13, size=9.2, bold=True)
        page += _text_commands(
            f"{finding.code} · {finding.category} · {finding.severity.upper()} · {_number(finding.affected_count, language)} · {_money(finding.estimated_impact_eur, language)}",
            x=54,
            y=y - 29,
            size=7.8,
            color=MUTED,
        )
        yy = y - 44
        for line in rec_lines:
            page += _text_commands(line, x=54, y=yy, size=8.1)
            yy -= 11
        y -= needed + 10
    pages.append(page)
    return pages


def _build_actions_methodology_page(report: ExecutiveReport, page_number: int) -> list[str]:
    language = report.language
    page = _page_header(report, page_number)
    page += _section_title("Remediation Roadmap" if language == "en" else "Bereinigungs-Roadmap", y=688)
    y = 655
    for index, action in enumerate(report.recommended_actions, start=1):
        for line_index, line in enumerate(_wrap(action, 86)):
            prefix = f"{index}. " if line_index == 0 else "   "
            page += _text_commands(prefix + line, x=48, y=y, size=8.7)
            y -= 13
        y -= 4
    y -= 8
    page += _section_title("Next Steps" if language == "en" else "Nächste Schritte", y=y)
    y -= 25
    for index, step in enumerate(report.next_steps, start=1):
        for line_index, line in enumerate(_wrap(step, 86)):
            prefix = f"{index}. " if line_index == 0 else "   "
            page += _text_commands(prefix + line, x=48, y=y, size=8.7)
            y -= 13
        y -= 4
    if report.validation_baseline_eligible:
        y -= 4
        page += _rect(42, y - 48, 512, 48, (1.0, 0.97, 0.90), LINE)
        page += _text_commands(
            "Validation baseline established" if language == "en" else "Validation-Baseline festgelegt",
            x=54,
            y=y - 18,
            size=9.5,
            bold=True,
            color=NAVY,
        )
        page += _text_commands(f"Scan {report.validation_baseline_scan_id}", x=54, y=y - 34, size=8, color=MUTED)
        y -= 64
    y -= 6
    page += _section_title("Methodology & Limitations" if language == "en" else "Methodik & Limitierungen", y=y)
    y -= 24
    methodology = (
        "Business-impact and potential-saving values are modeled decision-support estimates derived from scan findings and configured impact assumptions. They are not accounting-confirmed losses, guaranteed savings, realized savings or ROI. Recommendations describe remediation direction; unsupported root causes are not inferred."
        if language == "en"
        else "Business-Impact- und Einsparpotenzial-Werte sind modellierte Entscheidungsunterstützung auf Basis der Scan-Findings und konfigurierten Impact-Annahmen. Sie sind keine buchhalterisch bestätigten Verluste, garantierten Einsparungen, realisierten Einsparungen oder ROI-Werte. Empfehlungen beschreiben die Bereinigungsrichtung; nicht belegte Root Causes werden nicht abgeleitet."
    )
    for line in _wrap(methodology, 92):
        page += _text_commands(line, x=42, y=y, size=8.1, color=MUTED)
        y -= 12
    page += _text_commands(
        f"{report.contract_version} · {report.financial_methodology} · Clean Data – Higher Impact",
        x=42,
        y=max(62, y - 12),
        size=8,
        bold=True,
        color=NAVY,
    )
    return page


def _build_exception_pages(report: ExecutiveReport, start_page_number: int) -> list[list[str]]:
    if not report.applied_exceptions:
        return []
    language = report.language
    pages: list[list[str]] = []
    page_number = start_page_number
    page = _page_header(report, page_number)
    page += _section_title("Applied Exceptions" if language == "en" else "Angewendete Ausnahmen", y=688)
    y = 653
    for item in report.applied_exceptions:
        reason_lines = _wrap(item.reason, 84)[:3]
        needed = 50 + max(0, len(reason_lines) - 1) * 11
        if y - needed < 82:
            pages.append(page)
            page_number += 1
            page = _page_header(report, page_number)
            page += _section_title("Applied Exceptions" if language == "en" else "Angewendete Ausnahmen", y=688)
            y = 653
        title = f"{item.issue_code} · {item.record_caption or item.record_no or '-'}"
        page += _text_commands(title, x=48, y=y, size=9, bold=True)
        y -= 14
        for line in reason_lines:
            page += _text_commands(line, x=48, y=y, size=8, color=MUTED)
            y -= 11
        y -= 14
    pages.append(page)
    return pages


def _build_pages(report: ExecutiveReport) -> list[list[str]]:
    pages: list[list[str]] = [_build_summary_page(report)]
    pages.append(_build_scope_page(report, 2))
    finding_pages = _build_findings_pages(report, len(pages) + 1)
    pages.extend(finding_pages)
    pages.append(_build_actions_methodology_page(report, len(pages) + 1))
    pages.extend(_build_exception_pages(report, len(pages) + 1))
    return pages


def render_executive_report_pdf(report: ExecutiveReport) -> bytes:
    page_streams = _build_pages(report)
    objects: list[bytes] = []

    def add_object(content: bytes) -> int:
        objects.append(content)
        return len(objects)

    regular_font = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    bold_font = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    page_refs: list[int] = []

    for commands in page_streams:
        stream = "\n".join(commands).encode("latin-1", errors="replace")
        content_obj = add_object(
            b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream"
        )
        page_obj = add_object(
            b"<< /Type /Page /Parent 0 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 "
            + str(regular_font).encode("ascii")
            + b" 0 R /F2 "
            + str(bold_font).encode("ascii")
            + b" 0 R >> >> /Contents "
            + str(content_obj).encode("ascii")
            + b" 0 R >>"
        )
        page_refs.append(page_obj)

    kids = b" ".join(str(ref).encode("ascii") + b" 0 R" for ref in page_refs)
    pages_obj = add_object(
        b"<< /Type /Pages /Kids [" + kids + b"] /Count " + str(len(page_refs)).encode("ascii") + b" >>"
    )
    catalog_obj = add_object(b"<< /Type /Catalog /Pages " + str(pages_obj).encode("ascii") + b" 0 R >>")
    fixed = [
        content.replace(b"/Parent 0 0 R", b"/Parent " + str(pages_obj).encode("ascii") + b" 0 R")
        for content in objects
    ]

    buffer = BytesIO()
    buffer.write(b"%PDF-1.4\n%BCSentinel\n")
    offsets = [0]
    for index, content in enumerate(fixed, start=1):
        offsets.append(buffer.tell())
        buffer.write(f"{index} 0 obj\n".encode("ascii"))
        buffer.write(content)
        buffer.write(b"\nendobj\n")
    xref = buffer.tell()
    buffer.write(f"xref\n0 {len(fixed) + 1}\n".encode("ascii"))
    buffer.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        buffer.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    buffer.write(
        f"trailer\n<< /Size {len(fixed) + 1} /Root {catalog_obj} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    return buffer.getvalue()
