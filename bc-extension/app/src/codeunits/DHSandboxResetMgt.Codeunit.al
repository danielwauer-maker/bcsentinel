codeunit 53349 "DH Sandbox Reset Mgt."
{
    Permissions =
        tabledata "DH Setup" = RIMD,
        tabledata "DH Scan Header" = RIMD,
        tabledata "DH Scan Issue" = RIMD,
        tabledata "DH Scan Trend" = RIMD,
        tabledata "DH Deep Scan Run" = RIMD,
        tabledata "DH Deep Scan Finding" = RIMD,
        tabledata "DH Check Execution" = RIMD,
        tabledata "DH Scan Record Evidence" = RIMD,
        tabledata "DH Dashboard Issue" = RIMD,
        tabledata "DH Issue Exception" = RIMD,
        tabledata "DH Issue Action Log" = RIMD,
        tabledata "DH Duplicate Buffer" = RIMD,
        tabledata "DH Scan Check Selection" = RIMD,
        tabledata "DH Remediation Action" = RIMD,
        tabledata "DH Remediation Audit" = RIMD,
        tabledata "DH Notification Setup" = RIMD,
        tabledata "DH Notification Event" = RIMD,
        tabledata "DH Notification Rule" = RIMD,
        tabledata "DH Notification Recipient" = RIMD,
        tabledata "DH Notification Template" = RIMD,
        tabledata "DH Notification Delivery" = RIMD,
        tabledata "DH Notification Config Audit" = RIMD;

    procedure ResetSandboxData(var Setup: Record "DH Setup")
    var
        EnvironmentInfo: Codeunit "Environment Information";
        SecretMgt: Codeunit "DH Secret Mgt.";
        SchedulerMgt: Codeunit "DH Scan Scheduler Mgt.";
    begin
        // This is the authoritative guard. The page action is not a security boundary.
        if not EnvironmentInfo.IsSandbox() then
            Error('Reset Sandbox BCSentinel Data is available only in a Business Central sandbox. No data was changed.');

        EnsureNoActiveScan();
        SchedulerMgt.StopSchedulerForSandboxReset(Setup);
        // Cancellation can race with a task that was already starting. Re-check
        // before deleting any local data so a newly-created active run is protected.
        EnsureNoActiveScan();

        DeleteLocalBCSentinelData();
        SecretMgt.DeleteApiToken(Setup);
        Setup.ClearSandboxRegistrationState();
        Setup.Modify(true);
    end;

    local procedure EnsureNoActiveScan()
    var
        DeepScanRun: Record "DH Deep Scan Run";
    begin
        DeepScanRun.SetFilter(Status, '%1|%2', DeepScanRun.Status::Queued, DeepScanRun.Status::Running);
        if DeepScanRun.FindFirst() then
            Error('BCSentinel data was not reset because scan %1 is %2. Wait until it reaches a terminal state.', DeepScanRun."Run ID", Format(DeepScanRun.Status));
    end;

    local procedure DeleteLocalBCSentinelData()
    var
        ScanHeader: Record "DH Scan Header";
        ScanIssue: Record "DH Scan Issue";
        ScanTrend: Record "DH Scan Trend";
        DeepScanRun: Record "DH Deep Scan Run";
        DeepScanFinding: Record "DH Deep Scan Finding";
        CheckExecution: Record "DH Check Execution";
        ScanRecordEvidence: Record "DH Scan Record Evidence";
        DashboardIssue: Record "DH Dashboard Issue";
        IssueException: Record "DH Issue Exception";
        IssueActionLog: Record "DH Issue Action Log";
        DuplicateBuffer: Record "DH Duplicate Buffer";
        ScanCheckSelection: Record "DH Scan Check Selection";
        RemediationAction: Record "DH Remediation Action";
        RemediationAudit: Record "DH Remediation Audit";
        NotificationSetup: Record "DH Notification Setup";
        NotificationEvent: Record "DH Notification Event";
        NotificationRule: Record "DH Notification Rule";
        NotificationRecipient: Record "DH Notification Recipient";
        NotificationTemplate: Record "DH Notification Template";
        NotificationDelivery: Record "DH Notification Delivery";
        NotificationConfigAudit: Record "DH Notification Config Audit";
    begin
        // Immutable BCSentinel tables reject normal deletes. Every BCSentinel child
        // table is therefore explicitly purged as part of this sandbox-only reset.
        NotificationDelivery.DeleteAll(false);
        NotificationEvent.DeleteAll(false);
        NotificationConfigAudit.DeleteAll(false);
        NotificationRecipient.DeleteAll(false);
        NotificationRule.DeleteAll(false);
        NotificationTemplate.DeleteAll(false);
        NotificationSetup.DeleteAll(false);
        RemediationAudit.DeleteAll(false);
        RemediationAction.DeleteAll(false);
        IssueActionLog.DeleteAll(false);
        IssueException.DeleteAll(false);
        ScanRecordEvidence.DeleteAll(false);
        CheckExecution.DeleteAll(false);
        DeepScanFinding.DeleteAll(false);
        ScanIssue.DeleteAll(false);
        DashboardIssue.DeleteAll(false);
        DeepScanRun.DeleteAll(false);
        ScanHeader.DeleteAll(false);
        ScanTrend.DeleteAll(false);
        DuplicateBuffer.DeleteAll(false);
        ScanCheckSelection.DeleteAll(false);
    end;
}
