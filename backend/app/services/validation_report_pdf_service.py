from __future__ import annotations

import textwrap
from io import BytesIO

from app.schemas.validation_report import ValidationReport

PAGE_W = 595
PAGE_H = 842
NAVY = (20 / 255, 33 / 255, 61 / 255)
ORANGE = (255 / 255, 146 / 255, 31 / 255)
BLUE = (36 / 255, 107 / 255, 253 / 255)
GREEN = (17 / 255, 163 / 255, 106 / 255)
RED = (207 / 255, 58 / 255, 58 / 255)
INK = (23 / 255, 32 / 255, 51 / 255)
MUTED = (102 / 255, 112 / 255, 133 / 255)
LIGHT = (247 / 255, 249 / 255, 252 / 255)
LINE = (217 / 255, 222 / 255, 232 / 255)


def _pdf_escape(value: str) -> str:
    return (
        str(value or "")
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .encode("latin-1", errors="replace")
        .decode("latin-1")
    )


def _text(text: str, *, x: float, y: float, size: float = 10, bold: bool = False, color=INK) -> list[str]:
    font = "F2" if bold else "F1"
    r, g, b = color
    return ["BT", f"/{font} {size:.1f} Tf", f"{r:.4f} {g:.4f} {b:.4f} rg", f"{x:.1f} {y:.1f} Td", f"({_pdf_escape(text)}) Tj", "ET"]


def _rect(x: float, y: float, w: float, h: float, fill, stroke=None) -> list[str]:
    fr, fg, fb = fill
    commands = [f"{fr:.4f} {fg:.4f} {fb:.4f} rg"]
    if stroke:
        sr, sg, sb = stroke
        commands += [f"{sr:.4f} {sg:.4f} {sb:.4f} RG", f"{x} {y} {w} {h} re B"]
    else:
        commands.append(f"{x} {y} {w} {h} re f")
    return commands


def _wrap(value: str, width: int = 82) -> list[str]:
    return textwrap.wrap(str(value or ""), width=width, break_long_words=False, break_on_hyphens=False) or [""]


def _header(report: ValidationReport, page: int) -> list[str]:
    commands = _rect(0, PAGE_H - 112, PAGE_W, 112, NAVY)
    commands += _rect(0, PAGE_H - 118, PAGE_W, 6, ORANGE)
    commands += _text("BCSentinel", x=42, y=PAGE_H - 48, size=20, bold=True, color=(1, 1, 1))
    commands += _text("Validation Report", x=42, y=PAGE_H - 73, size=11, color=(0.87, 0.91, 0.97))
    commands += _text(f"{report.baseline_scan_id} -> {report.validation_scan_id}", x=42, y=PAGE_H - 94, size=8.5, color=(0.74, 0.81, 0.90))
    commands += _text(str(page), x=536, y=PAGE_H - 94, size=9, bold=True, color=(1, 1, 1))
    return commands


def _build_pages(report: ValidationReport) -> list[list[str]]:
    pages: list[list[str]] = []
    first = _header(report, 1)
    first += _text("Validation Summary", x=42, y=690, size=17, bold=True, color=NAVY)
    y = 664
    for line in _wrap(report.executive_summary, 90):
        first += _text(line, x=42, y=y, size=9.5)
        y -= 14

    y -= 12
    first += _rect(42, y - 92, 244, 92, LIGHT, LINE)
    first += _text("DATA HEALTH SCORE", x=56, y=y - 20, size=8, bold=True, color=MUTED)
    first += _text(f"{report.baseline_score} -> {report.validation_score}", x=56, y=y - 50, size=21, bold=True, color=NAVY)
    first += _text(f"Delta {report.score_delta:+d}", x=56, y=y - 72, size=10, bold=True, color=GREEN if report.score_delta >= 0 else RED)

    first += _rect(310, y - 92, 244, 92, LIGHT, LINE)
    first += _text("ESTIMATED EXPOSURE REDUCTION", x=324, y=y - 20, size=8, bold=True, color=MUTED)
    first += _text(f"EUR {report.estimated_exposure_reduction_eur:,.2f}", x=324, y=y - 50, size=18, bold=True, color=NAVY)
    first += _text(f"Loss delta EUR {report.estimated_loss_delta_eur:,.2f}", x=324, y=y - 72, size=9, color=MUTED)

    y -= 128
    first += _text("Outcome", x=42, y=y, size=15, bold=True, color=NAVY)
    y -= 30
    metrics = [
        ("Resolved", report.resolved_count, GREEN),
        ("Improved", report.improved_count, BLUE),
        ("Remaining", report.remaining_count, MUTED),
        ("Regressed", report.regressed_count, RED),
        ("New", report.new_count, RED),
    ]
    x = 42
    for label, value, color in metrics:
        first += _rect(x, y - 66, 94, 66, LIGHT, LINE)
        first += _text(label.upper(), x=x + 9, y=y - 19, size=7, bold=True, color=MUTED)
        first += _text(str(value), x=x + 9, y=y - 48, size=18, bold=True, color=color)
        x += 102
    pages.append(first)

    groups = [
        ("Regressed", report.regressed),
        ("New", report.new_findings),
        ("Resolved", report.resolved),
        ("Improved", report.improved),
        ("Remaining", report.remaining),
    ]
    page_no = 2
    page = _header(report, page_no)
    y = 690
    for title, items in groups:
        if not items:
            continue
        if y < 150:
            pages.append(page)
            page_no += 1
            page = _header(report, page_no)
            y = 690
        page += _text(title, x=42, y=y, size=15, bold=True, color=NAVY)
        y -= 24
        for item in items:
            if y < 118:
                pages.append(page)
                page_no += 1
                page = _header(report, page_no)
                y = 690
            page += _text(item.title, x=48, y=y, size=9, bold=True)
            y -= 13
            page += _text(
                f"{item.code} | {item.category} | affected {item.affected_before}->{item.affected_after} | EUR {item.impact_before_eur:,.2f}->{item.impact_after_eur:,.2f}",
                x=48, y=y, size=7.6, color=MUTED,
            )
            y -= 22
        y -= 8

    if y < 180:
        pages.append(page)
        page_no += 1
        page = _header(report, page_no)
        y = 690
    page += _text("Next Steps", x=42, y=y, size=15, bold=True, color=NAVY)
    y -= 24
    for idx, item in enumerate(report.next_steps, start=1):
        for line_no, line in enumerate(_wrap(item, 82)):
            prefix = f"{idx}. " if line_no == 0 else "   "
            page += _text(prefix + line, x=48, y=y, size=8.7)
            y -= 13
        y -= 4
    pages.append(page)
    return pages


def render_validation_report_pdf(report: ValidationReport) -> bytes:
    page_streams = _build_pages(report)
    objects: list[bytes] = []

    def add(content: bytes) -> int:
        objects.append(content)
        return len(objects)

    regular = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    bold = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    page_refs: list[int] = []
    for commands in page_streams:
        stream = "\n".join(commands).encode("latin-1", errors="replace")
        content_obj = add(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
        page_obj = add(
            b"<< /Type /Page /Parent 0 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 "
            + str(regular).encode() + b" 0 R /F2 " + str(bold).encode() + b" 0 R >> >> /Contents "
            + str(content_obj).encode() + b" 0 R >>"
        )
        page_refs.append(page_obj)

    kids = b" ".join(str(ref).encode() + b" 0 R" for ref in page_refs)
    pages_obj = add(b"<< /Type /Pages /Kids [" + kids + b"] /Count " + str(len(page_refs)).encode() + b" >>")
    catalog_obj = add(b"<< /Type /Catalog /Pages " + str(pages_obj).encode() + b" 0 R >>")
    fixed = [obj.replace(b"/Parent 0 0 R", b"/Parent " + str(pages_obj).encode() + b" 0 R") for obj in objects]

    buffer = BytesIO()
    buffer.write(b"%PDF-1.4\n%BCSentinel Validation\n")
    offsets = [0]
    for idx, content in enumerate(fixed, start=1):
        offsets.append(buffer.tell())
        buffer.write(f"{idx} 0 obj\n".encode())
        buffer.write(content)
        buffer.write(b"\nendobj\n")
    xref = buffer.tell()
    buffer.write(f"xref\n0 {len(fixed) + 1}\n".encode())
    buffer.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        buffer.write(f"{offset:010d} 00000 n \n".encode())
    buffer.write(f"trailer\n<< /Size {len(fixed) + 1} /Root {catalog_obj} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return buffer.getvalue()
