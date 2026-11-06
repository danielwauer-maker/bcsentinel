#!/usr/bin/env python3
"""Fail fast when frozen Fiverr launch copy drifts from the 2026-11-03 contract."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

FILES = [
    REPO / "docs" / "FIVERR_PILOT_RELEASE_CANDIDATE.md",
    REPO / "docs" / "FIVERR_GIG_LAUNCH_KIT.md",
    REPO / "docs" / "FIVERR_REQUIREMENTS_DELIVERY_FINAL.md",
    REPO / "docs" / "FIVERR_GOLIVE_AUTOMATED_READINESS.md",
]

REQUIRED = [
    "BASIC — Quick Assessment",
    "ADVANCED — Full Assessment",
    "$149",
    "$349",
    "$179",
    "$199",
    "$399",
    "$219",
    "$279",
    "$549",
    "$289",
    "$429",
    "$799",
    "$649",
    "$1,199",
    ">20",
    "Custom Offer",
]

FORBIDDEN = [
    "BASIC — Free Health Check",
    "STANDARD — Full Assessment",
    "PREMIUM — Assessment Plus",
    "Micro base $129",
    "Micro base $299",
    "Micro base $399",
]


def main() -> int:
    errors: list[str] = []
    combined = ""

    for path in FILES:
        if not path.is_file():
            errors.append(f"missing launch-contract file: {path.relative_to(REPO)}")
            continue
        combined += "\n" + path.read_text(encoding="utf-8")

    for token in REQUIRED:
        if token not in combined:
            errors.append(f"required frozen Fiverr token missing: {token!r}")

    for token in FORBIDDEN:
        if token in combined:
            errors.append(f"obsolete Fiverr launch token present: {token!r}")

    if errors:
        print("Fiverr launch contract drift detected:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Fiverr launch contract OK: package names and frozen pricing markers are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
