#!/usr/bin/env python3
"""Fail-closed static guard for GitHub's PROD deployment controller.

This verifies the control-plane source. GitHub environment reviewers and
repository variable values must also be checked by an authorized operator.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / ".github/workflows/deploy.yml").read_text(encoding="utf-8")

def require(condition: bool, reason: str) -> None:
    if not condition:
        raise SystemExit("PROD_RELEASE_CONTRACT_NO_GO: " + reason)

require(re.search(r"(?m)^on:\s*$", text) is not None,
        "events must have an explicit top-level on section")
on_section = text.split("\non:\n", 1)[1].split("\nconcurrency:", 1)[0]
require(re.search(r"(?m)^  workflow_dispatch:\s*$", on_section) is not None,
        "manual dispatch required")
require(re.search(r"(?m)^  (push|pull_request|schedule|workflow_run|repository_dispatch):", on_section) is None,
        "non-manual deployment trigger detected")
for fragment in (
    'test "${{ github.event_name }}" = "workflow_dispatch"',
    'test "${{ github.ref }}" = "refs/heads/main"',
    'test "$CONFIRM_PROD" = "PROMOTE_TO_PROD"',
    r'[[ "$RELEASE_REF" =~ ^[0-9a-f]{40}$ ]]',
    'test "$PROD_RELEASE_ENABLED" = "true"',
    'test "$PROD_RELEASE_SHA" = "$RELEASE_REF"',
    'git fetch --no-tags origin main',
    'test "$(git rev-parse origin/main)" = "$RELEASE_REF"',
    'git cat-file -e "$RELEASE_REF^{commit}"',
    "    environment: production",
    "    needs: [deployment-contract, regression-gate]",
    "  cancel-in-progress: false",
):
    require(fragment in text, "missing release guard: " + fragment)

require('echo "release_ref=${{ inputs.release_ref }}"' not in text,
        "untrusted release_ref shell interpolation reintroduced")
require('RELEASE_REF: ${{ inputs.release_ref }}' in text,
        "release input must enter through an environment variable")
require('printf \'release_ref=%s\\n\' "$RELEASE_REF" >> "$GITHUB_OUTPUT"' in text,
        "validated SHA must be emitted with a single-line output contract")
require("git reset --hard origin/main" not in text, "unsafe automatic PROD reset reintroduced")
print("PROD_RELEASE_CONTROLLER=MANUAL_EXACT_SHA_FAIL_CLOSED")
