#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "backend/app/services/product_migration_service.py"
MODEL = ROOT / "backend/app/product_migration_models.py"
MIGRATION = ROOT / "backend/alembic/versions/0020_product_migration_metadata.py"
OPS = ROOT / "scripts/migrate_product_identity.py"
PRICING = ROOT / "backend/app/services/product_pricing_service.py"

required = [SERVICE, MODEL, MIGRATION, OPS, PRICING]
missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
if missing:
    raise SystemExit(f"Missing D5 files: {missing}")

service = SERVICE.read_text(encoding="utf-8")
model = MODEL.read_text(encoding="utf-8")
migration = MIGRATION.read_text(encoding="utf-8")
ops = OPS.read_text(encoding="utf-8")
pricing = PRICING.read_text(encoding="utf-8")

expected_mappings = {
    '"full_analysis": CanonicalProductIdentity("assessment", "one_time", "compatibility")',
    '"validation_check": CanonicalProductIdentity("validation", "one_time", "compatibility")',
    '"monitoring_monthly": CanonicalProductIdentity("monitoring", "monthly", "compatibility")',
    '"monitoring_annual": CanonicalProductIdentity("monitoring", "annual", "compatibility")',
}
for value in expected_mappings:
    if value not in service:
        raise SystemExit(f"Missing canonical compatibility mapping: {value}")

for ambiguous in ['"premium"', '"full"']:
    if ambiguous not in service or "grandfathered_manual_review" not in service:
        raise SystemExit("Ambiguous legacy plans must be preserved for manual review, not guessed.")

for forbidden_assignment in [
    "row.product_code =",
    "row.plan_code =",
    "row.status =",
    "row.amount_total =",
    "row.amount_monthly =",
    "row.valid_until_utc =",
    "row.current_period_end_utc =",
]:
    if forbidden_assignment in service:
        raise SystemExit(f"Migration must be non-destructive; forbidden assignment found: {forbidden_assignment}")

for marker in ["rights_preserved", "non_destructive", "manual_review", "legacy_code", "commercial_offer_id", "billing_variant"]:
    if marker not in service + model + migration:
        raise SystemExit(f"Missing D5 safety marker: {marker}")

if "--confirm" not in ops or "--apply" not in ops:
    raise SystemExit("Apply mode must require explicit confirmation.")

for pricing_marker in [
    'PRICING_MODEL = "record_volume_tiers"',
    'PRICING_METRIC = "bcsentinel_analyzed_record_volume"',
    '"enterprise_plus"',
    "STRIPE_SYNC_WARNING",
]:
    if pricing_marker not in pricing:
        raise SystemExit(f"Active ARV pricing contract missing: {pricing_marker}")

print("D5 Pricing / Product Migration Quality Gate: PASS")
