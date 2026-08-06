from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "quality" / "release" / "ext-50-02-fresh-installation-evidence.json"
PLAN = ROOT / "docs" / "EXT_50_02_FRESH_INSTALLATION.md"

EXPECTED_VERSION = "1.0.2.20"
EXPECTED_FILE = "BCSentinel Analytics - Daniel Wauer_BCSentinel_1.0.2.20.app"
EXPECTED_SHA256 = "62a5a5d380008f3d212bbc2834429ad4b3f3d36787b4ee567b7e68a2f4e78756"
ALLOWED_EVIDENCE_STATES = {
    "PASS",
    "PASS_WITH_DEFECT",
    "DEFERRED_TO_EXT_50_04",
}


def _evidence() -> dict:
    assert EVIDENCE.exists()
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_ext_50_02_uses_verified_release_baseline():
    evidence = _evidence()
    baseline = evidence["baseline"]
    assert baseline["extension_version"] == EXPECTED_VERSION
    assert baseline["app_file"] == EXPECTED_FILE
    assert baseline["app_sha256"] == EXPECTED_SHA256
    assert baseline["source_branch"] == "staging"


def test_ext_50_02_requires_a_genuinely_fresh_bc_environment():
    target = _evidence()["target_environment"]
    assert target["tenant_type"] == "Business Central SaaS sandbox"
    assert target["fresh_install_required"] is True
    assert target["previous_bcsentinel_version_allowed"] is False
    assert target["environment_name"] == "BCSentinel-Pilot-Fresh"
    assert target["bc_version"] == "28.3"
    assert target["api_base_url"] == "https://dev-api.bcsentinel.com"


def test_ext_50_02_tracks_all_runtime_acceptance_evidence():
    evidence = _evidence()
    required = {
        "app_upload",
        "app_install",
        "extension_version_visible",
        "permission_assignment",
        "setup_page_open",
        "backend_registration",
        "duplicate_registration_protection",
        "free_scan_start",
        "free_scan_completed",
        "history_entry",
        "findings_visible",
        "html_report",
        "pdf_report",
        "dashboard_link",
        "manual_monitoring_scan",
        "scheduled_monitoring_scan",
    }
    assert required == set(evidence["required_evidence"])
    assert set(evidence["required_evidence"].values()).issubset(ALLOWED_EVIDENCE_STATES)


def test_ext_50_02_runtime_evidence_is_complete():
    evidence = _evidence()
    runtime = evidence["required_evidence"]
    assert evidence["status"] == "VERIFIED_WITH_KNOWN_DEFECTS"
    assert runtime["permission_assignment"] == "DEFERRED_TO_EXT_50_04"
    assert runtime["findings_visible"] == "PASS_WITH_DEFECT"
    for key, value in runtime.items():
        if key not in {"permission_assignment", "findings_visible"}:
            assert value == "PASS", f"{key} must be PASS"
    assert evidence["acceptance"]["all_required_evidence_pass"] is True


def test_ext_50_02_records_expected_permission_sets():
    evidence = _evidence()
    assert evidence["delivered_permission_sets"] == [
        "BCSENTINEL ADMIN",
        "BCSENTINEL SCAN",
        "BCSENTINEL SCHEDULER",
        "BCSENTINEL SETUP",
        "BCSENTINEL VIEWER",
    ]


def test_ext_50_02_records_monitoring_success():
    evidence = _evidence()
    monitoring = evidence["monitoring_access"]
    assert monitoring["plan"] == "Monitoring Monatsabo"
    assert monitoring["dashboard_access"] == "FULL"
    assert monitoring["findings_access"] == "FULL"
    assert monitoring["report_access"] == "FULL"
    assert monitoring["active_modules"] == "10/10"
    assert monitoring["active_checks"] == "199/199"

    manual = evidence["scan_result"]["manual_monitoring_scan"]
    scheduled = evidence["scan_result"]["scheduled_monitoring_scan"]
    assert manual["status"] == "Completed"
    assert manual["modules"] == "10/10"
    assert manual["checks"] == "199/199"
    assert scheduled["status"] == "Completed"
    assert scheduled["runs_without_open_bc_client"] is True


def test_ext_50_02_records_known_defects_without_hiding_them():
    evidence = _evidence()
    defects = {item["id"]: item for item in evidence["observed_defects"]}
    assert defects["EXT-50-02-FREE-ENTITLEMENT-01"]["severity"] == "P1"
    assert defects["EXT-50-02-UI-REFRESH-01"]["severity"] == "P2"


def test_ext_50_02_plan_contains_stop_and_acceptance_criteria():
    text = PLAN.read_text(encoding="utf-8")
    assert "## 6. Abnahmekriterien" in text
    assert "## 7. Stop-Kriterien" in text
    assert "kein zuvor installiertes BCSentinel-Paket" in text
    assert "kein SUPER als Dauerlösung" in text
