pageextension 53173 "DH Sales Line Access" extends "DH Sales Line Issue Worklist"
{
    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Product Access Guard";
    begin
        AccessGuard.RequireIssueDetails();
    end;
}
