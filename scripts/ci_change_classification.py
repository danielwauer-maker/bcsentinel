#!/usr/bin/env python3
"""Classify GitHub change sets conservatively for CI routing.

Unknown paths and an unreadable event are deliberately classified as every
category. This script only reports policy; it never starts deployments.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Iterable

CATEGORIES = (
    "documentation_evidence",
    "dashboard",
    "backend",
    "migrations",
    "security_auth_tenant",
    "bc_al_bc27",
    "report_frontend",
    "release_ci",
)
FULL_VALIDATION = {"migrations", "security_auth_tenant", "release_ci"}


def _matches(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix + "/")


def classify(paths: Iterable[str] | None) -> dict[str, object]:
    """Return a conservative category map for repository-relative paths."""
    normalized = [path.strip()[2:] if path.strip().startswith("./") else path.strip() for path in paths or [] if path.strip()]
    categories: set[str] = set()
    unknown = not normalized

    for path in normalized:
        matched = False

        if (_matches(path, "docs") or _matches(path, "quality") or
                path == "tools/ai-control-center/data/evidence-status.json"):
            categories.add("documentation_evidence")
            matched = True
        if _matches(path, "tools/ai-control-center") or _matches(path, "dashboard"):
            categories.add("dashboard")
            matched = True
        if _matches(path, "backend"):
            categories.add("backend")
            matched = True
        if _matches(path, "backend/alembic"):
            categories.add("migrations")
            matched = True
        if (path.startswith("backend/app/security/") or
                path.startswith("backend/app/routers/auth") or
                path.startswith("backend/app/services/access_control") or
                path.startswith("backend/app/services/product_license")):
            categories.add("security_auth_tenant")
            matched = True
        if (_matches(path, "bc-extension") or _matches(path, "bc-performance") or
                _matches(path, "bc-finding-tests")):
            categories.add("bc_al_bc27")
            matched = True
        if (_matches(path, "landingpage") or _matches(path, "landingpage_neu") or
                path.startswith("backend/app/templates/")):
            categories.add("report_frontend")
            matched = True
        if (path.startswith(".github/workflows/") or path == "AGENTS.md" or
                path.startswith("docs/release/") or path.startswith("docs/ci/") or
                path.startswith("scripts/ci_") or path.startswith("scripts/verify_") or
                path.startswith("scripts/validate_release")):
            categories.add("release_ci")
            matched = True

        if not matched:
            unknown = True

    if unknown:
        categories = set(CATEGORIES)

    return {
        "categories": {category: category in categories for category in CATEGORIES},
        "all_critical": unknown,
        "requires_full_validation": unknown or bool(categories & FULL_VALIDATION),
        "decision": "all-critical" if unknown else "targeted",
        "paths": normalized,
    }


def paths_from_event(event_path: Path) -> list[str] | None:
    """Read PR or merge-queue commit bounds and ask git for changed paths."""
    try:
        event = json.loads(event_path.read_text(encoding="utf-8"))
        payload = event.get("pull_request") or event.get("merge_group")
        base = payload["base"]["sha"] if "pull_request" in event else payload["base_sha"]
        head = payload["head"]["sha"] if "pull_request" in event else payload["head_sha"]
        if not all(isinstance(value, str) and len(value) == 40 for value in (base, head)):
            return None
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{base}...{head}"],
            check=True, capture_output=True, text=True,
        )
        return result.stdout.splitlines()
    except (KeyError, OSError, ValueError, subprocess.CalledProcessError):
        return None


def write_outputs(result: dict[str, object], output: Path) -> None:
    categories = result["categories"]
    with output.open("a", encoding="utf-8") as stream:
        for name, enabled in categories.items():
            stream.write(f"{name}={'true' if enabled else 'false'}\n")
        stream.write(f"all_critical={'true' if result['all_critical'] else 'false'}\n")
        stream.write(
            f"requires_full_validation={'true' if result['requires_full_validation'] else 'false'}\n"
        )
        stream.write(f"decision={result['decision']}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--event", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    paths = args.path or (paths_from_event(args.event) if args.event else None)
    result = classify(paths)
    print(json.dumps(result, sort_keys=True))
    if args.output:
        write_outputs(result, args.output)


if __name__ == "__main__":
    main()
