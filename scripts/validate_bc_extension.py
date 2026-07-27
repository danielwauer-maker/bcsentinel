from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BC_ROOT = ROOT / "bc-extension"
APP_JSON = BC_ROOT / "app.json"
SETTINGS_JSON = BC_ROOT / ".vscode" / "settings.json"
RULESET_JSON = BC_ROOT / "app.ruleset.json"
SOURCE_ROOT = BC_ROOT / "app" / "src"
SETUP_EXTENSION = SOURCE_ROOT / "pageextensions" / "DHSetupProductCopy.PageExt.al"

OBJECT_PATTERN = re.compile(
    r"^\s*(tableextension|table|pageextension|page|codeunit|reportextension|report|"
    r"enumextension|enum|query|xmlport|permissionsetextension|permissionset|controladdin|interface)"
    r"\s+(\d+)\s+\"([^\"]+)\"",
    re.IGNORECASE | re.MULTILINE,
)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"Required file is missing: {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}")


def main() -> None:
    manifest = load_json(APP_JSON)
    settings = load_json(SETTINGS_JSON)
    load_json(RULESET_JSON)

    id_ranges = manifest.get("idRanges")
    if not isinstance(id_ranges, list) or not id_ranges:
        fail("bc-extension/app.json must define at least one idRanges entry")

    allowed_ranges: list[tuple[int, int]] = []
    for entry in id_ranges:
        try:
            start = int(entry["from"])
            end = int(entry["to"])
        except (KeyError, TypeError, ValueError):
            fail("Every idRanges entry must contain integer from/to values")
        if start > end:
            fail(f"Invalid object range {start}..{end}")
        allowed_ranges.append((start, end))

    analyzers = settings.get("al.codeAnalyzers", [])
    required_analyzers = {"${CodeCop}", "${AppSourceCop}", "${PerTenantExtensionCop}"}
    missing_analyzers = required_analyzers.difference(analyzers)
    if missing_analyzers:
        fail(f"Missing configured AL analyzers: {sorted(missing_analyzers)}")

    if settings.get("al.ruleSetPath") != "./app.ruleset.json":
        fail("al.ruleSetPath must point to ./app.ruleset.json")

    if not SOURCE_ROOT.is_dir():
        fail(f"AL source directory is missing: {SOURCE_ROOT.relative_to(ROOT)}")

    objects_by_identity: dict[tuple[str, int], list[Path]] = defaultdict(list)
    names_by_type: dict[tuple[str, str], list[Path]] = defaultdict(list)
    parsed_objects = 0

    for path in sorted(SOURCE_ROOT.rglob("*.al")):
        text = path.read_text(encoding="utf-8-sig")
        for object_type, object_id_text, object_name in OBJECT_PATTERN.findall(text):
            parsed_objects += 1
            normalized_type = object_type.lower()
            object_id = int(object_id_text)
            relative_path = path.relative_to(ROOT)

            if not any(start <= object_id <= end for start, end in allowed_ranges):
                fail(
                    f"{normalized_type} {object_id} '{object_name}' in {relative_path} "
                    f"is outside app.json idRanges"
                )

            objects_by_identity[(normalized_type, object_id)].append(relative_path)
            names_by_type[(normalized_type, object_name.casefold())].append(relative_path)

    if parsed_objects == 0:
        fail("No AL objects were parsed from bc-extension/app/src")

    duplicate_ids = {
        key: paths for key, paths in objects_by_identity.items() if len(paths) > 1
    }
    if duplicate_ids:
        details = "; ".join(
            f"{object_type} {object_id}: {', '.join(map(str, paths))}"
            for (object_type, object_id), paths in sorted(duplicate_ids.items())
        )
        fail(f"Duplicate AL object IDs detected: {details}")

    duplicate_names = {
        key: paths for key, paths in names_by_type.items() if len(paths) > 1
    }
    if duplicate_names:
        details = "; ".join(
            f"{object_type} '{object_name}': {', '.join(map(str, paths))}"
            for (object_type, object_name), paths in sorted(duplicate_names.items())
        )
        fail(f"Duplicate AL object names detected: {details}")

    if not SETUP_EXTENSION.is_file():
        fail("ARCH-02A setup product-copy pageextension is missing")

    setup_text = SETUP_EXTENSION.read_text(encoding="utf-8-sig")
    required_fragments = (
        'pageextension 53199 "DH Setup Product Copy" extends "DH Setup"',
        "modify(BuyFullAnalysis)",
        "Caption = 'Start Assessment';",
        "modify(BuyValidationCheck)",
        "modify(StartMonitoringMonthly)",
        "modify(StartMonitoringAnnual)",
    )
    for fragment in required_fragments:
        if fragment not in setup_text:
            fail(f"Missing expected setup pageextension fragment: {fragment}")

    print(
        "BC extension source preflight PASS: "
        f"{parsed_objects} AL objects, ranges {allowed_ranges}, analyzers configured."
    )


if __name__ == "__main__":
    main()
