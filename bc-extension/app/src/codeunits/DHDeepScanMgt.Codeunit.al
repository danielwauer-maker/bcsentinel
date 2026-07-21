codeunit 53124 "DH Deep Scan Mgt."
{
    procedure QueueDeepScan(var Setup: Record "DH Setup"): Integer
    begin
        exit(QueueDeepScanInternal(Setup, true));
    end;

    procedure QueueDeepScanInBackground(var Setup: Record "DH Setup"): Integer
    begin
        exit(QueueDeepScanInternal(Setup, false));
    end;

    local procedure QueueDeepScanInternal(var Setup: Record "DH Setup"; ShowStartedMessage: Boolean): Integer
    var
        DeepScanRun: Record "DH Deep Scan Run";
        RunIdMgt: Codeunit "DH Run ID Mgt.";
        ApiClient: Codeunit "DH API Client";
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
        EntryNo: Integer;
        TotalModules: Integer;
        ScanStartedMsg: Label 'Validation Check successfully started. Opening the monitor. Run ID: %1', Comment = '%1 = run ID';
    begin
        if FindUnacceptedRun('', DeepScanRun) then begin
            StartBackendScanWithRecovery(Setup, DeepScanRun, DeepScanRun."Total Modules");
            RunDeepScanNow(DeepScanRun);
            exit(DeepScanRun."Entry No.");
        end;

        EnsureDeepScanAllowed(Setup);
        TotalModules := Setup.GetEnabledDeepScanModuleCount();
        if TotalModules <= 0 then
            Error(EnableScanModuleErr);

        EntryNo := GetNextRunEntryNo();

        DeepScanRun.Init();
        DeepScanRun."Entry No." := EntryNo;
        DeepScanRun."Run ID" := RunIdMgt.GetNextRunId(Setup);
        DeepScanRun."Client Request ID" := CreateGuid();
        DeepScanRun."Start Request Status" := DeepScanRun."Start Request Status"::Pending;
        DeepScanRun."Backend Sync Status" := DeepScanRun."Backend Sync Status"::NotStarted;
        DeepScanRun.Status := DeepScanRun.Status::Queued;
        DeepScanRun."Requested At" := CurrentDateTime();
        DeepScanRun."Requested By" := CopyStr(UserId(), 1, MaxStrLen(DeepScanRun."Requested By"));
        DeepScanRun."Company Name" := CopyStr(CompanyName(), 1, MaxStrLen(DeepScanRun."Company Name"));
        DeepScanRun."Scan Mode" := GetDeepScanMode(Setup, ShowStartedMessage);
        DeepScanRun."Headline" := 'Deep scan queued';
        DeepScanRun."Current Module" := 'Preparing';
        DeepScanRun."Progress %" := 0;
        DeepScanRun."Completed Modules" := 0;
        DeepScanRun."Total Modules" := TotalModules;
        DeepScanRun."ETA Text" := 'Pending';
        DeepScanRun."Backend Status" := 'queued';
        DeepScanRun."Current Step" := 'Waiting to start';
        DeepScanRun."Recent Events" := ScanCheckMgt.BuildCheckSelectionEventText(Setup);
        DeepScanRun."Last Heartbeat" := CurrentDateTime();

        DeepScanRun.Insert(true);
        CreateOrUpdateScanHeader(DeepScanRun);
        Commit();

        StartBackendScanWithRecovery(Setup, DeepScanRun, TotalModules);

        TryUpdateBackendQueued(Setup, DeepScanRun);

        Commit();

        RunDeepScanNow(DeepScanRun);

        if ShowStartedMessage then
            ShowScanResultMessage(DeepScanRun, ScanStartedMsg);

        exit(EntryNo);
    end;

    procedure QueueDataHealthScore(var Setup: Record "DH Setup"): Integer
    var
        DeepScanRun: Record "DH Deep Scan Run";
        RunIdMgt: Codeunit "DH Run ID Mgt.";
        ApiClient: Codeunit "DH API Client";
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
        EntryNo: Integer;
        TotalModules: Integer;
        ScanStartedMsg: Label 'Free Data Health Score successfully started. Opening the monitor. Run ID: %1', Comment = '%1 = run ID';
    begin
        if Setup."API Base URL" = '' then
            Error(ConfigureApiBaseUrlErr);

        if Setup."Tenant ID" = '' then
            Error(RegisterTenantErr);

        TotalModules := Setup.GetEnabledDeepScanModuleCount();
        if TotalModules <= 0 then
            Error(EnableScanModuleErr);

        if FindUnacceptedRun('data_health_score', DeepScanRun) then begin
            StartBackendScanWithRecovery(Setup, DeepScanRun, DeepScanRun."Total Modules");
            RunDeepScanNow(DeepScanRun);
            exit(DeepScanRun."Entry No.");
        end;

        EntryNo := GetNextRunEntryNo();

        DeepScanRun.Init();
        DeepScanRun."Entry No." := EntryNo;
        DeepScanRun."Run ID" := RunIdMgt.GetNextRunId(Setup);
        DeepScanRun."Client Request ID" := CreateGuid();
        DeepScanRun."Start Request Status" := DeepScanRun."Start Request Status"::Pending;
        DeepScanRun."Backend Sync Status" := DeepScanRun."Backend Sync Status"::NotStarted;
        DeepScanRun.Status := DeepScanRun.Status::Queued;
        DeepScanRun."Requested At" := CurrentDateTime();
        DeepScanRun."Requested By" := CopyStr(UserId(), 1, MaxStrLen(DeepScanRun."Requested By"));
        DeepScanRun."Company Name" := CopyStr(CompanyName(), 1, MaxStrLen(DeepScanRun."Company Name"));
        DeepScanRun."Scan Mode" := 'data_health_score';
        DeepScanRun."Headline" := 'Data Health Score queued';
        DeepScanRun."Current Module" := 'Preparing';
        DeepScanRun."Progress %" := 0;
        DeepScanRun."Completed Modules" := 0;
        DeepScanRun."Total Modules" := TotalModules;
        DeepScanRun."ETA Text" := 'Pending';
        DeepScanRun."Backend Status" := 'queued';
        DeepScanRun."Current Step" := 'Waiting to start';
        DeepScanRun."Recent Events" := ScanCheckMgt.BuildCheckSelectionEventText(Setup);
        DeepScanRun."Last Heartbeat" := CurrentDateTime();

        DeepScanRun.Insert(true);
        CreateOrUpdateScanHeader(DeepScanRun);
        Commit();

        StartBackendScanWithRecovery(Setup, DeepScanRun, TotalModules);
        TryUpdateBackendQueued(Setup, DeepScanRun);
        Commit();

        RunDeepScanNow(DeepScanRun);
        ShowScanResultMessage(DeepScanRun, ScanStartedMsg);
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
        DeepScanFailure: Codeunit "DH Deep Scan Failure";
        FailureText: Text;
    begin
        if TryRunDeepScan(DeepScanRun) then
            exit;

        FailureText := GetLastErrorText();
        if FailureText = '' then
            FailureText := 'The scan stopped because of an unexpected processing error.';
        DeepScanFailure.MarkRunAsFailed(DeepScanRun, FailureText);
        Error(FailureText);
    end;

    [TryFunction]
    local procedure TryRunDeepScan(var DeepScanRun: Record "DH Deep Scan Run")
    var
        DeepScanRunner: Codeunit "DH Deep Scan Runner";
    begin
        DeepScanRunner.Run(DeepScanRun);
    end;

    local procedure StartBackendScanWithRecovery(var Setup: Record "DH Setup"; var DeepScanRun: Record "DH Deep Scan Run"; TotalModules: Integer)
    var
        StartFailedErr: Label 'The scan start could not be confirmed. Retry the same scan from the start action. The existing request ID will be reused. Details: %1';
        StartUnexpectedErr: Label 'The scan start could not be confirmed because of an unexpected error. Retry the same scan.';
        ErrorText: Text;
        StartAccepted: Boolean;
        TerminalFailure: Boolean;
    begin
        DeepScanRun."Start Attempt Count" += 1;
        DeepScanRun."Last Start Attempt" := CurrentDateTime();
        DeepScanRun."Start Request Status" := DeepScanRun."Start Request Status"::Pending;
        DeepScanRun.Modify(true);
        Commit();

        if not TrySendBackendScanStart(Setup, DeepScanRun, TotalModules, StartAccepted, TerminalFailure, ErrorText) then begin
            ErrorText := CopyStr(GetLastErrorText(), 1, MaxStrLen(DeepScanRun."Error Message"));
            if ErrorText = '' then
                ErrorText := StartUnexpectedErr;
            MarkStartAsRetryRequired(DeepScanRun, ErrorText);
            Error(StartFailedErr, ErrorText);
        end;

        if not StartAccepted then begin
            ErrorText := CopyStr(ErrorText, 1, MaxStrLen(DeepScanRun."Error Message"));
            if TerminalFailure then begin
                MarkStartAsRejected(DeepScanRun, ErrorText);
                Error(ErrorText);
            end;
            MarkStartAsRetryRequired(DeepScanRun, ErrorText);
            Error(StartFailedErr, ErrorText);
        end;

        DeepScanRun.Get(DeepScanRun."Entry No.");
        DeepScanRun."Start Request Status" := DeepScanRun."Start Request Status"::Accepted;
        DeepScanRun."Backend Sync Status" := DeepScanRun."Backend Sync Status"::Pending;
        DeepScanRun."Backend Sync Error" := '';
        DeepScanRun."Backend Run Id" := DeepScanRun."Run ID";
        DeepScanRun."Error Message" := '';
        DeepScanRun.Modify(true);
        Commit();
    end;

    local procedure ShowScanResultMessage(var DeepScanRun: Record "DH Deep Scan Run"; ScanStartedMsg: Text)
    begin
        DeepScanRun.Get(DeepScanRun."Entry No.");
        if DeepScanRun."Backend Sync Status" in [DeepScanRun."Backend Sync Status"::Failed, DeepScanRun."Backend Sync Status"::RetryRequired] then begin
            if DeepScanRun."Backend Sync Error" <> '' then
                Message(DeepScanRun."Backend Sync Error");
            exit;
        end;
        Message(ScanStartedMsg, DeepScanRun."Run ID");
    end;

    [TryFunction]
    local procedure TrySendBackendScanStart(var Setup: Record "DH Setup"; var DeepScanRun: Record "DH Deep Scan Run"; TotalModules: Integer; var StartAccepted: Boolean; var TerminalFailure: Boolean; var ErrorText: Text)
    var
        ApiClient: Codeunit "DH API Client";
    begin
        StartAccepted := ApiClient.TryStartDeepScan(Setup, DeepScanRun, TotalModules, ErrorText, TerminalFailure);
    end;

    local procedure MarkStartAsRetryRequired(var DeepScanRun: Record "DH Deep Scan Run"; ErrorText: Text)
    begin
        DeepScanRun.Get(DeepScanRun."Entry No.");
        DeepScanRun."Start Request Status" := DeepScanRun."Start Request Status"::RetryRequired;
        DeepScanRun."Error Message" := CopyStr(ErrorText, 1, MaxStrLen(DeepScanRun."Error Message"));
        DeepScanRun.Modify(true);
        Commit();
    end;

    local procedure MarkStartAsRejected(var DeepScanRun: Record "DH Deep Scan Run"; ErrorText: Text)
    var
        StartRejectedLbl: Label 'Scan start rejected';
    begin
        DeepScanRun.Get(DeepScanRun."Entry No.");
        DeepScanRun."Start Request Status" := DeepScanRun."Start Request Status"::Rejected;
        DeepScanRun.Status := DeepScanRun.Status::Failed;
        DeepScanRun."Finished At" := CurrentDateTime();
        DeepScanRun.Headline := StartRejectedLbl;
        DeepScanRun."Current Module" := '';
        DeepScanRun."Current Step" := StartRejectedLbl;
        DeepScanRun."Backend Status" := 'rejected';
        DeepScanRun."ETA Text" := 'Stopped';
        Clear(DeepScanRun."Last Heartbeat");
        DeepScanRun."Error Message" := CopyStr(ErrorText, 1, MaxStrLen(DeepScanRun."Error Message"));
        DeepScanRun.Modify(true);
        CreateOrUpdateScanHeader(DeepScanRun);
        Commit();
    end;

    local procedure FindUnacceptedRun(ScanMode: Text; var DeepScanRun: Record "DH Deep Scan Run"): Boolean
    var
        EmptyGuid: Guid;
    begin
        DeepScanRun.Reset();
        if ScanMode <> '' then
            DeepScanRun.SetRange("Scan Mode", ScanMode);
        DeepScanRun.SetFilter("Client Request ID", '<>%1', EmptyGuid);
        DeepScanRun.SetFilter("Start Request Status", '%1|%2', DeepScanRun."Start Request Status"::Pending, DeepScanRun."Start Request Status"::RetryRequired);
        exit(DeepScanRun.FindLast());
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
            Error(ConfigureApiBaseUrlErr);

        if Setup."Tenant ID" = '' then
            Error(RegisterTenantErr);

        ApiClient.RefreshLicenseStatus(Setup);

        if not Setup."Can Run Deep Scan" then
            Error(ValidationOrMonitoringRequiredErr);
    end;

    local procedure GetDeepScanMode(var Setup: Record "DH Setup"; ShowStartedMessage: Boolean): Text[30]
    var
        AccessModel: Text;
    begin
        if not ShowStartedMessage then
            exit('monitoring');

        if Setup."Monitoring Active" then
            exit('monitoring');
        if Setup."Validation Credits Available" > 0 then
            exit('validation');

        AccessModel := LowerCase(Setup."Product Access Model");
        case AccessModel of
            'validation', 'validation_scan':
                exit('validation');
            'monitoring', 'subscription':
                exit('monitoring');
        end;

        exit('validation');
    end;

    local procedure GetNextRunEntryNo(): Integer
    var
        DeepScanRun: Record "DH Deep Scan Run";
    begin
        if DeepScanRun.FindLast() then
            exit(DeepScanRun."Entry No." + 1);

        exit(1);
    end;

    var
        ConfigureApiBaseUrlErr: Label 'Configure the API Base URL first.';
        EnableScanModuleErr: Label 'Enable at least one scan module on the BCSentinel setup page.';
        RegisterTenantErr: Label 'Register the tenant first.';
        ValidationOrMonitoringRequiredErr: Label 'A new scan requires a Validation Check or active Monitoring.';

}
