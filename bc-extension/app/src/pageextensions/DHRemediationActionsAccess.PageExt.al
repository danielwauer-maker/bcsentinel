pageextension 53175 "DH Remediation Actions Access" extends "DH Remediation Actions"
{
    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Product Access Guard";
    begin
        AccessGuard.RequireIssueDetails();
    end;
}
