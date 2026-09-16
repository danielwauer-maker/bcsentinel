codeunit 53200 "DH Copied Company Recovery"
{
    Permissions =
        tabledata "DH Setup" = RIMD,
        tabledata "DH Scan Header" = RIMD,
        tabledata "DH Scan Trend" = RIMD,
        tabledata "DH Deep Scan Run" = RIMD,
        tabledata "DH Dashboard Issue" = RIMD,
        tabledata "DH Issue Exception" = RIMD,
        tabledata "DH Issue Action Log" = RIMD,
        tabledata "DH Duplicate Buffer" = RIMD;

    procedure GetIdentityState(var Setup: Record "DH Setup"): Text[20]
    var
        IdentityMgt: Codeunit "DH Tenant Identity Mgt.";
    begin
        if not HasIdentitySnapshot(Setup) then
            exit('Legacy');

        if LowerCase(Setup."Access Snapshot Tenant ID") <> LowerCase(IdentityMgt.GetEntraTenantId()) then
            exit('Mismatch');
        if LowerCase(Setup."Access Snapshot Environment") <> LowerCase(IdentityMgt.GetEnvironmentName()) then
            exit('Mismatch');
        if LowerCase(Setup."Access Snapshot Env. Type") <> LowerCase(IdentityMgt.GetEnvironmentType()) then
            exit('Mismatch');
        if LowerCase(DelChr(Setup."Access Snapshot Company ID", '=', '{}')) <>
           LowerCase(DelChr(IdentityMgt.GetCompanyId(), '=', '{}'))
        then
            exit('Mismatch');

        exit('Matched');
    end;

    procedure HasCopiedCompanyMismatch(var Setup: Record "DH Setup"): Boolean
    begin
        exit(GetIdentityState(Setup) = 'Mismatch');
    end;

    procedure CanOfferRecovery(var Setup: Record "DH Setup"): Boolean
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
        IdentityState: Text[20];
        HasLocalBinding: Boolean;
    begin
        HasLocalBinding := Setup.Registered or (Setup."Tenant ID" <> '') or SecretMgt.HasApiToken(Setup);
        if not HasLocalBinding then
            exit(false);

        IdentityState := GetIdentityState(Setup);
        if IdentityState = 'Mismatch' then
            exit(true);

        // Legacy installations have no identity snapshot. Do not disturb a healthy registered
        // legacy company, but allow an already-unregistered stale binding to be recovered.
        exit((IdentityState = 'Legacy') and not Setup.Registered and
            ((Setup."Tenant ID" <> '') or SecretMgt.HasApiToken(Setup)));
    end;

    procedure GetIdentityStateDisplay(var Setup: Record "DH Setup"): Text[100]
    begin
        case GetIdentityState(Setup) of
            'Matched':
                exit(IdentityMatchedLbl);
            'Mismatch':
                exit(IdentityMismatchLbl);
            else
                exit(IdentityLegacyLbl);
        end;
    end;

    procedure RecoverCopiedCompany(var Setup: Record "DH Setup")
    begin
        if not CanOfferRecovery(Setup) then
            Error(RecoveryNotRequiredErr);

        if not Confirm(RecoveryConfirmQst, false) then
            exit;

        ResetCopiedSchedulerState(Setup);
        DeleteCopiedBCSentinelHistory();
        ResetCopiedRegistrationState(Setup);
        Setup.Modify(true);
    end;

    local procedure HasIdentitySnapshot(var Setup: Record "DH Setup"): Boolean
    begin
        exit(
            (Setup."Access Snapshot Tenant ID" <> '') and
            (Setup."Access Snapshot Environment" <> '') and
            (Setup."Access Snapshot Env. Type" <> '') and
            (Setup."Access Snapshot Company ID" <> ''));
    end;

    local procedure ResetCopiedSchedulerState(var Setup: Record "DH Setup")
    begin
        // A copied Task ID can refer to the source company's task. Never call CancelTask here:
        // doing so could modify the source company. Only detach and disable the copied state.
        Setup."Scheduled Scans Enabled" := false;
        Clear(Setup."Scheduled Scan Task ID");
        Setup."Next Scheduled Scan" := 0DT;
        Setup."Last Scheduled Scan" := 0DT;
        Clear(Setup."Last Scheduled Scan Result");
        Clear(Setup."Last Scheduled Scan Duration");
        Setup."Scheduled Scan Failure Count" := 0;
        Setup."Last Scheduled Scan Error" := '';
    end;

    local procedure DeleteCopiedBCSentinelHistory()
    var
        ScanHeader: Record "DH Scan Header";
        DeepScanRun: Record "DH Deep Scan Run";
        ScanTrend: Record "DH Scan Trend";
        DashboardIssue: Record "DH Dashboard Issue";
        IssueException: Record "DH Issue Exception";
        IssueActionLog: Record "DH Issue Action Log";
        DuplicateBuffer: Record "DH Duplicate Buffer";
    begin
        // These tables contain BCSentinel-local history copied from the source company.
        // OnDelete cascades remove scan issues/findings. No Business Central master/ledger data is touched.
        if not ScanHeader.IsEmpty() then
            ScanHeader.DeleteAll(true);
        if not DeepScanRun.IsEmpty() then
            DeepScanRun.DeleteAll(true);
        if not ScanTrend.IsEmpty() then
            ScanTrend.DeleteAll(true);
        if not DashboardIssue.IsEmpty() then
            DashboardIssue.DeleteAll(true);
        if not IssueException.IsEmpty() then
            IssueException.DeleteAll(true);
        if not IssueActionLog.IsEmpty() then
            IssueActionLog.DeleteAll(true);
        if not DuplicateBuffer.IsEmpty() then
            DuplicateBuffer.DeleteAll(true);
    end;

    local procedure ResetCopiedRegistrationState(var Setup: Record "DH Setup")
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        // Local-only recovery. There is intentionally no backend call and no force rebind.
        SecretMgt.DeleteApiToken(Setup);

        Setup."Tenant ID" := '';
        Setup."API Token" := '';
        Setup.Registered := false;
        Setup."Registration Date" := 0DT;
        Setup."Last Score" := 0;
        Setup."Last Scan Date" := 0DT;
        Setup."Last Run ID Date" := 0D;
        Setup."Last Run ID Counter" := 0;
        Setup."Premium Enabled" := false;
        Clear(Setup."Current Plan");
        Clear(Setup."License Status");
        Setup."Last License Check" := 0DT;
        Setup."Can Run Data Health Score" := true;
        Setup."Data Health Score Completed" := false;
        Setup."Scan Credits Available" := 0;
        Setup."Assessment Credits Available" := 0;
        Setup."Validation Credits Available" := 0;
        Setup."Monitoring Active" := false;
        Setup."Dashboard Access Until" := '';
        Setup."Issue Access Until" := '';
        Setup."Can Run Deep Scan" := false;
        Setup."Can View Dashboard" := false;
        Setup."Can View Issue Details" := false;
        Setup."Can View Reports" := false;
        Setup."Can Use Monitoring" := false;
        Setup."Subscription Active" := false;
        Setup."Report Access Until" := '';
        Setup."Premium Until" := '';
        Setup."Monitoring Until" := '';
        Setup."Product Access Model" := '';
        Setup."Free Assessment Used" := false;
        Setup.InvalidateAccessSnapshot();
    end;

    var
        IdentityMatchedLbl: Label 'Matches the current Business Central company';
        IdentityMismatchLbl: Label 'Different Business Central company identity detected';
        IdentityLegacyLbl: Label 'Legacy registration without an identity snapshot';
        RecoveryNotRequiredErr: Label 'Copied-company registration recovery is not required for the current local registration state.';
        RecoveryConfirmQst: Label 'This action is only for a copied Business Central company. The local BCSentinel registration binding, copied BCSentinel scan history, access state, and scheduler state in this company will be removed. The source company and its backend registration are not changed. Business Central business data is not deleted. Continue?';
}
