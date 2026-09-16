"""Source contracts, not BC runtime evidence. No database or conftest required."""
from __future__ import annotations

import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / "bc-performance"
SRC = QA / "src"


def source(name: str) -> str:
    return (SRC / name).read_text(encoding="utf-8")


def code(name: str) -> str:
    return re.sub(r"//[^\n]*", "", source(name))


def test_separate_app_and_nonoverlapping_object_inventory():
    product = json.loads((ROOT / "bc-extension/app.json").read_text())
    qa = json.loads((QA / "app.json").read_text())
    assert qa["id"] != product["id"]
    assert qa["idRanges"] == [{"from": 53400, "to": 53449}]
    assert product["version"] == "1.0.2.20"
    assert product["idRanges"] == [{"from": 53100, "to": 53202}]
    objects = set()
    for directory in [SRC, ROOT / "bc-extension/app/src"]:
        for path in directory.rglob("*.al"):
            for kind, number in re.findall(r"^(\w+)\s+(\d+)\s+\"", path.read_text(encoding="utf-8-sig"), re.M):
                key = kind, int(number)
                assert key not in objects, (path, key)
                objects.add(key)
                if directory == SRC:
                    assert 53400 <= int(number) <= 53449


@pytest.mark.parametrize("profile,total", [("DEV", 20000), ("LARGE", 500000), ("XL", 2000000), ("STRESS", 5000000)])
def test_central_profiles_count_business_records_only(profile, total):
    match = re.search(rf"::{profile}: SetTargets\(GenerationRun, (\d+), (\d+), (\d+)\)", source("BCPPolicy.Codeunit.al"))
    counts = tuple(map(int, match.groups()))
    assert sum(counts) == total
    assert counts == (total * 3 // 10, total // 10, total * 6 // 10)
    assert "exit(Customers + Vendors + Items);" in code("BCPRun.Table.al")


def test_config_bounds_and_safe_namespace_are_enforced():
    policy = code("BCPPolicy.Codeunit.al")
    for guard in ['in [1, 5, 10, 20]', 'GenerationRun.Seed < 0', 'GenerationRun.Seed > 1000000',
                  '"Batch Size" < 1', '"Batch Size" > 5000', 'TargetCount() > 10000000',
                  'RunId > 999999', 'Sequence > 9999999', '"Schema Version" <> 1']:
        assert guard in policy
    assert 'else Error(ConfigErr)' in policy


def test_seed_oracle_is_explicit_and_al_behavior_tests_exist():
    policy = code("BCPPolicy.Codeunit.al")
    assert '((Sequence mod 100) * 37 + (Seed mod 100)) mod 100 < Rate' in policy
    tests = source("BCPSelfTests.Codeunit.al")
    assert tests.count('[Test]') == 4
    assert 'for Sequence := 1 to 10000' in tests
    assert 'asserterror Policy.ValidateRun' in tests


def test_run_inputs_are_persisted_and_configuration_is_snapshotted():
    table = source("BCPRun.Table.al")
    for field in ['Seed', '"Error Rate"', '"Schema Version"', '"Customer Config"', '"Vendor Config"', '"Item Config"']:
        assert re.search(rf'field\(\d+; {field};', table)
    management = code("BCPManagement.Codeunit.al")
    assert management.count('Config.Snapshot(') == 3
    assert management.index('GenerationRun.Init()') < management.index('GenerationRun.Seed := TempRequest.Seed')
    config = code("BCPConfig.Codeunit.al")
    assert 'SourceField.TestField()' in config
    assert 'Source.Modify' not in config


def test_atomic_batch_checkpoint_and_terminal_status():
    batch = code("BCPBatch.Codeunit.al")
    assert '[CommitBehavior(CommitBehavior::Error)]' in batch
    assert not re.search(r'\bCommit\(', batch)
    assert batch.index('GenerationRun.LockTable()') < batch.index('GenerationRun.Get(')
    assert 'GenerationRun.BusinessCount() = GenerationRun.TargetCount()' in batch
    assert batch.index('GenerationRun.BusinessCount() = GenerationRun.TargetCount()') < batch.index('GenerationRun.Status := GenerationRun.Status::Completed')
    management = code("BCPManagement.Codeunit.al")
    assert 'Codeunit.Run(Codeunit::"BCP Batch", GenerationRun)' in management
    assert 'GetLastErrorText()' in management
    assert 'GenerationRun."Failed Batches" += 1' in management
    assert 'GenerationRun.Status := GenerationRun.Status::Failed' in management
    assert 'GenerationRun."Started At" := AttemptStartedAt' in management
    assert 'GenerationRun.Status := GenerationRun.Status::Cancelled' in management


def test_ownership_uses_systemid_recordid_and_modified_timestamp():
    batch = code("BCPBatch.Codeunit.al")
    for identity in ['Target.SystemIdNo', 'Target.RecordId', 'Target.SystemModifiedAtNo', 'Owned.Insert()']:
        assert identity in batch
    cleanup = code("BCPCleanupBatch.Codeunit.al")
    for guard in ['Target.GetBySystemId', 'Target.RecordId <> Owned."Record ID"', 'ModifiedAt <> Owned."Modified At"',
                  'Support.Get(Owned."Run ID", Database::"Item Unit of Measure", ItemUOM.SystemId)',
                  'VerifyIdentity(Support, SupportTarget)', 'Target.Delete(true)']:
        assert guard in cleanup
    assert cleanup.index('VerifyIdentity(Owned, Target)') < cleanup.index('Target.Delete(true)')
    assert cleanup.index('Target.Delete(true)') < cleanup.index('Owned.Delete()')


def test_cleanup_is_scoped_ordered_confirmed_and_refuses_dependencies():
    cleanup = code("BCPCleanupBatch.Codeunit.al")
    assert 'Owned.SetRange("Run ID", GenerationRun."Run ID")' in cleanup
    assert cleanup.index('Owned.SetRange("Table ID", Database::Item)') < cleanup.index('Owned.SetRange("Table ID", Database::Vendor)')
    refs = code("BCPReferences.Codeunit.al")
    assert 'Metadata.RelationTableNo = TargetTable' in refs
    assert 'Other.IsEmpty()' in refs
    assert 'RecordLink.SetRange("Record ID", Owned."Record ID")' in refs
    ui = code("BCPRuns.Page.al")
    assert 'Confirm(CleanupQst, false, Cleanup.Preview(' in ui
    assert 'GenerationRun.Status::Cleaning' in code("BCPCleanup.Codeunit.al")


def test_no_bulk_business_delete_no_findings_no_permission_escalation():
    all_code = '\n'.join(code(p.name) for p in SRC.glob('*.al'))
    assert not re.search(r'\bDeleteAll\s*\(', all_code, re.I)
    assert 'DH Deep Scan Finding' not in all_code
    assert 'DH Scan Issue' not in all_code
    assert not re.search(r'\bSUPER\b', all_code)
    generate = source('BCPGENERATE.PermissionSet.al')
    cleanup = source('BCPCLEANUP.PermissionSet.al')
    assert 'BCP CLEANUP' not in generate
    assert 'tabledata Customer = Ri' in generate
    assert 'tabledata Customer = Rd' in cleanup
    assert 'tabledata "BCP Owned Record" = Ri' in generate
    assert 'tabledata "BCP Owned Record" = Rd' in cleanup


def test_cleanup_covers_standard_guid_cascades_and_active_local_metadata():
    refs = code('BCPReferences.Codeunit.al')
    assert 'EntityText.SetRange("Source System Id", Owned."Record SystemId")' in refs
    assert 'UnitGroup.Get(UnitGroup."Source Type"::Item, Owned."Record SystemId")' in refs
    assert 'TableMetadata.TableType::Normal' in refs
    assert 'Metadata.SetRange(Enabled, true)' in refs
    assert 'Metadata.ObsoleteState::Removed' in refs


def test_all_mutation_entrypoints_require_sandbox_and_core_has_no_ui():
    policy = code('BCPPolicy.Codeunit.al')
    for guard in ['not EnvironmentInformation.IsSaaS()', 'not EnvironmentInformation.IsSandbox()',
                  'EnvironmentInformation.IsProduction()', "CopyStr(CompanyName(), 1, 9) <> 'BCS-PERF-'"]:
        assert guard in policy
    for name in ['BCPManagement.Codeunit.al', 'BCPBatch.Codeunit.al', 'BCPCleanup.Codeunit.al', 'BCPCleanupBatch.Codeunit.al']:
        text = code(name)
        assert 'Policy.RequireSandbox()' in text
        assert not re.search(r'\b(Message|Confirm|Dialog|GuiAllowed)\s*\(', text, re.I)


def test_scenarios_map_to_current_productive_deep_scan_checks():
    scanner = (ROOT / 'bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al').read_text()
    scenario_ids = re.findall(r"Scenario := '([^']+)'", source('BCPBatch.Codeunit.al'))
    assert len(scenario_ids) == 4
    for scenario in scenario_ids:
        assert f"'{scenario}'" in scanner


def test_de_and_en_translations_have_complete_matching_units():
    ns = {'x': 'urn:oasis:names:tc:xliff:document:1.2'}
    catalogs = []
    for language in ['de-DE', 'en-US']:
        root = ET.parse(QA / 'Translations' / f'BCSentinel Performance QA.{language}.xlf')
        units = root.findall('.//x:trans-unit', ns)
        assert len(units) > 100
        assert all(unit.find('x:target', ns) is not None and unit.find('x:target', ns).text for unit in units)
        catalogs.append({u.attrib['id']: u.find('x:source', ns).text for u in units})
    assert catalogs[0] == catalogs[1]


def test_ci_compiles_separate_qa_and_never_claims_runtime_pass():
    ci = (ROOT / '.github/workflows/bc-al-compile.yml').read_text()
    assert '-appFolders @($appFolder, (Join-Path $env:GITHUB_WORKSPACE "bc-performance"))' in ci
    assert ci.count('6.1.18') == 4
    assert '-containerEventLogFile' in ci
    assert '-doNotPublishApps' not in ci
    evidence = json.loads((ROOT / 'quality/release/ext-50-12a-test-data-generator-evidence.json').read_text())
    assert evidence['status'] == 'AWAITING_MANUAL_BC_RUNTIME_EVIDENCE'
    assert evidence['runtime']['profile'] == 'LARGE'
    assert evidence['runtime']['seed'] == 5001
    assert evidence['runtime']['error_rate'] == 10
    assert all(v == 'PENDING' for v in evidence['runtime']['required_evidence'].values())


def test_inherited_category_attributes_refused_before_any_batch_insert():
    config = code('BCPConfig.Codeunit.al')
    assert 'AttributeMapping.SetRange("Table ID", Database::"Item Category")' in config
    assert 'AttributeMapping.SetRange("No.", CategoryCode)' in config
    assert 'if not AttributeMapping.IsEmpty() then' in config
    assert 'CategoryCode := ItemCategory."Parent Category"' in config
    assert 'Visited.Contains(CategoryCode)' in config
    assert 'Config.ValidateItemConfig(GenerationRun."Item Config")' in code('BCPManagement.Codeunit.al')
    batch = code('BCPBatch.Codeunit.al')
    assert batch.index('Config.ValidateItemConfig(') < batch.index('while (Remaining > 0)')
    assert 'tabledata "Item Attribute Value Mapping" = R' in source('BCPGENERATE.PermissionSet.al')
