from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, quote, urlencode, urlparse, urlunparse

from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from app.core.settings import settings
from app.db import SessionLocal
from app.models import Scan, ScanIssueRecord, Tenant
from app.routers.billing import (
    BillingPortalRequest,
    CheckoutSessionRequest,
    create_billing_portal_session_for_tenant,
    create_checkout_session_for_tenant,
)
from app.security.tenant import (
    enforce_tenant_match,
    load_authenticated_tenant,
    require_tenant_headers,
)
from app.security.token import create_token, verify_token
from app.services.entitlement_guard_service import get_tenant_features, require_tenant_feature
from app.services.entitlement_service import is_premium_actions_enabled
from app.services.impact_service import normalize_stored_commercials
from app.services.localization_service import normalize_language, tenant_language, update_tenant_language
from app.services.dashboard_translation_service import dashboard_ui_translations
from app.services.product_license_service import (
    build_product_access_snapshot,
    PRODUCT_FULL_ANALYSIS,
    PRODUCT_MONITORING_ANNUAL,
    PRODUCT_MONITORING_MONTHLY,
    PRODUCT_VALIDATION_CHECK,
    normalize_product_code,
)
from app.services.product_pricing_service import (
    build_monitoring_pricing_breakdown,
    build_tier_pricing_payload,
    get_public_product_pricing_payload,
)

router = APIRouter(tags=["analytics"])
TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
ANALYTICS_EMBED_COOKIE_NAME = "bcs_at"
ANALYTICS_EMBED_COOKIE_MAX_AGE_SECONDS = 15 * 60
ANALYTICS_EMBED_TOKEN_TYPE = "analytics_embed"
ANALYTICS_EMBED_TOKEN_MINUTES = 5

DASHBOARD_UI = {
    "en": {
        "overview": "Overview",
        "subscription": "Subscription",
        "credits_needed": "Credits needed",
        "loading": "Loading...",
        "last_updated": "Last updated",
        "scanned_records": "Scanned records",
        "scanned_records_helper": "Total volume used for pricing and scope",
        "affected_records": "Affected records",
        "affected_records_helper": "Records with action potential",
        "estimated_annual_loss": "Estimated annual loss",
        "estimated_annual_loss_helper": "Monetized impact",
        "checks_run": "Checks run",
        "checks_run_helper": "Depth of this scan",
        "issues_found": "Issues found",
        "issues_found_helper": "Detected issue types",
        "roi": "ROI",
        "roi_helper": "Potential minus annual cost",
        "module_scores": "Data Scores by BC module",
        "module_scores_helper": "Score per module - 0 to 100",
        "issues_by_module": "Issues by BC module",
        "issues_by_module_helper": "Affected findings per module",
        "recent_scans": "Recent Scans",
        "recent_scans_helper": "Click a scan to load it",
        "date": "Date",
        "type": "Type",
        "score": "Score",
        "issues": "Issues",
        "headline": "Headline",
        "previous": "Previous",
        "next": "Next",
        "page": "Page",
        "score_trend": "Score Trend",
        "score_trend_helper": "History of selected scans",
        "loss_trend": "Loss Trend",
        "loss_trend_helper": "Estimated annual impact",
        "paid_scan_access": "Full Analysis access",
        "scan_preview": "Scan preview",
        "scan_preview_helper": "Record details, recommendations, actions",
        "estimated_monitoring_pricing": "Estimated monitoring pricing",
        "base_price": "Base price",
        "data_volume_add_on": "Data volume add-on",
        "estimated_monitoring_month": "Estimated monitoring / month",
        "annual_fixed_plan": "Annual fixed plan",
        "findings": "Findings",
        "findings_helper": "Visible with paid scan access, actionable in Business Central",
        "issue": "Issue",
        "area": "Area",
        "severity": "Severity",
        "count": "Count",
        "impact": "Impact",
        "access": "Access",
        "product_access": "Product access",
        "scan_credits": "Scan Credits",
        "scan_credits_helper": "Available paid scan starts",
        "dashboard_access_until": "Dashboard Access Until",
        "dashboard_access_helper": "Full Analysis / Validation result window",
        "issue_access_until": "Issue Access Until",
        "issue_access_helper": "Record details and recommendations",
        "monthly_price": "Monthly price",
        "monthly_price_helper": "Monitoring price",
        "annual_cost": "Annual cost",
        "annual_cost_helper": "12 months projection",
        "dashboard_load_error": "The dashboard could not be loaded.",
        "no_module_scores": "No module scores are available yet.",
        "no_module_data": "No module issue counts are available for this scan.",
        "no_trend_data": "No trend data available yet.",
        "no_scans": "No scans available yet.",
        "no_findings": "No findings are available for this scan.",
        "paid_access": "Paid Access",
        "open_in_bc": "Open in BC",
        "preview_after_scan": "The paid scan preview will appear after the next scan.",
        "recommendations_available": "Recommendations available",
        "affected": "affected",
        "monitoring_active": "Monitoring active",
        "assessment_validation_active": "Full Analysis / Validation active",
        "assessment_needed": "Full Analysis needed",
        "buy_assessment": "Buy Full Analysis",
        "start_monitoring": "Start Monitoring",
        "buy_more_credits": "Buy More Credits",
        "manage_subscription": "Manage subscription",
    },
    "de": {
        "overview": "Ueberblick",
        "subscription": "Produktzugriff",
        "credits_needed": "Credits benoetigt",
        "loading": "Wird geladen...",
        "last_updated": "Zuletzt aktualisiert",
        "scanned_records": "Gescannte Datensaetze",
        "scanned_records_helper": "Gesamtvolumen fuer Preis- und Scope-Bewertung",
        "affected_records": "Betroffene Datensaetze",
        "affected_records_helper": "Datensaetze mit Handlungspotenzial",
        "estimated_annual_loss": "Geschaetzter Jahresverlust",
        "estimated_annual_loss_helper": "Monetarisierter Impact",
        "checks_run": "Gepruefte Checks",
        "checks_run_helper": "Tiefe dieses Scans",
        "issues_found": "Gefundene Issues",
        "issues_found_helper": "Erkannte Problemtypen",
        "roi": "ROI",
        "roi_helper": "Potenzial minus Jahreskosten",
        "module_scores": "Data Scores nach BC-Modul",
        "module_scores_helper": "Score je Modul - 0 bis 100",
        "issues_by_module": "Issues nach BC-Modul",
        "issues_by_module_helper": "Betroffene Findings je Modul",
        "recent_scans": "Letzte Scans",
        "recent_scans_helper": "Scan anklicken, um ihn zu laden",
        "date": "Datum",
        "type": "Typ",
        "score": "Score",
        "issues": "Issues",
        "headline": "Headline",
        "previous": "Zurueck",
        "next": "Weiter",
        "page": "Seite",
        "score_trend": "Score-Trend",
        "score_trend_helper": "Historie der ausgewaehlten Scans",
        "loss_trend": "Verlust-Trend",
        "loss_trend_helper": "Geschaetzter Jahresimpact",
        "paid_scan_access": "Full-Analysis-Zugriff",
        "scan_preview": "Scan-Vorschau",
        "scan_preview_helper": "Datensaetze, Empfehlungen, Aktionen",
        "estimated_monitoring_pricing": "Geschaetzter Monitoring-Preis",
        "base_price": "Basispreis",
        "data_volume_add_on": "Datenvolumen-Zuschlag",
        "estimated_monitoring_month": "Geschaetztes Monitoring / Monat",
        "annual_fixed_plan": "Jahrespreis",
        "findings": "Findings",
        "findings_helper": "Sichtbar mit bezahltem Scan-Zugriff, umsetzbar in Business Central",
        "issue": "Issue",
        "area": "Bereich",
        "severity": "Schweregrad",
        "count": "Anzahl",
        "impact": "Impact",
        "access": "Zugriff",
        "product_access": "Produktzugriff",
        "scan_credits": "Scan Credits",
        "scan_credits_helper": "Verfuegbare bezahlte Scan-Starts",
        "dashboard_access_until": "Dashboard-Zugriff bis",
        "dashboard_access_helper": "Full-Analysis-/Validation-Ergebnisfenster",
        "issue_access_until": "Issue-Zugriff bis",
        "issue_access_helper": "Datensatzdetails und Empfehlungen",
        "monthly_price": "Monatspreis",
        "monthly_price_helper": "Monitoring-Preis",
        "annual_cost": "Jahreskosten",
        "annual_cost_helper": "12-Monats-Projektion",
        "dashboard_load_error": "Das Dashboard konnte nicht geladen werden.",
        "no_module_scores": "Noch keine Modul-Scores verfuegbar.",
        "no_module_data": "Fuer diesen Scan sind noch keine Modul-Issue-Zahlen verfuegbar.",
        "no_trend_data": "Noch keine Trenddaten verfuegbar.",
        "no_scans": "Noch keine Scans verfuegbar.",
        "no_findings": "Fuer diesen Scan sind keine Findings verfuegbar.",
        "paid_access": "Bezahlter Zugriff",
        "open_in_bc": "In BC oeffnen",
        "preview_after_scan": "Die bezahlte Scan-Vorschau erscheint nach dem naechsten Scan.",
        "recommendations_available": "Empfehlungen verfuegbar",
        "affected": "betroffen",
        "monitoring_active": "Monitoring aktiv",
        "assessment_validation_active": "Full Analysis / Validation aktiv",
        "assessment_needed": "Full Analysis benoetigt",
        "buy_assessment": "Full Analysis kaufen",
        "start_monitoring": "Monitoring starten",
        "buy_more_credits": "Weitere Credits kaufen",
        "manage_subscription": "Abo verwalten",
    },
}

SEVERITY_LABELS = {
    "en": {"critical": "Critical", "high": "High", "medium": "Medium", "low": "Low"},
    "de": {"critical": "Kritisch", "high": "Hoch", "medium": "Mittel", "low": "Niedrig"},
}

MODULE_LABELS = {
    "en": {},
    "de": {
        "System": "System",
        "Finance": "Finanzen",
        "Sales": "Verkauf",
        "Purchasing": "Einkauf",
        "Inventory": "Lager",
        "CRM": "CRM",
        "Manufacturing": "Produktion",
        "Service": "Service",
        "Jobs": "Projekte",
        "HR": "Personal",
    },
}


def _ui(lang: str) -> dict[str, str]:
    normalized = normalize_language(lang)
    merged = dict(DASHBOARD_UI.get(normalized, DASHBOARD_UI["en"]))
    merged.update(dashboard_ui_translations(normalized))
    return merged


def _module_label(name: str, lang: str) -> str:
    return MODULE_LABELS.get(normalize_language(lang), {}).get(name, name)


def _severity_label(value: str, lang: str) -> str:
    severity = _normalize_severity(value)
    return SEVERITY_LABELS.get(normalize_language(lang), SEVERITY_LABELS["en"]).get(severity, severity.title())


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value or default)
    except (TypeError, ValueError):
        return default


def _normalize_severity(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in {"critical", "high", "medium", "low"}:
        return text
    return "low"


def _severity_rank(value: Any) -> int:
    severity = _normalize_severity(value)
    if severity == "critical":
        return 0
    if severity == "high":
        return 1
    if severity == "medium":
        return 2
    return 3


def _normalize_plan(value: Any) -> str:
    plan = str(value or "").strip().lower()
    if plan in {"free", "standard", "premium"}:
        return "premium" if plan == "standard" else plan
    return "free"


def _issue_group_from_code(code: str) -> str:
    code_upper = (code or "").upper()

    # CRM
    if code_upper.startswith("CUSTOMERS_") or code_upper.startswith("CUSTOMER_"):
        return "CRM"

    # Purchasing
    if code_upper.startswith("VENDORS_") or code_upper.startswith("VENDOR_"):
        return "Purchasing"
    if code_upper.startswith("PURCHASE_") or code_upper.startswith("PURCH_"):
        return "Purchasing"

    # Inventory
    if code_upper.startswith("ITEMS_") or code_upper.startswith("ITEM_"):
        return "Inventory"
    if code_upper.startswith("INVENTORY_"):
        return "Inventory"
    if (
        code_upper.startswith("WAREHOUSE_")
        or code_upper.startswith("VALUE_ENTRY_")
        or code_upper.startswith("VALUE_ENTRIES_")
    ):
        return "Inventory"

    # Sales
    if code_upper.startswith("SALES_") or code_upper.startswith("SALE_"):
        return "Sales"

    # Finance
    if code_upper.startswith("GL_") or code_upper.startswith("G_L_") or "LEDGER" in code_upper:
        return "Finance"

    # Service
    if (
        code_upper.startswith("SERVICE_")
        or code_upper.startswith("SERV_")
        or code_upper.startswith("SERVICE_ITEM_")
    ):
        return "Service"

    # Jobs
    if code_upper.startswith("JOB_") or code_upper.startswith("JOBS_"):
        return "Jobs"

    # HR
    if (
        code_upper.startswith("HR_")
        or code_upper.startswith("EMPLOYEE_")
        or code_upper.startswith("EMPLOYEES_")
        or code_upper.startswith("RESOURCE_")
    ):
        return "HR"

    # Manufacturing
    if (
        code_upper.startswith("MFG_")
        or code_upper.startswith("MANUFACTURING_")
        or code_upper.startswith("PRODUCTION_")
        or code_upper.startswith("PROD_")
        or code_upper.startswith("BOM_")
        or code_upper.startswith("ROUTING_")
        or code_upper.startswith("WORKCENTER_")
        or code_upper.startswith("MACHINECENTER_")
    ):
        return "Manufacturing"

    # System
    if code_upper.startswith("SYSTEM_"):
        return "System"

    return "System"


def _normalize_issue_category(category: str | None, code: str) -> str:
    normalized = str(category or "").strip().upper()
    if normalized == "SYSTEM":
        return "System"
    if normalized == "FINANCE":
        return "Finance"
    if normalized == "SALES":
        return "Sales"
    if normalized in {"PURCHASE", "PURCHASING"}:
        return "Purchasing"
    if normalized in {"INVENTORY", "ITEM"}:
        return "Inventory"
    if normalized in {"CRM", "CUSTOMER"}:
        return "CRM"
    if normalized == "MANUFACTURING":
        return "Manufacturing"
    if normalized == "SERVICE":
        return "Service"
    if normalized in {"JOB", "JOBS"}:
        return "Jobs"
    if normalized == "HR":
        return "HR"
    return _issue_group_from_code(code)


def _issue_recommendation(issue: ScanIssueRecord) -> str:
    preview = (issue.recommendation_preview or "").strip()
    if preview:
        return preview

    group = _normalize_issue_category(getattr(issue, "category", None), issue.code)
    if group == "CRM":
        return "Review impacted customer and relationship data and complete the missing setup in Business Central."
    if group == "Purchasing":
        return "Resolve purchasing and vendor-related setup gaps before they create follow-up workload."
    if group == "Inventory":
        return "Prioritize inventory and item issues that affect planning, costing, or stock transactions."
    if group == "Sales":
        return "Resolve sales-side issues that can reduce margin, delay fulfillment, or create rework."
    if group == "Finance":
        return "Investigate financial postings and open entries with missing or inconsistent setup."
    if group == "Service":
        return "Review service-related records and complete the missing configuration before the next service cycle."
    if group == "Jobs":
        return "Review project and job-related records so postings and planning remain consistent."
    if group == "Manufacturing":
        return "Review manufacturing-related setup and master data before it impacts planning or execution."
    if group == "HR":
        return "Review HR-related configuration and records to avoid downstream process gaps."
    return "Review the affected records and resolve the underlying setup issue in Business Central."


def _build_open_in_bc_url(bc_issue_launch_url: str | None, issue_code: str | None) -> str:
    base_url = str(bc_issue_launch_url or "").strip()
    normalized_issue_code = str(issue_code or "").strip().upper()
    if not base_url or not normalized_issue_code:
        return ""

    direct_url = _build_direct_open_in_bc_url(base_url, normalized_issue_code)
    if direct_url:
        return direct_url

    separator = "&" if "?" in base_url else "?"
    filter_value = f"'Issue Drilldown Code' IS '{normalized_issue_code}'"
    return f"{base_url}{separator}filter={quote(filter_value, safe='')}"


def _replace_bc_page_url(base_url: str, page_id: int, filter_value: str | None = None) -> str:
    parsed = urlparse(base_url)
    query_items = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in {"page", "filter"}
    ]
    query_items.append(("page", str(page_id)))
    if filter_value:
        query_items.append(("filter", filter_value))

    return urlunparse(
        parsed._replace(
            query=urlencode(query_items, doseq=True, quote_via=quote),
        )
    )


def _build_direct_open_in_bc_url(base_url: str, normalized_issue_code: str) -> str:
    customer_filters = {
        "CUSTOMERS_MISSING_NAME": "Name IS ''",
        "CUSTOMERS_MISSING_SEARCH_NAME": "'Search Name' IS ''",
        "CUSTOMERS_MISSING_ADDRESS": "Address IS ''",
        "CUSTOMERS_MISSING_CITY": "City IS ''",
        "CUSTOMERS_MISSING_POST_CODE": "'Post Code' IS ''",
        "CUSTOMERS_MISSING_COUNTRY": "'Country/Region Code' IS ''",
        "CUSTOMERS_MISSING_EMAIL": "'E-Mail' IS ''",
        "CUSTOMERS_MISSING_PHONE": "'Phone No.' IS ''",
        "CUSTOMERS_MISSING_PAYMENT_TERMS": "'Payment Terms Code' IS ''",
        "CUSTOMERS_MISSING_PAYMENT_METHOD": "'Payment Method Code' IS ''",
        "CUSTOMERS_MISSING_POSTING_GROUP": "'Customer Posting Group' IS ''",
        "CUSTOMERS_MISSING_GEN_BUS_POSTING": "'Gen. Bus. Posting Group' IS ''",
        "CUSTOMERS_MISSING_VAT_BUS_POSTING": "'VAT Bus. Posting Group' IS ''",
        "CUSTOMERS_MISSING_CREDIT_LIMIT": "'Credit Limit (LCY)' IS '0'",
    }
    vendor_filters = {
        "VENDORS_MISSING_NAME": "Name IS ''",
        "VENDORS_MISSING_SEARCH_NAME": "'Search Name' IS ''",
        "VENDORS_MISSING_ADDRESS": "Address IS ''",
        "VENDORS_MISSING_CITY": "City IS ''",
        "VENDORS_MISSING_POST_CODE": "'Post Code' IS ''",
        "VENDORS_MISSING_COUNTRY": "'Country/Region Code' IS ''",
        "VENDORS_MISSING_EMAIL": "'E-Mail' IS ''",
        "VENDORS_MISSING_PHONE": "'Phone No.' IS ''",
        "VENDORS_MISSING_PAYMENT_TERMS": "'Payment Terms Code' IS ''",
        "VENDORS_MISSING_PAYMENT_METHOD": "'Payment Method Code' IS ''",
        "VENDORS_MISSING_POSTING_GROUP": "'Vendor Posting Group' IS ''",
        "VENDORS_MISSING_GEN_BUS_POSTING": "'Gen. Bus. Posting Group' IS ''",
        "VENDORS_MISSING_VAT_BUS_POSTING": "'VAT Bus. Posting Group' IS ''",
        "VENDORS_MISSING_BANK_ACCOUNT": "'Preferred Bank Account Code' IS ''",
    }
    direct_page_ids = {
        "ITEMS_NEGATIVE_INVENTORY": 53136,
        "ITEMS_WITHOUT_UNIT_COST": 53137,
        "BLOCKED_ITEMS_WITH_INVENTORY": 53138,
        "ITEMS_WITHOUT_UNIT_PRICE": 53148,
    }

    if normalized_issue_code in customer_filters:
        return _replace_bc_page_url(base_url, 53156, customer_filters[normalized_issue_code])
    if normalized_issue_code in vendor_filters:
        return _replace_bc_page_url(base_url, 53157, vendor_filters[normalized_issue_code])
    if normalized_issue_code in direct_page_ids:
        return _replace_bc_page_url(base_url, direct_page_ids[normalized_issue_code])

    return ""



def _load_recent_scans_desc(tenant_id: str, limit: int | None = None) -> list[Scan]:
    with SessionLocal() as db:
        query = (
            select(Scan)
            .where(Scan.tenant_id == tenant_id)
            .order_by(Scan.generated_at_utc.desc(), Scan.id.desc())
        )
        if limit is not None:
            query = query.limit(limit)

        scans = db.scalars(query).all()
    return list(scans)


def _load_scan_issues(scan_id: str) -> list[ScanIssueRecord]:
    with SessionLocal() as db:
        issues = db.scalars(select(ScanIssueRecord).where(ScanIssueRecord.scan_id == scan_id)).all()

    return sorted(
        issues,
        key=lambda row: (
            -_safe_float(row.estimated_impact_eur),
            _severity_rank(row.severity),
            -_safe_int(row.affected_count),
            row.code,
        ),
    )


def _has_profile_data(scan: Scan) -> bool:
    return any(
        _safe_int(value) > 0
        for value in (
            scan.total_records,
            scan.customers_count,
            scan.vendors_count,
            scan.items_count,
            scan.customer_ledger_entries_count,
            scan.vendor_ledger_entries_count,
            scan.item_ledger_entries_count,
            scan.sales_headers_count,
            scan.sales_lines_count,
            scan.purchase_headers_count,
            scan.purchase_lines_count,
            scan.gl_entries_count,
            scan.value_entries_count,
            scan.warehouse_entries_count,
        )
    )


def _has_commercial_data(scan: Scan) -> bool:
    return any(
        _safe_float(value) > 0
        for value in (
            scan.estimated_loss_eur,
            scan.potential_saving_eur,
            scan.estimated_premium_price_monthly,
        )
    )


def _is_valid_dashboard_scan(scan: Scan) -> bool:
    if _has_profile_data(scan):
        return True
    if _safe_int(scan.checks_count) > 0 and _safe_int(scan.issues_count) >= 0:
        return True
    if _has_commercial_data(scan):
        return True
    return False


def _select_active_scan(scans_desc: list[Scan], selected_scan_id: str | None) -> Scan:
    if not scans_desc:
        raise ValueError("At least one scan is required.")

    if selected_scan_id:
        for scan in scans_desc:
            if scan.scan_id == selected_scan_id:
                return scan

    for scan in scans_desc:
        if _is_valid_dashboard_scan(scan):
            return scan

    return scans_desc[0]


def _build_trend_points(
    scans_desc: list[Scan],
    active_scan_id: str,
    value_attr: str,
    max_points: int = 12,
) -> list[dict[str, Any]]:
    active_index = 0
    for index, scan in enumerate(scans_desc):
        if scan.scan_id == active_scan_id:
            active_index = index
            break

    visible_desc = scans_desc[active_index : active_index + max_points]
    visible_asc = list(reversed(visible_desc))

    return [
        {
            "scan_id": scan.scan_id,
            "label": scan.generated_at_utc.strftime("%d.%m"),
            "timestamp": scan.generated_at_utc.strftime("%d.%m.%Y %H:%M:%S"),
            "value": round(_safe_float(getattr(scan, value_attr, 0)), 2),
            "scan_type": scan.scan_type,
            "is_selected": scan.scan_id == active_scan_id,
        }
        for scan in visible_asc
    ]


def _scan_mode_label(scan_type: str | None, fallback: str | None) -> str:
    normalized = (scan_type or fallback or "").strip().lower()
    if normalized in {"deep", "premium_deep"}:
        return "Deep Scan"
    if normalized == "free_deep":
        return "Deep Scan"
    return "Quick Scan"


MODULE_SCORE_ORDER = [
    "System",
    "Finance",
    "Sales",
    "Purchasing",
    "Inventory",
    "CRM",
    "Manufacturing",
    "Service",
    "Jobs",
    "HR",
]


def _score_variant(score: int) -> str:
    safe_score = max(0, min(100, _safe_int(score)))
    if safe_score <= 60:
        return "critical"
    if safe_score <= 75:
        return "warning"
    if safe_score <= 85:
        return "moderate"
    if safe_score <= 95:
        return "good"
    return "excellent"


def _build_module_scores_from_scan(
    scan: Scan,
    active_modules: list[str] | None = None,
    language: str = "en",
) -> list[dict[str, Any]]:
    items = [
        ("System", _safe_int(getattr(scan, "system_score", 0))),
        ("Finance", _safe_int(getattr(scan, "finance_score", 0))),
        ("Sales", _safe_int(getattr(scan, "sales_score", 0))),
        ("Purchasing", _safe_int(getattr(scan, "purchasing_score", 0))),
        ("Inventory", _safe_int(getattr(scan, "inventory_score", 0))),
        ("CRM", _safe_int(getattr(scan, "crm_score", 0))),
        ("Manufacturing", _safe_int(getattr(scan, "manufacturing_score", 0))),
        ("Service", _safe_int(getattr(scan, "service_score", 0))),
        ("Jobs", _safe_int(getattr(scan, "jobs_score", 0))),
        ("HR", _safe_int(getattr(scan, "hr_score", 0))),
    ]
    active_names = set(active_modules or _active_module_names(scan))
    return [
        {
            "name": name,
            "score": max(0, min(100, score)),
            "value": max(0, min(100, score)),
            "label": _module_label(name, language),
            "variant": _score_variant(score),
        }
        for name, score in items
        if name in active_names
    ]


def _has_module_scores(scan: Scan) -> bool:
    return any(
        _safe_int(value) > 0
        for value in (
            getattr(scan, "system_score", 0),
            getattr(scan, "finance_score", 0),
            getattr(scan, "sales_score", 0),
            getattr(scan, "purchasing_score", 0),
            getattr(scan, "inventory_score", 0),
            getattr(scan, "crm_score", 0),
            getattr(scan, "manufacturing_score", 0),
            getattr(scan, "service_score", 0),
            getattr(scan, "jobs_score", 0),
            getattr(scan, "hr_score", 0),
        )
    )


def _build_module_counts(scan: Scan) -> dict[str, int]:
    return {
        "System": 0,
        "Finance": _safe_int(scan.customer_ledger_entries_count) + _safe_int(scan.vendor_ledger_entries_count) + _safe_int(scan.gl_entries_count),
        "Sales": _safe_int(scan.sales_headers_count) + _safe_int(scan.sales_lines_count),
        "Purchasing": _safe_int(scan.purchase_headers_count) + _safe_int(scan.purchase_lines_count),
        "Inventory": _safe_int(scan.items_count) + _safe_int(scan.item_ledger_entries_count) + _safe_int(scan.value_entries_count) + _safe_int(scan.warehouse_entries_count),
        "CRM": _safe_int(scan.customers_count),
        "Manufacturing": 0,
        "Service": 0,
        "Jobs": 0,
        "HR": 0,
    }


MODULE_SCORE_ORDER = [
    "System",
    "Finance",
    "Sales",
    "Purchasing",
    "Inventory",
    "CRM",
    "Manufacturing",
    "Service",
    "Jobs",
    "HR",
]

def _stored_enabled_modules(scan: Scan) -> list[str]:
    raw_value = str(getattr(scan, "enabled_modules", "") or "").strip()
    if not raw_value:
        return []

    enabled = []
    for value in raw_value.split(","):
        name = value.strip()
        if name in MODULE_SCORE_ORDER and name not in enabled:
            enabled.append(name)
    return enabled


def _active_module_names(scan: Scan, issue_groups: dict[str, int] | None = None) -> list[str]:
    stored_enabled = _stored_enabled_modules(scan)
    if stored_enabled:
        return stored_enabled

    issues_by_module = issue_groups or {}
    module_scores = {
        "System": _safe_int(getattr(scan, "system_score", 100)),
        "Finance": _safe_int(getattr(scan, "finance_score", 100)),
        "Sales": _safe_int(getattr(scan, "sales_score", 100)),
        "Purchasing": _safe_int(getattr(scan, "purchasing_score", 100)),
        "Inventory": _safe_int(getattr(scan, "inventory_score", 100)),
        "CRM": _safe_int(getattr(scan, "crm_score", 100)),
        "Manufacturing": _safe_int(getattr(scan, "manufacturing_score", 100)),
        "Service": _safe_int(getattr(scan, "service_score", 100)),
        "Jobs": _safe_int(getattr(scan, "jobs_score", 100)),
        "HR": _safe_int(getattr(scan, "hr_score", 100)),
    }
    active_names: list[str] = []

    for name in MODULE_SCORE_ORDER:
        if _safe_int(issues_by_module.get(name, 0)) > 0 or module_scores.get(name, 100) < 100:
            active_names.append(name)

    return active_names


def _build_profile_cards(scan: Scan, active_modules: list[str] | None = None) -> list[dict[str, Any]]:
    module_counts = _build_module_counts(scan)
    names = active_modules or MODULE_SCORE_ORDER
    return [{"label": name, "value": module_counts.get(name, 0)} for name in names]


def _severity_counts(issues: list[ScanIssueRecord]) -> dict[str, int]:
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for issue in issues:
        severity = _normalize_severity(issue.severity)
        if severity not in counts:
            severity = "low"
        counts[severity] += 1
    return counts


def _issue_distribution(issue_groups: dict[str, int], lang: str) -> list[dict[str, Any]]:
    total = max(sum(max(int(value or 0), 0) for value in issue_groups.values()), 0)
    if total <= 0:
        return []
    return [
        {
            "name": _module_label(name, lang),
            "count": count,
            "percent": round((count / total) * 100, 1),
        }
        for name, count in sorted(
            issue_groups.items(),
            key=lambda item: (-item[1], MODULE_SCORE_ORDER.index(item[0]) if item[0] in MODULE_SCORE_ORDER else 999),
        )
        if count > 0
    ]


def _records_by_module(scan: Scan, lang: str) -> list[dict[str, Any]]:
    module_counts = _build_module_counts(scan)
    return [
        {"name": _module_label(name, lang), "count": count}
        for name, count in sorted(
            module_counts.items(),
            key=lambda item: (-item[1], MODULE_SCORE_ORDER.index(item[0]) if item[0] in MODULE_SCORE_ORDER else 999),
        )
        if count > 0
    ]


def _dashboard_page_state(product_access: dict[str, Any], *, has_scan: bool) -> dict[str, Any]:
    premium_locked_copy = "Requires active Full Analysis, Validation Check, or Monitoring access."
    return {
        "overview": {"locked": False, "available": has_scan},
        "analytics": {"locked": not bool(product_access.get("can_view_issues")), "available": has_scan, "lock_reason": premium_locked_copy},
        "issues": {"locked": not bool(product_access.get("can_view_issues")), "available": has_scan, "lock_reason": premium_locked_copy},
        "actions": {"locked": not bool(product_access.get("can_view_actions")), "available": has_scan, "lock_reason": premium_locked_copy},
        "reports": {"locked": not bool(product_access.get("can_view_reports")), "available": has_scan, "lock_reason": premium_locked_copy},
        "subscription": {"locked": False, "available": True},
        "settings": {"locked": False, "available": True},
    }


def _get_current_plan_price_monthly(tenant: Tenant | None, scan: Scan | None) -> float:
    if tenant is None or scan is None:
        return 0.0

    plan = _normalize_plan(getattr(tenant, "current_plan", "free"))
    if plan == "free":
        return 0.0

    try:
        with SessionLocal() as db:
            pricing = build_tier_pricing_payload(db, record_count=_safe_int(scan.total_records))
            monthly = pricing["prices"].get(PRODUCT_MONITORING_MONTHLY, {})
            return round(_safe_float(monthly.get("amount_eur")), 2)
    except Exception:
        if plan == "premium":
            return round(_safe_float(getattr(scan, "estimated_premium_price_monthly", 0.0)), 2)
        return 0.0


def _get_premium_pricing_breakdown(scan: Scan | None) -> dict[str, Any]:
    with SessionLocal() as db:
        pricing = build_tier_pricing_payload(
            db,
            record_count=_safe_int(getattr(scan, "total_records", 0)) if scan is not None else 0,
        )
    monthly = pricing["prices"].get(PRODUCT_MONITORING_MONTHLY, {})
    annual = pricing["prices"].get(PRODUCT_MONITORING_ANNUAL, {})
    monthly_price = _safe_float(monthly.get("amount_eur"), 0.0)
    annual_price = _safe_float(annual.get("amount_eur"), 0.0)
    return {
        "base_price_monthly": monthly_price,
        "step_records": 0,
        "price_per_step": 0.0,
        "variable_price_monthly": 0.0,
        "raw_price_monthly": monthly_price,
        "final_price_monthly": monthly_price,
        "annual_fixed_price": annual_price,
        "pricing_tier": pricing["pricing_tier"],
        "contact_sales": pricing["contact_sales"],
        "monthly_note": "Tenant-tier Monitoring Monthly price from Pricing Matrix.",
        "annual_note": "Tenant-tier Monitoring Annual price from Pricing Matrix.",
    }

def _analytics_demo_mode_enabled() -> bool:
    return bool(settings.ANALYTICS_DEMO_MODE) and settings.ENV.strip().lower() != "prod"


def _build_demo_dashboard_payload(
    company: str,
    environment: str,
    scan_mode: str | None,
    language: str = "en",
) -> dict[str, Any]:
    with SessionLocal() as db:
        default_pricing = build_monitoring_pricing_breakdown(db)
        product_pricing = get_public_product_pricing_payload(db)
        tenant_pricing = build_tier_pricing_payload(db, record_count=24850)

    lang = normalize_language(language)
    ui = _ui(lang)
    generated_at = datetime.now(timezone.utc)
    last_updated = generated_at.strftime("%d.%m.%Y %H:%M:%S")
    demo_scan_id = "demo_preview_scan"
    product_access = {
        "can_view_free_insights": True,
        "can_view_issues": False,
        "can_view_actions": False,
        "can_view_reports": False,
        "can_view_record_details": False,
        "monitoring_active": False,
    }
    demo_issues = [
        {
            "code": "DEMO_MASTER_DATA_QUALITY",
            "title": "Demo: Missing master data on customer records",
            "severity": "critical",
            "severity_label": _severity_label("critical", lang),
            "count": 184,
            "impact_eur": 42800.0,
            "group": _module_label("CRM", lang),
            "recommendation_preview": "Sample recommendation: complete required posting and contact fields before the next billing run.",
            "premium_only": False,
            "open_in_bc_url": None,
        },
        {
            "code": "DEMO_DUPLICATE_VENDORS",
            "title": "Demo: Potential duplicate vendor records",
            "severity": "high",
            "severity_label": _severity_label("high", lang),
            "count": 67,
            "impact_eur": 23600.0,
            "group": _module_label("Purchasing", lang),
            "recommendation_preview": "Sample recommendation: merge duplicate vendor profiles and lock inactive payment targets.",
            "premium_only": False,
            "open_in_bc_url": None,
        },
        {
            "code": "DEMO_INVENTORY_RISK",
            "title": "Demo: Inconsistent item and inventory records",
            "severity": "medium",
            "severity_label": _severity_label("medium", lang),
            "count": 129,
            "impact_eur": 18500.0,
            "group": _module_label("Inventory", lang),
            "recommendation_preview": "Sample recommendation: align item status, costing setup, and warehouse handling rules.",
            "premium_only": False,
            "open_in_bc_url": None,
        },
    ]
    module_scores = [
        {"name": "Finance", "score": 71, "value": 71, "label": _module_label("Finance", lang), "variant": _score_variant(71)},
        {"name": "Sales", "score": 76, "value": 76, "label": _module_label("Sales", lang), "variant": _score_variant(76)},
        {"name": "Purchasing", "score": 63, "value": 63, "label": _module_label("Purchasing", lang), "variant": _score_variant(63)},
        {"name": "Inventory", "score": 68, "value": 68, "label": _module_label("Inventory", lang), "variant": _score_variant(68)},
        {"name": "CRM", "score": 58, "value": 58, "label": _module_label("CRM", lang), "variant": _score_variant(58)},
    ]
    issue_groups = [
        {"name": _module_label("CRM", lang), "count": 184},
        {"name": _module_label("Purchasing", lang), "count": 67},
        {"name": _module_label("Inventory", lang), "count": 129},
        {"name": _module_label("Finance", lang), "count": 41},
    ]
    recent_scans = [
        {"scan_id": demo_scan_id, "generated_at": last_updated, "scan_type": "demo_preview", "data_score": 68, "issues_count": 421, "headline": "Demo Preview - Sample data", "is_selected": True, "is_valid": True},
        {"scan_id": "demo_preview_previous", "generated_at": (generated_at - timedelta(days=31)).strftime("%d.%m.%Y %H:%M:%S"), "scan_type": "demo_preview", "data_score": 72, "issues_count": 389, "headline": "Demo Preview - Previous sample", "is_selected": False, "is_valid": True},
    ]
    score_trend = [
        {"scan_id": "demo_preview_previous", "label": (generated_at - timedelta(days=31)).strftime("%d.%m"), "timestamp": (generated_at - timedelta(days=31)).strftime("%d.%m.%Y %H:%M:%S"), "value": 72, "scan_type": "demo_preview", "is_selected": False},
        {"scan_id": demo_scan_id, "label": generated_at.strftime("%d.%m"), "timestamp": last_updated, "value": 68, "scan_type": "demo_preview", "is_selected": True},
    ]
    loss_trend = [
        {"scan_id": "demo_preview_previous", "label": (generated_at - timedelta(days=31)).strftime("%d.%m"), "timestamp": (generated_at - timedelta(days=31)).strftime("%d.%m.%Y %H:%M:%S"), "value": 64200.0, "scan_type": "demo_preview", "is_selected": False},
        {"scan_id": demo_scan_id, "label": generated_at.strftime("%d.%m"), "timestamp": last_updated, "value": 84900.0, "scan_type": "demo_preview", "is_selected": True},
    ]

    return {
        "is_demo": True,
        "data_source": "demo_preview",
        "title": "BCSentinel Analytics",
        "language": lang,
        "ui": ui,
        "subtitle": f"Demo Preview - Sample data - {company} - {environment}",
        "scan_mode_label": _scan_mode_label("demo_preview", scan_mode),
        "last_updated": last_updated,
        "selected_scan_id": demo_scan_id,
        "current_plan": "free",
        "product_access": product_access,
        "visibility": {
            "is_premium": False,
            "can_view_free_insights": True,
            "show_findings": False,
            "show_trends": False,
            "show_upgrade_preview": True,
        },
        "hero": {
            "eyebrow": "Demo Preview - Sample data",
            "headline_prefix": "Your sample data health is",
            "headline_highlight": "at risk",
            "headline_suffix": "and ready for dashboard review.",
        },
        "score_label": "Demo Preview Score",
        "kpis": {
            "health_score": 68,
            "total_records": 24850,
            "affected_records": 421,
            "estimated_premium_price_monthly": round(_safe_float(default_pricing.get("final_price_monthly")), 2),
            "estimated_loss_eur": 84900.0,
            "potential_saving_eur": 51700.0,
            "roi_eur": 49912.0,
            "checks_run": 312,
            "issues_count": 421,
        },
        "profile_cards": [
            {"label": "Customers", "value": 4200, "helper": "Demo sample"},
            {"label": "Vendors", "value": 1380, "helper": "Demo sample"},
            {"label": "Items", "value": 9270, "helper": "Demo sample"},
            {"label": "Ledger Entries", "value": 10000, "helper": "Demo sample"},
        ],
        "module_counts": {"System": 0, "Finance": 41, "Sales": 52, "Purchasing": 67, "Inventory": 129, "CRM": 184, "Manufacturing": 0, "Service": 0, "Jobs": 0, "HR": 0},
        "module_scores": module_scores,
        "top_risk_modules": module_scores[-3:],
        "recent_scans": recent_scans,
        "recent_scans_pagination": {"page": 1, "page_size": 10, "total_items": len(recent_scans), "total_pages": 1, "has_prev": False, "has_next": False},
        "score_trend": score_trend,
        "loss_trend": loss_trend,
        "issue_groups": issue_groups,
        "top_findings": [],
        "free_insights": {
            "top_findings": demo_issues,
            "business_impacts": [{"title": item["title"], "group": item["group"], "impact_eur": item["impact_eur"], "count": item["count"]} for item in demo_issues],
            "module_distribution": issue_groups,
            "records_by_module": [
                {"name": _module_label("CRM", lang), "count": 4200},
                {"name": _module_label("Purchasing", lang), "count": 1380},
                {"name": _module_label("Inventory", lang), "count": 9270},
            ],
            "active_issues_summary": {"critical": 1, "high": 1, "medium": 1, "low": 0},
        },
        "critical_issues_summary": {"critical": 1, "high": 1, "medium": 1, "low": 0, "total": 421},
        "recommended_actions": [
            {"issue": item["title"], "suggested_action": item["recommendation_preview"], "priority": item["severity"], "potential_saving_eur": item["impact_eur"], "effort": "Sample"}
            for item in demo_issues
        ],
        "issue_preview": demo_issues,
        "premium_preview_findings": [{"title": item["title"], "group": item["group"], "count": item["count"], "impact_eur": item["impact_eur"], "recommendation_preview": item["recommendation_preview"]} for item in demo_issues],
        "premium_unlock": {
            "headline": "Demo Preview shows how Full Analysis will explain business impact.",
            "body": "This is synthetic sample data for local dashboard review. Real scan data always replaces this preview.",
            "button_label": ui["buy_assessment"],
            "button_action": "checkout",
            "highlights": ["Sample affected records", "Sample recommendations", "Sample business impact"],
        },
        "pricing_breakdown": default_pricing,
        "product_pricing": product_pricing,
        "tenant_pricing": tenant_pricing,
        "pages": _dashboard_page_state(product_access, has_scan=True),
        "issues_page": {"locked": True, "items": [], "empty": False},
        "actions_page": {"locked": True, "items": [], "empty": False},
        "reports_page": {"locked": True, "items": [], "empty": False},
        "settings_page": {"locked": False, "tenant_id": None, "company": company, "language": lang, "last_scan": last_updated, "connection_status": "demo_preview"},
        "scan_information": {"scan_id": demo_scan_id, "scan_type": "demo_preview", "last_updated": last_updated, "records": 24850, "checks_run": 312, "data_source": "demo_preview"},
        "monitoring_preview": {"status": "demo_preview", "frequency": "daily sample status", "last_check": last_updated, "trend": "sample deterioration versus previous scan", "alert": "Sample alert: critical deterioration detected"},
        "subscription": {
            "plan_label": "Demo Preview",
            "price_monthly": 0.0,
            "annual_cost": 0.0,
            "cta_label": ui["buy_assessment"],
            "cta_action": "checkout",
            "cta_product_code": PRODUCT_FULL_ANALYSIS,
            "plan_note": "Synthetic local preview. Real scans and real access rights take precedence.",
            "pricing_breakdown": default_pricing,
            "billing_options": {"monthly_label": "Monthly billing", "monthly_note": default_pricing.get("monthly_note", ""), "annual_label": ui["annual_fixed_plan"], "annual_note": default_pricing.get("annual_note", "")},
        },
    }

def _build_fallback_payload(company: str, environment: str, scan_mode: str | None, language: str = "en") -> dict[str, Any]:
    with SessionLocal() as db:
        default_pricing = build_monitoring_pricing_breakdown(db)
        product_pricing = get_public_product_pricing_payload(db)
        tenant_pricing = build_tier_pricing_payload(db, record_count=0)
    fallback_monthly = _safe_float(default_pricing.get("final_price_monthly"), 0.0)
    lang = normalize_language(language)
    ui = _ui(lang)

    return {
        "title": "BCSentinel Analytics",
        "language": lang,
        "ui": ui,
        "subtitle": f"{company} - {environment}",
        "scan_mode_label": _scan_mode_label(None, scan_mode),
        "last_updated": datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M:%S"),
        "selected_scan_id": None,
        "current_plan": "free",
        "visibility": {
            "is_premium": False,
            "can_view_free_insights": False,
            "show_findings": False,
            "show_trends": False,
            "show_upgrade_preview": True,
        },
        "hero": {
            "eyebrow": "Data Health Score zuerst. Full Analysis fuer Details." if lang == "de" else "Data Health Score first. Full Analysis unlocks the details.",
            "headline_prefix": "Deine Datenqualitaet ist" if lang == "de" else "Your data health is",
            "headline_highlight": "kritisch" if lang == "de" else "critical",
            "headline_suffix": "und braucht Aufmerksamkeit." if lang == "de" else "and requires immediate attention.",
        },
        "kpis": {
            "health_score": 0,
            "total_records": 0,
            "affected_records": 0,
            "estimated_premium_price_monthly": fallback_monthly,
            "estimated_loss_eur": 0.0,
            "potential_saving_eur": 0.0,
            "roi_eur": 0.0,
            "checks_run": 0,
            "issues_count": 0,
        },
        "profile_cards": [],
        "module_counts": {name: 0 for name in MODULE_SCORE_ORDER},
        "module_scores": [],
        "recent_scans": [],
        "recent_scans_pagination": {
            "page": 1,
            "page_size": 10,
            "total_items": 0,
            "total_pages": 1,
            "has_prev": False,
            "has_next": False,
        },
        "score_trend": [],
        "loss_trend": [],
        "issue_groups": [],
        "top_findings": [],
        "free_insights": {
            "top_findings": [],
            "business_impacts": [],
            "module_distribution": [],
            "records_by_module": [],
            "active_issues_summary": {"critical": 0, "high": 0, "medium": 0, "low": 0},
        },
        "premium_preview_findings": [],
        "premium_unlock": {
            "headline": "Full Analysis oeffnet Datensatzdetails und konkrete Aktionen." if lang == "de" else "Full Analysis unlocks record-level details and direct action.",
            "body": "Kaufe Full Analysis, Validation Check oder Monitoring, um betroffene Datensaetze, Empfehlungen und Business-Central-Aktionen zu sehen." if lang == "de" else "Buy Full Analysis, Validation Check, or Monitoring to see affected records, recommendations, and Business Central actions for your highest-impact issues.",
            "button_label": ui["buy_assessment"],
            "button_action": "checkout",
            "highlights": [
                "Betroffene Datensaetze und Issue-Details" if lang == "de" else "Affected records and issue details",
                "Handlungsempfehlungen" if lang == "de" else "Action recommendations",
                "Business-Central-Navigation" if lang == "de" else "Business Central navigation",
            ],
        },
        "pricing_breakdown": default_pricing,
        "product_pricing": product_pricing,
        "tenant_pricing": tenant_pricing,
        "pages": _dashboard_page_state({}, has_scan=False),
        "issues_page": {"locked": True, "items": [], "empty": True},
        "actions_page": {"locked": True, "items": [], "empty": True},
        "reports_page": {"locked": True, "items": [], "empty": True},
        "settings_page": {"locked": False, "tenant_id": None, "company": company, "language": lang, "last_scan": None},
        "subscription": {
            "plan_label": ui["assessment_needed"],
            "price_monthly": 0.0,
            "annual_cost": 0.0,
            "cta_label": ui["buy_assessment"],
            "cta_action": "checkout",
            "cta_product_code": PRODUCT_FULL_ANALYSIS,
            "plan_note": "Insight startet mit dem Data Health Score. Full Analysis oeffnet Details." if lang == "de" else "Insight starts with the Data Health Score. Full Analysis opens the details.",
            "pricing_breakdown": default_pricing,
            "billing_options": {
                "monthly_label": "Monatliche Abrechnung" if lang == "de" else "Monthly billing",
                "monthly_note": default_pricing.get("monthly_note", ""),
                "annual_label": ui["annual_fixed_plan"],
                "annual_note": default_pricing.get("annual_note", ""),
            },
        },
    }


def _hero_copy_for_score(score: int) -> dict[str, str]:
    if score <= 60:
        return {
            "headline_prefix": "Your data health is",
            "headline_highlight": "critical",
            "headline_suffix": "and costing money.",
        }
    if score <= 75:
        return {
            "headline_prefix": "Your data health needs",
            "headline_highlight": "attention",
            "headline_suffix": "before process friction gets worse.",
        }
    if score <= 85:
        return {
            "headline_prefix": "Your data health score is",
            "headline_highlight": "moderate",
            "headline_suffix": "with meaningful room for improvement.",
        }
    if score <= 95:
        return {
            "headline_prefix": "Your data health score is",
            "headline_highlight": "good",
            "headline_suffix": "with a few improvement opportunities left.",
        }
    return {
        "headline_prefix": "Your data health score is",
        "headline_highlight": "excellent",
        "headline_suffix": "with very low operational risk.",
    }


def _hero_copy_for_score_de(score: int) -> dict[str, str]:
    if score <= 60:
        return {
            "headline_prefix": "Deine Datenqualitaet ist",
            "headline_highlight": "kritisch",
            "headline_suffix": "und kostet Geld.",
        }
    if score <= 75:
        return {
            "headline_prefix": "Deine Datenqualitaet braucht",
            "headline_highlight": "Aufmerksamkeit",
            "headline_suffix": "bevor Prozessreibung groesser wird.",
        }
    if score <= 85:
        return {
            "headline_prefix": "Dein Data Health Score ist",
            "headline_highlight": "mittel",
            "headline_suffix": "mit spuerbarem Verbesserungspotenzial.",
        }
    if score <= 95:
        return {
            "headline_prefix": "Dein Data Health Score ist",
            "headline_highlight": "gut",
            "headline_suffix": "mit wenigen offenen Verbesserungsmoeglichkeiten.",
        }
    return {
        "headline_prefix": "Dein Data Health Score ist",
        "headline_highlight": "exzellent",
        "headline_suffix": "mit sehr geringem operativem Risiko.",
    }


def _build_dashboard_payload(
    company: str,
    environment: str,
    tenant: Tenant | None,
    scan_mode: str | None,
    selected_scan_id: str | None,
    recent_scans_page: int = 1,
    recent_scans_page_size: int = 10,
    bc_issue_launch_url: str | None = None,
) -> dict[str, Any]:
    lang = tenant_language(tenant)
    if tenant is None:
        return _build_fallback_payload(company, environment, scan_mode, lang)

    recent_scans_desc = _load_recent_scans_desc(tenant.tenant_id)
    if not recent_scans_desc:
        if _analytics_demo_mode_enabled():
            return _build_demo_dashboard_payload(company, environment, scan_mode, lang)
        return _build_fallback_payload(company, environment, scan_mode, lang)

    active_scan = _select_active_scan(recent_scans_desc, selected_scan_id)
    issues = _load_scan_issues(active_scan.scan_id)
    with SessionLocal() as db:
        tenant_features = get_tenant_features(db, tenant)
        product_access = build_product_access_snapshot(db, tenant)
        product_pricing = get_public_product_pricing_payload(db)
        tenant_pricing = build_tier_pricing_payload(db, record_count=_safe_int(active_scan.total_records))

    current_plan = _normalize_plan(getattr(tenant, "current_plan", "free"))
    is_premium = is_premium_actions_enabled(tenant_features) and bool(product_access["can_view_issues"])
    monitoring_active = bool(product_access["monitoring_active"])
    can_view_recommendations = "recommendations" in tenant_features

    pricing_breakdown = _get_premium_pricing_breakdown(active_scan)

    premium_price_monthly = round(
        _safe_float(pricing_breakdown.get("final_price_monthly"), 0.0),
        2,
    )

    current_plan_price_monthly = _get_current_plan_price_monthly(tenant, active_scan)
    if current_plan == "free":
        current_plan_price_monthly = 0.0
    elif current_plan_price_monthly <= 0:
        current_plan_price_monthly = premium_price_monthly

    normalized_commercials = normalize_stored_commercials(
        total_records=_safe_int(active_scan.total_records),
        estimated_loss_eur=_safe_float(active_scan.estimated_loss_eur),
        potential_saving_eur=_safe_float(active_scan.potential_saving_eur),
        estimated_premium_price_monthly=premium_price_monthly,
    )

    affected_records = sum(_safe_int(issue.affected_count) for issue in issues)

    issue_groups: dict[str, int] = {name: 0 for name in MODULE_SCORE_ORDER}
    for issue in issues:
        group = _normalize_issue_category(getattr(issue, "category", None), issue.code)
        issue_groups[group] = issue_groups.get(group, 0) + _safe_int(issue.affected_count)

    active_modules = _active_module_names(active_scan, issue_groups)
    module_scores = _build_module_scores_from_scan(active_scan, active_modules, lang)

    total_recent_scans = len(recent_scans_desc)
    page_size = max(1, recent_scans_page_size)
    total_pages = max(1, math.ceil(total_recent_scans / page_size))
    current_page = min(max(1, recent_scans_page), total_pages)

    start_index = (current_page - 1) * page_size
    end_index = start_index + page_size
    visible_recent_scans = recent_scans_desc[start_index:end_index]

    recent_scans_payload = [
        {
            "scan_id": scan.scan_id,
            "generated_at": scan.generated_at_utc.strftime("%d.%m.%Y %H:%M:%S"),
            "scan_type": scan.scan_type,
            "data_score": _safe_int(scan.data_score),
            "issues_count": _safe_int(scan.issues_count),
            "headline": scan.summary_headline,
            "is_selected": scan.scan_id == active_scan.scan_id,
            "is_valid": _is_valid_dashboard_scan(scan),
        }
        for scan in visible_recent_scans
    ]

    top_findings = [
        {
            "code": issue.code,
            "title": issue.title,
            "severity": _normalize_severity(issue.severity),
            "severity_label": _severity_label(issue.severity, lang),
            "count": _safe_int(issue.affected_count),
            "impact_eur": round(_safe_float(issue.estimated_impact_eur), 2),
            "group": _module_label(_normalize_issue_category(getattr(issue, "category", None), issue.code), lang),
            "recommendation_preview": _issue_recommendation(issue) if can_view_recommendations else "",
            "premium_only": bool(issue.premium_only),
            "open_in_bc_url": _build_open_in_bc_url(bc_issue_launch_url, issue.code),
        }
        for issue in issues
    ]
    top_findings_sorted = sorted(top_findings, key=lambda item: (-_safe_float(item.get("impact_eur")), -_safe_int(item.get("count"))))

    premium_preview_findings = [
        {
            "title": item["title"],
            "group": item["group"],
            "count": item["count"],
            "impact_eur": item["impact_eur"],
            "recommendation_preview": item["recommendation_preview"],
        }
        for item in top_findings_sorted[:5]
    ]
    business_impacts = [
        {
            "title": item["title"],
            "group": item["group"],
            "impact_eur": item["impact_eur"],
            "count": item["count"],
        }
        for item in top_findings_sorted
    ]
    pages = _dashboard_page_state(product_access, has_scan=True)
    actions_items = [
        {
            "issue": item["title"],
            "suggested_action": item["recommendation_preview"] or "Review the affected records and resolve the underlying setup issue in Business Central.",
            "priority": item["severity"],
            "potential_saving_eur": item["impact_eur"],
            "effort": None,
        }
        for item in top_findings_sorted
    ]
    report_cards = [
        {"key": "executive_summary", "title": "Executive Summary", "available": is_premium},
        {"key": "data_quality_report", "title": "Data Quality Report", "available": is_premium},
        {"key": "issue_detail_report", "title": "Issue Detail Report", "available": is_premium},
        {"key": "business_impact_report", "title": "Business Impact Report", "available": is_premium},
        {"key": "action_plan_report", "title": "Action Plan Report", "available": is_premium},
        {"key": "trend_report", "title": "Trend Report", "available": is_premium and monitoring_active},
    ]

    return {
        "title": "BCSentinel Analytics",
        "language": lang,
        "ui": _ui(lang),
        "subtitle": f"{company} - {environment}",
        "scan_mode_label": _scan_mode_label(active_scan.scan_type, scan_mode),
        "last_updated": active_scan.generated_at_utc.strftime("%d.%m.%Y %H:%M:%S"),
        "selected_scan_id": active_scan.scan_id,
        "current_plan": current_plan,
        "product_access": product_access,
        "visibility": {
            "is_premium": is_premium,
            "can_view_free_insights": bool(product_access["can_view_free_insights"]),
            "show_findings": bool(product_access["can_view_issues"]),
            "show_trends": is_premium,
            "show_upgrade_preview": not is_premium,
        },
        "hero": {
            "eyebrow": "Data Health Score zuerst. Full Analysis fuer Details." if lang == "de" else "Data Health Score first. Full Analysis unlocks the details.",
            **(_hero_copy_for_score_de(_safe_int(active_scan.data_score)) if lang == "de" else _hero_copy_for_score(_safe_int(active_scan.data_score))),
        },
        "kpis": {
            "health_score": _safe_int(active_scan.data_score),
            "total_records": _safe_int(active_scan.total_records),
            "affected_records": affected_records,
            "estimated_premium_price_monthly": float(
                normalized_commercials["estimated_premium_price_monthly"]
            ),
            "estimated_loss_eur": float(normalized_commercials["estimated_loss_eur"]),
            "potential_saving_eur": float(normalized_commercials["potential_saving_eur"]),
            "roi_eur": float(normalized_commercials["roi_eur"]),
            "checks_run": _safe_int(active_scan.checks_count),
            "issues_count": _safe_int(active_scan.issues_count),
        },
        "profile_cards": _build_profile_cards(active_scan, active_modules),
        "module_counts": _build_module_counts(active_scan),
        "module_scores": module_scores,
        "recent_scans": recent_scans_payload,
        "recent_scans_pagination": {
            "page": current_page,
            "page_size": page_size,
            "total_items": total_recent_scans,
            "total_pages": total_pages,
            "has_prev": current_page > 1,
            "has_next": current_page < total_pages,
        },
        "score_trend": _build_trend_points(recent_scans_desc, active_scan.scan_id, "data_score"),
        "loss_trend": _build_trend_points(recent_scans_desc, active_scan.scan_id, "estimated_loss_eur"),
        "issue_groups": [
            {"name": _module_label(name, lang), "count": count}
            for name, count in sorted(
                ((name, issue_groups.get(name, 0)) for name in active_modules),
                key=lambda item: (-item[1], MODULE_SCORE_ORDER.index(item[0]) if item[0] in MODULE_SCORE_ORDER else 999),
            )
        ],
        "top_findings": top_findings_sorted if is_premium else [],
        "free_insights": {
            "top_findings": [
                {
                    "title": item["title"],
                    "severity": item["severity"],
                    "severity_label": item["severity_label"],
                    "count": item["count"],
                    "impact_eur": item["impact_eur"],
                    "group": item["group"],
                }
                for item in top_findings_sorted[:5]
            ],
            "business_impacts": business_impacts,
            "module_distribution": _issue_distribution(issue_groups, lang),
            "records_by_module": _records_by_module(active_scan, lang),
            "active_issues_summary": _severity_counts(issues),
        },
        "premium_preview_findings": premium_preview_findings,
        "premium_unlock": {
            "headline": "Willst du weiter Geld verlieren oder die Ursachen beheben?" if lang == "de" else "Do you want to keep losing money or start fixing the root causes?",
            "body": "Full Analysis, Validation Check oder Monitoring zeigen betroffene Datensaetze, konkrete Empfehlungen und Priorisierung nach Business Impact." if lang == "de" else "Full Analysis, Validation Check, or Monitoring reveal the exact affected records, explain what to fix, and prioritize the work by business impact.",
            "button_label": _ui(lang)["buy_assessment"],
            "button_action": "checkout",
            "highlights": [
                "Betroffene Datensaetze in Business Central" if lang == "de" else "Affected records in Business Central",
                "Klare Empfehlungen je Issue" if lang == "de" else "Clear recommendations per issue",
                "Priorisierte Aktionen nach finanziellem Impact" if lang == "de" else "Prioritized actions by financial impact",
            ],
        },
        "pricing_breakdown": pricing_breakdown,
        "product_pricing": product_pricing,
        "tenant_pricing": tenant_pricing,
        "pages": pages,
        "issues_page": {"locked": not is_premium, "items": top_findings_sorted if is_premium else [], "empty": not bool(top_findings_sorted)},
        "actions_page": {"locked": not is_premium, "items": actions_items if is_premium else [], "empty": not bool(actions_items)},
        "reports_page": {"locked": not bool(product_access["can_view_reports"]), "items": report_cards if product_access["can_view_reports"] else [], "empty": False},
        "settings_page": {
            "locked": False,
            "tenant_id": tenant.tenant_id,
            "company": company,
            "language": lang,
            "last_scan": active_scan.generated_at_utc.isoformat(),
            "connection_status": "connected",
        },
        "subscription": {
            "plan_label": "Monitoring" if monitoring_active else (("Full Analysis / Validation aktiv" if lang == "de" else "Full Analysis / Validation access") if is_premium else ("Full Analysis benoetigt" if lang == "de" else "Full Analysis needed")),
            "price_monthly": current_plan_price_monthly if monitoring_active else 0.0,
            "annual_cost": round(current_plan_price_monthly * 12, 2) if monitoring_active else 0.0,
            "cta_label": _ui(lang)["manage_subscription"] if monitoring_active else (_ui(lang)["start_monitoring"] if is_premium else _ui(lang)["buy_more_credits"]),
            "cta_action": "portal" if monitoring_active else "checkout",
            "cta_product_code": None if monitoring_active else (PRODUCT_MONITORING_MONTHLY if is_premium else PRODUCT_FULL_ANALYSIS),
            "plan_note": ("Aktueller Monitoring-Zugriff" if lang == "de" else "Current monitoring access") if monitoring_active else (("7-Tage-Premiumzugriff aktiv" if lang == "de" else "7-day premium access active") if is_premium else ("Kaufe Full Analysis, einen Validation Check oder starte Monitoring, um Details zu oeffnen." if lang == "de" else "Buy Full Analysis, a Validation Check, or start Monitoring to open details.")),
            "pricing_breakdown": pricing_breakdown,
            "billing_options": {
                "monthly_label": "Monatliche Abrechnung" if lang == "de" else "Monthly billing",
                "monthly_note": pricing_breakdown.get("monthly_note", ""),
                "annual_label": _ui(lang)["annual_fixed_plan"],
                "annual_note": pricing_breakdown.get("annual_note", ""),
            },
        },
    }


@router.get("/analytics/get-token", response_class=JSONResponse)
def get_analytics_token(
    company: str = Query(default="CRONUS DE"),
    environment: str = Query(default="BC Cloud"),
    tenant_id: str | None = Query(default=None),
    preferred_language: str | None = Query(default=None),
    scan_mode: str | None = Query(default=None),
    bc_issue_launch_url: str | None = Query(default=None),
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
    x_preferred_language: str | None = Header(default=None, alias="X-Preferred-Language"),
):
    header_tenant_id, header_api_token = tenant_auth

    if tenant_id:
        enforce_tenant_match(tenant_id, header_tenant_id, "Query tenant_id")

    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, header_tenant_id, header_api_token)
        update_tenant_language(tenant, x_preferred_language or preferred_language)
        resolved_tenant_id = tenant.tenant_id
        resolved_language = tenant_language(tenant)
        db.commit()

    token = _create_analytics_embed_token(
        company=company,
        environment=environment,
        tenant_id=resolved_tenant_id,
        language=resolved_language,
        scan_mode=scan_mode,
        bc_issue_launch_url=bc_issue_launch_url,
    )
    return JSONResponse(
        content={
            "token": token,
            "token_type": ANALYTICS_EMBED_TOKEN_TYPE,
            "expires_in_seconds": ANALYTICS_EMBED_TOKEN_MINUTES * 60,
        }
    )


@router.get("/analytics/embed/data", response_class=JSONResponse)
def get_analytics_data(
    token: str | None = Query(default=None),
    embed_token: str | None = Query(default=None),
    analytics_cookie_token: str | None = Cookie(default=None, alias=ANALYTICS_EMBED_COOKIE_NAME),
    scan_id: str | None = Query(default=None),
    recent_scans_page: int = Query(default=1, ge=1),
    recent_scans_page_size: int = Query(default=10, ge=1, le=25),
):
    effective_token = embed_token or token or analytics_cookie_token
    if not effective_token:
        raise HTTPException(status_code=401, detail="Missing analytics embed token.")

    payload = _verify_analytics_embed_payload(effective_token)

    tenant_id = str(payload.get("tenant_id") or "").strip()
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Analytics embed token is missing tenant_id.")

    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))

    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found.")

    return JSONResponse(
        content=_build_dashboard_payload(
            company=payload.get("company", "BCSentinel"),
            environment=payload.get("environment", "BC Cloud"),
            tenant=tenant,
            scan_mode=payload.get("scan_mode"),
            selected_scan_id=scan_id,
            recent_scans_page=recent_scans_page,
            recent_scans_page_size=recent_scans_page_size,
            bc_issue_launch_url=payload.get("bc_issue_launch_url"),
        )
    )


def _load_dashboard_payload_from_embed_token(
    *,
    token: str | None,
    embed_token: str | None,
    analytics_cookie_token: str | None,
    scan_id: str | None = None,
) -> dict[str, Any]:
    effective_token = embed_token or token or analytics_cookie_token
    if not effective_token:
        raise HTTPException(status_code=401, detail="Missing analytics embed token.")

    payload = _verify_analytics_embed_payload(effective_token)
    tenant_id = str(payload.get("tenant_id") or "").strip()
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Analytics embed token is missing tenant_id.")

    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))

    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found.")

    return _build_dashboard_payload(
        company=payload.get("company", "BCSentinel"),
        environment=payload.get("environment", "BC Cloud"),
        tenant=tenant,
        scan_mode=payload.get("scan_mode"),
        selected_scan_id=scan_id,
        bc_issue_launch_url=payload.get("bc_issue_launch_url"),
    )


@router.get("/analytics/embed/{section}", response_class=JSONResponse)
def get_analytics_section(
    section: str,
    token: str | None = Query(default=None),
    embed_token: str | None = Query(default=None),
    analytics_cookie_token: str | None = Cookie(default=None, alias=ANALYTICS_EMBED_COOKIE_NAME),
    scan_id: str | None = Query(default=None),
):
    normalized_section = (section or "").strip().lower()
    if normalized_section not in {"issues", "actions", "reports"}:
        raise HTTPException(status_code=404, detail="Analytics section not found.")

    payload = _load_dashboard_payload_from_embed_token(
        token=token,
        embed_token=embed_token,
        analytics_cookie_token=analytics_cookie_token,
        scan_id=scan_id,
    )
    page_key = f"{normalized_section}_page"
    page_payload = payload.get(page_key, {})
    if page_payload.get("locked"):
        raise HTTPException(
            status_code=402,
            detail=f"{normalized_section.title()} require active Full Analysis, Validation Check, or Monitoring access.",
        )
    return JSONResponse(content=page_payload)


def _load_analytics_tenant(
    token: str | None,
    embed_token: str | None,
    analytics_cookie_token: str | None,
) -> Tenant:
    effective_token = embed_token or token or analytics_cookie_token
    if not effective_token:
        raise HTTPException(status_code=401, detail="Missing analytics embed token.")

    payload = _verify_analytics_embed_payload(effective_token)

    tenant_id = str(payload.get("tenant_id") or "").strip()
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Analytics embed token is missing tenant_id.")

    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
        if tenant is None:
            raise HTTPException(status_code=404, detail="Tenant not found.")
        require_tenant_feature(db, tenant, "quick_scan")
        return tenant


@router.post("/analytics/billing/checkout", response_class=JSONResponse)
def analytics_billing_checkout(
    token: str | None = Query(default=None),
    embed_token: str | None = Query(default=None),
    analytics_cookie_token: str | None = Cookie(default=None, alias=ANALYTICS_EMBED_COOKIE_NAME),
    product_code: str | None = Query(default=None),
):
    tenant = _load_analytics_tenant(token, embed_token, analytics_cookie_token)
    requested_product = normalize_product_code(product_code or PRODUCT_FULL_ANALYSIS)
    allowed_products = {
        PRODUCT_FULL_ANALYSIS,
        PRODUCT_VALIDATION_CHECK,
        PRODUCT_MONITORING_MONTHLY,
        PRODUCT_MONITORING_ANNUAL,
    }
    if requested_product not in allowed_products:
        raise HTTPException(status_code=400, detail="Unsupported product_code.")

    checkout_payload = CheckoutSessionRequest(
        tenant_id=tenant.tenant_id,
        product_code=requested_product,
        billing_interval="monthly",
    )

    session = create_checkout_session_for_tenant(checkout_payload)
    return JSONResponse(
        content={
            "action": "checkout",
            "provider": session.provider,
            "checkout_url": session.checkout_url,
        }
    )


@router.post("/analytics/billing/portal", response_class=JSONResponse)
def analytics_billing_portal(
    token: str | None = Query(default=None),
    embed_token: str | None = Query(default=None),
    analytics_cookie_token: str | None = Cookie(default=None, alias=ANALYTICS_EMBED_COOKIE_NAME),
):
    tenant = _load_analytics_tenant(token, embed_token, analytics_cookie_token)

    portal = create_billing_portal_session_for_tenant(
        BillingPortalRequest(tenant_id=tenant.tenant_id)
    )
    return JSONResponse(
        content={
            "action": "portal",
            "provider": portal.provider,
            "portal_url": portal.portal_url,
        }
    )


def _create_analytics_embed_token(
    *,
    company: str,
    environment: str,
    tenant_id: str,
    language: str,
    scan_mode: str | None,
    bc_issue_launch_url: str | None,
) -> str:
    return create_token(
        {
            "type": ANALYTICS_EMBED_TOKEN_TYPE,
            "company": company,
            "environment": environment,
            "tenant_id": tenant_id,
            "preferred_language": normalize_language(language),
            "scan_mode": scan_mode,
            "bc_issue_launch_url": bc_issue_launch_url,
            "scope": "analytics:embed",
        },
        expires_delta=timedelta(minutes=ANALYTICS_EMBED_TOKEN_MINUTES),
    )


def _verify_analytics_embed_payload(token: str) -> dict[str, Any]:
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired analytics embed token.")

    if str(payload.get("type") or "") != ANALYTICS_EMBED_TOKEN_TYPE:
        raise HTTPException(status_code=401, detail="Invalid analytics embed token.")

    if str(payload.get("scope") or "") != "analytics:embed":
        raise HTTPException(status_code=401, detail="Invalid analytics embed token scope.")

    tenant_id = str(payload.get("tenant_id") or "").strip()
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Analytics embed token is missing tenant_id.")

    return payload


@router.get("/analytics/embed", response_class=HTMLResponse)
def render_analytics_dashboard(
    request: Request,
    token: str | None = Query(default=None),
    embed_token: str | None = Query(default=None),
    analytics_cookie_token: str | None = Cookie(default=None, alias=ANALYTICS_EMBED_COOKIE_NAME),
):
    supplied_token = embed_token or token
    if supplied_token:
        payload = _verify_analytics_embed_payload(supplied_token)

        tenant_id = str(payload.get("tenant_id") or "").strip()
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Analytics embed token is missing tenant_id.")

        with SessionLocal() as db:
            tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))

        if tenant is None:
            raise HTTPException(status_code=404, detail="Tenant not found.")

        response = RedirectResponse(url="/analytics/embed", status_code=303)
        response.set_cookie(
            key=ANALYTICS_EMBED_COOKIE_NAME,
            value=supplied_token,
            max_age=ANALYTICS_EMBED_COOKIE_MAX_AGE_SECONDS,
            httponly=True,
            secure=(settings.ENV.lower() == "prod"),
            samesite="lax",
            path="/analytics",
        )
        return response

    if not analytics_cookie_token:
        raise HTTPException(status_code=401, detail="Missing analytics embed token.")

    payload = _verify_analytics_embed_payload(analytics_cookie_token)

    tenant_id = str(payload.get("tenant_id") or "").strip()
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Analytics embed token is missing tenant_id.")

    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))

    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found.")

    return TEMPLATES.TemplateResponse(
        name="analytics_embed.html",
        context={
            "request": request,
            "page_title": "BCSentinel Analytics",
        },
    )
