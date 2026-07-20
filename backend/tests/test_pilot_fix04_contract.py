from __future__ import annotations

import os
from pathlib import Path
import xml.etree.ElementTree as ET


def _project_root() -> Path:
    candidates: list[Path] = []
    if os.environ.get("PROJECT_ROOT"):
        candidates.append(Path(os.environ["PROJECT_ROOT"]).expanduser().resolve())
    for anchor in (Path(__file__).resolve(), Path.cwd().resolve()):
        candidates.extend((anchor, *anchor.parents))
    required = (Path("backend/app"), Path("bc-extension/app/src"), Path("bc-extension/Translations"))
    for candidate in dict.fromkeys(candidates):
        if all((candidate / path).is_dir() for path in required):
            return candidate
    raise RuntimeError("Set PROJECT_ROOT to the mounted BCSentinel repository root.")


ROOT = _project_root()
AL_ROOT = ROOT / "bc-extension" / "app" / "src"
XLIFF_NS = {"x": "urn:oasis:names:tc:xliff:document:1.2"}


def _backend(path: str) -> str:
    return (ROOT / "backend" / "app" / path).read_text(encoding="utf-8")


def _al(path: str) -> str:
    return (AL_ROOT / path).read_text(encoding="utf-8")


def test_backend_preserves_current_lease_and_returns_structured_conflicts():
    service = _backend("services/scan_status_service.py")
    router = _backend("routers/scans.py")
    assert "stale_running = lease_expired and heartbeat_stale" in service
    assert "run.tenant_id != tenant_id" in service
    for code in (
        "scan_execution_token_stale",
        "scan_execution_lease_expired",
        "scan_worker_mismatch",
        "scan_execution_not_owned",
    ):
        assert code in service
    assert '"code": exc.code' in router
    assert '"worker_id": request_id' in router


def test_start_identity_is_validated_and_persisted_before_scan_work():
    api = _al("codeunits/DHApiClient.Codeunit.al")
    manager = _al("codeunits/DHDeepScanMgt.Codeunit.al")
    assert "WorkerId <> DeepScanRun.\"Client Request ID\"" in api
    assert 'DeepScanRun."Execution Token" := ExecutionToken;' in api
    assert 'DeepScanRun."Correlation ID" := \'\';' in api
    accepted = manager.split('DeepScanRun."Start Request Status" := DeepScanRun."Start Request Status"::Accepted;', 1)[1]
    assert 'DeepScanRun."Backend Sync Status" := DeepScanRun."Backend Sync Status"::Pending;' in accepted
    assert "Commit();" in accepted.split("end;", 1)[0]


def test_all_progress_and_sync_calls_reuse_persisted_identity_and_stop_after_rejection():
    api = _al("codeunits/DHApiClient.Codeunit.al")
    runner = _al("codeunits/DHDeepScanRunner.Codeunit.al")
    assert "JsonRequest.Add('execution_token', Format(DeepScanRun.\"Execution Token\"))" in api
    assert "JsonRequest.Add('worker_id', Format(DeepScanRun.\"Client Request ID\"))" in api
    assert "Payload.Add('execution_token', Format(DeepScanRun.\"Execution Token\"))" in runner
    assert "Payload.Add('worker_id', Format(DeepScanRun.\"Client Request ID\"))" in runner
    assert 'DeepScanRun."Backend Sync Status" = DeepScanRun."Backend Sync Status"::Failed' in runner
    assert "CreateGuid()" not in runner


def test_local_completion_is_not_rewritten_as_engine_failure_when_sync_fails():
    runner = _al("codeunits/DHDeepScanRunner.Codeunit.al")
    history = _al("pages/DHDeepScanRuns.Page.al")
    monitor = _al("pages/DHDeepScanMonitor.Page.al")
    failure_block = runner.split("local procedure MarkLocalCompletionWithSyncFailure", 1)[1]
    assert "DeepScanRun.Status := DeepScanRun.Status::Completed;" in failure_block
    assert 'DeepScanRun."Backend Sync Status" := DeepScanRun."Backend Sync Status"::Failed' in failure_block
    assert 'DeepScanRun."Error Message" := \'\';' in failure_block
    assert "CompletedSyncFailedLbl" in history
    assert "BackendSyncStatusTxt" in monitor
    assert 'Rec."Backend Sync Error"' in monitor


def test_fix04_customer_messages_have_german_targets():
    source = ET.parse(ROOT / "bc-extension" / "Translations" / "BCSentinel.g.xlf")
    german = ET.parse(ROOT / "bc-extension" / "Translations" / "BCSentinel.de-DE.xlf")
    required_sources = {
        "Backend synchronization stopped because the scan execution ownership expired or changed. Your local scan result is preserved. Start a new scan or contact BCSentinel support.",
        "The scan status could not be sent to BCSentinel. The local scan continues and synchronization will be retried.",
        "The local scan completed, but its result could not be sent to BCSentinel. Check the connection and retry synchronization.",
        "Scan completed locally; backend synchronization failed.",
        "Completed; sync failed",
    }
    source_units = {
        unit.find("x:source", XLIFF_NS).text: unit.attrib["id"]
        for unit in source.findall(".//x:trans-unit", XLIFF_NS)
        if unit.find("x:source", XLIFF_NS) is not None
    }
    targets = {
        unit.attrib["id"]: (unit.find("x:target", XLIFF_NS).text or "").strip()
        for unit in german.findall(".//x:trans-unit", XLIFF_NS)
        if unit.find("x:target", XLIFF_NS) is not None
    }
    assert required_sources <= source_units.keys()
    assert all(targets.get(source_units[text]) for text in required_sources)
