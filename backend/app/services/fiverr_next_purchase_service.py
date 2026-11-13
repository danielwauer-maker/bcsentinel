from __future__ import annotations

from typing import Any

from sqlalchemy import select

from app.models import Scan, Tenant
from app.services.product_license_service import PRODUCT_ASSESSMENT, PRODUCT_VALIDATION_CHECK
from app.services.quick_assessment_access_service import PRODUCT_QUICK_ASSESSMENT
from app.services.record_volume_pricing_service import fiverr_price_recommendation
from app.services.report_access_service import (
    REPORT_ASSESSMENT,
    REPORT_FREE,
    REPORT_QUICK,
    REPORT_VALIDATION,
    resolve_preferred_report_variant,
)


_NEXT_PRODUCT_BY_REPORT = {
    REPORT_FREE: {
        "product_code": PRODUCT_QUICK_ASSESSMENT,
        "product_name": "Quick Assessment",
        "fiverr_package": "BASIC",
        "requires_new_scan": False,
        "after_remediation": False,
    },
    REPORT_QUICK: {
        "product_code": PRODUCT_ASSESSMENT,
        "product_name": "Full Assessment",
        "fiverr_package": "ADVANCED",
        "requires_new_scan": False,
        "after_remediation": False,
    },
    REPORT_ASSESSMENT: {
        "product_code": PRODUCT_VALIDATION_CHECK,
        "product_name": "Validation",
        "fiverr_package": "VALIDATION",
        "requires_new_scan": True,
        "after_remediation": True,
    },
}


def build_fiverr_next_purchase_recommendation(
    db,
    *,
    tenant_id: str,
    scan_id: str,
) -> dict[str, Any] | None:
    """Build one authoritative Fiverr next-purchase recommendation.

    Reports remain channel-neutral. This read model is intended for lifecycle
    communication only and derives its price from the shared Fiverr pricing
    service using the completed scan's persisted total_records value.
    """
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
    scan = db.scalar(
        select(Scan).where(
            Scan.tenant_id == tenant_id,
            Scan.scan_id == scan_id,
        )
    )
    if tenant is None or scan is None:
        return None

    report_variant = resolve_preferred_report_variant(db, tenant, scan_id=scan_id)
    if report_variant == REPORT_VALIDATION:
        return None

    next_product = _NEXT_PRODUCT_BY_REPORT.get(report_variant)
    if next_product is None:
        return None

    product_code = str(next_product["product_code"])
    total_quote = fiverr_price_recommendation(
        total_records=int(scan.total_records or 0),
        product_code=product_code,
    )
    base_quote = fiverr_price_recommendation(
        total_records=0,
        product_code=product_code,
    )

    total_price = total_quote["price"]
    base_price = base_quote["price"]
    addon_price = None
    if total_price is not None and base_price is not None:
        addon_price = max(float(total_price) - float(base_price), 0.0)

    return {
        "channel": "fiverr",
        "current_report_variant": report_variant,
        "total_records": int(scan.total_records or 0),
        "record_class": total_quote["record_class"],
        "product_code": product_code,
        "product_name": next_product["product_name"],
        "fiverr_package": next_product["fiverr_package"],
        "currency": "USD",
        "base_gig_price": base_price,
        "total_price": total_price,
        "addon_price": addon_price,
        "custom_offer_required": bool(total_quote["custom_offer_required"]),
        "recommendation_type": total_quote["recommendation_type"],
        "requires_new_scan": bool(next_product["requires_new_scan"]),
        "after_remediation": bool(next_product["after_remediation"]),
    }


def _format_records(value: int, *, de: bool) -> str:
    formatted = f"{int(value):,}"
    return formatted.replace(",", ".") if de else formatted


def _format_usd(value: float | int | None) -> str:
    if value is None:
        return ""
    numeric = float(value)
    return f"${numeric:,.0f}" if numeric.is_integer() else f"${numeric:,.2f}"


def render_fiverr_next_purchase_html(
    recommendation: dict[str, Any] | None,
    *,
    language: str,
) -> str:
    if not recommendation:
        return ""

    de = str(language or "").lower().startswith("de")
    total_records = _format_records(int(recommendation["total_records"]), de=de)
    product_name = str(recommendation["product_name"])
    package = str(recommendation["fiverr_package"])

    if recommendation["custom_offer_required"]:
        if de:
            return (
                "<hr><h3>Ihr nächster Schritt auf Fiverr</h3>"
                f"<p>BCSentinel hat <strong>{total_records} Datensätze</strong> analysiert. "
                f"Für <strong>{product_name}</strong> ist bei diesem Datenvolumen ein "
                "<strong>individuelles Fiverr Custom Offer</strong> erforderlich.</p>"
                "<p>Bitte nutzen Sie hierfür die Fiverr-Kommunikation. Ein automatischer "
                "Standardpreis wird für diese Datenklasse nicht verwendet.</p>"
            )
        return (
            "<hr><h3>Your next step on Fiverr</h3>"
            f"<p>BCSentinel analyzed <strong>{total_records} records</strong>. "
            f"For <strong>{product_name}</strong>, this data volume requires an "
            "<strong>individual Fiverr Custom Offer</strong>.</p>"
            "<p>Please use Fiverr communication for this step. No automatic standard "
            "price is used for this record class.</p>"
        )

    total_price = _format_usd(recommendation["total_price"])
    addon_price = float(recommendation.get("addon_price") or 0)
    base_price = _format_usd(recommendation["base_gig_price"])

    if de:
        if addon_price > 0:
            purchase = (
                f"Kaufen Sie den Fiverr-Gig <strong>{package} – {product_name}</strong> "
                f"zum Basispreis von <strong>{base_price}</strong> plus das "
                f"<strong>Datenvolumen-Add-on {_format_usd(addon_price)}</strong>. "
                f"Gesamtpreis für Ihre Datenklasse: <strong>{total_price}</strong>."
            )
        else:
            purchase = (
                f"Kaufen Sie den Fiverr-Gig <strong>{package} – {product_name}</strong> "
                f"für <strong>{total_price}</strong>. Für Ihre Datenklasse ist kein "
                "zusätzliches Datenvolumen-Add-on erforderlich."
            )
        timing = (
            "<p><strong>Wichtig:</strong> Bestellen Sie die Validation erst nach der Umsetzung "
            "Ihrer Maßnahmen. Dafür wird anschließend genau ein neuer Scan gegen die bestätigte "
            "Full-Assessment-Baseline durchgeführt.</p>"
            if recommendation["after_remediation"]
            else "<p>Es ist <strong>kein neuer Scan erforderlich</strong>. Die nächste Stufe wird auf Basis des bereits vorhandenen Scans freigeschaltet.</p>"
        )
        return (
            "<hr><h3>Ihr nächster Schritt auf Fiverr</h3>"
            f"<p>Analysiertes Datenvolumen: <strong>{total_records} Datensätze</strong>.</p>"
            f"<p>{purchase}</p>{timing}"
        )

    if addon_price > 0:
        purchase = (
            f"Purchase the Fiverr Gig <strong>{package} – {product_name}</strong> at the "
            f"<strong>{base_price}</strong> base price plus the "
            f"<strong>{_format_usd(addon_price)} data-volume Add-on</strong>. "
            f"Total price for your record class: <strong>{total_price}</strong>."
        )
    else:
        purchase = (
            f"Purchase the Fiverr Gig <strong>{package} – {product_name}</strong> for "
            f"<strong>{total_price}</strong>. No additional data-volume Add-on is required "
            "for your record class."
        )
    timing = (
        "<p><strong>Important:</strong> Order Validation only after you have implemented your remediation measures. It then runs exactly one new scan against the confirmed Full Assessment baseline.</p>"
        if recommendation["after_remediation"]
        else "<p><strong>No new scan is required.</strong> The next level is unlocked from the scan that already exists.</p>"
    )
    return (
        "<hr><h3>Your next step on Fiverr</h3>"
        f"<p>Analyzed data volume: <strong>{total_records} records</strong>.</p>"
        f"<p>{purchase}</p>{timing}"
    )
