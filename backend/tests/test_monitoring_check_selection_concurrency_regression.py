from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "bc-extension/app/src/codeunits/DHScanCheckMgt.Codeunit.al"


def _source() -> str:
    return SOURCE.read_text(encoding="utf-8")


def _procedure(source: str, name: str, next_name: str) -> str:
    return source.split(name, 1)[1].split(next_name, 1)[0]


def test_is_check_enabled_is_read_only_during_scan_execution():
    source = _source()
    procedure = _procedure(
        source,
        "procedure IsCheckEnabled",
        "procedure UpdateLastRun",
    )

    assert "EnsureDefaultChecks();" not in procedure
    assert "AddCheck(" not in procedure
    assert "ScanCheck.Modify" not in procedure
    assert "ScanCheck.Insert" not in procedure
    assert "if not ScanCheck.Get(CheckCode) then" in procedure
    assert "exit(true);" in procedure
    assert "exit(ScanCheck.Enabled);" in procedure


def test_add_check_skips_unchanged_catalog_entries():
    source = _source()
    procedure = _procedure(
        source,
        "local procedure AddCheck",
        "var\n        CustomerModuleLbl",
    )

    unchanged_guard = 'if (ScanCheck."Module" = ModuleName) and'
    modify_call = "ScanCheck.Modify(true);"

    assert unchanged_guard in procedure
    assert "ExpectedName := CopyStr(CheckCode" in procedure
    assert "ExpectedDescription := CopyStr(CheckCode" in procedure
    assert procedure.index(unchanged_guard) < procedure.index(modify_call)
    assert "then\n                exit;" in procedure
