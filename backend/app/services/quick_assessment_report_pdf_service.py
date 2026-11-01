from __future__ import annotations

import textwrap
from io import BytesIO

from app.schemas.quick_assessment_report import QuickAssessmentReport

PAGE_W = 595
PAGE_H = 842
NAVY = (20 / 255, 33 / 255, 61 / 255)
ORANGE = (255 / 255, 146 / 255, 31 / 255)
BLUE = (36 / 255, 107 / 255, 253 / 255)
INK = (23 / 255, 32 / 255, 51 / 255)
MUTED = (102 / 255, 112 / 255, 133 / 255)
LIGHT = (247 / 255, 249 / 255, 252 / 255)
LINE = (217 / 255, 222 / 255, 232 / 255)


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
        result += [f"{sr:.4f} {sg:.4f} {sb:.4f} RG", f"{x} {y} {w} {h} re B"]
    else:
        result += [f"{x} {y} {w} {h} re f"]
    return result


def _wrap(value: str, width: int) -> list[str]:
    return textwrap.wrap(str(value or ""), width=width, break_long_words=False, break_on_hyphens=False) or [""]


def _build_pages(report: QuickAssessmentReport) -> list[list[str]]:
    de = report.language == "de"
    pages: list[list[str]] = []

    c: list[str] = []
    c += _rect(0, PAGE_H - 170, PAGE_W, 170, NAVY)
    c += _rect(0, PAGE_H - 176, PAGE_W, 6, ORANGE)
    c += _text("BCSentinel", 42, 795, 22, True, (1, 1, 1))
    c += _text("Clean Data - Higher Impact", 42, 774, 9, False, (0.84, 0.88, 0.94))
    c += _text("QUICK ASSESSMENT", 42, 735, 10, True, ORANGE)
    c += _text("Fokussierte Data-Health-Prioritaeten" if de else "Focused Data Health Priorities", 42, 705, 22, True, (1, 1, 1))
    c += _text(f"Scan {report.scan_id}", 42, 682, 8.5, False, (0.78, 0.83, 0.91))

    cards = [
        ("Data Health Score", f"{report.data_health_score}/100"),
        ("Auffaelligkeiten" if de else "Issues", str(report.issues_count)),
        ("Impact Band", report.impact_band),
    ]
    x = 42
    for label, value in cards:
        c += _rect(x, 570, 164, 78, LIGHT, LINE)
        c += _text(label.upper(), x + 12, 628, 7.2, True, MUTED)
        c += _text(value, x + 12, 594, 16, True, BLUE if label == "Data Health Score" else INK)
        x += 174

    c += _text("Management-Einordnung" if de else "Management Interpretation", 42, 536, 16, True, NAVY)
    y = 512
    for line in _wrap(report.management_interpretation, 88):
        c += _text(line, 42, y, 9.2, False, INK)
        y -= 14

    y -= 8
    c += _text("Priorisierte Risikobereiche" if de else "Priority Risk Areas", 42, y, 15, True, NAVY)
    y -= 24
    for area in report.risk_areas[:6]:
        c += _rect(42, y - 21, 512, 28, (1, 1, 1), LINE)
        c += _text(area.name, 50, y - 9, 8.6, True, INK)
        c += _text(f"{area.score}/100", 205, y - 9, 8.3, True, NAVY)
        c += _text(f"{area.issue_count} issues", 280, y - 9, 8.0, False, MUTED)
        c += _text(f"{area.affected_records} affected", 365, y - 9, 8.0, False, MUTED)
        c += _text(area.highest_severity.upper(), 485, y - 9, 7.4, True, INK)
        y -= 30
        if y < 235:
            break

    c += _rect(42, 52, 512, 150, (1.0, 0.98, 0.94), LINE)
    c += _text("Priorisierte Findings" if de else "Prioritized Findings", 54, 180, 12, True, NAVY)
    fy = 158
    if report.findings:
        for item in report.findings[:5]:
            c += _text(f"#{item.rank} {item.title} - {item.severity.upper()}", 54, fy, 8.4, True, INK)
            fy -= 12
            for line in _wrap(f"{item.risk_area} · {item.affected_count} affected · {item.next_action}", 78)[:2]:
                c += _text(line, 62, fy, 7.4, False, MUTED)
                fy -= 10
            fy -= 4
            if fy < 70:
                break
    else:
        note = (
            "Finding-Auswahl wird erst durch die dedizierte serverseitige Quick-Assessment-Grenze aktiviert."
            if de else
            "Finding selection is activated only by the dedicated server-side Quick Assessment boundary."
        )
        for line in _wrap(note, 82):
            c += _text(line, 54, fy, 8.2, False, INK)
            fy -= 12

    c += _text(f"{report.contract_version} · Limited paid scope", 42, 24, 6.8, False, MUTED)
    pages.append(c)

    c2: list[str] = []
    c2 += _rect(0, PAGE_H - 92, PAGE_W, 92, NAVY)
    c2 += _rect(0, PAGE_H - 98, PAGE_W, 6, ORANGE)
    c2 += _text("BCSentinel · Quick Assessment", 42, 790, 18, True, (1, 1, 1))
    c2 += _text("Empfohlene naechste Schritte" if de else "Recommended Next Actions", 42, 730, 16, True, NAVY)
    y = 700
    for idx, action in enumerate(report.recommended_next_actions, start=1):
        c2 += _text(f"{idx}.", 48, y, 10, True, BLUE)
        line_y = y
        for line in _wrap(action, 78):
            c2 += _text(line, 70, line_y, 9.2, False, INK)
            line_y -= 14
        y = line_y - 14

    c2 += _rect(42, max(250, y - 125), 512, 105, (1.0, 0.96, 0.90), LINE)
    box_y = max(250, y - 125)
    c2 += _text("Full Assessment", 54, box_y + 80, 13, True, NAVY)
    ty = box_y + 61
    for line in _wrap(report.upgrade_message, 82)[:5]:
        c2 += _text(line, 54, ty, 8.4, False, INK)
        ty -= 12

    c2 += _text(
        "Keine Datensatzdetails oder exakten Finanzwerte." if de else "No record-level detail or exact financial values.",
        42, 54, 8.0, False, MUTED,
    )
    c2 += _text(f"BCSentinel · {report.contract_version}", 42, 30, 6.8, False, MUTED)
    pages.append(c2)
    return pages


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
