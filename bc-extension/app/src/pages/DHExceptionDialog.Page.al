page 53173 "DH Exception Dialog"
{
    PageType = StandardDialog;
    Caption = 'Create DH Exception';

    layout
    {
        area(Content)
        {
            group(ExceptionDetails)
            {
                Caption = 'Exception Details';
                field(RecordNo; RecordNoValue) { ApplicationArea = All; Caption = 'Record No.'; Editable = false; ToolTip = 'Specifies the affected record.'; }
                field(RecordCaption; RecordCaptionValue) { ApplicationArea = All; Caption = 'Record Caption'; Editable = false; ToolTip = 'Specifies the affected record caption.'; }
                field(IssueCode; IssueCodeValue) { ApplicationArea = All; Caption = 'Issue Code'; Editable = IssueCodeEditable; NotBlank = true; ToolTip = 'Specifies the check from which the record will be excluded.'; }
                field(Reason; ReasonValue) { ApplicationArea = All; Caption = 'Reason'; NotBlank = true; MultiLine = true; ToolTip = 'Specifies the required business reason for the exception.'; }
                field(ScoreEffect; ScoreEffectTxt) { ApplicationArea = All; Caption = 'Score Effect'; Editable = false; MultiLine = true; ToolTip = 'Explains how the exception affects the next scan.'; }
            }
        }
    }

    trigger OnOpenPage()
    begin
        ScoreEffectTxt := ScoreEffectLbl;
    end;

    trigger OnQueryClosePage(CloseAction: Action): Boolean
    begin
        if CloseAction = Action::OK then begin
            if IssueCodeValue = '' then
                Error(IssueCodeRequiredErr);
            ReasonValue := CopyStr(ReasonValue.Trim(), 1, MaxStrLen(ReasonValue));
            if ReasonValue = '' then
                Error(ReasonRequiredErr);
        end;
        exit(true);
    end;

    procedure SetContext(NewRecordNo: Code[20]; NewRecordCaption: Text[100]; NewIssueCode: Code[50]; NewReason: Text[250])
    begin
        RecordNoValue := NewRecordNo;
        RecordCaptionValue := NewRecordCaption;
        IssueCodeValue := NewIssueCode;
        ReasonValue := NewReason;
        IssueCodeEditable := NewIssueCode = '';
    end;

    procedure GetValues(var SelectedIssueCode: Code[50]; var SelectedReason: Text[250])
    begin
        SelectedIssueCode := IssueCodeValue;
        SelectedReason := ReasonValue;
    end;

    var
        RecordNoValue: Code[20];
        RecordCaptionValue: Text[100];
        IssueCodeValue: Code[50];
        ReasonValue: Text[250];
        ScoreEffectTxt: Text[250];
        IssueCodeEditable: Boolean;
        ScoreEffectLbl: Label 'This record will be excluded from this check and from the effective score, penalty, and financial impact calculation until the exception is manually deactivated.';
        IssueCodeRequiredErr: Label 'An issue code is required.';
        ReasonRequiredErr: Label 'A reason is required for a DH exception.';
}
