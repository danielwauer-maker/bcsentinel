"""Fail-closed static contract for the pre-BC27 manual acceptance template."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_fiverr_bc27_template_never_implies_automatic_approval():
    path = ROOT / "quality" / "release" / "dev-bc27-fiverr-acceptance-20261114.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["status"] == "NOT_EXECUTED"
    assert data["decision"] == "NO_GO"
    assert data["reference"]["core_sha"] == "caf245b23a74d4691fe62dfc5c4de805c730a171"
    assert data["reference"]["alembic"] == "0041_pilot_enrollment"
    assert data["reference"]["extension_source_version"] == "1.0.2.60"
    assert data["reference"]["actual_installed_version"] is None
    assert data["safety"]["automatic_fiverr_approval"] is False
    cases = data["cases"]
    assert len(cases) == 12
    assert len({c["id"] for c in cases}) == 12
    assert all(c["status"] == "NOT_EXECUTED" and not c["evidence_refs"] and c["reviewed_by"] is None for c in cases)
    expected = {"21", "30", "31", "32", "33", "43", "121", "18"}
    seen = {ref.rsplit("#", 1)[-1] for c in cases for ref in c["issue_refs"]}
    assert expected.issubset(seen)
