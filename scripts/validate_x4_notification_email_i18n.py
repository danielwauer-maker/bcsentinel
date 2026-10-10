#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "config" / "x4-notification-email-i18n.json").read_text(encoding="utf-8"))
service = (ROOT / "backend" / "app" / "services" / "email_template_service.py").read_text(encoding="utf-8")
admin = (ROOT / "backend" / "app" / "routers" / "admin.py").read_text(encoding="utf-8")
tests = (ROOT / "backend" / "tests" / "test_x4_email_i18n.py").read_text(encoding="utf-8")
codeunit_dir = ROOT / "bc-extension" / "app" / "src" / "codeunits"
bc_sources = "\n".join(path.read_text(encoding="utf-8") for path in codeunit_dir.glob("DHNotificationI18n*.al"))

if contract.get("status") != "complete":
    raise SystemExit("X4 closure contract must be complete.")
if contract.get("official_e4_done") is not False:
    raise SystemExit("X4 code closure must not claim external E4 acceptance.")

for needle in (
    'SUPPORTED_EMAIL_LANGUAGES = ("en", "de")',
    'storage_key(base_key',
    'normalized_language != "en"',
    'render_email_template_preview',
    'Unsupported placeholders',
    'Unsafe active content is not allowed',
):
    if needle not in service:
        raise SystemExit(f"X4 SaaS email fragment missing: {needle}")

for needle in (
    '@router.post("/admin/config/email-templates/{template_key}")',
    '@router.post("/admin/config/email-templates/{template_key}/test-send")',
    'config.email_template.test_send',
    'render_email_template_preview',
):
    if needle not in admin:
        raise SystemExit(f"X4 admin email surface missing: {needle}")

for needle in (
    'test_default_catalog_seeds_english_and_german_variants',
    'test_render_selects_german_and_keeps_english_fallback',
    'test_admin_editing_preserves_language_record_and_rejects_unsafe_content',
):
    if needle not in tests:
        raise SystemExit(f"X4 regression test missing: {needle}")

if not bc_sources:
    raise SystemExit("X4 BC notification i18n codeunits are missing.")
for needle in ('German', 'Language'):
    if needle not in bc_sources:
        raise SystemExit(f"X4 BC localization evidence missing: {needle}")

print("X4 Notification & Email i18n contract: PASS")
print("External SMTP/DNS acceptance remains E4 manual evidence.")
