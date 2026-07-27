#!/usr/bin/env python3
"""Validate parity and basic quality of centralized landing-page translations."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LANG_DIR = ROOT / "landingpage" / "lang"
FILES = {"de": LANG_DIR / "redesign.de.json", "en": LANG_DIR / "redesign.en.json"}


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


def main() -> int:
    payloads = {locale: load(path) for locale, path in FILES.items()}
    flattened = {locale: flatten(payload) for locale, payload in payloads.items()}
    errors: list[str] = []

    de_keys = set(flattened["de"])
    en_keys = set(flattened["en"])
    for key in sorted(de_keys - en_keys):
        errors.append(f"Missing EN key: {key}")
    for key in sorted(en_keys - de_keys):
        errors.append(f"Missing DE key: {key}")

    for locale, values in flattened.items():
        for key, value in values.items():
            if isinstance(value, str) and not value.strip():
                errors.append(f"Empty {locale.upper()} value: {key}")
            if isinstance(value, str) and value.strip() == key:
                errors.append(f"Visible key fallback in {locale.upper()}: {key}")

    if errors:
        print("Landing translation validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Landing translation validation PASS ({len(de_keys)} values per locale)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
