pageextension 53168 "DH Duplicate Worklist Access" extends "DH Duplicate Worklist"
{
    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Product Access Guard";
    begin
        AccessGuard.RequireIssueDetails();
    end;
}
