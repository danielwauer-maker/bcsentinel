#!/usr/bin/env python3
"""Static preflight: preserve the schema in user-supplied BCSentinel 1.0.2.25 .app.

This is a *baseline* compatibility gate, not a substitute for comparing against
the tenant's installed 1.0.2.28 package or running a real BC SaaS upgrade.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "bc-extension" / "app" / "src"
MANIFEST = ROOT / "bc-extension" / "app.json"

TABLE_FIELDS = {
    "DHSetup.Table.al": {**{n: None for n in range(1, 76)}},
    "DHScanCheckSelection.Table.al": {**{n: None for n in range(1, 12)}},
    "DHDeepScanFinding.Table.al": {13: ("Group Key", "Text[64]")},
    "DHScanHeader.Table.al": {36: ("Applied Exception Count", "Integer")},
    "DHDeepScanRun.Table.al": {
        55: ("Scan Mode", "Text[30]"),
        56: ("Client Request ID", "Guid"),
        57: ("Start Request Status", "Option"),
        58: ("Start Attempt Count", "Integer"),
        59: ("Last Start Attempt", "DateTime"),
        60: ("Execution Token", "Guid"),
        61: ("Correlation ID", "Text[50]"),
        62: ("Execution Attempt", "Integer"),
        63: ("Lease Expires At", "DateTime"),
        64: ("Backend Sync Status", "Option"),
        65: ("Backend Sync Error", "Text[250]"),
        66: ("Applied Exception Count", "Integer"),
    },
}

SETUP_LEGACY = {
    36: ("Contact Email", "Text[100]"),
    37: ("Can Run Data Health Score", "Boolean"),
    38: ("Data Health Score Completed", "Boolean"),
    39: ("Scheduled Scans Enabled", "Boolean"),
    40: ("Schedule Frequency", 'Enum "DH Scan Schedule Frequency"'),
    41: ("Schedule Time", "Time"),
    **{i: (f"Schedule {name}", "Boolean") for i, name in enumerate(
        ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"), 42)},
    49: ("Monthly Schedule Day", "Integer"),
    50: ("Next Scheduled Scan", "DateTime"),
    51: ("Last Scheduled Scan", "DateTime"),
    52: ("Last Scheduled Scan Result", 'Enum "DH Scheduled Scan Result"'),
    53: ("Last Scheduled Scan Duration", "Duration"),
    54: ("Scheduled Scan Failure Count", "Integer"),
    55: ("Last Scheduled Scan Error", "Text[250]"),
    56: ("Scheduled Scan Task ID", "Guid"),
    57: ("Assessment Credits Available", "Integer"),
    58: ("Validation Credits Available", "Integer"),
    59: ("Access Snapshot Received At", "DateTime"),
    60: ("Access Server Time UTC", "DateTime"),
    61: ("Access Snapshot Expires At", "DateTime"),
    62: ("Access Snapshot Version", "Text[30]"),
    63: ("Access Snapshot Tenant ID", "Text[100]"),
    64: ("Access Snapshot Environment", "Text[100]"),
    65: ("Access Snapshot Env. Type", "Text[20]"),
    66: ("Access Snapshot Company ID", "Text[50]"),
    67: ("Access Snapshot API URL", "Text[250]"),
    68: ("Can View Reports", "Boolean"),
    69: ("Can Use Monitoring", "Boolean"),
    70: ("Subscription Active", "Boolean"),
    71: ("Report Access Until", "Text[50]"),
    72: ("Access Correlation ID", "Text[50]"),
    73: ("Free Assessment Used", "Boolean"),
    74: ("Premium Until", "Text[50]"),
    75: ("Monitoring Until", "Text[50]"),
}
TABLE_FIELDS["DHSetup.Table.al"].update(SETUP_LEGACY)
TABLE_FIELDS["DHScanCheckSelection.Table.al"].update({
    1: ("Check Code", "Code[50]"), 2: ("Module", "Text[100]"),
    3: ("Name", "Text[150]"), 4: ("Description", "Text[250]"),
    5: ("Enabled", "Boolean"), 6: ("Default Enabled", "Boolean"),
    7: ("Risk Level", "Code[20]"), 8: ("Sort Order", "Integer"),
    9: ("Last Modified At", "DateTime"), 10: ("Last Run At", "DateTime"),
    11: ("Last Finding Count", "Integer"),
})

FIELD = re.compile(r'field\(\s*(\d+)\s*;\s*("[^"]+"|[\w .%-]+)\s*;\s*(Enum\s+"[^"]+"|\w+(?:\[\d+\])?)\s*\)', re.I)

def main() -> int:
    errors: list[str] = []
    app = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    if tuple(map(int, app["version"].split("."))) < (1, 0, 2, 31):
        errors.append("Schema fix must ship as 1.0.2.31 or later")
    for filename, expected in TABLE_FIELDS.items():
        path = SRC / "tables" / filename
        if not path.exists():
            errors.append(f"Missing legacy table {filename}")
            continue
        code = path.read_text(encoding="utf-8-sig")
        # Field declarations must occur within the table's fields block.
        # A regex over the complete file alone misses the AL syntax regression
        # that caused widespread missing-method diagnostics in 1.0.2.31.
        begin_fields = re.search(r"\bfields\s*\{", code)
        begin_keys = re.search(r"\bkeys\s*\{", code)
        if not begin_fields or not begin_keys or begin_keys.start() <= begin_fields.end():
            errors.append(f"{filename}: malformed fields/keys sections")
            continue
        depth = 1
        fields_end = None
        for pos in range(begin_fields.end(), len(code)):
            if code[pos] == "{":
                depth += 1
            elif code[pos] == "}":
                depth -= 1
                if depth == 0:
                    fields_end = pos
                    break
        if fields_end is None or fields_end > begin_keys.start():
            errors.append(f"{filename}: fields block is not correctly closed before keys")
            continue
        field_section = code[begin_fields.end():fields_end]
        found = {
            int(m.group(1)): (m.group(2).strip('"'), m.group(3))
            for m in FIELD.finditer(field_section)
        }
        for field_id, signature in expected.items():
            if field_id not in found:
                errors.append(f"{filename}: missing field {field_id}")
            elif signature is not None and found[field_id] != signature:
                errors.append(f"{filename}: field {field_id} is {found[field_id]!r} rather than {signature!r}")
    expected_tables = {
        53194: "DH Scan Check Selection",
        53196: "DH Remediation Action",
    }
    for table_id, table_name in expected_tables.items():
        file = SRC / "tables" / ("DHScanCheckSelection.Table.al" if table_id == 53194 else "DHRemediationAction.Table.al")
        if f'table {table_id} "{table_name}"' not in file.read_text(encoding="utf-8-sig"):
            errors.append(f"Table ID {table_id} must belong to {table_name}")
    for name in ("DHScanScheduleFrequency.Enum.al", "DHScheduledScanResult.Enum.al", "DHScanTriggerContext.Enum.al"):
        if not (SRC / "enums" / name).exists():
            errors.append(f"Missing legacy enum {name}")
    if errors:
        print("BC legacy schema compatibility baseline: FAIL")
        for e in errors:
            print(f"- {e}")
        return 1
    print("BC legacy schema compatibility baseline: PASS (1.0.2.25 source)")
    print("Still requires compile and actual installed tenant schema comparison / upgrade test.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
