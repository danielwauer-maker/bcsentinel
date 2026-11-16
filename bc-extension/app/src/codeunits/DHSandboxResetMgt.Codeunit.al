codeunit 53201 "DH Sandbox Reset Mgt."
{
    Permissions =
        tabledata "DH Setup" = RIMD,
        tabledata "DH Scan Header" = RIMD,
        tabledata "DH Scan Issue" = RIMD,
        tabledata "DH Scan Trend" = RIMD,
        tabledata "DH Deep Scan Run" = RIMD,
        tabledata "DH Deep Scan Finding" = RIMD,
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
    begin
        // This is the authoritative guard. The page action is not a security boundary.
        if not EnvironmentInfo.IsSandbox() then
            Error('Reset Sandbox BCSentinel Data is available only in a Business Central sandbox. No data was changed.');

        EnsureNoActiveScan();
        EnsureNoUnmanagedScheduledTask(Setup);

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

    local procedure EnsureNoUnmanagedScheduledTask(Setup: Record "DH Setup")
    begin
        // This source version has no scheduler manager that can prove a Task Scheduler
        // cancellation succeeded. Refuse the reset instead of silently ignoring a task.
        if Setup."Scheduled Scans Enabled" then
            Error('BCSentinel data was not reset because scheduled scans are enabled and this version cannot prove scheduler cancellation. Disable and verify the scheduler first.');

        if not IsNullGuid(Setup."Scheduled Scan Task ID") then
            Error('BCSentinel data was not reset because legacy scheduled task %1 cannot be stopped reliably by this version. Cancel and verify the task first.', Setup."Scheduled Scan Task ID");
    end;

    local procedure DeleteLocalBCSentinelData()
    var
        ScanHeader: Record "DH Scan Header";
        ScanIssue: Record "DH Scan Issue";
        ScanTrend: Record "DH Scan Trend";
        DeepScanRun: Record "DH Deep Scan Run";
        DeepScanFinding: Record "DH Deep Scan Finding";
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
        // Delete children and immutable evidence with triggers disabled. The reset is a
        // sandbox-only administrative purge, so normal retention/immutability triggers
        // must not leave orphaned BCSentinel records behind.
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
