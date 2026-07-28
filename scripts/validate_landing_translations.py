#!/usr/bin/env python3
"""Validate parity and basic quality of centralized landing-page translations."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LANG_DIR = ROOT / "landingpage" / "lang"
BUNDLES = (
    "redesign",
    "loss-examples",
    "security",
    "docs",
    "contact",
    "privacy",
    "terms",
    "impressum",
    "help",
    "support",
)


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    result: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            result.update(flatten(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            result.update(flatten(child, f"{prefix}[{index}]"))
    else:
        result[prefix] = value
    return result


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def validate_bundle(bundle: str) -> tuple[list[str], int]:
    files = {locale: LANG_DIR / f"{bundle}.{locale}.json" for locale in ("de", "en")}
    missing_files = [str(path) for path in files.values() if not path.exists()]
    if missing_files:
        return [f"Missing translation file: {path}" for path in missing_files], 0

    payloads = {locale: load(path) for locale, path in files.items()}
    flattened = {locale: flatten(payload) for locale, payload in payloads.items()}
    errors: list[str] = []
    de_keys = set(flattened["de"])
    en_keys = set(flattened["en"])

    for key in sorted(de_keys - en_keys):
        errors.append(f"[{bundle}] Missing EN key: {key}")
    for key in sorted(en_keys - de_keys):
        errors.append(f"[{bundle}] Missing DE key: {key}")

    for locale, values in flattened.items():
        expected_locale = payloads[locale].get("meta", {}).get("locale")
        if expected_locale != locale:
            errors.append(f"[{bundle}] Invalid meta.locale in {locale.upper()}: {expected_locale!r}")
        for key, value in values.items():
            if isinstance(value, str) and not value.strip():
                errors.append(f"[{bundle}] Empty {locale.upper()} value: {key}")
            if isinstance(value, str) and value.strip() == key:
                errors.append(f"[{bundle}] Visible key fallback in {locale.upper()}: {key}")

    return errors, len(de_keys)


def main() -> int:
    errors: list[str] = []
    totals: list[str] = []
    for bundle in BUNDLES:
        bundle_errors, count = validate_bundle(bundle)
        errors.extend(bundle_errors)
        totals.append(f"{bundle}: {count} values per locale")

    if errors:
        print("Landing translation validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Landing translation validation PASS")
    for total in totals:
        print(f"- {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
