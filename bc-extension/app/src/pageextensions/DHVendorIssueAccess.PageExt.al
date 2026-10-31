pageextension 53166 "DH Vendor Issue Access" extends "DH Vendor Issue List"
{
    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Product Access Guard";
    begin
        AccessGuard.RequireIssueDetails();
    end;
}
