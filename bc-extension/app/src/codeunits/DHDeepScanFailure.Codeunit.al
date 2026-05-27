codeunit 53129 "DH Deep Scan Failure"
{
    TableNo = "DH Deep Scan Run";

    trigger OnRun()
    begin
        MarkRunAsFailed(Rec);
    end;

    local procedure MarkRunAsFailed(var DeepScanRun: Record "DH Deep Scan Run")
    begin
        if not DeepScanRun.Get(DeepScanRun."Entry No.") then
            exit;

        DeepScanRun.Status := DeepScanRun.Status::Failed;
        DeepScanRun."Finished At" := CurrentDateTime();
        DeepScanRun."Headline" := 'Deep scan failed';
        DeepScanRun."Error Message" := CopyStr(GetLastErrorText(), 1, MaxStrLen(DeepScanRun."Error Message"));
        DeepScanRun."Current Step" := 'Scan failed';
        DeepScanRun."Last Heartbeat" := CurrentDateTime();
        DeepScanRun.Modify(true);
        TryUpdateBackendFailure(DeepScanRun);
    end;

    local procedure TryUpdateBackendFailure(var DeepScanRun: Record "DH Deep Scan Run")
    begin
        if not SendBackendFailure(DeepScanRun) then;
    end;

    [TryFunction]
    local procedure SendBackendFailure(var DeepScanRun: Record "DH Deep Scan Run")
    var
        Setup: Record "DH Setup";
        ApiClient: Codeunit "DH API Client";
    begin
        if not Setup.Get('SETUP') then
            exit;

        if (Setup."Tenant ID" = '') or (Setup."API Token" = '') or (Setup."API Base URL" = '') then
            exit;

        ApiClient.UpdateScanProgress(Setup, DeepScanRun, 'failed', 'Scan failed', 'Scan failed');
        DeepScanRun.Modify(true);
    end;
}
