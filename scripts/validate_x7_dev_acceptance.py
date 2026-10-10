#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "config" / "x7-dev-acceptance.json").read_text(encoding="utf-8"))
workflow = (ROOT / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")
release = json.loads((ROOT / "config" / "release-policy.json").read_text(encoding="utf-8"))

if contract["promotion_path"] != ["DEV", "RC", "PROD"]:
    raise SystemExit("X7 promotion path must remain DEV -> RC -> PROD.")
if release.get("dev_host") != "dev.bcsentinel.com":
    raise SystemExit("Release policy and X7 DEV host are inconsistent.")

for forbidden in (
    "branches:\n      - main\n      - staging",
    "if: github.ref == 'refs/heads/main'",
):
    if forbidden in workflow:
        raise SystemExit("Automatic main->PROD deployment path is forbidden.")

for required in (
    "workflow_dispatch:",
    "- staging",
    "PROMOTE_TO_PROD",
    "environment: development",
    "environment: production",
    "https://dev-api.bcsentinel.com/health/ready",
    "https://dev.bcsentinel.com/",
    "https://dev.bcsentinel.com/pilot.html",
    "https://api.bcsentinel.com/health/ready",
    ".previous-release-ref",
    "git checkout --detach",
):
    if required not in workflow:
        raise SystemExit(f"X7 deployment contract fragment missing: {required}")

if "${{ secrets.SSH_PRIVATE_KEY }}" not in workflow or "${{ secrets.SERVER_HOST }}" not in workflow:
    raise SystemExit("Deployment secrets must remain GitHub secrets, not repository values.")

print("X7 DEV acceptance deployment contract: PASS")
