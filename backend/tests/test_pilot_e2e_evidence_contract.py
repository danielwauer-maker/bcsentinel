from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "generate_pilot_e2e_evidence.py"


def _module():
    spec = importlib.util.spec_from_file_location("pilot_e2e_evidence", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _junit(path: Path, *, failures: int = 0, errors: int = 0) -> Path:
    path.write_text(
        f'<testsuite tests="3" failures="{failures}" errors="{errors}" skipped="1" time="0.25" />',
        encoding="utf-8",
    )
    return path


def test_canonical_matrix_is_valid_and_ids_are_unique() -> None:
    matrix = json.loads(
        (ROOT / "quality" / "pilot-e2e" / "pilot_test_matrix.json").read_text(encoding="utf-8")
    )
    ids = [entry["id"] for entry in matrix["tests"]]

    assert matrix["schema_version"] == "pilot-e2e-01a-v1"
    assert len(ids) == len(set(ids))
    assert all(entry["priority"] in {"P0", "P1", "P2"} for entry in matrix["tests"])
    assert all(entry["execution"] for entry in matrix["tests"])
    assert any(entry["execution"] == "manual_or_sandbox_automation" for entry in matrix["tests"])


def test_automated_gate_passes_only_with_matching_source_and_green_junit(tmp_path, monkeypatch) -> None:
    module = _module()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    test_file = tmp_path / "backend" / "tests" / "test_registration.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def test_placeholder(): pass\n", encoding="utf-8")
    matrix = {
        "schema_version": "test",
        "tests": [
            {
                "id": "AUTO-1",
                "priority": "P0",
                "area": "registration",
                "title": "Registration",
                "execution": "automated",
                "source_patterns": ["backend/tests/test_*registration*.py"],
                "expected": "pass",
                "evidence": "junit",
            }
        ],
    }

    report = module.build_report(matrix, module._read_junit(_junit(tmp_path / "junit.xml")))

    assert report["tests"][0]["status"] == "PASS"
    assert report["summary"]["p0_automated_ready"] is True


def test_automated_gate_fails_closed_when_coverage_is_missing(tmp_path, monkeypatch) -> None:
    module = _module()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    matrix = {
        "schema_version": "test",
        "tests": [
            {
                "id": "AUTO-1",
                "priority": "P0",
                "area": "credits",
                "title": "Credits",
                "execution": "automated",
                "source_patterns": ["backend/tests/test_*credit*.py"],
                "expected": "pass",
                "evidence": "junit",
            }
        ],
    }

    report = module.build_report(matrix, module._read_junit(_junit(tmp_path / "junit.xml")))

    assert report["tests"][0]["status"] == "FAIL"
    assert report["summary"]["overall_decision"] == "NOT_READY"
    assert report["summary"]["p0_automated_ready"] is False


def test_manual_and_sandbox_gates_never_become_pass_from_junit(tmp_path, monkeypatch) -> None:
    module = _module()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    matrix = {
        "schema_version": "test",
        "tests": [
            {
                "id": "BC-1",
                "priority": "P0",
                "area": "bc_sandbox",
                "title": "BC runtime",
                "execution": "manual_or_sandbox_automation",
                "source_patterns": [],
                "expected": "pass",
                "evidence": "screenshots",
                "blocker": "Real sandbox required.",
            },
            {
                "id": "UAT-1",
                "priority": "P1",
                "area": "ux",
                "title": "UAT",
                "execution": "manual",
                "source_patterns": [],
                "expected": "pass",
                "evidence": "checklist",
            },
        ],
    }

    report = module.build_report(matrix, module._read_junit(_junit(tmp_path / "junit.xml")))

    assert report["tests"][0]["status"] == "BLOCKED"
    assert report["tests"][1]["status"] == "MANUAL"
    assert report["summary"]["overall_decision"] == "NOT_READY"


def test_failed_junit_marks_covered_automated_gate_failed(tmp_path, monkeypatch) -> None:
    module = _module()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    source = tmp_path / "backend" / "tests" / "test_access.py"
    source.parent.mkdir(parents=True)
    source.write_text("def test_placeholder(): pass\n", encoding="utf-8")
    matrix = {
        "schema_version": "test",
        "tests": [
            {
                "id": "AUTO-1",
                "priority": "P0",
                "area": "access",
                "title": "Access",
                "execution": "automated",
                "source_patterns": ["backend/tests/test_*access*.py"],
                "expected": "pass",
                "evidence": "junit",
            }
        ],
    }

    report = module.build_report(
        matrix,
        module._read_junit(_junit(tmp_path / "junit.xml", failures=1)),
    )

    assert report["tests"][0]["status"] == "FAIL"
