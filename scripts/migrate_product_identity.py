#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.db import SessionLocal  # noqa: E402
from app.services.product_migration_service import (  # noqa: E402
    apply_product_migration_metadata,
    build_product_migration_preview,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="BCSentinel non-destructive product identity migration")
    parser.add_argument("--apply", action="store_true", help="Persist canonical migration metadata. Legacy business fields are never rewritten.")
    parser.add_argument("--confirm", action="store_true", help="Required together with --apply.")
    args = parser.parse_args()

    if args.apply and not args.confirm:
        parser.error("--apply requires --confirm")

    with SessionLocal() as db:
        result = apply_product_migration_metadata(db) if args.apply else build_product_migration_preview(db)

    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
