#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
policy = json.loads((ROOT / "config" / "bc-compatibility.json").read_text(encoding="utf-8"))
app = json.loads((ROOT / "bc-extension" / "app.json").read_text(encoding="utf-8"))


def version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))


minimum = version_tuple(policy["minimum_extension_version"])
manifest = version_tuple(app["version"])
if minimum > manifest:
    raise SystemExit(
        f"Compatibility floor {policy['minimum_extension_version']} exceeds extension manifest {app['version']}."
    )

application_major = version_tuple(app["application"])[0]
if application_major not in set(policy["supported_bc_major_versions"]):
    raise SystemExit(
        f"Extension application major {application_major} is missing from supported_bc_major_versions."
    )

print(
    "BC compatibility contract: PASS "
    f"(extension floor {policy['minimum_extension_version']}, manifest {app['version']}, BC major {application_major})"
)
