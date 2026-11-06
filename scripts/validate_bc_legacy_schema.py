#!/usr/bin/env python3
"""Static preflight: preserve the schema in user-supplied BCSentinel 1.0.2.22 .app.

This is a *baseline* compatibility gate, not a substitute for comparing against
the tenant's installed 1.0.2.22 package or running a real BC SaaS upgrade.
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
    # Installed Finding Identity Tests extension depends on this public API.
    finding_source = (SRC / "tables" / "DHDeepScanFinding.Table.al").read_text(encoding="utf-8-sig")
    for required in (
        "procedure ApplyBackendImpact(",
        "procedure BuildGroupKey(",
        'key(GroupIdentity; "Deep Scan Entry No.", "Issue Code", "Group Key")',
    ):
        if required not in finding_source:
            errors.append(f"Missing externally referenced finding identity API: {required}")
    permissions = (SRC / "permissionsets" / "BCSentinelPermissionSets.al").read_text(encoding="utf-8-sig")
    if 'table "DH Scan Check Selection" = X' not in permissions:
        errors.append("Legacy table 53194 must appear as executable table object in a permission set")
    if 'tabledata "DH Scan Check Selection" = R' not in permissions:
        errors.append("Legacy table 53194 needs data read permissions")

    # A reset must invalidate cached entitlements without deleting scan history.
    setup_source = (SRC / "tables" / "DHSetup.Table.al").read_text(encoding="utf-8-sig")
    page_source = (SRC / "pages" / "DHSetup.Page.al").read_text(encoding="utf-8-sig")
    reset_proc = page_source.split("local procedure ResetLocalRegistrationState()", 1)
    if len(reset_proc) < 2:
        errors.append("Missing local registration reset action")
    elif "Rec.ClearCachedProductAccess();" not in reset_proc[1].split("local procedure", 1)[0]:
        errors.append("Registration reset does not clear cached product access")
    clear_proc = setup_source.split("procedure ClearCachedProductAccess()", 1)
    if len(clear_proc) < 2:
        errors.append("Missing cached access reset procedure")
    else:
        block = clear_proc[1].split("    procedure", 1)[0]
        for name in ('"Product Access Model"', '"Monitoring Active"', '"Scan Credits Available"',
                     '"Dashboard Access Until"', '"Issue Access Until"', '"Can Run Deep Scan"',
                     '"Can View Dashboard"', '"Can View Issue Details"', '"Premium Enabled"',
                     '"Last License Check"'):
            if name not in block:
                errors.append(f"Cached access reset does not invalidate {name}")
        for history_field in ('"Last Score"', '"Last Scan Date"'):
            if history_field in block:
                errors.append(f"Registration reset must preserve historical {history_field}")

    # Free Entry is a UI state, while the backend 'none' access_model means no paid entitlement.
    setup_source = (SRC / "tables" / "DHSetup.Table.al").read_text(encoding="utf-8-sig")
    setup_page = (SRC / "pages" / "DHSetup.Page.al").read_text(encoding="utf-8-sig")
    if "procedure GetProductAccessDisplayText()" not in setup_source:
        errors.append("Missing display-only Free Entry product access mapping")
    if "exit('Free');" not in setup_source:
        errors.append("Registered Free Entry users must display Free")
    if 'field(ProductAccessModel; Rec.GetProductAccessDisplayText())' not in setup_page:
        errors.append("Setup page must use display-only access mapping instead of raw backend model")

    pilot_actions = (SRC / "pageextensions" / "DHSetupPilotActions.PageExt.al").read_text(encoding="utf-8-sig")
    for required in (
        'Visible = ShowRegisterTenantAction;',
        'action(RunFreeScan)',
        "Caption = 'Run Free Scan';",
        'Promoted = true;',
        'Visible = ShowFreeScanAction;',
        'trigger OnAfterGetCurrRecord()',
        'UpdatePilotActionVisibility();',
    ):
        if required not in pilot_actions:
            errors.append(f"BC onboarding UI missing required action visibility behavior: {required}")
    if "ShowRegisterTenantAction := not Rec.Registered" not in pilot_actions:
        errors.append("Register Tenant must disappear once tenant is registered")
    if 'Rec."Scan Credits Available" > 0' not in pilot_actions:
        errors.append("Free Scan action must respect available scan credits")

    # The backend consumes the Free Entry credit at /scan/start. A matching
    # /scan/sync must never require a second unused credit locally.
    api_source = (SRC / "codeunits" / "DHApiClient.Codeunit.al").read_text(encoding="utf-8-sig")
    sync_start = api_source.find('procedure SyncScanToBackendAndGetResponse(')
    sync_end = api_source.find('procedure DeleteScanFromBackend(', sync_start)
    if sync_start < 0 or sync_end < 0:
        errors.append("Missing backend scan result sync API")
    else:
        sync_body = api_source[sync_start:sync_end]
        if 'EnsureTenantAccessConfigured(Setup);' not in sync_body or 'EnsureReadyForScan(Setup);' in sync_body:
            errors.append("Scan result sync must authorize registered tenant without checking unused credit")
    runner = (SRC / "codeunits" / "DHDeepScanRunner.Codeunit.al").read_text(encoding="utf-8-sig")
    if runner.find('SyncResponseText := ApiClient.SyncScanToBackendAndGetResponse') < 0:
        errors.append("Scan runner must transmit results to backend")
    else:
        sync_pos = runner.find('SyncResponseText := ApiClient.SyncScanToBackendAndGetResponse')
        first_terminal = runner.find('DeepScanRun.Status := DeepScanRun.Status::Completed;')
        if first_terminal < sync_pos:
            errors.append("Runner marks scan Completed before backend result synchronization")
    if "DeepScanRun.\"Progress %\" := 99;" not in runner:
        errors.append("Finalization must remain below 100% until backend result sync completes")

    # Scan monitor must query the backend on open and before attempting to
    # heal a cached terminal state; stale-state warnings must not be cosmetic.
    monitor = (SRC / "pages" / "DHDeepScanMonitor.Page.al").read_text(encoding="utf-8-sig")
    onopen = monitor.split("trigger OnOpenPage()", 1)
    if len(onopen) < 2 or "ReloadMonitor();" not in onopen[1].split("    end;", 1)[0]:
        errors.append("Scan monitor must fetch backend status when opened")
    reload_start = monitor.find("local procedure ReloadMonitor()")
    reload_end = monitor.find("local procedure ReloadDisplayValuesFromRec()", reload_start)
    if reload_start < 0 or reload_end < 0:
        errors.append("Scan monitor backend refresh procedure missing")
    else:
        reload_code = monitor[reload_start:reload_end]
        first_refresh = reload_code.find("TryRefreshBackendStatus(")
        first_heal = reload_code.find("TrySyncLocalTerminalStatus(")
        if first_refresh < 0 or first_heal < 0 or first_refresh >= first_heal:
            errors.append("Scan monitor must read authoritative backend state before healing")
        if 'DeepScanRun."Warning Message" := \'\';' not in reload_code:
            errors.append("Scan monitor must clear stale warnings on confirmed completed status")
    if errors:
        print("BC legacy schema compatibility baseline: FAIL")
        for e in errors:
            print(f"- {e}")
        return 1
    print("BC legacy schema compatibility baseline: PASS (1.0.2.22 installed-source baseline)")
    print("Still requires compile and actual installed tenant schema comparison / upgrade test.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
