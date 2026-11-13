#!/usr/bin/env python3
"""Fail-closed AL schema compatibility audit against *verified installed-app* metadata.

Input JSON must be produced from the actual installed BC SaaS .app/symbol metadata
by a reviewer. Never use GitHub main/staging as a substitute for that baseline.

JSON format:
{"tables": [{"id": 53100, "name": "DH Setup", "fields": [
    {"id": 1, "name": "Primary Key", "type": "Code[10]"}]}]}

This is a conservative source-level audit, NOT proof that an in-place SaaS upgrade
will succeed. Table fields are aggregated with tableextension fields by table name.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TABLE = re.compile(r'^\s*table\s+(\d+)\s+"([^"]+)"', re.M | re.I)
EXTENSION = re.compile(r'^\s*tableextension\s+\d+\s+"[^"]+"\s+extends\s+"([^"]+)"', re.M | re.I)
FIELD = re.compile(r'\bfield\s*\(\s*(\d+)\s*;\s*("[^"]+"|[A-Za-z_][\w]*)\s*;\s*([^\)]+?)\s*\)', re.I | re.S)


def norm(value: str) -> str:
    return re.sub(r'\s+', '', str(value)).casefold()


def collect_source(source: Path) -> dict[str, dict]:
    if not source.is_dir():
        raise ValueError("AL source directory does not exist")
    tables: dict[str, dict] = {}
    extensions: list[tuple[str, list[dict]]] = []
    paths = sorted(source.rglob("*.al"))
    if not paths:
        raise ValueError("No AL files found")
    for path in paths:
        raw = path.read_text(encoding="utf-8-sig")
        # Avoid commented-out declarations being counted as persisted fields.
        raw = re.sub(r'/\*.*?\*/', '', raw, flags=re.S)
        raw = re.sub(r'(?m)^\s*//.*$', '', raw)
        table = TABLE.search(raw)
        extension = EXTENSION.search(raw)
        if not table and not extension:
            continue
        fields: list[dict] = []
        for match in FIELD.finditer(raw):
            fields.append({"id": int(match.group(1)),
                           "name": match.group(2).strip('"'),
                           "type": match.group(3).strip()})
        if table:
            table_id, name = int(table.group(1)), table.group(2)
            key = name.casefold()
            if key in tables:
                raise ValueError(f"Duplicate AL table declaration: {name}")
            tables[key] = {"id": table_id, "name": name, "fields": fields}
        else:
            extensions.append((extension.group(1).casefold(), fields))
    for target, fields in extensions:
        if target in tables:
            tables[target]["fields"].extend(fields)
    return tables


def compare_installed(baseline: dict, source: dict[str, dict]) -> list[str]:
    if not isinstance(baseline, dict) or not isinstance(baseline.get("tables"), list) or not baseline["tables"]:
        raise ValueError("Verified installed-app baseline must contain a non-empty tables array")
    failures = []
    seen_tables = set()
    for table in baseline["tables"]:
        if not isinstance(table, dict) or not isinstance(table.get("id"), int) or not isinstance(table.get("name"), str) or not isinstance(table.get("fields"), list):
            raise ValueError("Invalid installed table metadata")
        key = table["name"].casefold()
        if key in seen_tables:
            raise ValueError("Duplicate table in baseline")
        seen_tables.add(key)
        actual = source.get(key)
        if actual is None or actual["id"] != table["id"]:
            failures.append(f"Missing/renumbered table {table['id']} {table['name']}")
            continue
        indexed: dict[int, dict] = {}
        for field in actual["fields"]:
            if field["id"] in indexed:
                failures.append(f"Duplicate field ID {field['id']} in table {table['name']}")
            indexed[field["id"]] = field
        seen_fields = set()
        for field in table["fields"]:
            if not isinstance(field, dict) or not isinstance(field.get("id"), int) or not isinstance(field.get("name"), str) or not isinstance(field.get("type"), str):
                raise ValueError("Invalid installed field metadata")
            number = field["id"]
            if number in seen_fields:
                raise ValueError("Duplicate field ID in installed baseline")
            seen_fields.add(number)
            candidate = indexed.get(number)
            if candidate is None:
                failures.append(f"Missing persisted field {table['name']} #{number} {field['name']}")
            elif candidate["name"].casefold() != field["name"].casefold() or norm(candidate["type"]) != norm(field["type"]):
                failures.append(f"Changed persisted field {table['name']} #{number}: installed {field['name']} ({field['type']}); source {candidate['name']} ({candidate['type']})")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed-baseline", type=Path, required=True, help="Reviewed JSON extracted from the actually installed .app")
    parser.add_argument("--source", type=Path, default=Path("bc-extension/app/src"))
    args = parser.parse_args()
    try:
        if not args.installed_baseline.is_file():
            raise ValueError("Verified installed-app baseline not supplied; refusing release gate")
        baseline = json.loads(args.installed_baseline.read_text(encoding="utf-8"))
        issues = compare_installed(baseline, collect_source(args.source))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"SCHEMA GATE NOT VERIFIED: {exc}", file=sys.stderr)
        return 3
    for issue in issues:
        print(f"SCHEMA INCOMPATIBLE: {issue}", file=sys.stderr)
    if issues:
        return 2
    print("Source schema matches supplied installed baseline for declared tables/fields; real BC upgrade remains mandatory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
