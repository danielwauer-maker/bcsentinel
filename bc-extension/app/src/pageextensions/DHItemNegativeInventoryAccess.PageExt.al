pageextension 53171 "DH Item Neg Inventory Access" extends "DH Item Neg. Inventory"
{
    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Product Access Guard";
    begin
        AccessGuard.RequireIssueDetails();
    end;
}
