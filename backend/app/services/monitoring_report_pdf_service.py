from __future__ import annotations

import textwrap
from io import BytesIO

from app.schemas.monitoring_report import MonitoringReport

PAGE_W = 595
PAGE_H = 842
NAVY = (20 / 255, 33 / 255, 61 / 255)
ORANGE = (255 / 255, 146 / 255, 31 / 255)
GREEN = (17 / 255, 163 / 255, 106 / 255)
RED = (207 / 255, 58 / 255, 58 / 255)
INK = (23 / 255, 32 / 255, 51 / 255)
MUTED = (102 / 255, 112 / 255, 133 / 255)
LIGHT = (247 / 255, 249 / 255, 252 / 255)
LINE = (217 / 255, 222 / 255, 232 / 255)


def _pdf_escape(value: str) -> str:
    return str(value or "").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").encode("latin-1", errors="replace").decode("latin-1")


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


def _header(report: MonitoringReport, page: int, total: int = 4) -> list[str]:
    commands = _rect(0, PAGE_H - 112, PAGE_W, 112, NAVY)
    commands += _rect(0, PAGE_H - 118, PAGE_W, 6, ORANGE)
    commands += _text("BCSentinel", x=42, y=PAGE_H - 48, size=20, bold=True, color=(1, 1, 1))
    commands += _text("Monitoring Report", x=42, y=PAGE_H - 73, size=11, color=(0.87, 0.91, 0.97))
    commands += _text(f"{report.coverage.scans_in_period} scans | current {report.current_scan_id}", x=42, y=PAGE_H - 94, size=8.5, color=(0.74, 0.81, 0.90))
    commands += _text(f"{page}/{total}", x=530, y=PAGE_H - 94, size=9, bold=True, color=(1, 1, 1))
    return commands


def _build_pages(report: MonitoringReport) -> list[list[str]]:
    pages: list[list[str]] = []

    p1 = _header(report, 1)
    p1 += _text("Business Health Monitoring", x=42, y=690, size=18, bold=True, color=NAVY)
    y = 655
    metrics = [
        ("Data Health Score", f"{report.current_data_health_score}/100", f"{report.score_delta_previous:+d} vs previous"),
        ("Modeled Business Impact", f"EUR {report.current_business_impact_eur:,.0f}", f"{report.business_impact_delta_previous_eur:+,.0f} EUR vs previous"),
        ("Findings", str(report.current_findings_count), f"{report.findings_delta_previous:+d} vs previous"),
        ("Critical / High", f"{report.current_critical_findings} / {report.current_high_findings}", f"{report.current_affected_records:,} affected"),
    ]
    x_positions = [42, 174, 306, 438]
    for x, (label, value, delta) in zip(x_positions, metrics):
        p1 += _rect(x, y - 88, 116, 88, LIGHT, LINE)
        p1 += _text(label, x=x + 8, y=y - 18, size=7.2, bold=True, color=MUTED)
        p1 += _text(value, x=x + 8, y=y - 46, size=14, bold=True, color=NAVY)
        p1 += _text(delta, x=x + 8, y=y - 68, size=7.3, color=MUTED)
    y -= 126
    p1 += _text("Management Interpretation", x=42, y=y, size=15, bold=True, color=NAVY)
    y -= 26
    for item in report.management_interpretation:
        for line in _wrap(item, 88):
            p1 += _text(line, x=48, y=y, size=8.7)
            y -= 13
        y -= 7
    y -= 8
    p1 += _text("Monitoring Coverage", x=42, y=y, size=15, bold=True, color=NAVY)
    y -= 24
    p1 += _text(f"Period: {report.coverage.period_start_utc.date()} -> {report.coverage.period_end_utc.date()}", x=48, y=y, size=8.5)
    y -= 15
    p1 += _text(f"Scans: {report.coverage.scans_in_period} | Freshness: {report.coverage.data_freshness} ({report.coverage.freshness_hours:.1f} h)", x=48, y=y, size=8.5)
    pages.append(p1)

    p2 = _header(report, 2)
    p2 += _text("Trends & Business Areas", x=42, y=690, size=18, bold=True, color=NAVY)
    y = 660
    for point in report.trend_points:
        p2 += _text(f"{point.generated_at_utc.date()} | Score {point.data_health_score} | Findings {point.findings_count} | Affected {point.affected_records} | EUR {point.modeled_business_impact_eur:,.0f}", x=48, y=y, size=7.8)
        y -= 15
    y -= 14
    p2 += _text("Business Area Trends", x=42, y=y, size=14, bold=True, color=NAVY)
    y -= 22
    for area in report.business_areas:
        color = GREEN if area.trend == "improving" else RED if area.trend == "deteriorating" else MUTED
        p2 += _text(area.label, x=48, y=y, size=8.2, bold=True)
        p2 += _text(f"Score {area.baseline_score}/{area.previous_score}/{area.current_score}", x=190, y=y, size=7.8)
        p2 += _text(f"Findings {area.baseline_findings_count}/{area.previous_findings_count}/{area.current_findings_count}", x=315, y=y, size=7.8)
        p2 += _text(area.trend, x=475, y=y, size=7.8, bold=True, color=color)
        y -= 18
    pages.append(p2)

    p3 = _header(report, 3)
    p3 += _text("Risk Dynamics", x=42, y=690, size=18, bold=True, color=NAVY)
    y = 655
    summary = [
        ("New", report.new_findings_count),
        ("Resolved", report.resolved_findings_count),
        ("Persistent", report.persistent_findings_count),
        ("Improving", report.improving_findings_count),
        ("Regressing", report.regressing_findings_count),
        ("Reopened", report.reopened_findings_count),
    ]
    x = 42
    for label, value in summary:
        p3 += _rect(x, y - 62, 80, 62, LIGHT, LINE)
        p3 += _text(label, x=x + 7, y=y - 18, size=7, bold=True, color=MUTED)
        p3 += _text(str(value), x=x + 7, y=y - 44, size=17, bold=True, color=NAVY)
        x += 86
    y -= 100
    for row in report.finding_lifecycle[:22]:
        p3 += _text(f"{row.status.upper():10} {row.code} | {row.category_label} | {row.current_severity or '-'} | affected {row.previous_affected_records}->{row.current_affected_records} | EUR {row.previous_impact_eur:,.0f}->{row.current_impact_eur:,.0f}", x=48, y=y, size=7.1)
        y -= 16
        if y < 90:
            break
    pages.append(p3)

    p4 = _header(report, 4)
    p4 += _text("Management Attention", x=42, y=690, size=18, bold=True, color=NAVY)
    y = 655
    p4 += _text("Current Priorities", x=42, y=y, size=14, bold=True, color=NAVY)
    y -= 24
    for idx, row in enumerate(report.top_priorities, start=1):
        for line_no, line in enumerate(_wrap(f"{row.title} | {row.category_label} | {row.status} | {row.current_severity or '-'} | EUR {row.current_impact_eur:,.0f}", 82)):
            prefix = f"{idx}. " if line_no == 0 else "   "
            p4 += _text(prefix + line, x=48, y=y, size=8.2)
            y -= 13
        y -= 5
        if y < 260:
            break
    y -= 10
    p4 += _text("Monitoring Status", x=42, y=y, size=14, bold=True, color=NAVY)
    y -= 22
    p4 += _text(f"Latest scan: {report.coverage.latest_scan_at_utc.isoformat()}", x=48, y=y, size=8.2)
    y -= 15
    p4 += _text(f"Baseline scan: {report.coverage.baseline_scan_at_utc.isoformat()}", x=48, y=y, size=8.2)
    y -= 15
    p4 += _text(f"Freshness: {report.coverage.data_freshness} ({report.coverage.freshness_hours:.1f} hours)", x=48, y=y, size=8.2)
    pages.append(p4)
    return pages


def render_monitoring_report_pdf(report: MonitoringReport) -> bytes:
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
    buffer.write(b"%PDF-1.4\n%BCSentinel Monitoring\n")
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
        buffer.write(f"{offset:010d} 00000 n \n")
    buffer.write(f"trailer\n<< /Size {len(fixed) + 1} /Root {catalog_obj} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return buffer.getvalue()
