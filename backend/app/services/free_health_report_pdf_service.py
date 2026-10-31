from __future__ import annotations

import textwrap
from io import BytesIO

from app.schemas.free_health_report import FreeHealthReport

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


def _build_page(report: FreeHealthReport) -> list[str]:
    de = report.language == "de"
    c: list[str] = []
    c += _rect(0, PAGE_H - 170, PAGE_W, 170, NAVY)
    c += _rect(0, PAGE_H - 176, PAGE_W, 6, ORANGE)
    c += _text("BCSentinel", 42, 795, 22, True, (1, 1, 1))
    c += _text("Clean Data - Higher Impact", 42, 774, 9, False, (0.84, 0.88, 0.94))
    c += _text("FREE HEALTH REPORT", 42, 735, 10, True, ORANGE)
    c += _text("Business Central Data Health Check", 42, 705, 23, True, (1, 1, 1))
    c += _text(f"Scan {report.scan_id}", 42, 682, 8.5, False, (0.78, 0.83, 0.91))

    cards = [
        ("Data Health Score", f"{report.data_health_score}/100"),
        ("Auffaelligkeiten" if de else "Issues detected", str(report.issues_count)),
        ("Impact Band", report.impact_band),
    ]
    x = 42
    for label, value in cards:
        c += _rect(x, 570, 164, 78, LIGHT, LINE)
        c += _text(label.upper(), x + 12, 628, 7.2, True, MUTED)
        c += _text(value, x + 12, 594, 16, True, BLUE if label == "Data Health Score" else INK)
        x += 174

    c += _text("Management-Zusammenfassung" if de else "Management Summary", 42, 536, 16, True, NAVY)
    y = 512
    for line in _wrap(report.summary, 88):
        c += _text(line, 42, y, 9.2, False, INK)
        y -= 14

    y -= 8
    c += _text("Risikobereiche" if de else "Risk Areas", 42, y, 15, True, NAVY)
    y -= 24
    c += _text("AREA", 48, y, 7, True, MUTED)
    c += _text("SCORE", 210, y, 7, True, MUTED)
    c += _text("STATUS", 270, y, 7, True, MUTED)
    c += _text("ISSUES", 405, y, 7, True, MUTED)
    c += _text("SEVERITY", 470, y, 7, True, MUTED)
    y -= 15
    for area in report.risk_areas[:8]:
        c += _rect(42, y - 21, 512, 27, (1, 1, 1), LINE)
        c += _text(area.name, 48, y - 10, 8.5, True, INK)
        c += _text(f"{area.score}/100", 210, y - 10, 8.2, False, INK)
        c += _text(area.status, 270, y - 10, 8.0, False, MUTED)
        c += _text(str(area.issue_count), 414, y - 10, 8.2, False, INK)
        c += _text(area.highest_severity.upper(), 470, y - 10, 7.6, True, INK)
        y -= 29
        if y < 140:
            break

    c += _rect(42, 48, 512, 78, (1.0, 0.96, 0.90), LINE)
    c += _text("Assessment", 54, 104, 12, True, NAVY)
    upgrade_lines = _wrap(report.upgrade_message, 82)
    uy = 86
    for line in upgrade_lines[:3]:
        c += _text(line, 54, uy, 8.2, False, INK)
        uy -= 12
    c += _text(f"{report.contract_version} · Aggregate-only", 42, 24, 6.8, False, MUTED)
    return c


def render_free_health_report_pdf(report: FreeHealthReport) -> bytes:
    stream = "\n".join(_build_page(report)).encode("latin-1", errors="replace")
    objects: list[bytes] = []

    def add(content: bytes) -> int:
        objects.append(content)
        return len(objects)

    regular = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    bold = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    content_obj = add(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")
    page_obj = add(b"<< /Type /Page /Parent 0 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 " + str(regular).encode("ascii") + b" 0 R /F2 " + str(bold).encode("ascii") + b" 0 R >> >> /Contents " + str(content_obj).encode("ascii") + b" 0 R >>")
    pages_obj = add(b"<< /Type /Pages /Kids [" + str(page_obj).encode("ascii") + b" 0 R] /Count 1 >>")
    catalog_obj = add(b"<< /Type /Catalog /Pages " + str(pages_obj).encode("ascii") + b" 0 R >>")
    fixed = [content.replace(b"/Parent 0 0 R", b"/Parent " + str(pages_obj).encode("ascii") + b" 0 R") for content in objects]

    buffer = BytesIO()
    buffer.write(b"%PDF-1.4\n%BCSentinel-Free-Health\n")
    offsets = [0]
    for index, content in enumerate(fixed, start=1):
        offsets.append(buffer.tell())
        buffer.write(f"{index} 0 obj\n".encode("ascii")); buffer.write(content); buffer.write(b"\nendobj\n")
    xref = buffer.tell()
    buffer.write(f"xref\n0 {len(fixed) + 1}\n".encode("ascii")); buffer.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        buffer.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    buffer.write(f"trailer\n<< /Size {len(fixed) + 1} /Root {catalog_obj} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
    return buffer.getvalue()
