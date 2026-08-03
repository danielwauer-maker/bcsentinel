from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AL_ROOT = ROOT / "bc-extension/app/src"


def _source(relative_path: str) -> str:
    return (AL_ROOT / relative_path).read_text(encoding="utf-8")


def test_manual_monitoring_action_creates_history_before_background_processing():
    page_extension = _source("pageextensions/DHSetupMonitoringAsync.PageExt.al")
    manager = _source("codeunits/DHDeepScanMgt.Codeunit.al")

    action = page_extension.split("trigger OnAction()", 1)[1]

    assert "QueueDeepScanInNewSession(Setup);" in action
    assert "Codeunit::\"DH Manual Monitoring BG\"" not in action
    assert action.index("QueueDeepScanInNewSession(Setup);") < action.index(
        "Message(MonitoringScanStartedMsg);"
    )

    queue_path = manager.split("procedure QueueDeepScanInNewSession", 1)[1].split(
        "procedure QueueDeepScanWithContext", 1
    )[0]
    internal_path = manager.split("local procedure QueueDeepScanInternal", 1)[1].split(
        "procedure QueueDataHealthScore", 1
    )[0]

    assert (
    'QueueDeepScanInternal(Setup, Enum::"DH Scan Trigger Context"::Scheduled, false, true)'
    in queue_path
    )
    assert "DeepScanRun.Insert(true);" in internal_path
    assert "CreateOrUpdateScanHeader(DeepScanRun);" in internal_path
    assert internal_path.index("DeepScanRun.Insert(true);") < internal_path.index(
        "StartDeepScanSession(DeepScanRun)"
    )
    assert internal_path.index("CreateOrUpdateScanHeader(DeepScanRun);") < internal_path.index(
        "StartDeepScanSession(DeepScanRun)"
    )
