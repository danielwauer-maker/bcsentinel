from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

from app.schemas.report import ExecutiveReport, ReportCategoryScore, ReportSeverityBucket
from app.services.executive_report_service import render_executive_report_html, render_executive_report_pdf


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "pdf"
OUTPUT.mkdir(parents=True, exist_ok=True)

report = ExecutiveReport(
    report_id="report-01f-sample", tenant_id="CRONUS-DE", language="de", scan_id="sample-report-01f",
    generated_at_utc=datetime(2026, 5, 14, 9, 41, tzinfo=timezone.utc),
    scan_generated_at_utc=datetime(2026, 5, 14, 9, 37, tzinfo=timezone.utc),
    company_label="CRONUS Deutschland GmbH", environment_label="Produktivumgebung", app_version="1.0.2.6",
    scan_type="Manueller Scan",
    executive_summary="", data_health_score=47, score_status="Kritisch", total_records=35528,
    checks_count=224, checks_total=224, issues_count=224, affected_records=35528,
    estimated_loss_eur=21908, potential_saving_eur=15336, headline="", rating="",
    data_quality=[
        ReportCategoryScore(name="Duplikate", score=78, status="Gut"),
        ReportCategoryScore(name="Integrität", score=55, status="Kritisch"),
        ReportCategoryScore(name="Vollständigkeit", score=42, status="Kritisch"),
        ReportCategoryScore(name="Validierung", score=38, status="Kritisch"),
        ReportCategoryScore(name="Konsistenz", score=68, status="Braucht Aufmerksamkeit"),
    ],
    severity_distribution=[
        ReportSeverityBucket(label="Kritisch", key="critical", count=92, percentage=41),
        ReportSeverityBucket(label="Hoch", key="high", count=65, percentage=29),
        ReportSeverityBucket(label="Mittel", key="medium", count=45, percentage=20),
        ReportSeverityBucket(label="Niedrig", key="low", count=22, percentage=10),
    ],
)

html = render_executive_report_html(report, inline_css=True)
html_path = OUTPUT / "bcsentinel-report-01f-sample.html"
pdf_path = OUTPUT / "bcsentinel-report-01f-sample.pdf"
html_path.write_text(html, encoding="utf-8")
pdf_path.write_bytes(render_executive_report_pdf(report))

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    page = browser.new_page(viewport={"width": 794, "height": 1123}, device_scale_factor=2)
    page.set_content(html, wait_until="load")
    page.locator(".report-page").nth(0).screenshot(path=str(OUTPUT / "bcsentinel-report-01f-page-1.png"))
    page.locator(".report-page").nth(1).screenshot(path=str(OUTPUT / "bcsentinel-report-01f-page-2.png"))
    browser.close()

print(html_path)
print(pdf_path)
