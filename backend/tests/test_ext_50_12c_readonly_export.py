"""Safety contracts for the separately packaged diagnostic; not a SaaS execution claim."""
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / 'bc-diagnostics'


def test_export_package_is_separate_and_has_no_persistent_tables_or_hooks():
    manifest = json.loads((QA / 'app.json').read_text())
    assert manifest['id'] not in {d['id'] for d in manifest['dependencies']}
    assert manifest['idRanges'] == [{'from': 53450, 'to': 53459}]
    declarations = '\n'.join(p.read_text(encoding='utf-8') for p in (QA / 'src').glob('*.al'))
    assert not re.search(r'^\s*(table|tableextension|pageextension)\s+\d+', declarations, re.M)
    assert not re.search(r'Subtype\s*=\s*(Install|Upgrade)|\[EventSubscriber', declarations)


def test_all_table_permissions_are_read_only():
    source = (QA / 'src/BCREVIDENCE.PermissionSet.al').read_text()
    rights = re.findall(r'tabledata\s+(?:"[^"]+"|\w+)\s*=\s*(\w+)', source)
    assert len(rights) == 9
    assert set(rights) == {'R'}
    assert 'SUPER' not in source


def test_code_has_no_mutating_or_remote_execution_surface():
    source = (QA / 'src/BCREvidenceExport.Codeunit.al').read_text()
    for method in ('Insert', 'Modify', 'ModifyAll', 'Delete', 'DeleteAll', 'Rename', 'Validate',
                   'Commit', 'LockTable', 'ChangeCompany', 'StartSession'):
        assert not re.search(r'\b' + method + r'\s*\(', source, re.I), method
    for token in ('HttpClient', 'HttpRequestMessage', 'Codeunit.Run', 'BCP Management',
                  'BCP Cleanup', 'DH Deep Scan Runner', 'DH API Client', 'DH Exception Mgt.'):
        assert token not in source
    # Writing the client download stream is the only output, backed by in-memory Temp Blob.
    assert 'Codeunit "Temp Blob"' in source
    assert 'DownloadFromStream(InputStream' in source


def test_guard_precedes_every_business_read_and_pins_exact_completed_run():
    source = (QA / 'src/BCREvidenceExport.Codeunit.al').read_text()
    body = source.split('procedure BuildEvidence()', 1)[1].split('local procedure RequireSandbox', 1)[0]
    assert body.index('RequireSandbox();') < body.index('ScanRun.SetRange(')
    for guard in ('not EnvironmentInformation.IsSaaS()', 'not EnvironmentInformation.IsSandbox()',
                  'EnvironmentInformation.IsProduction()', "CompanyName() <> 'BCS-PERF-DEV'",
                  'ScanRun.Status <> ScanRun.Status::Completed', 'ScanRun.Count() <> 1'):
        assert guard in source
    assert 'RUN_20260916_000001_43F57A071BFF485BAF20C68FF578B' in source


def test_export_preserves_rows_and_uses_owned_systemids_not_namespace_guessing():
    source = (QA / 'src/BCREvidenceExport.Codeunit.al').read_text()
    assert 'Finding.SetRange("Deep Scan Entry No.", ScanRun."Entry No.")' in source
    assert 'Finding.SetCurrentKey("Entry No.")' in source
    assert 'Rows.Add(Row)' in source
    assert 'RowsRead += 1' in source
    assert 'Target.GetBySystemId(Owned."Record SystemId")' in source
    assert 'AnyOwned.Get(1, TableId, SystemId)' in source
    assert 'IssueException.SetRange(Active, true)' in source
    assert 'modified_since_generation' in source
    assert 'SystemId' not in '\n'.join(re.findall(r"Row\.Add\([^\n]+", source))


def test_no_secret_or_full_setup_serialization():
    source = (QA / 'src/BCREvidenceExport.Codeunit.al').read_text()
    for token in ('API Token', 'Execution Token', 'Tenant ID', 'Email', 'Phone No.'):
        assert not re.search(r"(?:Row|Context|Snapshot)\.Add\([^\n]*" + re.escape(token), source)
    assert 'current_setup_not_scan_time_snapshot' in source
    assert 'pre-sync' not in source.lower()  # Does not pretend to have pre-sync severity.


def test_both_languages_have_complete_matching_translation_units():
    ns = {'x': 'urn:oasis:names:tc:xliff:document:1.2'}
    catalogs = []
    for language in ('en-US', 'de-DE'):
        tree = ET.parse(QA / 'Translations' / f'BCSentinel Runtime Evidence QA.{language}.xlf')
        units = tree.findall('.//x:trans-unit', ns)
        assert len(units) == 12
        assert all(u.find('x:target', ns) is not None and u.find('x:target', ns).text for u in units)
        catalogs.append({u.attrib['id']: u.find('x:source', ns).text for u in units})
    assert catalogs[0] == catalogs[1]
