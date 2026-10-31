pageextension 53169 "DH Item Missing Cost Access" extends "DH Item Missing Cost List"
{
    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Product Access Guard";
    begin
        AccessGuard.RequireIssueDetails();
    end;
}
