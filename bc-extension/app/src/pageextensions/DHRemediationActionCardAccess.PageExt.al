pageextension 53176 "DH Remediation Card Access" extends "DH Remediation Action Card"
{
    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Product Access Guard";
    begin
        AccessGuard.RequireIssueDetails();
    end;
}
