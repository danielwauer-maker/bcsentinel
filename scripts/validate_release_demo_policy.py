#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
release = json.loads((ROOT / "config" / "release-policy.json").read_text(encoding="utf-8"))
demo = json.loads((ROOT / "config" / "demo-tenant.json").read_text(encoding="utf-8"))

if release.get("promotion_path") != ["DEV", "RC", "PROD"]:
    raise SystemExit("Release promotion path must be DEV -> RC -> PROD.")
if release.get("dev_host") != "dev.bcsentinel.com":
    raise SystemExit("DEV host must remain dev.bcsentinel.com.")
if not release.get("rollback", {}).get("previous_release_reference_required"):
    raise SystemExit("Rollback policy must require a previous release reference.")
if release.get("secrets_in_manifest_forbidden") is not True:
    raise SystemExit("Release manifests must forbid secrets.")

if demo.get("synthetic") is not True or demo.get("customer_data") is not False:
    raise SystemExit("Demo tenant must be explicitly synthetic and contain no customer data.")
if not str(demo.get("tenant", {}).get("tenant_id", "")).startswith("demo_"):
    raise SystemExit("Demo tenant_id must use demo_ prefix.")
scan = demo.get("scan", {})
for legacy_key in ("roi_eur", "estimated_premium_price_monthly"):
    if legacy_key in scan:
        raise SystemExit(f"Demo scan must not expose legacy financial field {legacy_key}.")
for required in ("estimated_loss_eur", "potential_saving_eur", "validated_improvement_eur", "realized_saving_eur"):
    if required not in scan:
        raise SystemExit(f"Demo scan missing canonical fin-v1 field {required}.")
if not demo.get("disclaimer_de") or not demo.get("disclaimer_en"):
    raise SystemExit("Demo dataset requires DE/EN synthetic-data disclaimers.")

print("Release safety + synthetic demo contract: PASS")
