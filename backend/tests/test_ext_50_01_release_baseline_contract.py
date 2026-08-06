from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP_MANIFEST = ROOT / "bc-extension" / "app.json"
CLOUD_MANIFEST = ROOT / "bc-extension" / "app.cloud.json"
RELEASE_MANIFEST = ROOT / "quality" / "release" / "ext-50-01-release-baseline.json"

REQUIRED_VERSION = "1.0.2.20"
REQUIRED_PLATFORM = "27.0.0.0"
REQUIRED_RUNTIME = "16.0"
EXPECTED_APP_FILE = "BCSentinel Analytics - Daniel Wauer_BCSentinel_1.0.2.20.app"
EXPECTED_APP_SHA256 = "62a5a5d380008f3d212bbc2834429ad4b3f3d36787b4ee567b7e68a2f4e78756"


def _read_json(path: Path) -> dict:
    assert path.exists(), f"Required release file is missing: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_al_manifests_are_identical_for_release_critical_fields():
    app = _read_json(APP_MANIFEST)
    cloud = _read_json(CLOUD_MANIFEST)

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
        assert app[key] == cloud[key], f"Manifest drift detected for {key}"


def test_release_baseline_targets_bc27_and_version_1_0_2_20():
    app = _read_json(APP_MANIFEST)
    assert app["version"] == REQUIRED_VERSION
    assert app["platform"] == REQUIRED_PLATFORM
    assert app["application"] == REQUIRED_PLATFORM
    assert app["runtime"] == REQUIRED_RUNTIME


def test_release_manifest_matches_al_manifest_and_final_artifact():
    app = _read_json(APP_MANIFEST)
    release = _read_json(RELEASE_MANIFEST)

    assert release["sprint"] == "EXT-50-01"
    assert release["release_status"] == "VERIFIED_IN_CI"
    assert release["extension"]["name"] == app["name"]
    assert release["extension"]["app_id"] == app["id"]
    assert release["extension"]["version"] == app["version"]
    assert release["extension"]["platform"] == app["platform"]
    assert release["extension"]["application"] == app["application"]
    assert release["extension"]["runtime"] == app["runtime"]
    assert release["source_branch"] == "staging"
    assert release["artifact"]["file_name"] == EXPECTED_APP_FILE
    assert release["artifact"]["sha256"] == EXPECTED_APP_SHA256
    assert re.fullmatch(r"[0-9a-f]{64}", release["artifact"]["sha256"])
    assert release["artifact"]["workflow_run_id"] == 31081200637
    assert release["artifact"]["workflow_artifact_id"] == 8960052092


def test_release_baseline_documents_remaining_manual_gates():
    release = _read_json(RELEASE_MANIFEST)
    required = {
        "fresh_installation",
        "upgrade_matrix",
        "production_release_approval",
    }
    assert required.issubset(set(release["manual_gates_open"]))
    assert "artifact_archive_and_sha256" not in release["manual_gates_open"]
