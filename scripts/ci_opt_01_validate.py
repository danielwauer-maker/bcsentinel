#!/usr/bin/env python3
"""CI-OPT-01: verify supersession only affects pull-request invocations."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "bc-al-compile.yml",
    "ext-50-12b-bc27-runtime-gate.yml",
    "ext-50-12c-3-al.yml",
    "core-pilot-50-readiness.yml",
    "pilot-e2e-01a.yml",
    "p0-04-postgres-migration-cycle.yml",
    "p0-05-postgres-backup-restore.yml",
)
EXPECTED_GROUP = "group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}"
EXPECTED_CANCEL = "cancel-in-progress: ${{ github.event_name == 'pull_request' }}"

for filename in FILES:
    path = ROOT / ".github" / "workflows" / filename
    text = path.read_text(encoding="utf-8")
    assert text.count("concurrency:") == 1, f"{filename}: expected exactly one concurrency block"
    assert EXPECTED_GROUP in text, f"{filename}: workflow / PR identity isolation missing"
    assert EXPECTED_CANCEL in text, f"{filename}: release runs must not be cancelled"
    assert "  workflow_dispatch:" in text, f"{filename}: manually approved release run missing"
    assert "  pull_request:" in text, f"{filename}: existing PR trigger must remain"
    assert "jobs:" in text, f"{filename}: jobs missing"
    assert text.count("cancel-in-progress:") == 1, f"{filename}: unexpected cancellation behavior"
    print(f"PASS {filename}")

assert (
    (ROOT / "docs" / "ci" / "CI_OPT_01_SAFE_ROLLOUT.md").exists()
), "release-gate guidance missing"
print("CI_OPT_01_STATIC_CONTRACT=PASS")
