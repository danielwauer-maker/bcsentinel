codeunit 53142 "DH Issue Drilldown Mgt."
{
    procedure OpenDashboardIssue(var DashboardIssue: Record "DH Dashboard Issue")
    begin
        RequirePremiumAccess();
        OpenByIssueCodeInternal(DashboardIssue."Issue Code");
    end;

    procedure OpenScanIssue(var ScanIssue: Record "DH Scan Issue")
    begin
        RequirePremiumAccess();
        OpenByIssueCodeInternal(ScanIssue."Issue Code");
    end;

    procedure OpenDeepScanFinding(var DeepFinding: Record "DH Deep Scan Finding")
    begin
        RequirePremiumAccess();
        OpenByIssueCodeInternal(DeepFinding."Issue Code");
    end;

    procedure OpenByIssueCode(IssueCode: Code[50])
    begin
        RequirePremiumAccess();
        OpenByIssueCodeInternal(IssueCode);
    end;

    local procedure OpenByIssueCodeInternal(IssueCode: Code[50])
    var
        IssueDrilldownDispatcher: Codeunit "DH Issue Drilldown Dispatcher";
    begin
        IssueDrilldownDispatcher.OpenByIssueCode(IssueCode);
    end;

    local procedure RequirePremiumAccess()
    var
        AccessGuard: Codeunit "DH Product Access Guard";
    begin
        AccessGuard.RequireIssueDetails();
    end;
}
