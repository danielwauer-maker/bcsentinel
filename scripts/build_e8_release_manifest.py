#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def alembic_heads() -> list[str]:
    result = subprocess.run(
        ["alembic", "heads"],
        cwd=ROOT / "backend",
        check=True,
        capture_output=True,
        text=True,
    )
    heads: list[str] = []
    for line in result.stdout.splitlines():
        value = line.strip().split()[0] if line.strip() else ""
        if value:
            heads.append(value)
    return heads


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--git-sha", required=True)
    parser.add_argument("--output", default="artifacts/e8/release-manifest.json")
    args = parser.parse_args()

    sha = args.git_sha.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise SystemExit("E8 manifest requires a full immutable 40-character Git SHA.")

    contract = load_json("config/e8-release-candidate-freeze.json")
    x8 = load_json("config/x8-pre-manual-pilot-audit.json")
    bc_app = load_json("bc-extension/app.json")
    dashboard = load_json("dashboard/package.json")
    heads = alembic_heads()
    if len(heads) != 1:
        raise SystemExit(f"E8 requires exactly one Alembic head, found: {heads}")
    if x8.get("pre_manual_ready") is not True or x8.get("code_blockers"):
        raise SystemExit("E8 cannot build an RC manifest while X8 is not pre-manual ready.")
    if contract.get("official_sprint_done") is not False:
        raise SystemExit("E8 automation must not claim official E8 completion.")

    evidence: dict[str, dict] = {}
    for relative in contract["required_evidence_contracts"]:
        data = load_json(relative)
        evidence[relative] = {
            "contract": data.get("contract"),
            "status": data.get("status"),
            "official_sprint_done": data.get("official_sprint_done"),
        }

    manifest = {
        "schema_version": "1.0.0",
        "contract": "bcsentinel-release-candidate-manifest-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "release_ref": sha,
        "official_e8_done": False,
        "pre_manual_ready": True,
        "versions": {
            "bc_extension": bc_app["version"],
            "bc_runtime": bc_app.get("runtime"),
            "bc_platform": bc_app.get("platform"),
            "dashboard": dashboard["version"],
            "alembic_head": heads[0],
        },
        "evidence_contracts": evidence,
        "manual_evidence_required": contract["manual_evidence_required"],
    }

    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    print(f"release_ref={sha}")
    print(f"bc_extension={bc_app['version']}")
    print(f"dashboard={dashboard['version']}")
    print(f"alembic_head={heads[0]}")


if __name__ == "__main__":
    main()
