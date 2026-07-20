#!/usr/bin/env python3
"""Validate the BCSentinel Product Master Book without modifying the repository."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required (module 'yaml' is not installed).", file=sys.stderr)
    raise SystemExit(2)


BOOK = Path(__file__).resolve().parent.parent
REPO = BOOK.parents[1]
DATA = BOOK / "data"
YAML_FILES = ("components.yaml", "features.yaml", "workflows.yaml", "tests.yaml", "gaps.yaml")
TEST_STATUSES = {"none", "identified", "partial", "broad", "manual_only", "execution_unconfirmed"}
LEVELS = {"capability", "feature", "subfeature"}
FEATURE_FIELDS = {
    "id", "name", "level", "parent_id", "component", "area", "status", "description",
    "evidence", "interfaces", "tests", "documentation", "uncertainties", "related_features",
    "related_workflows", "source_confidence",
}
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


def load_yaml(name: str, check: Validation):
    path = DATA / name
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # parser diagnostics are part of the report
        check.error(f"{path.relative_to(BOOK)}: YAML parse failed: {exc}")
        return []
    if not isinstance(value, list):
        check.error(f"{path.relative_to(BOOK)}: root must be a list")
        return []
    return value


def index(items: list, label: str, check: Validation) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for pos, item in enumerate(items, 1):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            check.error(f"{label}[{pos}]: object with string id required")
            continue
        item_id = item["id"]
        if item_id in result:
            check.error(f"{label}: duplicate id {item_id}")
        result[item_id] = item
    return result


def evidence_paths(value, owner: str, check: Validation) -> None:
    if isinstance(value, dict):
        if "path" in value:
            raw = value["path"]
            if not isinstance(raw, str) or not raw.strip():
                check.error(f"{owner}: evidence path must be a non-empty string")
            else:
                target = (REPO / raw).resolve()
                try:
                    target.relative_to(REPO)
                except ValueError:
                    check.error(f"{owner}: evidence path escapes repository: {raw}")
                else:
                    if not target.exists():
                        check.error(f"{owner}: evidence path does not exist: {raw}")
        for child in value.values():
            evidence_paths(child, owner, check)
    elif isinstance(value, list):
        for child in value:
            evidence_paths(child, owner, check)


def validate_features(features: list, components: dict, workflows: dict, check: Validation) -> dict:
    by_id = index(features, "features", check)
    for feature_id, feature in by_id.items():
        missing = sorted(FEATURE_FIELDS - feature.keys())
        if missing:
            check.error(f"{feature_id}: missing fields: {', '.join(missing)}")
        level = feature.get("level")
        parent = feature.get("parent_id")
        if level not in LEVELS:
            check.error(f"{feature_id}: invalid level {level!r}")
        if feature.get("component") not in components:
            check.error(f"{feature_id}: unknown component {feature.get('component')!r}")
        if level == "capability" and parent is not None:
            check.error(f"{feature_id}: capability parent_id must be null")
        if level in {"feature", "subfeature"}:
            if parent not in by_id:
                check.error(f"{feature_id}: unknown parent_id {parent!r}")
            elif level == "feature" and by_id[parent].get("level") != "capability":
                check.error(f"{feature_id}: feature parent must be a capability")
            elif level == "subfeature" and by_id[parent].get("level") != "feature":
                check.error(f"{feature_id}: subfeature parent must be a feature")
        tests = feature.get("tests")
        if not isinstance(tests, dict) or tests.get("status") not in TEST_STATUSES:
            check.error(f"{feature_id}: invalid tests.status")
        evidence = feature.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            check.error(f"{feature_id}: at least one evidence item required")
        else:
            for pos, item in enumerate(evidence, 1):
                if not isinstance(item, dict) or not item.get("path") or not item.get("symbol"):
                    check.error(f"{feature_id}: evidence[{pos}] requires path and symbol")
        for related in feature.get("related_features", []):
            if related not in by_id:
                check.error(f"{feature_id}: unknown related feature {related}")
        for related in feature.get("related_workflows", []):
            if related not in workflows:
                check.error(f"{feature_id}: unknown related workflow {related}")
        evidence_paths(feature, feature_id, check)

    for feature_id in by_id:
        seen: set[str] = set()
        current = feature_id
        while current in by_id and by_id[current].get("parent_id") is not None:
            if current in seen:
                check.error(f"{feature_id}: parent cycle detected")
                break
            seen.add(current)
            current = by_id[current]["parent_id"]
    return by_id


def validate_workflows(workflows: dict, features: dict, components: dict, check: Validation) -> None:
    for workflow_id, workflow in workflows.items():
        if workflow.get("execution_mode") not in {"synchronous", "asynchronous", "mixed"}:
            check.error(f"{workflow_id}: invalid execution_mode")
        declared = workflow.get("components")
        if not isinstance(declared, list) or not declared:
            check.error(f"{workflow_id}: components must be a non-empty list")
        else:
            for component in declared:
                if component not in components:
                    check.error(f"{workflow_id}: unknown component {component}")
        steps = workflow.get("steps")
        if not isinstance(steps, list) or not steps:
            check.error(f"{workflow_id}: steps must be a non-empty list")
        else:
            for step in steps:
                feature_id = step.get("feature_id") if isinstance(step, dict) else None
                if feature_id not in features:
                    check.error(f"{workflow_id}: step references unknown feature {feature_id!r}")
        evidence_paths(workflow, workflow_id, check)


def validate_tests_and_gaps(items: list, label: str, features: dict, workflows: dict, check: Validation) -> None:
    by_id = index(items, label, check)
    for item_id, item in by_id.items():
        if label == "tests" and item.get("status") not in TEST_STATUSES:
            check.error(f"{item_id}: invalid suite status {item.get('status')!r}")
        for feature_id in item.get("related_features", []):
            if feature_id not in features:
                check.error(f"{item_id}: unknown related feature {feature_id}")
        for workflow_id in item.get("related_workflows", []):
            if workflow_id not in workflows:
                check.error(f"{item_id}: unknown related workflow {workflow_id}")
        evidence_paths(item, item_id, check)


def validate_markdown_links(check: Validation) -> None:
    for source in BOOK.rglob("*.md"):
        text = source.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            raw = match.group(1).strip().split(maxsplit=1)[0].strip("<>")
            if not raw or raw.startswith(("#", "http://", "https://", "mailto:")):
                continue
            raw = unquote(raw.split("#", 1)[0])
            target = (source.parent / raw).resolve()
            try:
                target.relative_to(BOOK)
            except ValueError:
                continue  # repository links outside the book are evidence, not internal navigation
            if not target.exists():
                check.error(f"{source.relative_to(BOOK)}: broken internal link {raw}")


def main() -> int:
    check = Validation()
    loaded = {name: load_yaml(name, check) for name in YAML_FILES}
    components = index(loaded["components.yaml"], "components", check)
    workflows = index(loaded["workflows.yaml"], "workflows", check)
    features = validate_features(loaded["features.yaml"], components, workflows, check)
    validate_workflows(workflows, features, components, check)
    validate_tests_and_gaps(loaded["tests.yaml"], "tests", features, workflows, check)
    validate_tests_and_gaps(loaded["gaps.yaml"], "gaps", features, workflows, check)
    validate_markdown_links(check)

    for warning in check.warnings:
        print(f"WARNING: {warning}")
    for error in check.errors:
        print(f"ERROR: {error}")
    if check.errors:
        print(f"FAILED: {len(check.errors)} error(s), {len(check.warnings)} warning(s).")
        return 1
    print(
        "OK: 5 YAML files; "
        f"{len(components)} components; {len(features)} inventory entries; "
        f"{len(workflows)} workflows; {len(loaded['tests.yaml'])} test suites; "
        f"{len(loaded['gaps.yaml'])} gaps; internal links and evidence paths valid."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
