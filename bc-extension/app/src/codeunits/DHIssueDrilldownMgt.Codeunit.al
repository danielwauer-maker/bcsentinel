codeunit 53142 "DH Issue Drilldown Mgt."
{
    procedure OpenDashboardIssue(var DashboardIssue: Record "DH Dashboard Issue")
    begin
        EnsureIssuesAccess();
        OpenByIssueCode(DashboardIssue."Issue Code");
    end;

    procedure OpenScanIssue(var ScanIssue: Record "DH Scan Issue")
    begin
        EnsureIssuesAccess();
        OpenByIssueCode(ScanIssue."Issue Code");
    end;

    procedure OpenDeepScanFinding(var DeepFinding: Record "DH Deep Scan Finding")
    begin
        EnsureIssuesAccess();
        OpenByIssueCode(DeepFinding."Issue Code");
    end;

    procedure OpenByIssueCode(IssueCode: Code[50])
    var
        IssueDrilldownDispatcher: Codeunit "DH Issue Drilldown Dispatcher";
        RemediationContext: Codeunit "DH Remediation Context";
    begin
        EnsureIssuesAccess();
        RemediationContext.SetIssueCode(IssueCode);
        IssueDrilldownDispatcher.OpenByIssueCode(IssueCode);
    end;

    local procedure EnsureIssuesAccess()
    var
        AccessGuard: Codeunit "DH Access Guard";
    begin
        AccessGuard.EnsureIssuesAccess();
    end;
}
