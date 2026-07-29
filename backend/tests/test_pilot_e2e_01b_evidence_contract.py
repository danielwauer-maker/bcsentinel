from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate_pilot_sandbox_evidence.py"
spec = spec_from_file_location("sandbox_evidence", SCRIPT)
module = module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def valid_payload():
    return {
        "schema_version": "pilot-e2e-01b-v1",
        "environment": {
            "environment_type": "sandbox",
            "environment_name": "BCS-PILOT",
            "bc_version": "28.3",
            "company_name": "BCSentinel Pilot E2E",
            "company_system_id": "11111111-1111-1111-1111-111111111111",
            "backend_tier": "staging",
            "backend_ready_http_status": 200,
            "app_version": "1.0.2.7",
            "app_commit_sha": "a" * 40,
        },
        "gates": [
            {
                "id": gate_id,
                "status": "PASS",
                "executed_at_utc": "2026-07-29T16:00:00Z",
                "evidence_files": [f"{gate_id}.txt"],
            }
            for gate_id in sorted(module.REQUIRED_GATES)
        ],
        "attestation": {
            "production_used": False,
            "real_customer_data_used": False,
            "secrets_in_evidence": False,
            "completed_by": "Daniel Wauer",
            "completed_at_utc": "2026-07-29T16:00:00Z",
        },
    }


def test_complete_sandbox_evidence_is_accepted_without_file_check():
    assert module.validate(valid_payload()) == []


def test_production_or_missing_evidence_fails_closed():
    payload = valid_payload()
    payload["environment"]["environment_type"] = "production"
    payload["gates"][0]["evidence_files"] = []
    errors = module.validate(payload)
    assert any("environment_type" in error for error in errors)
    assert any("requires at least one evidence file" in error for error in errors)


def test_evidence_paths_cannot_escape_root(tmp_path):
    payload = valid_payload()
    payload["gates"][0]["evidence_files"] = ["../secret.txt"]
    errors = module.validate(payload, tmp_path)
    assert any("unsafe evidence path" in error for error in errors)


def test_missing_gate_and_duplicate_gate_are_rejected():
    payload = valid_payload()
    payload["gates"].pop()
    payload["gates"].append(dict(payload["gates"][0]))
    errors = module.validate(payload)
    assert any("duplicate gate id" in error for error in errors)
    assert any("missing gates" in error for error in errors)
