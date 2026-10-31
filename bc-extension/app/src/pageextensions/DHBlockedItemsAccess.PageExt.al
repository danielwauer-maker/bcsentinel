pageextension 53167 "DH Blocked Items Access" extends "DH Blocked Items Inv"
{
    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Product Access Guard";
    begin
        AccessGuard.RequireIssueDetails();
    end;
}
