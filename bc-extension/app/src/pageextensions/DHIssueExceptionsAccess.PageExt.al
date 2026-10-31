pageextension 53174 "DH Issue Exceptions Access" extends "DH Issue Exceptions"
{
    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Product Access Guard";
    begin
        AccessGuard.RequireIssueDetails();
    end;
}
