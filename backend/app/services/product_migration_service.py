from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select

from app.models import Subscription, TenantProductEntitlement, TenantProductPurchase, TenantScanCredit
from app.services.billing_service import utc_now


@dataclass(frozen=True)
class CanonicalProductIdentity:
    commercial_offer_id: str | None
    billing_variant: str | None
    resolution: str


UNAMBIGUOUS_PRODUCT_CODE_MAP: dict[str, CanonicalProductIdentity] = {
    "assessment": CanonicalProductIdentity("assessment", "one_time", "canonical"),
    "full_analysis": CanonicalProductIdentity("assessment", "one_time", "compatibility"),
    "validation": CanonicalProductIdentity("validation", "one_time", "compatibility"),
    "validation_check": CanonicalProductIdentity("validation", "one_time", "compatibility"),
    "monitoring_monthly": CanonicalProductIdentity("monitoring", "monthly", "compatibility"),
    "monitoring_annual": CanonicalProductIdentity("monitoring", "annual", "compatibility"),
}

NON_OFFER_CODES = {"data_health_score", "free", "locked"}
AMBIGUOUS_GRANDFATHERED_CODES = {"premium", "full"}


def _norm(value: str | None) -> str:
    return (value or "").strip().lower().replace("-", "_").replace(" ", "_")


def resolve_canonical_product_identity(
    code: str | None,
    *,
    billing_interval: str | None = None,
) -> CanonicalProductIdentity:
    normalized = _norm(code)
    if not normalized:
        return CanonicalProductIdentity(None, None, "missing")

    direct = UNAMBIGUOUS_PRODUCT_CODE_MAP.get(normalized)
    if direct is not None:
        return direct

    if normalized == "monitoring":
        interval = _norm(billing_interval)
        if interval in {"month", "monthly"}:
            return CanonicalProductIdentity("monitoring", "monthly", "compatibility")
        if interval in {"year", "annual", "yearly"}:
            return CanonicalProductIdentity("monitoring", "annual", "compatibility")
        return CanonicalProductIdentity(None, None, "manual_review")

    if normalized in NON_OFFER_CODES:
        return CanonicalProductIdentity(None, None, "non_offer")
    if normalized in AMBIGUOUS_GRANDFATHERED_CODES:
        return CanonicalProductIdentity(None, None, "grandfathered_manual_review")
    return CanonicalProductIdentity(None, None, "unknown_manual_review")


def _candidate(entity_type: str, entity_id: int, tenant_id: str, legacy_code: str, identity: CanonicalProductIdentity) -> dict[str, Any]:
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "tenant_id": tenant_id,
        "legacy_code": legacy_code,
        "commercial_offer_id": identity.commercial_offer_id,
        "billing_variant": identity.billing_variant,
        "resolution": identity.resolution,
        "rights_preserved": True,
    }


def build_product_migration_preview(db) -> dict[str, Any]:
    items: list[dict[str, Any]] = []

    for row in db.scalars(select(TenantProductPurchase).order_by(TenantProductPurchase.id)).all():
        items.append(_candidate("purchase", row.id, row.tenant_id, row.product_code, resolve_canonical_product_identity(row.product_code)))

    for row in db.scalars(select(TenantScanCredit).order_by(TenantScanCredit.id)).all():
        items.append(_candidate("scan_credit", row.id, row.tenant_id, row.product_code, resolve_canonical_product_identity(row.product_code)))

    for row in db.scalars(select(TenantProductEntitlement).order_by(TenantProductEntitlement.id)).all():
        items.append(_candidate("entitlement", row.id, row.tenant_id, row.product_code, resolve_canonical_product_identity(row.product_code)))

    for row in db.scalars(select(Subscription).order_by(Subscription.id)).all():
        interval = None
        normalized = _norm(row.plan_code)
        if normalized == "monitoring_monthly":
            interval = "month"
        elif normalized == "monitoring_annual":
            interval = "year"
        items.append(_candidate("subscription", row.id, row.tenant_id, row.plan_code, resolve_canonical_product_identity(row.plan_code, billing_interval=interval)))

    counts: dict[str, int] = {}
    for item in items:
        counts[item["resolution"]] = counts.get(item["resolution"], 0) + 1

    return {
        "mode": "preview",
        "non_destructive": True,
        "rights_preserved": True,
        "items": items,
        "counts_by_resolution": counts,
        "total": len(items),
    }


def apply_product_migration_metadata(db) -> dict[str, Any]:
    """Backfill canonical identity metadata without changing legacy business fields."""
    from app.product_migration_models import ProductMigrationRecord

    preview = build_product_migration_preview(db)
    created = 0
    updated = 0
    now = utc_now()

    for item in preview["items"]:
        row = db.scalar(
            select(ProductMigrationRecord).where(
                ProductMigrationRecord.entity_type == item["entity_type"],
                ProductMigrationRecord.entity_id == item["entity_id"],
            )
        )
        if row is None:
            row = ProductMigrationRecord(entity_type=item["entity_type"], entity_id=item["entity_id"])
            db.add(row)
            created += 1
        else:
            updated += 1

        row.tenant_id = item["tenant_id"]
        row.legacy_code = item["legacy_code"]
        row.commercial_offer_id = item["commercial_offer_id"]
        row.billing_variant = item["billing_variant"]
        row.resolution = item["resolution"]
        row.rights_preserved = True
        row.migrated_at_utc = now

    db.commit()
    return {
        "mode": "apply_metadata",
        "non_destructive": True,
        "rights_preserved": True,
        "created": created,
        "updated": updated,
        "total": preview["total"],
        "counts_by_resolution": preview["counts_by_resolution"],
    }
