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

        DeepScanRun.Insert(true);
        CreateOrUpdateScanHeader(DeepScanRun);
        Commit();

        ApiClient.StartDeepScan(Setup, DeepScanRun."Run ID", TotalModules);

        TryUpdateBackendQueued(Setup, DeepScanRun);

        Commit();

        RunDeepScanNow(DeepScanRun);

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

    local procedure RunDeepScanNow(var DeepScanRun: Record "DH Deep Scan Run")
    var
        DeepScanRunner: Codeunit "DH Deep Scan Runner";
    begin
        DeepScanRunner.Run(DeepScanRun);
    end;

    local procedure CreateOrUpdateScanHeader(var DeepScanRun: Record "DH Deep Scan Run")
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

        if ScanHeader."Run ID" = '' then
            ScanHeader."Run ID" := DeepScanRun."Run ID";

        if ScanHeader."Backend Scan Id" = '' then
            ScanHeader."Backend Scan Id" := DeepScanRun."Run ID";

        ScanHeader."Scan DateTime" := DeepScanRun."Requested At";
        ScanHeader."Data Score" := DeepScanRun."Deep Score";
        ScanHeader."Checks Count" := DeepScanRun."Checks Count";
        ScanHeader."Issues Count" := DeepScanRun."Issues Count";
        ScanHeader."Affected Records" := DeepScanRun."Affected Records";
        ScanHeader."System Score" := DeepScanRun."System Score";
        ScanHeader."Finance Score" := DeepScanRun."Finance Score";
        ScanHeader."Sales Score" := DeepScanRun."Sales Score";
        ScanHeader."Purchasing Score" := DeepScanRun."Purchasing Score";
        ScanHeader."Inventory Score" := DeepScanRun."Inventory Score";
        ScanHeader."CRM Score" := DeepScanRun."CRM Score";
        ScanHeader."Manufacturing Score" := DeepScanRun."Manufacturing Score";
        ScanHeader."Service Score" := DeepScanRun."Service Score";
        ScanHeader."Jobs Score" := DeepScanRun."Jobs Score";
        ScanHeader."HR Score" := DeepScanRun."HR Score";
        ScanHeader."Estimated Loss (EUR)" := DeepScanRun."Estimated Loss (EUR)";
        ScanHeader."Potential Saving (EUR)" := DeepScanRun."Potential Saving (EUR)";
        ScanHeader."Est. Loss" := DeepScanRun."Estimated Loss (EUR)";
        ScanHeader."Potential Saving" := DeepScanRun."Potential Saving (EUR)";
        ScanHeader."Total Records" := DeepScanRun."Total Records";
        ScanHeader."Est. Premium Price" := DeepScanRun."Est. Premium Price";
        ScanHeader."ROI" := DeepScanRun."ROI";
        ScanHeader."Headline" := CopyStr(DeepScanRun."Headline", 1, MaxStrLen(ScanHeader."Headline"));
        ScanHeader."Rating" := CopyStr(DeepScanRun."Rating", 1, MaxStrLen(ScanHeader."Rating"));

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
