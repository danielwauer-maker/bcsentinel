pageextension 53177 "DH Remediation Audit Access" extends "DH Remediation Audit"
{
    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Product Access Guard";
    begin
        AccessGuard.RequireIssueDetails();
    end;
}
