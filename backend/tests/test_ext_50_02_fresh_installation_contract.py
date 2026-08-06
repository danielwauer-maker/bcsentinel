from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "quality" / "release" / "ext-50-02-fresh-installation-evidence.json"
PLAN = ROOT / "docs" / "EXT_50_02_FRESH_INSTALLATION.md"

EXPECTED_VERSION = "1.0.2.20"
EXPECTED_FILE = "BCSentinel Analytics - Daniel Wauer_BCSentinel_1.0.2.20.app"
EXPECTED_SHA256 = "62a5a5d380008f3d212bbc2834429ad4b3f3d36787b4ee567b7e68a2f4e78756"


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
    assert target["environment_name"]
    assert target["company"]


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


def test_ext_50_02_does_not_claim_runtime_pass_before_manual_evidence():
    evidence = _evidence()
    assert evidence["status"] == "AWAITING_MANUAL_BC_RUNTIME_EVIDENCE"
    assert set(evidence["required_evidence"].values()) == {"PENDING"}
    assert evidence["acceptance"]["all_required_evidence_pass"] is False


def test_ext_50_02_plan_contains_stop_and_acceptance_criteria():
    text = PLAN.read_text(encoding="utf-8")
    assert "## 6. Abnahmekriterien" in text
    assert "## 7. Stop-Kriterien" in text
    assert "kein zuvor installiertes BCSentinel-Paket" in text
    assert "kein SUPER als Dauerlösung" in text
