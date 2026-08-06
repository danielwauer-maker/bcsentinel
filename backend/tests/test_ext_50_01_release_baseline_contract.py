from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP_MANIFEST = ROOT / "bc-extension" / "app.json"
CLOUD_MANIFEST = ROOT / "bc-extension" / "app.cloud.json"
RELEASE_MANIFEST = ROOT / "quality" / "release" / "ext-50-01-release-baseline.json"

REQUIRED_VERSION = "1.0.2.20"
REQUIRED_PLATFORM = "27.0.0.0"
REQUIRED_RUNTIME = "16.0"


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


def test_release_manifest_matches_al_manifest_and_is_not_placeholder():
    app = _read_json(APP_MANIFEST)
    release = _read_json(RELEASE_MANIFEST)

    assert release["sprint"] == "EXT-50-01"
    assert release["release_status"] == "BASELINE_LOCKED_FOR_RC_VALIDATION"
    assert release["extension"]["name"] == app["name"]
    assert release["extension"]["app_id"] == app["id"]
    assert release["extension"]["version"] == app["version"]
    assert release["extension"]["platform"] == app["platform"]
    assert release["extension"]["application"] == app["application"]
    assert release["extension"]["runtime"] == app["runtime"]
    assert release["source_branch"] == "staging"
    assert release["artifact"]["sha256"] == "PENDING_CI_ARTIFACT"
    assert release["artifact"]["file_name"] == "PENDING_CI_ARTIFACT"


def test_release_baseline_documents_required_manual_gates():
    release = _read_json(RELEASE_MANIFEST)
    required = {
        "fresh_installation",
        "upgrade_matrix",
        "artifact_archive_and_sha256",
        "production_release_approval",
    }
    assert required.issubset(set(release["manual_gates_open"]))
