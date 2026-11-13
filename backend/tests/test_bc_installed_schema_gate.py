"""Installed-BC-app AL compatibility gate: no invented field IDs or approval."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json


def load_gate():
    path = Path(__file__).resolve().parents[2] / "scripts" / "check_bc_installed_schema.py"
    spec = spec_from_file_location("bc_installed_schema_gate", path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_al_table_and_tableextension_fields_collected(tmp_path):
    gate = load_gate()
    source = tmp_path / "src"
    source.mkdir()
    (source / "setup.al").write_text('''
table 53100 "DH Setup"
{
    fields
    {
        field(1; "Primary Key"; Code[10]) { }
        field(5; "Last Score"; Integer) { }
    }
}
''')
    (source / "extension.al").write_text('''
tableextension 53355 "DH Setup Legacy Fields" extends "DH Setup"
{
    fields
    {
        field(90; "Report Notification Email"; Text[250]) { }
        field(91; "Preferred Report Language"; Code[10]) { }
    }
}
''')
    source_tables = gate.collect_source(source)
    baseline = {"tables": [{"id": 53100, "name": "DH Setup", "fields": [
        {"id": 1, "name": "Primary Key", "type": "Code[10]"},
        {"id": 90, "name": "Report Notification Email", "type": "Text[250]"},
        {"id": 91, "name": "Preferred Report Language", "type": "Code[10]"},
    ]}]}
    assert gate.compare_installed(baseline, source_tables) == []


def test_installed_fields_cannot_be_dropped_or_changed(tmp_path):
    gate = load_gate()
    src = tmp_path / "src"
    src.mkdir()
    (src / "table.al").write_text('table 53100 "DH Setup" { fields { field(1; "Primary Key"; Code[10]) { } } }')
    actual = gate.collect_source(src)
    baseline = {"tables": [{"id": 53100, "name": "DH Setup", "fields": [
        {"id": 1, "name": "Primary Key", "type": "Code[10]"},
        {"id": 90, "name": "Report Notification Email", "type": "Text[250]"},
    ]}]}
    issues = gate.compare_installed(baseline, actual)
    assert any("Missing persisted field" in item for item in issues)
    baseline["tables"][0]["fields"][0]["type"] = "Text[10]"
    issues = gate.compare_installed(baseline, actual)
    assert any("Changed persisted field" in item for item in issues)


def test_missing_or_empty_baseline_fails_closed():
    gate = load_gate()
    import pytest
    for baseline in ({}, {"tables": []}, {"tables": "not a list"}):
        with pytest.raises(ValueError):
            gate.compare_installed(baseline, {})


def test_missing_table_or_duplicate_ids_cannot_pass(tmp_path):
    gate = load_gate()
    src = tmp_path / "src"
    src.mkdir()
    (src / "table.al").write_text('table 53100 "DH Setup" { fields { field(1; "Primary Key"; Code[10]) { } } }')
    actual = gate.collect_source(src)
    baseline = {"tables": [{"id": 53101, "name": "DH Setup", "fields": []}]}
    assert any("Missing/renumbered table" in item for item in gate.compare_installed(baseline, actual))
    baseline = {"tables": [{"id": 53100, "name": "DH Setup", "fields": [
        {"id": 1, "name": "Primary Key", "type": "Code[10]"},
        {"id": 1, "name": "Duplicate", "type": "Code[10]"},
    ]}]}
    import pytest
    with pytest.raises(ValueError):
        gate.compare_installed(baseline, actual)
