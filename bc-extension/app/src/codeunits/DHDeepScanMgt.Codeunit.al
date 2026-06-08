codeunit 53124 "DH Deep Scan Mgt."
{
    procedure QueueDeepScan(var Setup: Record "DH Setup"): Integer
    var
        DeepScanRun: Record "DH Deep Scan Run";
        RunIdMgt: Codeunit "DH Run ID Mgt.";
        ApiClient: Codeunit "DH API Client";
        TaskId: Guid;
        EntryNo: Integer;
        TotalModules: Integer;
        ScanStartedMsg: Label 'Scan started. Open the monitor to view progress. Run ID: %1';
    begin
        EnsureDeepScanAllowed(Setup);
        TotalModules := Setup.GetEnabledDeepScanModuleCount();
        if TotalModules <= 0 then
            Error('Please enable at least one scan module on the BCSentinel setup page.');

        EntryNo := GetNextRunEntryNo();

        DeepScanRun.Init();
        DeepScanRun."Entry No." := EntryNo;
        DeepScanRun."Run ID" := RunIdMgt.GetNextRunId(Setup);
        DeepScanRun.Status := DeepScanRun.Status::Queued;
        DeepScanRun."Requested At" := CurrentDateTime();
        DeepScanRun."Requested By" := CopyStr(UserId(), 1, MaxStrLen(DeepScanRun."Requested By"));
        DeepScanRun."Company Name" := CopyStr(CompanyName(), 1, MaxStrLen(DeepScanRun."Company Name"));
        DeepScanRun."Headline" := 'Deep scan queued';
        DeepScanRun."Current Module" := 'Preparing';
        DeepScanRun."Progress %" := 0;
        DeepScanRun."Completed Modules" := 0;
        DeepScanRun."Total Modules" := TotalModules;
        DeepScanRun."ETA Text" := 'Pending';
        DeepScanRun."Backend Status" := 'queued';
        DeepScanRun."Current Step" := 'Waiting to start';
        DeepScanRun."Last Heartbeat" := CurrentDateTime();
        ApiClient.StartDeepScan(Setup, DeepScanRun."Run ID", TotalModules);
        DeepScanRun.Insert(true);
        Commit();
        TryUpdateBackendQueued(Setup, DeepScanRun);

        TaskId :=
            TaskScheduler.CreateTask(
                Codeunit::"DH Deep Scan Runner",
                Codeunit::"DH Deep Scan Failure",
                true,
                CompanyName(),
                CurrentDateTime(),
                DeepScanRun.RecordId);

        DeepScanRun."Task ID" := TaskId;
        DeepScanRun.Modify(true);
        Commit();

        Message(ScanStartedMsg, DeepScanRun."Run ID");

        exit(EntryNo);
    end;

    local procedure TryUpdateBackendQueued(var Setup: Record "DH Setup"; var DeepScanRun: Record "DH Deep Scan Run")
    begin
        if not SendBackendQueued(Setup, DeepScanRun) then;
    end;

    [TryFunction]
    local procedure SendBackendQueued(var Setup: Record "DH Setup"; var DeepScanRun: Record "DH Deep Scan Run")
    var
        ApiClient: Codeunit "DH API Client";
    begin
        ApiClient.UpdateScanProgress(Setup, DeepScanRun, 'queued', 'Waiting to start', 'Scan queued');
        DeepScanRun.Modify(true);
    end;

    local procedure EnsureDeepScanAllowed(var Setup: Record "DH Setup")
    var
        ApiClient: Codeunit "DH API Client";
    begin
        if Setup."API Base URL" = '' then
            Error('Please configure API Base URL first.');

        if Setup."Tenant ID" = '' then
            Error('Please register the tenant first.');

        ApiClient.RefreshLicenseStatus(Setup);

        if not Setup."Can Run Deep Scan" then
            if not Setup.IsPremiumLicenseActive() then
                Error('No scan credit or active monitoring available. Please buy an Assessment, Validation Check or start Monitoring.');
    end;

    local procedure GetNextRunEntryNo(): Integer
    var
        DeepScanRun: Record "DH Deep Scan Run";
    begin
        if DeepScanRun.FindLast() then
            exit(DeepScanRun."Entry No." + 1);

        exit(1);
    end;

}
