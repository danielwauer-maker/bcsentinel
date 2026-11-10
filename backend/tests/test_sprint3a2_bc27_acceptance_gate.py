"""Offline runbook evidence gate: not a claim of actual BC27 acceptance."""
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "quality/release/sprint3a2-bc27-acceptance-template.json"
VALIDATOR = ROOT / "scripts/check_sprint3a2_bc27_acceptance.py"


def _load():
    spec = importlib.util.spec_from_file_location("sprint3a2_acceptance_checker", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _synthetic_complete():
    evidence = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    evidence["head_sha"] = "a" * 40
    evidence["status"] = "PASS"
    evidence["decision"] = "GO"
    evidence["reviewer"] = "SYNTHETIC-REVIEWER-NOT-A-REAL-SIGNOFF"
    evidence["decision_utc"] = "2026-11-10T12:00:00Z"
    evidence["run_context"].update({
        "bc_version": "27.0", "sandbox_environment": "SYNTHETIC-SANDBOX",
        "company_id": "11111111-2222-3333-4444-555555555555",
        "extension_package_sha256": "b" * 64,
        "backend_commit_sha": "c" * 40,
        "utc_started_at": "2026-11-10T10:00:00Z",
        "utc_finished_at": "2026-11-10T11:00:00Z",
    })
    for role in evidence["roles"]:
        evidence["roles"][role] = "PASS"
    for gate in evidence["gates"]:
        evidence["gates"][gate] = "PASS"
    for case in evidence["scenarios"]:
        case["status"] = "PASS"
        case["evidence_refs"] = ["SYNTHETIC-NO-RUNTIME-EVIDENCE"]
        if case["id"] in ("BC27-03", "BC27-04"):
            case["scan_id"] = "synthetic-" + case["id"]
    return evidence


def test_official_template_cannot_pass_without_execution():
    evidence = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    assert evidence["decision"] == "NO_GO"
    assert evidence["status"] == "NOT_EXECUTED"
    assert _load().evaluate(evidence)


def test_structurally_complete_synthetic_record_passes_offline_only():
    checker = _load()
    assert not checker.evaluate(_synthetic_complete())


def test_gate_rejects_missing_runtime_provenance_and_incorrect_status():
    checker = _load()
    synthetic = _synthetic_complete()
    for change in ("backend_sha", "app_hash", "scenario", "role", "gate", "reviewer", "company"):
        data = copy.deepcopy(synthetic)
        if change == "backend_sha":
            data["run_context"]["backend_commit_sha"] = None
        elif change == "app_hash":
            data["run_context"]["extension_package_sha256"] = "invalid"
        elif change == "scenario":
            data["scenarios"][2]["status"] = "BLOCKED"
        elif change == "role":
            data["roles"]["scan_user_non_super"] = "NOT_EXECUTED"
        elif change == "gate":
            data["gates"]["tenant_isolation"] = "FAIL"
        elif change == "reviewer":
            data["reviewer"] = None
        else:
            data["run_context"]["company_id"] = "00000000-0000-0000-0000-000000000000"
        assert checker.evaluate(data), change


def test_gate_rejects_duplicate_scenario_and_secrets_even_with_pass():
    checker = _load()
    data = _synthetic_complete()
    data["scenarios"][0]["id"] = "BC27-02"
    assert checker.evaluate(data)
    data = _synthetic_complete()
    data["findings"] = ["X-Api-Token: secret-do-not-commit"]
    assert any("redact" in e for e in checker.evaluate(data))
    data = _synthetic_complete()
    data["scenarios"][0]["id"] = None
    assert checker.evaluate(data)


def test_runbook_and_build_artifact_are_pinned_to_current_facts():
    runbook = (ROOT / "docs/SPRINT3A2_BC27_ACCEPTANCE_RUNBOOK.md").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/bc-extension-build-test.yml").read_text(encoding="utf-8")
    assert "NO-GO" in runbook and "BC27-08" in runbook
    assert "BCSentinel-BC27-Sandbox-Extension" in workflow
    assert "SHA256SUMS" in workflow
    assert "retention-days: 14" in workflow
