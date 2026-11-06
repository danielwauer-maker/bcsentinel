pageextension 53172 "DH Purchase Line Access" extends "DH Purch. Line Worklist"
{
    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Product Access Guard";
    begin
        AccessGuard.RequireIssueDetails();
    end;
}
