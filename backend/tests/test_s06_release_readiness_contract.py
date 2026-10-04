from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "bc-extension" / "app.json"
CLOUD = ROOT / "bc-extension" / "app.cloud.json"
READINESS = ROOT / "quality" / "release" / "s06-release-readiness.json"


def _read(path: Path) -> dict:
    assert path.exists(), f"Missing required release-readiness file: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_s06_manifest_matches_current_extension_truth() -> None:
    app = _read(APP)
    cloud = _read(CLOUD)
    readiness = _read(READINESS)

    for key in (
        "id",
        "name",
        "publisher",
        "version",
        "runtime",
        "platform",
        "application",
        "idRanges",
        "resourceExposurePolicy",
        "features",
    ):
        assert app[key] == cloud[key], f"Cloud manifest drift for {key}"

    ext = readiness["extension"]
    assert ext["name"] == app["name"]
    assert ext["version"] == app["version"]
    assert ext["app_id"] == app["id"]
    assert ext["publisher"] == app["publisher"]
    assert ext["runtime"] == app["runtime"]
    assert ext["platform"] == app["platform"]
    assert ext["application"] == app["application"]
    assert ext["id_range"] == app["idRanges"][0]


def test_s06_reuses_existing_verified_install_upgrade_and_restore_evidence() -> None:
    readiness = _read(READINESS)
    evidence = readiness["verified_existing_evidence"]

    expected = {
        "fresh_installation": ("VERIFIED_WITH_KNOWN_DEFECTS", "quality/release/ext-50-02-fresh-installation-evidence.json"),
        "upgrade_data_preservation": ("PASS_WITH_KNOWN_DEFECTS", "quality/release/ext-50-03-upgrade-evidence.json"),
        "postgres_backup_restore": ("VERIFIED_IN_CI", "docs/P0_05_POSTGRES_BACKUP_RESTORE_AUDIT.md"),
        "operator_alerting": ("VERIFIED_IN_CI", "docs/P0_06_ALERTING_INCIDENT_ROLLBACK_AUDIT.md"),
    }

    for key, (status, relpath) in expected.items():
        assert evidence[key]["status"] == status
        assert evidence[key]["evidence"] == relpath
        assert (ROOT / relpath).exists(), f"Evidence target missing: {relpath}"


def test_s06_does_not_claim_release_candidate_or_manual_drill_completion() -> None:
    readiness = _read(READINESS)
    candidate = readiness["release_candidate"]

    assert readiness["status"] == "AUTOMATED_PREWORK_COMPLETE_MANUAL_GATES_OPEN"
    assert candidate == {
        "frozen": False,
        "source_commit": None,
        "artifact_file": None,
        "artifact_sha256": None,
    }

    manual = set(readiness["manual_gates_open"])
    assert {
        "final_release_candidate_sha_and_artifact_hash",
        "real_pilot_infrastructure_restore_with_rpo_rto",
        "bc_sandbox_rollback_or_roll_forward_drill",
        "pilot_release_approval",
    }.issubset(manual)


def test_s06_rollback_policy_is_non_destructive_and_fail_safe() -> None:
    policy = _read(READINESS)["rollback_policy"]

    assert policy["strategy"] == "ROLL_FORWARD_PREFERRED"
    assert policy["database_restore_required_before_destructive_recovery"] is True
    assert policy["automatic_tenant_or_extension_data_deletion_forbidden"] is True
    assert policy["backend_and_extension_must_be_treated_as_compatible_pair"] is True
    assert policy["real_infrastructure_drill_required_before_customer_go"] is True
