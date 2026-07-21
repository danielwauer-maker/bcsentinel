page 53159 "DH Issue Drilldown Launch"
{
    PageType = Card;
    SourceTable = "DH Setup";
    ApplicationArea = All;
    UsageCategory = None;
    Caption = 'DH Issue Drilldown Launch';
    Editable = false;
    InsertAllowed = false;
    DeleteAllowed = false;
    ModifyAllowed = false;

    layout
    {
        area(Content)
        {
            group(Launch)
            {
                field(StatusTxt; StatusTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Status';
                    ToolTip = 'Specifies Status.';
                    Editable = false;
                }
            }
        }
    }

    trigger OnOpenPage()
    var
        IssueCode: Code[50];
        SetupRef: RecordRef;
        IssueCodeField: FieldRef;
        IssueDrilldownDispatcher: Codeunit "DH Issue Drilldown Dispatcher";
        AccessGuard: Codeunit "DH Access Guard";
    begin
        SetupRef.GetTable(Rec);
        IssueCodeField := SetupRef.Field(26);
        IssueCode := GetNormalizedIssueCode(IssueCodeField);
        if IssueCode = '' then
            Error(MissingIssueCodeErr);

        if not Rec.Get('SETUP') then
            Error(SetupNotFoundErr);

        AccessGuard.EnsureIssuesAccess();

        CurrPage.Close();
        IssueDrilldownDispatcher.OpenByIssueCode(IssueCode);
    end;

    local procedure GetNormalizedIssueCode(IssueCodeField: FieldRef): Code[50]
    var
        FilterText: Text;
        NormalizedIssueCode: Code[50];
    begin
        FilterText := UpperCase(Format(IssueCodeField.GetFilter()));
        FilterText := DelChr(FilterText, '=', '@*''" ');
        NormalizedIssueCode := CopyStr(FilterText, 1, MaxStrLen(NormalizedIssueCode));
        exit(NormalizedIssueCode);
    end;

    var
        MissingIssueCodeErr: Label 'The issue code for opening the details is missing.';
        SetupNotFoundErr: Label 'BCSentinel setup was not found.';
        StatusTxt: Text[100];
}
