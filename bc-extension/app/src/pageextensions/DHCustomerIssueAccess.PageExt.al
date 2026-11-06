pageextension 53165 "DH Customer Issue Access" extends "DH Customer Issue List"
{
    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Product Access Guard";
    begin
        AccessGuard.RequireIssueDetails();
    end;
}
