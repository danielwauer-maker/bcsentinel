from __future__ import annotations

import textwrap
from io import BytesIO

from app.schemas.quick_assessment_report import QuickAssessmentReport

PAGE_W, PAGE_H = 595, 842
NAVY = (20 / 255, 33 / 255, 61 / 255)
ORANGE = (1.0, 146 / 255, 31 / 255)
BLUE = (36 / 255, 107 / 255, 253 / 255)
SUCCESS = (17 / 255, 163 / 255, 106 / 255)
WARNING = (217 / 255, 142 / 255, 4 / 255)
CRITICAL = (207 / 255, 58 / 255, 58 / 255)
INK = (23 / 255, 32 / 255, 51 / 255)
MUTED = (102 / 255, 112 / 255, 133 / 255)
LIGHT = (247 / 255, 249 / 255, 252 / 255)
SOFT_BLUE = (238 / 255, 243 / 255, 1.0)
LINE = (217 / 255, 222 / 255, 232 / 255)
WHITE = (1.0, 1.0, 1.0)


def _escape(value: str) -> str:
    return (
        str(value or "")
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .encode("latin-1", errors="replace")
        .decode("latin-1")
    )


def _text(value: str, x: float, y: float, size: float = 10, bold: bool = False, color=INK) -> list[str]:
    r, g, b = color
    return [
        "BT",
        f"/{'F2' if bold else 'F1'} {size:.1f} Tf",
        f"{r:.4f} {g:.4f} {b:.4f} rg",
        f"{x:.1f} {y:.1f} Td",
        f"({_escape(value)}) Tj",
        "ET",
    ]


def _rect(x: float, y: float, w: float, h: float, fill, stroke=None) -> list[str]:
    fr, fg, fb = fill
    commands = [f"{fr:.4f} {fg:.4f} {fb:.4f} rg"]
    if stroke:
        sr, sg, sb = stroke
        commands += [f"{sr:.4f} {sg:.4f} {sb:.4f} RG", f"{x:.1f} {y:.1f} {w:.1f} {h:.1f} re B"]
    else:
        commands += [f"{x:.1f} {y:.1f} {w:.1f} {h:.1f} re f"]
    return commands


def _wrap(value: str, width: int) -> list[str]:
    return textwrap.wrap(str(value or ""), width, break_long_words=False, break_on_hyphens=False) or [""]


def _sev_label(value: str, de: bool) -> str:
    return ({"critical": "Kritisch", "high": "Hoch", "medium": "Mittel", "low": "Niedrig", "info": "Info"}.get(value, value.title()) if de else value.title())


def _sev_color(value: str):
    return {
        "critical": CRITICAL,
        "high": (179 / 255, 77 / 255, 34 / 255),
        "medium": WARNING,
        "low": SUCCESS,
        "info": MUTED,
    }.get(value, MUTED)


def _footer(report: QuickAssessmentReport, page: int) -> list[str]:
    de = report.language == "de"
    return (
        _rect(42, 48, 511, 1, LINE)
        + _text("BCSentinel · Quick Assessment", 42, 31, 6.8, color=MUTED)
        + _text(f"{'Seite' if de else 'Page'} {page} {'von' if de else 'of'} 2", 492, 31, 6.8, color=MUTED)
    )


def _page_one(report: QuickAssessmentReport) -> list[str]:
    de = report.language == "de"
    c: list[str] = []
    c += _rect(0, 652, PAGE_W, 190, NAVY) + _rect(0, 646, PAGE_W, 6, ORANGE)
    c += _text("BCSentinel", 42, 795, 22, True, WHITE)
    c += _text("Clean Data - Higher Impact", 42, 775, 8.5, color=(.84, .88, .94))
    c += _rect(42, 730, 92, 20, BLUE) + _text("QUICK ASSESSMENT", 51, 736, 7.5, True, WHITE)
    headline = "Ihre wichtigsten Data-Health-Prioritaeten in Microsoft Dynamics 365 Business Central" if de else "Your highest Data Health priorities in Microsoft Dynamics 365 Business Central"
    hy = 707
    for line in _wrap(headline, 52)[:3]:
        c += _text(line, 42, hy, 18.5, True, WHITE)
        hy -= 22
    c += _text("Top 5 Findings - priorisiert, bewertet und mit klarem naechsten Pruefschritt." if de else "Top 5 findings - prioritized, assessed and paired with a clear next review step.", 42, 648, 8.0, color=(.84, .88, .94))

    c += _rect(42, 586, 511, 52, WHITE, LINE)
    identity = [
        ("Unternehmen" if de else "Company", report.company_label, 52, 20),
        ("BC Environment", report.environment_label, 190, 18),
        ("Scan-Datum" if de else "Scan date", report.scan_generated_at_utc.strftime("%d.%m.%Y %H:%M"), 315, 16),
        ("Scan ID", report.scan_id, 430, 14),
    ]
    for label, value, x, width in identity:
        c += _text(label.upper(), x, 621, 6.2, True, MUTED)
        c += _text(_wrap(value, width)[0], x, 602, 8.0, True, NAVY)

    for x, label, value, note, color in [
        (42, "DATA HEALTH SCORE", f"{report.data_health_score}/100", report.score_status, BLUE),
        (207, "BUSINESS IMPACT BAND", report.impact_band, "Keine exakten EUR-Werte" if de else "No exact EUR values", NAVY),
    ]:
        c += _rect(x, 504, 155, 68, WHITE, LINE)
        c += _text(label, x + 10, 554, 6.2, True, MUTED)
        c += _text(value, x + 10, 532, 16, True, color)
        c += _text(_wrap(note, 28)[0], x + 10, 515, 6.4, color=MUTED)
    c += _rect(372, 504, 181, 68, WHITE, LINE)
    c += _text("SCAN-UMFANG" if de else "SCAN SCOPE", 382, 554, 6.2, True, MUTED)
    records = f"{report.total_records:,}".replace(",", ".") if de else f"{report.total_records:,}"
    c += _text(records, 382, 532, 12, True, NAVY)
    c += _text("Datensaetze" if de else "records", 382, 518, 6.3, color=MUTED)
    c += _text(f"{report.checks_count} Checks · {report.modules_analyzed} {'Module' if de else 'modules'}", 445, 538, 6.3)
    c += _text(f"{report.issues_count} Findings", 445, 521, 6.3)

    c += _text("Ihre Top 5 Findings - nach Prioritaet" if de else "Your Top 5 findings - by priority", 42, 477, 13.2, True, NAVY)
    c += _text("Exakte Finanzwerte und Detailursachen bleiben dem Full Assessment vorbehalten." if de else "Exact financial values and detailed root causes remain reserved for Full Assessment.", 42, 462, 6.8, color=MUTED)

    # Fixed 55pt rows + 4pt gaps keep five findings above the management block on A4.
    y, row_h, gap = 440, 55, 4
    for item in report.findings[:5]:
        bottom = y - row_h
        c += _rect(42, bottom, 511, row_h, WHITE, LINE) + _rect(42, bottom, 34, row_h, LIGHT)
        c += _text(str(item.rank), 54, y - 33, 14, True, NAVY)
        c += _text(_wrap(item.title, 48)[0], 86, y - 16, 8.6, True, NAVY)
        c += _text(_sev_label(item.severity, de).upper(), 427, y - 16, 6.4, True, _sev_color(item.severity))
        c += _text(f"IMPACT {item.impact_band}", 485, y - 16, 6.2, True, BLUE)
        affected = f"{item.affected_count:,}".replace(",", ".") if de else f"{item.affected_count:,}"
        c += _text(f"{item.risk_area_label} · {affected} {'betroffene Datensaetze' if de else 'affected records'}", 86, y - 30, 6.4, color=MUTED)
        action = ("Naechster Pruefschritt: " if de else "Next review step: ") + item.next_action
        for idx, line in enumerate(_wrap(action, 90)[:2]):
            c += _text(line, 86, y - 42 - idx * 8, 6.3)
        y = bottom - gap

    if not report.findings:
        c += _rect(42, 385, 511, 42, LIGHT, LINE)
        c += _text("Keine priorisierbaren Findings erkannt." if de else "No findings eligible for prioritization were detected.", 54, 402, 8.2, True, NAVY)

    c += _rect(42, 76, 511, 58, NAVY)
    c += _text("MANAGEMENT-EINORDNUNG" if de else "MANAGEMENT INTERPRETATION", 54, 117, 6.5, True, (.70, .78, .90))
    ty = 101
    for line in _wrap(report.management_interpretation, 92)[:4]:
        c += _text(line, 54, ty, 6.8, color=WHITE)
        ty -= 9
    c += _footer(report, 1)
    return c


def _page_two(report: QuickAssessmentReport) -> list[str]:
    de = report.language == "de"
    c: list[str] = []
    c += _rect(0, 746, PAGE_W, 96, NAVY) + _rect(0, 740, PAGE_W, 6, ORANGE)
    c += _text("BCSentinel · Quick Assessment", 42, 790, 17, True, WHITE)
    c += _text("Prioritaet & naechste Entscheidung" if de else "Priority & next decision", 42, 765, 9, color=(.84, .88, .94))

    c += _text("Priority Map · Severity x Impact", 42, 715, 13.2, True, NAVY)
    c += _text("Die Nummern entsprechen Seite 1." if de else "Numbers match page 1.", 42, 699, 6.8, color=MUTED)
    bands = ["Niedrig", "Moderat", "Hoch", "Sehr hoch"] if de else ["Low", "Moderate", "High", "Very high"]
    sevs = ["critical", "high", "medium", "low", "info"]
    gx, gy, gw, rh, lw = 42, 548, 511, 25, 86
    cw = (gw - lw) / 4
    c += _rect(gx, gy + 5 * rh, gw, 22, LIGHT, LINE)
    for col, band in enumerate(bands):
        c += _text(band, gx + lw + col * cw + 14, gy + 5 * rh + 8, 6.4, True, MUTED)
    for row, sev in enumerate(sevs):
        cy = gy + (4 - row) * rh
        c += _rect(gx, cy, lw, rh, LIGHT, LINE) + _text(_sev_label(sev, de), gx + 9, cy + 9, 6.7, True, NAVY)
        for col, band in enumerate(bands):
            cx = gx + lw + col * cw
            c += _rect(cx, cy, cw, rh, WHITE, LINE)
            hits = [f for f in report.findings if f.severity == sev and f.impact_band == band]
            for hit_idx, item in enumerate(hits[:3]):
                bx = cx + 14 + hit_idx * 18
                c += _rect(bx, cy + 7, 13, 13, BLUE) + _text(str(item.rank), bx + 4.2, cy + 10.3, 6.3, True, WHITE)

    c += _text("Empfohlene Reihenfolge" if de else "Recommended sequence", 42, 521, 13.2, True, NAVY)
    y = 497
    for item in report.findings[:5]:
        c += _rect(42, y - 35, 28, 28, NAVY) + _text(str(item.rank), 52, y - 25, 8.5, True, WHITE)
        c += _text(_wrap(item.title, 64)[0], 80, y - 14, 8.0, True, NAVY)
        for idx, line in enumerate(_wrap(item.next_action, 82)[:2]):
            c += _text(line, 80, y - 26 - idx * 9, 6.4, color=MUTED)
        y -= 42

    c += _text("Quick vs. Full Assessment", 42, 278, 13.2, True, NAVY)
    c += _rect(42, 152, 247, 108, WHITE, LINE) + _rect(306, 152, 247, 108, SOFT_BLUE, LINE)
    c += _text("QUICK ASSESSMENT", 54, 241, 7.2, True, NAVY) + _text("FULL ASSESSMENT", 318, 241, 7.2, True, NAVY)
    quick = [
        "Top 5 priorisierte Findings" if de else "Top 5 prioritized findings",
        "Severity, Impact Band, betroffene Datensaetze" if de else "Severity, impact band, affected records",
        "Risk Area + naechster Pruefschritt" if de else "Risk area + next review step",
        "Dauerhafter Quick-Zugriff" if de else "Permanent Quick access",
    ]
    full = [
        "Vollstaendige Finding-Liste" if de else "Complete finding list",
        "Exakte modellierte Business-Impact-Werte" if de else "Exact modeled business-impact values",
        "Ursachenanalyse + detaillierte Empfehlungen" if de else "Root-cause analysis + detailed recommendations",
        "Bereinigungs-Roadmap + Validation-Baseline" if de else "Remediation roadmap + Validation baseline",
    ]
    for idx, line in enumerate(quick):
        c += _text("- " + line, 54, 222 - idx * 18, 6.8)
    for idx, line in enumerate(full):
        c += _text("- " + line, 318, 222 - idx * 18, 6.8)

    c += _rect(42, 74, 511, 62, (1.0, .96, .90), (1.0, .82, .60))
    c += _text("NAECHSTER SCHRITT: FULL ASSESSMENT" if de else "NEXT STEP: FULL ASSESSMENT", 54, 117, 7.3, True, NAVY)
    ty = 101
    for line in _wrap(report.upgrade_message, 92)[:3]:
        c += _text(line, 54, ty, 6.8)
        ty -= 10
    c += _footer(report, 2)
    return c


def _build_pdf(page_streams: list[bytes]) -> bytes:
    objects: list[bytes] = []

    def add(content: bytes) -> int:
        objects.append(content)
        return len(objects)

    regular = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    bold = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    content_ids, page_ids = [], []
    for stream in page_streams:
        content_ids.append(add(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream"))
        page_ids.append(add(b"PENDING_PAGE"))
    pages_obj = add(b"PENDING_PAGES")
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids).encode("ascii")
    objects[pages_obj - 1] = b"<< /Type /Pages /Kids [" + kids + b"] /Count " + str(len(page_ids)).encode("ascii") + b" >>"
    for idx, page_id in enumerate(page_ids):
        objects[page_id - 1] = (
            b"<< /Type /Page /Parent " + str(pages_obj).encode("ascii") + b" 0 R /MediaBox [0 0 595 842] "
            b"/Resources << /Font << /F1 " + str(regular).encode("ascii") + b" 0 R /F2 " + str(bold).encode("ascii")
            + b" 0 R >> >> /Contents " + str(content_ids[idx]).encode("ascii") + b" 0 R >>"
        )
    catalog = add(b"<< /Type /Catalog /Pages " + str(pages_obj).encode("ascii") + b" 0 R >>")
    out = BytesIO()
    out.write(b"%PDF-1.4\n%BCSentinel-Quick-Assessment\n")
    offsets = [0]
    for index, content in enumerate(objects, 1):
        offsets.append(out.tell())
        out.write(f"{index} 0 obj\n".encode("ascii") + content + b"\nendobj\n")
    xref = out.tell()
    out.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii") + b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        out.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    out.write(f"trailer\n<< /Size {len(objects) + 1} /Root {catalog} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
    return out.getvalue()


def render_quick_assessment_report_pdf(report: QuickAssessmentReport) -> bytes:
    streams = ["\n".join(page).encode("latin-1", errors="replace") for page in (_page_one(report), _page_two(report))]
    return _build_pdf(streams)
