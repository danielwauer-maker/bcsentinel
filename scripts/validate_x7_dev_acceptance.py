#!/usr/bin/env python3
"""Validate the current DEV/PROD deployment policy without erasing historical X7 evidence."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "config" / "x7-dev-acceptance.json").read_text(encoding="utf-8"))
release = json.loads((ROOT / "config" / "release-policy.json").read_text(encoding="utf-8"))
prod = (ROOT / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")
dev = (ROOT / ".github" / "workflows" / "dev-release.yml").read_text(encoding="utf-8")


def require(text: str, fragments: tuple[str, ...], label: str) -> None:
    for fragment in fragments:
        if fragment not in text:
            raise SystemExit(f"X7 {label} contract fragment missing: {fragment}")


def reject(text: str, fragments: tuple[str, ...], label: str) -> None:
    for fragment in fragments:
        if fragment in text:
            raise SystemExit(f"Unsafe X7 {label} contract fragment: {fragment}")


if contract["promotion_path"] != ["DEV", "RC", "PROD"]:
    raise SystemExit("X7 promotion path must remain DEV -> RC -> PROD.")
if release.get("dev_host") != "dev.bcsentinel.com":
    raise SystemExit("Release policy and X7 DEV host are inconsistent.")
if release.get("dev_branch") != "staging":
    raise SystemExit("Current DEV release source must be staging.")
dev_contract = contract.get("environments", {}).get("dev", {})
if dev_contract.get("deployment_branch") != "staging":
    raise SystemExit("X7 current DEV release source must be staging.")
if dev_contract.get("deployment_trigger") != "manual_exact_sha_approved":
    raise SystemExit("X7 current DEV release must require manual exact-SHA approval.")
if contract.get("dev_acceptance_evidence", {}).get("deployment_branch") != "dev-acceptance":
    raise SystemExit("Historical X7 DEV-acceptance evidence must remain unchanged.")

# No branch push may start either deployment workflow.
reject(prod, ("  push:", "branches:\\n      - dev-acceptance", "branches:\\n      - main", "branches:\\n      - staging"), "PROD")
reject(dev, ("  push:",), "DEV")
require(prod, (
    "workflow_dispatch:", "PROMOTE_TO_PROD", "environment: production",
    "https://api.bcsentinel.com/health/ready", ".previous-release-ref",
), "PROD")
require(dev, (
    "workflow_dispatch:", "target_environment:", "release_sha:",
    'test "$TARGET_ENVIRONMENT" = "dev"',
    '[[ "$RELEASE_SHA" =~ ^[0-9a-f]{40}$ ]]',
    'test "$DEV_RELEASE_ENABLED" = "true"',
    'test "$APPROVED_RELEASE_SHA" = "$RELEASE_SHA"',
    'test "$(git rev-parse origin/staging)" = "$RELEASE_SHA"',
    "environment: development",
    "pg_dump", "pg_restore --list",
    "git status --porcelain --untracked-files=all",
    "sudo -n /usr/sbin/nginx -t",
    "http://127.0.0.1:8001/health/ready",
    "https://dev-api.bcsentinel.com/health/ready",
), "DEV")
reject(dev, ("git clean -fd", "cp config/nginx", "rm -rf /var/www"), "DEV")
for name, content in (("PROD", prod), ("DEV", dev)):
    require(content, ("secrets.SSH_PRIVATE_KEY", "secrets.SERVER_HOST"), name)
print("X7 DEV acceptance deployment contract: PASS")
print("Historical dev-acceptance evidence retained; current DEV is manual, staging-tip SHA-approved.")
