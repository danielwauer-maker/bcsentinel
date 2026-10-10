#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "config" / "e4-provider-contract.json").read_text(encoding="utf-8"))
commercial = (ROOT / "backend" / "app" / "routers" / "commercial_billing.py").read_text(encoding="utf-8")
billing_tests = (ROOT / "backend" / "tests" / "test_billing.py").read_text(encoding="utf-8")
commercial_tests = (ROOT / "backend" / "tests" / "test_e4_provider_contract.py").read_text(encoding="utf-8")
email_tests = (ROOT / "backend" / "tests" / "test_x4_email_i18n.py").read_text(encoding="utf-8")

if contract.get("official_sprint_done") is not False:
    raise SystemExit("E4 automation must not claim official completion before real provider acceptance.")

for needle in (
    'if commercial["pilot_sponsorship_active"]',
    'checkout_required=False',
    'allow_promotion_codes = override is None',
    'session_kwargs["discounts"]',
    'Promotion-code stacking with a tenant-specific commercial override is not enabled',
):
    if needle not in commercial:
        raise SystemExit(f"E4 commercial checkout contract missing: {needle}")

for needle in (
    "test_billing_webhook_processes_valid_signed_event_and_is_idempotent",
    "test_billing_portal_uses_safe_return_url",
):
    if needle not in billing_tests:
        raise SystemExit(f"E4 Stripe regression evidence missing: {needle}")

for needle in (
    "test_sponsored_pilot_commercial_checkout_skips_stripe_entirely",
    "test_list_price_commercial_checkout_allows_stripe_promotion_codes",
    "test_tenant_override_uses_one_controlled_discount_and_disables_stacking",
):
    if needle not in commercial_tests:
        raise SystemExit(f"E4 commercial provider test missing: {needle}")

for needle in (
    "test_default_catalog_seeds_english_and_german_variants",
    "test_render_selects_german_and_keeps_english_fallback",
    "test_admin_editing_preserves_language_record_and_rejects_unsafe_content",
):
    if needle not in email_tests:
        raise SystemExit(f"E4 email contract evidence missing: {needle}")

manual = contract.get("manual_evidence_required", [])
if not any("SPF" in item and "DKIM" in item and "DMARC" in item for item in manual):
    raise SystemExit("E4 must retain real SPF/DKIM/DMARC acceptance evidence.")
if not any("real Stripe" in item for item in manual):
    raise SystemExit("E4 must retain real Stripe provider acceptance evidence.")

print("E4 Provider Contract Automation: PASS")
print("Official E4 remains open pending real Stripe/SMTP/DNS acceptance.")
