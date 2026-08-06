from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP_JSON = ROOT / "bc-extension" / "app.json"
EVIDENCE = ROOT / "quality" / "release" / "ext-50-03-upgrade-evidence.json"
PLAN = ROOT / "docs" / "EXT_50_03_UPGRADE_AND_DATA_PRESERVATION.md"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_target_extension_baseline_is_release_1_0_2_20() -> None:
    app = _json(APP_JSON)
    assert app["id"] == "8c7f0f9c-0c1a-4a4e-9c6f-111111111111"
    assert app["name"] == "BCSentinel"
    assert app["publisher"] == "BCSentinel Analytics - Daniel Wauer"
    assert app["version"] == "1.0.2.20"
    assert app["runtime"] == "16.0"
    assert app["platform"] == "27.0.0.0"
    assert app["application"] == "27.0.0.0"
    assert app["idRanges"] == [{"from": 53100, "to": 53201}]


def test_upgrade_baseline_and_manual_gate_are_explicit() -> None:
    evidence = _json(EVIDENCE)
    assert evidence["sprint"] == "EXT-50-03"
    assert evidence["baseline"]["source_version"] == "1.0.2.16"
    assert evidence["baseline"]["target_version"] == "1.0.2.20"
    assert evidence["status"] == "AWAITING_MANUAL_BC_RUNTIME_EVIDENCE"
    assert evidence["decision"] == "NOT_READY_FOR_PASS_UNTIL_MANUAL_RUNTIME_EVIDENCE"


def test_all_runtime_checks_are_present_and_not_prematurely_passed() -> None:
    evidence = _json(EVIDENCE)
    required_sections = (
        "pre_upgrade",
        "upgrade",
        "data_preservation",
        "post_upgrade_function",
    )
    for section_name in required_sections:
        section = evidence[section_name]
        assert section, f"{section_name} must not be empty"
        assert all(value == "PENDING" for value in section.values()), (
            f"{section_name} contains a premature result before manual BC evidence"
        )


def test_plan_contains_stop_and_acceptance_criteria() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    for required in (
        "1.0.2.16",
        "1.0.2.20",
        "ohne Deinstallation",
        "Scan-Historie",
        "Job-Queue-Eintrag",
        "manueller Monitoring-Scan",
        "Geplanten Scan",
        "Stop-Kriterien",
        "EXT-50-04",
    ):
        assert required in plan


def test_known_defects_are_carried_forward() -> None:
    evidence = _json(EVIDENCE)
    defects = {item["id"]: item["severity"] for item in evidence["known_defects_carried_forward"]}
    assert defects["P1-free-entitlement-leak"] == "P1"
    assert defects["P2-background-page-refresh"] == "P2"
