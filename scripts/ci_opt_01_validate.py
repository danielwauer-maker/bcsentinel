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
    "ext-50-12c-3-backend.yml",
    "report-native-access-qa.yml",
    "arch-02a-compatibility.yml",
)
EXPECTED_GROUP = "group: ${{ github.event_name == 'pull_request' && format('{0}-pr-{1}', github.workflow, github.event.pull_request.number) || format('{0}-{1}-{2}', github.workflow, github.event_name, github.run_id) }}"
EXPECTED_CANCEL = "cancel-in-progress: ${{ github.event_name == 'pull_request' }}"

for filename in FILES:
    path = ROOT / ".github" / "workflows" / filename
    text = path.read_text(encoding="utf-8")
    assert text.count("concurrency:") == 1, f"{filename}: expected exactly one concurrency block"
    assert EXPECTED_GROUP in text, f"{filename}: PR/manual/push group isolation missing"
    assert EXPECTED_CANCEL in text, f"{filename}: release runs must not be cancelled"
    assert "  workflow_dispatch:" in text, f"{filename}: manually approved release run missing"
    assert "  pull_request:" in text, f"{filename}: existing PR trigger must remain"
    assert "jobs:" in text, f"{filename}: jobs missing"
    assert text.count("cancel-in-progress:") == 1, f"{filename}: unexpected cancellation behavior"
    print(f"PASS {filename}")

classifier = ROOT / ".github" / "workflows" / "ci-change-classification.yml"
classifier_text = classifier.read_text(encoding="utf-8")
assert "  pull_request:" in classifier_text, "classifier must run for PRs"
assert "  merge_group:" in classifier_text, "classifier must run for merge queues"
assert "fetch-depth: 0" in classifier_text, "classifier must resolve the exact Git graph"
assert "scripts/test_ci_change_classification.py" in classifier_text, "classifier regression matrix missing"
assert "scripts/ci_change_classification.py" in classifier_text, "central classifier missing"
assert "all_critical" in classifier_text, "unknown changes must be fail-closed"

assert (
    (ROOT / "docs" / "ci" / "CI_OPT_01_SAFE_ROLLOUT.md").exists()
), "release-gate guidance missing"
print("CI_OPT_01_STATIC_CONTRACT=PASS")

# CI-OPT-02: in-progress Draft PRs must not allocate Windows BC27 runners.
# A transition to Ready for review must start the unchanged final gates.
BC27_WORKFLOWS = ("bc-al-compile.yml", "ext-50-12b-bc27-runtime-gate.yml", "ext-50-12c-3-al.yml")
FINAL_GATE_IF = "if: ${{ github.event_name != 'pull_request' || github.event.pull_request.draft == false }}"
for filename in BC27_WORKFLOWS:
    text = (ROOT / ".github" / "workflows" / filename).read_text(encoding="utf-8")
    assert "ready_for_review" in text, f"{filename}: review-ready event missing"
    assert "synchronize" in text, f"{filename}: final-head resync missing"
    assert text.count(FINAL_GATE_IF) == 1, f"{filename}: draft-only Windows gate missing"
    assert "  workflow_dispatch:" in text, f"{filename}: approved manual execution must remain"
    if filename != "ext-50-12b-bc27-runtime-gate.yml":
        push_section = text.split("  push:\n", 1)[1].split("  workflow_dispatch:", 1)[0]
        assert "    paths:\n" in push_section, f"{filename}: staging push needs path filtering"
        assert '".github/workflows/**"' in push_section, f"{filename}: workflow changes must be covered"
        assert '"bc-extension/**"' in push_section, f"{filename}: AL changes must be covered"
    if filename == "ext-50-12b-bc27-runtime-gate.yml":
        assert "Compile publish and install extension" in text
    else:
        assert "BC 27 AL compile with CodeCop and PTECop" in text
print("CI_OPT_02_DRAFT_FINAL_GATE_CONTRACT=PASS")
