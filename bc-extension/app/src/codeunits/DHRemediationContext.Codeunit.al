codeunit 53196 "DH Remediation Context"
{
    SingleInstance = true;

    procedure SetIssueCode(IssueCode: Code[50])
    begin
        CurrentIssueCode := IssueCode;
    end;

    procedure GetIssueCode(): Code[50]
    begin
        exit(CurrentIssueCode);
    end;

    procedure ClearIssueCode()
    begin
        Clear(CurrentIssueCode);
    end;

    var
        CurrentIssueCode: Code[50];
}
