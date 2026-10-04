from __future__ import annotations

import json
from pathlib import Path

from app.core.product_model import (
    canonical_offer_for_storage_code,
    entitlements_for_storage_code,
    product_contract_for_storage_code,
)
from app.db import SessionLocal
from app.models import Tenant
from app.services.product_license_service import (
    PRODUCT_FULL_ANALYSIS,
    build_product_access_snapshot,
    normalize_product_code,
    product_code_storage_aliases,
)

ROOT = Path(__file__).resolve().parents[2]


def test_legacy_assessment_maps_losslessly_to_canonical_assessment() -> None:
    assert normalize_product_code("assessment") == PRODUCT_FULL_ANALYSIS
    assert product_code_storage_aliases(PRODUCT_FULL_ANALYSIS) == {
        "assessment",
        "full_analysis",
    }
    assert canonical_offer_for_storage_code("assessment").value == "assessment"
    assert canonical_offer_for_storage_code("full_analysis").value == "assessment"


def test_legacy_premium_plan_is_not_a_canonical_offer_or_entitlement() -> None:
    assert canonical_offer_for_storage_code("premium") is None
    assert entitlements_for_storage_code("premium") == frozenset()
    contract = product_contract_for_storage_code("premium")
    assert contract["commercial_offer_id"] is None
    assert contract["access_state"] == "locked"


def test_legacy_premium_tenant_does_not_gain_monitoring_by_plan_name(tenant_factory) -> None:
    tenant_info = tenant_factory(plan="premium", license_status="active")
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_info["tenant_id"]).one()
        snapshot = build_product_access_snapshot(db, tenant)

    assert snapshot["monitoring_active"] is False
    assert snapshot["can_use_monitoring"] is False
    assert snapshot["access_model"] == "none"


def test_legacy_pricing_config_declares_compatibility_only_role() -> None:
    config = json.loads((ROOT / "config" / "pricing_canonical.json").read_text(encoding="utf-8"))
    assert config["contract_role"] == "legacy_tenant_pricing_compatibility"
    assert config["canonical_product_authority"] == "backend/app/core/product_model.py"
    assert "premium" in config["plans"]
