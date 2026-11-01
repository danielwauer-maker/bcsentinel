from __future__ import annotations

import textwrap
from io import BytesIO

from app.schemas.quick_assessment_report import QuickAssessmentReport

PAGE_W = 595
PAGE_H = 842
NAVY = (20 / 255, 33 / 255, 61 / 255)
ORANGE = (255 / 255, 146 / 255, 31 / 255)
BLUE = (36 / 255, 107 / 255, 253 / 255)
SUCCESS = (17 / 255, 163 / 255, 106 / 255)
WARNING = (217 / 255, 142 / 255, 4 / 255)
CRITICAL = (207 / 255, 58 / 255, 58 / 255)
INK = (23 / 255, 32 / 255, 51 / 255)
MUTED = (102 / 255, 112 / 255, 133 / 255)
LIGHT = (247 / 255, 249 / 255, 252 / 255)
SOFT_BLUE = (238 / 255, 243 / 255, 1.0)
LINE = (217 / 255, 222 / 255, 232 / 255)
WHITE = (1, 1, 1)


def _escape(value: str) -> str:
    return str(value or "").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").encode("latin-1", errors="replace").decode("latin-1")


def _text(text: str, x: float, y: float, size: float = 10, bold: bool = False, color=INK) -> list[str]:
    font = "F2" if bold else "F1"
    r, g, b = color
    return ["BT", f"/{font} {size:.1f} Tf", f"{r:.4f} {g:.4f} {b:.4f} rg", f"{x:.1f} {y:.1f} Td", f"({_escape(text)}) Tj", "ET"]


def _rect(x: float, y: float, w: float, h: float, fill, stroke=None) -> list[str]:
    fr, fg, fb = fill
    result = [f"{fr:.4f} {fg:.4f} {fb:.4f} rg"]
    if stroke:
        sr, sg, sb = stroke
        result += [f"{sr:.4f} {sg:.4f} {sb:.4f} RG", f"{x:.1f} {y:.1f} {w:.1f} {h:.1f} re B"]
    else:
        result += [f"{x:.1f} {y:.1f} {w:.1f} {h:.1f} re f"]
    return result


def _wrap(value: str, width: int) -> list[str]:
    return textwrap.wrap(str(value or ""), width=width, break_long_words=False, break_on_hyphens=False) or [""]


def _severity_label(value: str, de: bool) -> str:
    if not de:
        return value.title()
    return {
        "critical": "Kritisch",
        "high": "Hoch",
        "medium": "Mittel",
        "low": "Niedrig",
        "info": "Info",
    }.get(value, value.title())


def _severity_color(value: str):
    return {
        "critical": CRITICAL,
        "high": (179 / 255, 77 / 255, 34 / 255),
        "medium": WARNING,
        "low": SUCCESS,
        "info": MUTED,
    }.get(value, MUTED)


def _footer(page_no: int, report: QuickAssessmentReport) -> list[str]:
    de = report.language == "de"
    content: list[str] = []
    content += _rect(42, 48, 511, 1, LINE)
    content += _text("BCSentinel · Quick Assessment", 42, 31, 6.8, False, MUTED)
    content += _text((f"Seite {page_no} von 2" if de else f"Page {page_no} of 2"), 492, 31, 6.8, False, MUTED)
    return content


def _page_one(report: QuickAssessmentReport) -> list[str]:
    de = report.language == "de"
    c: list[str] = []

    c += _rect(0, PAGE_H - 190, PAGE_W, 190, NAVY)
    c += _rect(0, PAGE_H - 196, PAGE_W, 6, ORANGE)
    c += _text("BCSentinel", 42, 795, 22, True, WHITE)
    c += _text("Clean Data - Higher Impact", 42, 775, 8.5, False, (0.84, 0.88, 0.94))
    c += _rect(42, 730, 92, 20, BLUE)
    c += _text("QUICK ASSESSMENT", 51, 736, 7.5, True, WHITE)
    headline = (
        "Ihre wichtigsten Data-Health-Prioritaeten in Microsoft Dynamics 365 Business Central"
        if de else
        "Your highest Data Health priorities in Microsoft Dynamics 365 Business Central"
    )
    hy = 707
    for line in _wrap(headline, 52)[:3]:
        c += _text(line, 42, hy, 18.5, True, WHITE)
        hy -= 22
    subtitle = (
        "Top 5 Findings - priorisiert, bewertet und mit einem klaren naechsten Pruefschritt."
        if de else
        "Top 5 findings - prioritized, assessed and paired with a clear next review step."
    )
    c += _text(subtitle, 42, 648, 8.2, False, (0.84, 0.88, 0.94))

    c += _rect(42, 586, 511, 52, WHITE, LINE)
    identity = [
        ("Unternehmen" if de else "Company", report.company_label),
        ("BC Environment", report.environment_label),
        ("Scan-Datum" if de else "Scan date", report.scan_generated_at_utc.strftime("%d.%m.%Y %H:%M")),
        ("Scan ID", report.scan_id),
    ]
    x_positions = [52, 190, 315, 430]
    widths = [20, 18, 16, 14]
    for (label, value), x, width in zip(identity, x_positions, widths):
        c += _text(label.upper(), x, 621, 6.2, True, MUTED)
        c += _text(_wrap(value, width)[0], x, 602, 8.0, True, NAVY)

    cards = [
        (42, 504, 155, "DATA HEALTH SCORE", f"{report.data_health_score}/100", report.score_status, BLUE),
        (207, 504, 155, "BUSINESS IMPACT BAND", report.impact_band, ("Keine exakten EUR-Werte" if de else "No exact EUR values"), NAVY),
    ]
    for x, y, w, label, value, note, color in cards:
        c += _rect(x, y, w, 68, WHITE, LINE)
        c += _text(label, x + 10, y + 50, 6.2, True, MUTED)
        c += _text(value, x + 10, y + 28, 16.0, True, color)
        c += _text(_wrap(note, 28)[0], x + 10, y + 11, 6.5, False, MUTED)

    c += _rect(372, 504, 181, 68, WHITE, LINE)
    c += _text("SCAN-UMFANG" if de else "SCAN SCOPE", 382, 554, 6.2, True, MUTED)
    c += _text(f"{report.total_records:,}".replace(",", ".") if de else f"{report.total_records:,}", 382, 532, 12.0, True, NAVY)
    c += _text("Datensaetze" if de else "records", 382, 518, 6.3, False, MUTED)
    c += _text(f"{report.checks_count} Checks · {report.modules_analyzed} " + ("Module" if de else "modules") + f" · {report.issues_count} Findings", 445, 532, 6.4, False, INK)

    c += _text("Ihre Top 5 Findings - nach Prioritaet" if de else "Your Top 5 findings - by priority", 42, 477, 13.2, True, NAVY)
    c += _text(
        "Exakte Finanzwerte und Detailursachen bleiben dem Full Assessment vorbehalten." if de else "Exact financial values and detailed root causes remain reserved for Full Assessment.",
        42, 462, 6.8, False, MUTED,
    )

    y = 440
    if report.findings:
        for item in report.findings[:5]:
            height = 64
            c += _rect(42, y - height, 511, height, WHITE, LINE)
            c += _rect(42, y - height, 34, height, LIGHT)
            c += _text(str(item.rank), 54, y - 38, 14, True, NAVY)
            c += _text(_wrap(item.title, 48)[0], 86, y - 18, 8.8, True, NAVY)
            c += _text(_severity_label(item.severity, de).upper(), 427, y - 18, 6.6, True, _severity_color(item.severity))
            c += _text(f"IMPACT {item.impact_band}", 485, y - 18, 6.4, True, BLUE)
            affected = f"{item.affected_count:,}".replace(",", ".") if de else f"{item.affected_count:,}"
            meta = f"{item.risk_area_label} · {affected} " + ("betroffene Datensaetze" if de else "affected records")
            c += _text(meta, 86, y - 34, 6.6, False, MUTED)
            action_label = "Naechster Pruefschritt: " if de else "Next review step: "
            action_lines = _wrap(action_label + item.next_action, 88)[:2]
            ay = y - 49
            for line in action_lines:
                c += _text(line, 86, ay, 6.7, False, INK)
                ay -= 9
            y -= 69
    else:
        c += _rect(42, 374, 511, 52, LIGHT, LINE)
        c += _text("Keine priorisierbaren Findings erkannt." if de else "No findings eligible for prioritization were detected.", 54, 397, 8.2, True, NAVY)
        y = 360

    box_y = 76
    box_h = max(58, min(94, y - 88))
    c += _rect(42, box_y, 511, box_h, NAVY)
    c += _text("MANAGEMENT-EINORDNUNG" if de else "MANAGEMENT INTERPRETATION", 54, box_y + box_h - 17, 6.5, True, (0.70, 0.78, 0.90))
    ty = box_y + box_h - 34
    for line in _wrap(report.management_interpretation, 92)[:5]:
        c += _text(line, 54, ty, 7.1, False, WHITE)
        ty -= 10

    c += _footer(1, report)
    return c


def _page_two(report: QuickAssessmentReport) -> list[str]:
    de = report.language == "de"
    c: list[str] = []
    c += _rect(0, PAGE_H - 96, PAGE_W, 96, NAVY)
    c += _rect(0, PAGE_H - 102, PAGE_W, 6, ORANGE)
    c += _text("BCSentinel · Quick Assessment", 42, 790, 17, True, WHITE)
    c += _text("Prioritaet & naechste Entscheidung" if de else "Priority & next decision", 42, 765, 9, False, (0.84, 0.88, 0.94))

    c += _text("Priority Map · Severity x Impact", 42, 715, 13.2, True, NAVY)
    c += _text("Die Nummern entsprechen Seite 1." if de else "Numbers match page 1.", 42, 699, 6.8, False, MUTED)

    bands = (["Niedrig", "Moderat", "Hoch", "Sehr hoch"] if de else ["Low", "Moderate", "High", "Very high"])
    sevs = ["critical", "high", "medium", "low", "info"]
    grid_x, grid_y, grid_w = 42, 548, 511
    row_h, label_w = 25, 86
    col_w = (grid_w - label_w) / 4
    c += _rect(grid_x, grid_y + 5 * row_h, grid_w, 22, LIGHT, LINE)
    for idx, band in enumerate(bands):
        c += _text(band, grid_x + label_w + idx * col_w + 14, grid_y + 5 * row_h + 8, 6.4, True, MUTED)
    for row, sev in enumerate(sevs):
        y = grid_y + (4 - row) * row_h
        c += _rect(grid_x, y, label_w, row_h, LIGHT, LINE)
        c += _text(_severity_label(sev, de), grid_x + 9, y + 9, 6.7, True, NAVY)
        for col, band in enumerate(bands):
            x = grid_x + label_w + col * col_w
            c += _rect(x, y, col_w, row_h, WHITE, LINE)
            hits = [item for item in report.findings if item.severity == sev and item.impact_band == band]
            for hit_idx, item in enumerate(hits[:3]):
                cx = x + 14 + hit_idx * 18
                c += _rect(cx, y + 7, 13, 13, BLUE)
                c += _text(str(item.rank), cx + 4.2, y + 10.3, 6.3, True, WHITE)

    c += _text("Empfohlene Reihenfolge" if de else "Recommended sequence", 42, 521, 13.2, True, NAVY)
    y = 497
    for item in report.findings[:5]:
        c += _rect(42, y - 35, 28, 28, NAVY)
        c += _text(str(item.rank), 52, y - 25, 8.5, True, WHITE)
        c += _text(_wrap(item.title, 64)[0], 80, y - 14, 8.0, True, NAVY)
        for line_idx, line in enumerate(_wrap(item.next_action, 82)[:2]):
            c += _text(line, 80, y - 26 - line_idx * 9, 6.5, False, MUTED)
        y -= 42

    c += _text("Quick vs. Full Assessment", 42, 278, 13.2, True, NAVY)
    c += _rect(42, 152, 247, 108, WHITE, LINE)
    c += _rect(306, 152, 247, 108, SOFT_BLUE, LINE)
    c += _text("QUICK ASSESSMENT", 54, 241, 7.2, True, NAVY)
    c += _text("FULL ASSESSMENT", 318, 241, 7.2, True, NAVY)
    quick_lines = [
        "Top 5 priorisierte Findings" if de else "Top 5 prioritized findings",
        "Severity, Impact Band, betroffene Datensaetze" if de else "Severity, impact band, affected records",
        "Risk Area + naechster Pruefschritt" if de else "Risk area + next review step",
        "Dauerhafter Quick-Zugriff" if de else "Permanent Quick access",
    ]
    full_lines = [
        "Vollstaendige Finding-Liste" if de else "Complete finding list",
        "Exakte modellierte Business-Impact-Werte" if de else "Exact modeled business-impact values",
        "Ursachenanalyse + detaillierte Empfehlungen" if de else "Root-cause analysis + detailed recommendations",
        "Bereinigungs-Roadmap + Validation-Baseline" if de else "Remediation roadmap + Validation baseline",
    ]
    qy = fy = 222
    for line in quick_lines:
        c += _text("- " + line, 54, qy, 6.8, False, INK)
        qy -= 18
    for line in full_lines:
        c += _text("- " + line, 318, fy, 6.8, False, INK)
        fy -= 18

    c += _rect(42, 74, 511, 62, (1.0, 0.96, 0.90), (1.0, 0.82, 0.60))
    c += _text("NAECHSTER SCHRITT: FULL ASSESSMENT" if de else "NEXT STEP: FULL ASSESSMENT", 54, 117, 7.3, True, NAVY)
    ty = 101
    for line in _wrap(report.upgrade_message, 92)[:3]:
        c += _text(line, 54, ty, 6.8, False, INK)
        ty -= 10

    c += _footer(2, report)
    return c


def _build_pages(report: QuickAssessmentReport) -> list[list[str]]:
    return [_page_one(report), _page_two(report)]


def render_quick_assessment_report_pdf(report: QuickAssessmentReport) -> bytes:
    page_streams = ["\n".join(page).encode("latin-1", errors="replace") for page in _build_pages(report)]
    objects: list[bytes] = []

    def add(content: bytes) -> int:
        objects.append(content)
        return len(objects)

    regular = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    bold = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")

    content_ids: list[int] = []
    page_ids: list[int] = []
    for stream in page_streams:
        content_ids.append(add(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream"))
        page_ids.append(add(b"PENDING_PAGE"))

    pages_obj = add(b"PENDING_PAGES")
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids).encode("ascii")
    objects[pages_obj - 1] = b"<< /Type /Pages /Kids [" + kids + b"] /Count " + str(len(page_ids)).encode("ascii") + b" >>"

    for idx, page_id in enumerate(page_ids):
        objects[page_id - 1] = (
            b"<< /Type /Page /Parent " + str(pages_obj).encode("ascii") + b" 0 R /MediaBox [0 0 595 842] "
            b"/Resources << /Font << /F1 " + str(regular).encode("ascii") + b" 0 R /F2 " + str(bold).encode("ascii") +
            b" 0 R >> >> /Contents " + str(content_ids[idx]).encode("ascii") + b" 0 R >>"
        )

    catalog_obj = add(b"<< /Type /Catalog /Pages " + str(pages_obj).encode("ascii") + b" 0 R >>")

    buffer = BytesIO()
    buffer.write(b"%PDF-1.4\n%BCSentinel-Quick-Assessment\n")
    offsets = [0]
    for index, content in enumerate(objects, start=1):
        offsets.append(buffer.tell())
        buffer.write(f"{index} 0 obj\n".encode("ascii"))
        buffer.write(content)
        buffer.write(b"\nendobj\n")
    xref = buffer.tell()
    buffer.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    buffer.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        buffer.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    buffer.write(f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_obj} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
    return buffer.getvalue()
