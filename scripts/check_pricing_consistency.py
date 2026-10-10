#!/usr/bin/env python3
"""Verify the generated landing pricing fallback against canonical backend pricing.

No product prices are hard-coded here. The generator imports the backend pricing
service, and this check proves that the committed fallback is exactly what that
canonical source generates.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SNAPSHOT = REPO / "landingpage" / "pricing-snapshot.js"
GENERATOR = REPO / "scripts" / "generate_landing_pricing.py"


def main() -> int:
    if not SNAPSHOT.is_file():
        print("FAIL: landingpage/pricing-snapshot.js missing.")
        return 1
    if not GENERATOR.is_file():
        print("FAIL: scripts/generate_landing_pricing.py missing.")
        return 1

    committed = SNAPSHOT.read_bytes()
    try:
        result = subprocess.run(
            [sys.executable, str(GENERATOR)],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print("FAIL: canonical pricing snapshot generator failed.")
            if result.stdout:
                print(result.stdout.rstrip())
            if result.stderr:
                print(result.stderr.rstrip())
            return result.returncode or 1

        generated = SNAPSHOT.read_bytes()
        if generated != committed:
            print("FAIL: pricing-snapshot.js is stale relative to canonical backend pricing.")
            print("Run: python scripts/generate_landing_pricing.py")
            return 1

        print("pricing consistency OK: generated landing fallback matches canonical backend pricing.")
        return 0
    finally:
        # A validator must not leave the working tree modified.
        SNAPSHOT.write_bytes(committed)


if __name__ == "__main__":
    raise SystemExit(main())
