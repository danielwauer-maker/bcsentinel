codeunit 53348 "DH Findings Diagnostics Mgt."
{
    Permissions = tabledata "DH Deep Scan Run" = R,
                  tabledata "DH Deep Scan Finding" = R;

    procedure ShowLatestCompletedScanDiagnostics()
    var
        DeepScanRun: Record "DH Deep Scan Run";
        Finding: Record "DH Deep Scan Finding";
        PageFilteredFinding: Record "DH Deep Scan Finding";
        AccessGuard: Codeunit "DH Access Guard";
        IdentityMgt: Codeunit "DH Tenant Identity Mgt.";
        PhysicalFindingCount: Integer;
        PageFilteredFindingCount: Integer;
        FullAccessConfirmed: Boolean;
        SandboxOnlyErr: Label 'Findings persistence diagnostics are available only in a Business Central sandbox.';
        NoCompletedScanErr: Label 'No completed local Deep Scan is available for findings diagnostics.';
        FindingsDiagnosticsMsg: Label 'Findings persistence diagnostics\Run entry no.: %1\Run ID: %2\Status: %3\Stored issues count: %4\Physical finding rows for this run: %5\Rows after Findings page run filter: %6\Fresh Full/Monitoring access confirmed: %7', Comment = '%1 = local run entry number, %2 = run ID, %3 = status, %4 = stored issues count, %5 = physical row count, %6 = filtered row count, %7 = access status';
    begin
        if IdentityMgt.GetEnvironmentType() <> 'sandbox' then
            Error(SandboxOnlyErr);

        DeepScanRun.SetCurrentKey("Requested At");
        DeepScanRun.SetRange(Status, DeepScanRun.Status::Completed);
        DeepScanRun.Ascending(false);
        if not DeepScanRun.FindFirst() then
            Error(NoCompletedScanErr);

        Finding.SetRange("Deep Scan Entry No.", DeepScanRun."Entry No.");
        PhysicalFindingCount := Finding.Count();

        // This exactly mirrors the explicit run selector used by the temporary
        // Findings List. It does not copy, modify, or expose finding content.
        PageFilteredFinding.SetRange("Deep Scan Entry No.", DeepScanRun."Entry No.");
        PageFilteredFindingCount := PageFilteredFinding.Count();
        FullAccessConfirmed := AccessGuard.HasFreshFullOrMonitoringAccess();

        Message(FindingsDiagnosticsMsg,
            DeepScanRun."Entry No.",
            DeepScanRun."Run ID",
            Format(DeepScanRun.Status),
            DeepScanRun."Issues Count",
            PhysicalFindingCount,
            PageFilteredFindingCount,
            Format(FullAccessConfirmed));
    end;
}
