codeunit 53129 "DH Deep Scan Failure"
{
    TableNo = "DH Deep Scan Run";

    trigger OnRun()
    begin
        MarkRunAsFailed(Rec, GetLastErrorText());
    end;

    procedure MarkRunAsFailed(var DeepScanRun: Record "DH Deep Scan Run"; FailureText: Text)
    var
        CheckExecution: Record "DH Check Execution";
        Finding: Record "DH Deep Scan Finding";
        ExceptionMgt: Codeunit "DH Exception Mgt.";
    begin
        ExceptionMgt.EndFrozenExceptionScope();
        if not DeepScanRun.Get(DeepScanRun."Entry No.") then
            exit;

        // Only explicit individual STARTED markers can be finalized as FAILED.
        // Missing observations from grouped checks remain unknown.
        CheckExecution.SetRange("Run Entry No.", DeepScanRun."Entry No.");
        CheckExecution.SetRange("Execution Status", 'STARTED');
        if CheckExecution.FindSet(true) then
            repeat
                Finding.SetRange("Deep Scan Entry No.", DeepScanRun."Entry No.");
                Finding.SetRange("Issue Code", CheckExecution."Check Code");
                CheckExecution."Finding Count" := Finding.Count();
                CheckExecution."Execution Status" := 'FAILED';
                CheckExecution."Observed At" := CurrentDateTime();
                CheckExecution.Modify(true);
            until CheckExecution.Next() = 0;
        if not RecordUnreachedChecks(DeepScanRun) then;

        DeepScanRun.Status := DeepScanRun.Status::Failed;
        DeepScanRun."Finished At" := CurrentDateTime();
        DeepScanRun."Headline" := 'Deep scan failed';
        if FailureText = '' then
            FailureText := 'The scan stopped because of an unexpected processing error.';
        DeepScanRun."Error Message" := CopyStr(FailureText, 1, MaxStrLen(DeepScanRun."Error Message"));
        DeepScanRun."Current Step" := 'Scan failed';
        DeepScanRun."Backend Status" := 'failed';
        DeepScanRun."Last Heartbeat" := CurrentDateTime();
        DeepScanRun.Modify(true);
        CreateOrUpdateFailedScanHeader(DeepScanRun);
        Commit();
        if DeepScanRun.GetStartExpectationText() <> '' then begin
            if not SendBackendFailure(DeepScanRun) then begin
                DeepScanRun.Get(DeepScanRun."Entry No.");
                DeepScanRun."Backend Sync Status" := DeepScanRun."Backend Sync Status"::RetryRequired;
                DeepScanRun.Modify(true);
                Commit();
                exit;
            end;
        end else
            TryUpdateBackendFailure(DeepScanRun);

        if not DeepScanRun.Get(DeepScanRun."Entry No.") then
            exit;

        Clear(DeepScanRun."Lease Expires At");
        Clear(DeepScanRun."Execution Token");
        DeepScanRun.Modify(true);
        Commit();
    end;

    [TryFunction]
    local procedure RecordUnreachedChecks(var DeepScanRun: Record "DH Deep Scan Run")
    var
        Expectation: JsonObject;
        Entry: JsonObject;
        Checks: JsonArray;
        Token: JsonToken;
        Value: JsonToken;
        CheckExecution: Record "DH Check Execution";
        CheckCode: Code[50];
        CheckModule: Text;
        Enabled: Boolean;
        StartState: Code[20];
        ExpectationInvalidErr: Label 'SCAN_EXPECTATION_INVALID', Locked = true;
    begin
        if DeepScanRun.GetStartExpectationText() = '' then
            exit;
        if not Expectation.ReadFrom(DeepScanRun.GetStartExpectationText()) then
            Error(ExpectationInvalidErr);
        if not Expectation.Get('checks', Token) then
            Error(ExpectationInvalidErr);
        if not Token.IsArray() then
            Error(ExpectationInvalidErr);
        Checks := Token.AsArray();
        foreach Token in Checks do begin
            if not Token.IsObject() then
                Error(ExpectationInvalidErr);
            Entry := Token.AsObject();
            if not Entry.Get('code', Value) then
                Error(ExpectationInvalidErr);
            CheckCode := CopyStr(Value.AsValue().AsText(), 1, MaxStrLen(CheckCode));
            if not Entry.Get('module', Value) then
                Error(ExpectationInvalidErr);
            CheckModule := Value.AsValue().AsText();
            if not Entry.Get('enabled', Value) then
                Error(ExpectationInvalidErr);
            Enabled := Value.AsValue().AsBoolean();
            if not CheckExecution.Get(DeepScanRun."Entry No.", CheckCode) then begin
                Clear(StartState);
                if not Enabled then
                    StartState := 'SKIPPED'
                else
                    if ModuleDefinitelyNotStarted(DeepScanRun, CheckModule) then
                        StartState := 'NOT_EXECUTED';
                if StartState <> '' then begin
                    CheckExecution.Init();
                    CheckExecution."Run Entry No." := DeepScanRun."Entry No.";
                    CheckExecution."Check Code" := CheckCode;
                    CheckExecution."Execution Status" := StartState;
                    CheckExecution."Finding Count" := 0;
                    CheckExecution."Observed At" := CurrentDateTime();
                    CheckExecution.Insert(true);
                end;
            end;
        end;
    end;

    local procedure ModuleDefinitelyNotStarted(var DeepScanRun: Record "DH Deep Scan Run"; CheckModule: Text): Boolean
    var
        RuntimeModule: Text;
    begin
        // A stale 0% progress counter must never override the observed module
        // start marker. An active group's unobserved checks remain unknown.
        case UpperCase(CheckModule) of
            'CUSTOMER', 'VENDOR', 'LEDGER', 'FINANCE': RuntimeModule := 'Finance';
            'PURCHASE': RuntimeModule := 'Purchasing';
            'ITEM', 'INVENTORY': RuntimeModule := 'Inventory';
            'JOB': RuntimeModule := 'Jobs';
            else
                RuntimeModule := CheckModule;
        end;
        if UpperCase(DeepScanRun."Current Module") = UpperCase(RuntimeModule) then
            exit(false);
        case UpperCase(CheckModule) of
            'SYSTEM': exit(DeepScanRun."System Progress %" = 0);
            'CUSTOMER', 'VENDOR', 'LEDGER', 'FINANCE': exit(DeepScanRun."Finance Progress %" = 0);
            'SALES': exit(DeepScanRun."Sales Progress %" = 0);
            'PURCHASE': exit(DeepScanRun."Purchasing Progress %" = 0);
            'ITEM', 'INVENTORY': exit(DeepScanRun."Inventory Progress %" = 0);
            'CRM': exit(DeepScanRun."CRM Progress %" = 0);
            'MANUFACTURING': exit(DeepScanRun."Manufacturing Progress %" = 0);
            'SERVICE': exit(DeepScanRun."Service Progress %" = 0);
            'JOB': exit(DeepScanRun."Jobs Progress %" = 0);
            'HR': exit(DeepScanRun."HR Progress %" = 0);
        end;
        exit(false);
    end;

    procedure RetryFailedEvidence(var DeepScanRun: Record "DH Deep Scan Run")
    begin
        if (DeepScanRun.Status <> DeepScanRun.Status::Failed) or
           (DeepScanRun."Backend Sync Status" <> DeepScanRun."Backend Sync Status"::RetryRequired) or
           (DeepScanRun.GetStartExpectationText() = '') or IsNullGuid(DeepScanRun."Execution Token")
        then
            exit;
        if not SendBackendFailure(DeepScanRun) then
            exit;
        if not DeepScanRun.Get(DeepScanRun."Entry No.") then
            exit;
        DeepScanRun."Backend Sync Status" := DeepScanRun."Backend Sync Status"::Synchronized;
        Clear(DeepScanRun."Lease Expires At");
        Clear(DeepScanRun."Execution Token");
        DeepScanRun.Modify(true);
        Commit();
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
        FailureSyncUnavailableErr: Label 'SCAN_FAILURE_SYNC_UNAVAILABLE', Locked = true;
    begin
        if not Setup.Get('SETUP') then begin
            if DeepScanRun.GetStartExpectationText() <> '' then
                Error(FailureSyncUnavailableErr);
            exit;
        end;

        if (Setup."Tenant ID" = '') or (GetApiToken(Setup) = '') or (Setup."API Base URL" = '') then begin
            if DeepScanRun.GetStartExpectationText() <> '' then
                Error(FailureSyncUnavailableErr);
            exit;
        end;

        ApiClient.UpdateScanProgress(Setup, DeepScanRun, 'failed', 'Scan failed', 'Scan failed');

        // UpdateScanProgress may refresh or modify the run record. Reload it before
        // any later write so the original scan error is not replaced by an
        // optimistic-concurrency error such as "This page was just updated".
        DeepScanRun.Get(DeepScanRun."Entry No.");
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
