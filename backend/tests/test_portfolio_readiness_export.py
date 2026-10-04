from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "quality" / "portfolio-readiness-evidence.json"


def test_portfolio_evidence_snapshot_is_current() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "export_portfolio_readiness.py"), "--check"],
        cwd=ROOT,
        check=True,
    )


def test_portfolio_evidence_contains_only_facts_not_percentages() -> None:
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    facts = payload["facts"]
    rendered_facts = json.dumps(facts).lower()
    assert "percentage" not in rendered_facts
    assert "readiness_pct" not in rendered_facts
    assert all("complete" in fact for fact in facts.values())
