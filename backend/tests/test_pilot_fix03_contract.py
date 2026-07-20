from __future__ import annotations

import os
from pathlib import Path
import xml.etree.ElementTree as ET


def _project_root() -> Path:
    candidates: list[Path] = []
    configured_root = os.environ.get("PROJECT_ROOT")
    if configured_root:
        candidates.append(Path(configured_root).expanduser().resolve())

    for anchor in (Path(__file__).resolve(), Path.cwd().resolve()):
        candidates.extend((anchor, *anchor.parents))

    required_paths = (
        Path("backend/app"),
        Path("bc-extension/app/src"),
        Path("bc-extension/Translations"),
    )
    checked: set[Path] = set()
    for candidate in candidates:
        if candidate in checked:
            continue
        checked.add(candidate)
        if all((candidate / required_path).is_dir() for required_path in required_paths):
            return candidate

    searched = ", ".join(str(candidate) for candidate in checked)
    raise RuntimeError(
        "Could not locate the BCSentinel project root containing backend/app, "
        "bc-extension/app/src and bc-extension/Translations. "
        f"Set PROJECT_ROOT when the repository is mounted elsewhere. Searched: {searched}"
    )


ROOT = _project_root()
AL_ROOT = ROOT / "bc-extension" / "app" / "src"
XLIFF_NS = {"x": "urn:oasis:names:tc:xliff:document:1.2"}


def _source(relative_path: str) -> str:
    return (AL_ROOT / relative_path).read_text(encoding="utf-8")


def _backend_source(relative_path: str) -> str:
    return (ROOT / "backend" / "app" / relative_path).read_text(encoding="utf-8")


def test_backend_recovery_requires_tenant_ownership_empty_result_and_no_ledger():
    service = _backend_source("services/atomic_scan_start_service.py")
    assert "def _assert_recoverable_orphan_scan" in service
    assert "scan.tenant_id != tenant.tenant_id" in service
    assert "CreditLedgerEntry.scan_id == scan.scan_id" in service
    assert "ScanIssueRecord.scan_id == scan.scan_id" in service
    assert "run.result_persisted_at_utc is not None" in service
    assert "run.lease_owner is not None" in service
    assert "existing_run.tenant_id != tenant.tenant_id" in service
    assert "unbound lifecycle and cannot be adopted safely" in service
    assert 'code="SCAN_ID_TENANT_CONFLICT"' in service
    assert 'code="SCAN_ID_REQUEST_CONFLICT"' in service


def test_backend_returns_structured_conflict_without_weakening_authentication():
    router = _backend_source("routers/scans.py")
    assert "load_authenticated_tenant(db, header_tenant_id, header_api_token)" in router
    assert "enforce_tenant_match(payload.tenant_id, header_tenant_id" in router
    assert '"code": exc.code' in router
    assert '"message_de": exc.message_de' in router
    assert 'status_code=409' in router


def test_run_id_is_readable_and_globally_unique_per_start():
    source = _source("codeunits/DHRunIdMgt.Codeunit.al")
    assert "CreateGuid()" in source
    assert "DelChr(LowerCase(Format(CreateGuid())), '=', '{}-')" in source
    assert "CounterText + '_' + CopyStr(UniqueSuffix, 1, 29)" in source
    assert "CopyStr(" in source and "1,\n            50" in source


def test_scan_start_reuses_client_identity_and_maps_stable_conflicts():
    api = _source("codeunits/DHApiClient.Codeunit.al")
    manager = _source("codeunits/DHDeepScanMgt.Codeunit.al")
    assert "JsonRequest.Add('client_request_id', Format(DeepScanRun.\"Client Request ID\"))" in api
    assert "procedure TryStartDeepScan" in api
    assert "GetScanStartErrorMessage" in api
    for code in (
        "SCAN_ID_TENANT_CONFLICT",
        "SCAN_ID_REQUEST_CONFLICT",
        "SCAN_ID_CONFLICT",
        "SCAN_REQUEST_PAYLOAD_CONFLICT",
        "FREE_SCAN_ALREADY_USED",
    ):
        assert code in api
    assert 'DeepScanRun."Client Request ID" := CreateGuid();' in manager
    assert manager.count('DeepScanRun."Client Request ID" := CreateGuid();') == 2
    assert 'DeepScanRun."Client Request ID" :=' not in manager.split("local procedure StartBackendScanWithRecovery", 1)[1]


def test_terminal_rejection_finishes_local_run_and_stops_retry_selection():
    manager = _source("codeunits/DHDeepScanMgt.Codeunit.al")
    table = _source("tables/DHDeepScanRun.Table.al")
    assert "OptionMembers = Pending,Accepted,RetryRequired,Rejected;" in table
    assert 'DeepScanRun."Start Request Status" := DeepScanRun."Start Request Status"::Rejected;' in manager
    assert "DeepScanRun.Status := DeepScanRun.Status::Failed;" in manager
    assert 'DeepScanRun."Finished At" := CurrentDateTime();' in manager
    assert 'DeepScanRun."Backend Status" := \'rejected\';' in manager
    assert 'Clear(DeepScanRun."Last Heartbeat");' in manager
    retry_filter = manager.split("local procedure FindUnacceptedRun", 1)[1].split("local procedure", 1)[0]
    assert "::Rejected" not in retry_filter


def test_dashboard_access_rejection_returns_normally_after_one_message():
    guard = _source("codeunits/DHAccessGuard.Codeunit.al")
    assert "procedure TryEnsureDashboardAccess(var AccessError: Text): Boolean" in guard
    assert "ClearLastError();" in guard
    for relative_path in (
        "pages/DHSetup.Page.al",
        "pages/DHDeepScanMonitor.Page.al",
        "pages/DHMAnalyticsPage.al",
    ):
        page = _source(relative_path)
        assert "if not AccessGuard.TryEnsureDashboardAccess(AccessError) then begin" in page
        rejection_branch = page.split("if not AccessGuard.TryEnsureDashboardAccess(AccessError) then begin", 1)[1][:180]
        assert "Message(AccessError);" in rejection_branch
        assert "exit;" in rejection_branch


def test_fix03_customer_messages_have_complete_german_targets():
    source_xlf = ET.parse(ROOT / "bc-extension" / "Translations" / "BCSentinel.g.xlf")
    german_xlf = ET.parse(ROOT / "bc-extension" / "Translations" / "BCSentinel.de-DE.xlf")
    required_sources = {
        "BCSentinel could not send the scan start request. Check the API connection and retry the same scan.",
        "The scan could not be started because the request identity or required scan data is invalid. Start a new scan.",
        "BCSentinel accepted the connection but returned an incomplete scan start response. Retry the same scan.",
        "The scan start was rejected because this environment is not authorized. Refresh product access and try again.",
        "This scan ID is already assigned to another scan. The local run was stopped safely. Start the scan again to create a new unique run.",
        "This scan request was already used with different start data. The local run was stopped safely. Start a new scan.",
        "The one-time free Data Health Score has already been started for this environment.",
        "The scan start conflicts with an existing request. The local run was stopped safely. Start a new scan.",
        "BCSentinel could not confirm the scan start because of a temporary backend error. Retry the same scan request.",
    }

    source_units = {
        unit.find("x:source", XLIFF_NS).text: unit.attrib["id"]
        for unit in source_xlf.findall(".//x:trans-unit", XLIFF_NS)
        if unit.find("x:source", XLIFF_NS) is not None
    }
    german_targets = {
        unit.attrib["id"]: (unit.find("x:target", XLIFF_NS).text or "").strip()
        for unit in german_xlf.findall(".//x:trans-unit", XLIFF_NS)
        if unit.find("x:target", XLIFF_NS) is not None
    }
    assert required_sources <= source_units.keys()
    assert all(german_targets.get(source_units[source]) for source in required_sources)
