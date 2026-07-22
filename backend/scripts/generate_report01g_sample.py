import os
import re
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("ENV", "test")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("SECRET_KEY", "report-sample-secret-key-with-sufficient-length")
os.environ.setdefault("ADMIN_USERNAME", "report-sample")
os.environ.setdefault("ADMIN_PASSWORD", "report-sample-password")
os.environ.setdefault("DATABASE_URL", "sqlite:///./output/pdf/report-01g-sample.sqlite3")

from playwright.sync_api import sync_playwright

from app.schemas.report import ExecutiveReport, ReportCategoryScore, ReportSeverityBucket
from app.services.executive_report_service import render_executive_report_html, render_executive_report_pdf


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "pdf"
OUTPUT.mkdir(parents=True, exist_ok=True)

report = ExecutiveReport(
    report_id="report-01g-sample",
    tenant_id="CRONUS-DE",
    language="de",
    scan_id="RUN_20260702_000003",
    generated_at_utc=datetime(2026, 7, 12, 18, 58, tzinfo=timezone.utc),
    scan_generated_at_utc=datetime(2026, 7, 12, 18, 55, tzinfo=timezone.utc),
    company_label="CRONUS DE",
    environment_label="BC Cloud",
    app_version="0.4.0",
    scan_type="Manueller Scan",
    executive_summary="",
    data_health_score=58,
    score_status="Kritisch",
    total_records=1468,
    checks_count=119,
    checks_total=165,
    issues_count=57,
    affected_records=1468,
    applied_exception_count=4,
    estimated_loss_eur=18024.26,
    potential_saving_eur=12616.98,
    estimated_premium_price_monthly=149.0,
    roi_eur=12467.98,
    headline="",
    rating="",
    data_quality=[
        ReportCategoryScore(name="Lager", score=24, status="Kritisch"),
        ReportCategoryScore(name="Einkauf", score=44, status="Kritisch"),
        ReportCategoryScore(name="Produktion", score=61, status="Braucht Aufmerksamkeit"),
        ReportCategoryScore(name="Finanzen", score=100, status="Exzellent"),
        ReportCategoryScore(name="Vertrieb", score=100, status="Exzellent"),
    ],
    severity_distribution=[
        ReportSeverityBucket(label="Kritisch", key="critical", count=9, percentage=15.8),
        ReportSeverityBucket(label="Hoch", key="high", count=6, percentage=10.5),
        ReportSeverityBucket(label="Mittel", key="medium", count=24, percentage=42.1),
        ReportSeverityBucket(label="Niedrig", key="low", count=18, percentage=31.6),
    ],
)

html = render_executive_report_html(report, inline_css=True)
html_path = OUTPUT / "bcsentinel-report-01g-sample.html"
pdf_path = OUTPUT / "bcsentinel-report-01g-sample.pdf"
html_path.write_text(html, encoding="utf-8")
pdf_bytes = render_executive_report_pdf(report)
pdf_path.write_bytes(pdf_bytes)
pdf_pages = len(re.findall(rb"/Type\s*/Page\b", pdf_bytes))
if pdf_pages != 2:
    raise RuntimeError(f"Expected a two-page PDF, got {pdf_pages} pages.")

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 794, "height": 1123}, device_scale_factor=2)
    page.set_content(html, wait_until="load")
    page.evaluate("document.fonts.ready")
    pages = page.locator(".report-page")
    if pages.count() != 2:
        raise RuntimeError(f"Expected two report pages, got {pages.count()}.")
    pages.nth(0).screenshot(path=str(OUTPUT / "bcsentinel-report-01g-page-1.png"))
    pages.nth(1).screenshot(path=str(OUTPUT / "bcsentinel-report-01g-page-2.png"))
    overflow = page.evaluate(
        """() => [...document.querySelectorAll('.report-page')].map((node) => ({
          scrollWidth: node.scrollWidth, clientWidth: node.clientWidth,
          scrollHeight: node.scrollHeight, clientHeight: node.clientHeight
        }))"""
    )
    large_money_html = render_executive_report_html(
        report.model_copy(update={"estimated_loss_eur": 1_250_480.75, "potential_saving_eur": 125_480.75}),
        inline_css=True,
    )
    page.set_content(large_money_html, wait_until="load")
    page.evaluate("document.fonts.ready")
    money_overflow = page.evaluate(
        """() => [...document.querySelectorAll('.kpi-value-money')].map((node) => ({
          text: node.textContent.trim(), scrollWidth: node.scrollWidth, clientWidth: node.clientWidth,
          fits: node.scrollWidth <= node.clientWidth
        }))"""
    )
    if not all(item["fits"] for item in money_overflow):
        raise RuntimeError(f"Money KPI overflow detected: {money_overflow}")
    browser.close()

print(html_path)
print(pdf_path)
print({"pdf_pages": pdf_pages, "money": money_overflow})
print(overflow)
