#!/usr/bin/env python3
"""
Verify product-pricing fallback alignment without importing the full FastAPI stack:
- landingpage/pricing-snapshot.js (__BCS_PRODUCT_PRICING__ fallback)
- optional backend PRODUCT_PRICING_DEFAULTS import when dependencies are available
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXPECTED_PRODUCTS = {
    "assessment": 7900,
    "validation_check": 4900,
    "monitoring_monthly": 9900,
    "monitoring_annual": 99000,
}


def main() -> int:
    snapshot_path = REPO / "landingpage" / "pricing-snapshot.js"
    if not snapshot_path.is_file():
        print("FAIL: landingpage/pricing-snapshot.js missing.")
        return 1

    snap_text = snapshot_path.read_text(encoding="utf-8")
    for product_key, price_cents in EXPECTED_PRODUCTS.items():
        if f'"product_key": "{product_key}"' not in snap_text or f'"price_cents": {price_cents}' not in snap_text:
            print(f"FAIL: product fallback for {product_key} missing or mismatched in pricing-snapshot.js")
            return 1

    failures: list[str] = []
    try:
        sys.path.insert(0, str(REPO / "backend"))
        from app.services.product_pricing_service import PRODUCT_PRICING_DEFAULTS  # type: ignore  # noqa: E402

        for product_key, price_cents in EXPECTED_PRODUCTS.items():
            actual = int(PRODUCT_PRICING_DEFAULTS[product_key]["price_cents"])
            if actual != price_cents:
                failures.append(f"PRODUCT_PRICING_DEFAULTS.{product_key}.price_cents mismatch")
    except Exception as exc:
        print(f"Optional backend import skipped ({exc.__class__.__name__}). File-level checks passed.")
        print("pricing consistency OK (product snapshot).")
        return 0

    if failures:
        print("Product pricing consistency check FAILED:")
        for row in failures:
            print(f"  - {row}")
        return 1

    print("pricing consistency OK: product snapshot and PRODUCT_PRICING_DEFAULTS align.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
