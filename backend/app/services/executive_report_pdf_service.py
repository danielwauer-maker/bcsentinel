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


def _pdf_escape(value: str) -> str:
    return (
        str(value or "")
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .encode("latin-1", errors="replace")
        .decode("latin-1")
    )


def _text_commands(text: str, *, x: float, y: float, size: float = 10, bold: bool = False,
                   color: tuple[float, float, float] = INK) -> list[str]:
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
    return textwrap.wrap(str(value or ""), width=width, break_long_words=False, break_on_hyphens=False) or [""]


def _rect(x: float, y: float, w: float, h: float, fill: tuple[float, float, float], stroke=None) -> list[str]:
    fr, fg, fb = fill
    result = [f"{fr:.4f} {fg:.4f} {fb:.4f} rg"]
    if stroke:
        sr, sg, sb = stroke
        result.extend([f"{sr:.4f} {sg:.4f} {sb:.4f} RG", f"{x} {y} {w} {h} re B"])
    else:
        result.append(f"{x} {y} {w} {h} re f")
    return result


def _page_header(report: ExecutiveReport, page_number: int) -> list[str]:
    language = report.language
    commands = _rect(0, PAGE_H - 116, PAGE_W, 116, NAVY)
    commands += _rect(0, PAGE_H - 122, PAGE_W, 6, ORANGE)
    commands += _text_commands("BCSentinel", x=42, y=PAGE_H - 51, size=20, bold=True, color=(1, 1, 1))
    commands += _text_commands(
        "Executive Management Report" if language == "en" else "Executive Management Report",
        x=42, y=PAGE_H - 76, size=11, color=(0.88, 0.91, 0.96),
    )
    commands += _text_commands(f"Scan {report.scan_id}", x=42, y=PAGE_H - 98, size=8.5, color=(0.75, 0.81, 0.90))
    commands += _text_commands(f"{page_number}", x=536, y=PAGE_H - 96, size=9, bold=True, color=(1, 1, 1))
    return commands


def _kpi_card(label: str, value: str, x: float, y: float, w: float = 164, h: float = 72) -> list[str]:
    commands = _rect(x, y, w, h, LIGHT, LINE)
    commands += _text_commands(label.upper(), x=x + 12, y=y + h - 19, size=7.5, bold=True, color=MUTED)
    commands += _text_commands(value, x=x + 12, y=y + 22, size=14, bold=True, color=INK)
    return commands


def _build_pages(report: ExecutiveReport) -> list[list[str]]:
    language = report.language
    pages: list[list[str]] = []

    first = _page_header(report, 1)
    first += _text_commands(
        "Management Summary" if language == "en" else "Management-Zusammenfassung",
        x=42, y=688, size=17, bold=True, color=NAVY,
    )
    y = 662
    for line in _wrap(report.executive_summary, 90):
        first += _text_commands(line, x=42, y=y, size=9.5, color=INK)
        y -= 14
    y -= 10
    first += _kpi_card("Data Health Score", f"{report.data_health_score}/100", 42, y - 72)
    first += _kpi_card("Estimated Loss" if language == "en" else "Estimated Loss", _money(report.estimated_loss_eur, language), 216, y - 72)
    first += _kpi_card("Potential Saving" if language == "en" else "Potential Saving", _money(report.potential_saving_eur, language), 390, y - 72)
    y -= 105
    if report.exceptions_applied:
        first += _rect(42, y - 48, 512, 48, (1.0, 0.97, 0.90), LINE)
        first += _text_commands(
            f"{report.exception_count} scan-time exception(s) applied" if language == "en" else f"{report.exception_count} Scan-Ausnahme(n) angewendet",
            x=54, y=y - 18, size=10, bold=True, color=NAVY,
        )
        first += _text_commands(
            "Historical results use the immutable exception snapshot captured for this scan."
            if language == "en" else
            "Historische Ergebnisse verwenden den unveränderlichen Exception-Snapshot dieses Scans.",
            x=54, y=y - 35, size=8, color=MUTED,
        )
        y -= 66
    first += _text_commands("Top Risks" if language == "en" else "Top-Risiken", x=42, y=y, size=15, bold=True, color=NAVY)
    y -= 24
    for finding in report.top_risks[:6]:
        first += _text_commands(f"{finding.rank}. {finding.title}", x=48, y=y, size=9, bold=True, color=INK)
        y -= 13
        first += _text_commands(
            f"{finding.category} · {finding.severity.upper()} · {_money(finding.estimated_impact_eur, language)}",
            x=48, y=y, size=8, color=MUTED,
        )
        y -= 20
        if y < 90:
            break
    pages.append(first)

    second = _page_header(report, 2)
    y = 688
    second += _text_commands("Priority & Next Steps" if language == "en" else "Prioritäten & nächste Schritte", x=42, y=y, size=17, bold=True, color=NAVY)
    y -= 30
    for item in report.priority_matrix:
        second += _rect(42, y - 62, 512, 62, LIGHT, LINE)
        second += _text_commands(item.priority, x=54, y=y - 19, size=10, bold=True, color=BLUE)
        second += _text_commands(item.focus, x=92, y=y - 19, size=9.5, bold=True, color=INK)
        wrapped = _wrap(item.recommendation, 78)
        for idx, line in enumerate(wrapped[:2]):
            second += _text_commands(line, x=54, y=y - 38 - idx * 12, size=8, color=MUTED)
        y -= 76
    y -= 6
    second += _text_commands("Recommended Actions" if language == "en" else "Empfohlene Maßnahmen", x=42, y=y, size=14, bold=True, color=NAVY)
    y -= 22
    for index, action in enumerate(report.recommended_actions, start=1):
        for line_idx, line in enumerate(_wrap(action, 82)):
            prefix = f"{index}. " if line_idx == 0 else "   "
            second += _text_commands(prefix + line, x=48, y=y, size=8.7, color=INK)
            y -= 13
        y -= 4
    pages.append(second)

    if report.applied_exceptions:
        third = _page_header(report, 3)
        y = 688
        third += _text_commands("Applied Exceptions" if language == "en" else "Angewendete Ausnahmen", x=42, y=y, size=17, bold=True, color=NAVY)
        y -= 23
        third += _text_commands(
            "Snapshot captured at scan time; later BC exception changes do not rewrite this report."
            if language == "en" else
            "Snapshot zum Scan-Zeitpunkt; spätere BC-Änderungen verändern diesen Report nicht rückwirkend.",
            x=42, y=y, size=8.5, color=MUTED,
        )
        y -= 28
        for item in report.applied_exceptions:
            if y < 105:
                pages.append(third)
                third = _page_header(report, len(pages) + 1)
                y = 688
            title = f"{item.issue_code} · {item.record_caption or item.record_no or '-'}"
            third += _text_commands(title, x=48, y=y, size=9, bold=True, color=INK)
            y -= 13
            for line in _wrap(item.reason, 82)[:3]:
                third += _text_commands(line, x=48, y=y, size=8, color=MUTED)
                y -= 12
            y -= 10
        pages.append(third)

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
        content_obj = add_object(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")
        page_obj = add_object(
            b"<< /Type /Page /Parent 0 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 "
            + str(regular_font).encode("ascii") + b" 0 R /F2 " + str(bold_font).encode("ascii")
            + b" 0 R >> >> /Contents " + str(content_obj).encode("ascii") + b" 0 R >>"
        )
        page_refs.append(page_obj)

    kids = b" ".join(str(ref).encode("ascii") + b" 0 R" for ref in page_refs)
    pages_obj = add_object(b"<< /Type /Pages /Kids [" + kids + b"] /Count " + str(len(page_refs)).encode("ascii") + b" >>")
    catalog_obj = add_object(b"<< /Type /Catalog /Pages " + str(pages_obj).encode("ascii") + b" 0 R >>")
    fixed = [content.replace(b"/Parent 0 0 R", b"/Parent " + str(pages_obj).encode("ascii") + b" 0 R") for content in objects]

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
    buffer.write(f"trailer\n<< /Size {len(fixed) + 1} /Root {catalog_obj} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
    return buffer.getvalue()
