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
        CreateOrUpdateFailedScanHeader(DeepScanRun);
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

        if (Setup."Tenant ID" = '') or (GetApiToken(Setup) = '') or (Setup."API Base URL" = '') then
            exit;

        ApiClient.UpdateScanProgress(Setup, DeepScanRun, 'failed', 'Scan failed', 'Scan failed');
        DeepScanRun.Modify(true);
    end;

    local procedure CreateOrUpdateFailedScanHeader(var DeepScanRun: Record "DH Deep Scan Run")
    var
        ScanHeader: Record "DH Scan Header";
    begin
        ScanHeader.Reset();
        ScanHeader.SetRange("Scan Type", ScanHeader."Scan Type"::Deep);
        ScanHeader.SetRange("Run ID", DeepScanRun."Run ID");

        if not ScanHeader.FindFirst() then begin
            ScanHeader.Reset();
            ScanHeader.SetRange("Scan Type", ScanHeader."Scan Type"::Deep);
            ScanHeader.SetRange("Backend Scan Id", DeepScanRun."Run ID");

            if not ScanHeader.FindFirst() then begin
                ScanHeader.Init();
                ScanHeader."Entry No." := GetNextHeaderEntryNo();
                ScanHeader."Scan Type" := ScanHeader."Scan Type"::Deep;
                ScanHeader."Run ID" := DeepScanRun."Run ID";
                ScanHeader."Backend Scan Id" := DeepScanRun."Run ID";
                ScanHeader.Insert(true);
            end;
        end;

        ScanHeader."Scan DateTime" := DeepScanRun."Finished At";
        ScanHeader."Data Score" := DeepScanRun."Deep Score";
        ScanHeader."Checks Count" := DeepScanRun."Checks Count";
        ScanHeader."Issues Count" := DeepScanRun."Issues Count";
        ScanHeader."Headline" := CopyStr(DeepScanRun."Headline", 1, MaxStrLen(ScanHeader."Headline"));
        ScanHeader."Rating" := 'FAILED';
        ScanHeader.Modify(true);
    end;

    local procedure GetNextHeaderEntryNo(): Integer
    var
        ScanHeader: Record "DH Scan Header";
    begin
        if ScanHeader.FindLast() then
            exit(ScanHeader."Entry No." + 1);

        exit(1);
    end;

    local procedure GetApiToken(var Setup: Record "DH Setup"): Text
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        exit(SecretMgt.GetApiToken(Setup));
    end;
}
