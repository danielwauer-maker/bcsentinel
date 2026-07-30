codeunit 53142 "DH Issue Drilldown Mgt."
{
    procedure OpenDashboardIssue(var DashboardIssue: Record "DH Dashboard Issue")
    begin
        EnsureFullIssueDetailsAccess();
        OpenByIssueCode(DashboardIssue."Issue Code");
    end;

    procedure OpenScanIssue(var ScanIssue: Record "DH Scan Issue")
    begin
        EnsureFullIssueDetailsAccess();
        OpenByIssueCode(ScanIssue."Issue Code");
    end;

    procedure OpenDeepScanFinding(var DeepFinding: Record "DH Deep Scan Finding")
    begin
        EnsureFullIssueDetailsAccess();
        OpenByIssueCode(DeepFinding."Issue Code");
    end;

    procedure OpenByIssueCode(IssueCode: Code[50])
    var
        IssueDrilldownDispatcher: Codeunit "DH Issue Drilldown Dispatcher";
    begin
        EnsureFullIssueDetailsAccess();
        IssueDrilldownDispatcher.OpenByIssueCode(IssueCode);
    end;

    local procedure EnsureFullIssueDetailsAccess()
    var
        AccessGuard: Codeunit "DH Access Guard";
    begin
        AccessGuard.EnsureFullIssueDetailsAccess();
    end;
}
