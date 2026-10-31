pageextension 53170 "DH Item Missing Price Access" extends "DH Item Missing Price List"
{
    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Product Access Guard";
    begin
        AccessGuard.RequireIssueDetails();
    end;
}
