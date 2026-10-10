from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "config" / "e2-regression-matrix.json"
REQUIRED_CATEGORIES = {
    "al_and_contracts",
    "backend",
    "dashboard",
    "accessibility",
    "responsive",
    "security",
}


def fail(message: str) -> None:
    raise SystemExit(f"E2 Automated Regression Quality Gate: FAIL - {message}")


def main() -> None:
    if not MATRIX.exists():
        fail("missing config/e2-regression-matrix.json")

    data = json.loads(MATRIX.read_text(encoding="utf-8"))
    if data.get("sprint") != "E2":
        fail("matrix sprint must be E2")
    if float(data.get("target_readiness_pct", 0)) != 97.5:
        fail("target readiness must be 97.5")

    categories = data.get("categories") or {}
    missing_categories = REQUIRED_CATEGORIES.difference(categories)
    if missing_categories:
        fail(f"missing categories: {sorted(missing_categories)}")

    for name in REQUIRED_CATEGORIES:
        if categories[name].get("required") is not True:
            fail(f"category {name} must be required")

    contract_checks = categories["al_and_contracts"].get("checks") or []
    if len(contract_checks) < 10:
        fail("AL/contract regression list is unexpectedly small")
    for relative in contract_checks:
        if not (ROOT / relative).is_file():
            fail(f"missing referenced validator: {relative}")

    evidence_paths: set[str] = set()
    for name in ("accessibility", "security"):
        path = categories[name].get("evidence_check")
        if path:
            evidence_paths.add(path)
    evidence_paths.update(categories["responsive"].get("evidence_checks") or [])
    for relative in evidence_paths:
        if not (ROOT / relative).is_file():
            fail(f"missing evidence validator: {relative}")

    backend = categories["backend"]
    if backend.get("command") != "pytest -q" or backend.get("scope") != "backend/tests":
        fail("backend regression must cover the full backend test suite")

    dashboard_commands = categories["dashboard"].get("commands") or []
    if dashboard_commands != ["npm run check", "npm run build"]:
        fail("dashboard regression must type-check and production-build")

    deferred = data.get("deferred_runtime_gates") or {}
    if set(deferred) != {"E3", "E4"}:
        fail("runtime/external acceptance may only be deferred to E3 and E4")

    workflow = ROOT / ".github" / "workflows" / "automated-regression-quality.yml"
    if not workflow.is_file():
        fail("missing E2 workflow")
    workflow_text = workflow.read_text(encoding="utf-8")
    for marker in (
        "E2 Automated Regression Quality Gate",
        "validate_e2_automated_regression.py",
        "pytest -q",
        "npm run check",
        "npm run build",
        "release-gate",
    ):
        if marker not in workflow_text:
            fail(f"workflow missing required marker: {marker}")

    print("E2 Automated Regression Quality Gate: PASS")


if __name__ == "__main__":
    main()
