page 53199 "DH Corrections"
{
    PageType = List;
    SourceTable = "DH Issue Action Log";
    SourceTableView = sorting("Table ID", "Record SystemId", "Action At") order(descending) where("Action Type" = filter(CORRECTED | REOPENED));
    ApplicationArea = All;
    UsageCategory = History;
    Caption = 'BCSentinel Corrections';
    Editable = false;
    InsertAllowed = false;
    ModifyAllowed = false;
    DeleteAllowed = false;

    layout
    {
        area(Content)
        {
            group(Explanation)
            {
                ShowCaption = false;
                field(ExplanationText; ExplanationTxt)
                {
                    ApplicationArea = All;
                    ShowCaption = false;
                    Editable = false;
                    MultiLine = true;
                    ToolTip = 'Explains the difference between a documented correction and a permanent analysis exclusion.';
                }
            }
            repeater(Corrections)
            {
                field(CurrentStatus; CurrentStatusTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Current Status';
                    Editable = false;
                    StyleExpr = CurrentStatusStyle;
                    ToolTip = 'Shows whether the correction is currently documented as corrected or has been reopened.';
                }
                field("Record No."; Rec."Record No.")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the affected record.';
                }
                field("Record Caption"; Rec."Record Caption")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the affected record caption.';
                }
                field("Issue Code"; Rec."Issue Code")
                {
                    ApplicationArea = All;
                    Caption = 'Finding Code';
                    ToolTip = 'Specifies the finding for which the correction was documented.';
                }
                field("Action At"; Rec."Action At")
                {
                    ApplicationArea = All;
                    Caption = 'Last Action At';
                    ToolTip = 'Specifies when this correction action was recorded.';
                }
                field("Action User"; Rec."Action User")
                {
                    ApplicationArea = All;
                    Caption = 'Last Action By';
                    ToolTip = 'Specifies who recorded the correction action.';
                }
                field(Comment; Rec.Comment)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the correction or reopen comment.';
                }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(ReopenCorrection)
            {
                Caption = 'Reopen Correction';
                ApplicationArea = All;
                Image = ReOpen;
                Promoted = true;
                PromotedCategory = Process;
                ToolTip = 'Removes the active corrected status by recording a REOPENED lifecycle action. This does not create an analysis exclusion.';

                trigger OnAction()
                var
                    Remediation: Codeunit "DH Generic Remediation";
                begin
                    Remediation.ReopenCorrection(Rec);
                    CurrPage.Update(false);
                end;
            }

            action(OpenFullHistory)
            {
                Caption = 'Open Full History';
                ApplicationArea = All;
                Image = History;
                ToolTip = 'Opens all BCSentinel actions for the selected record and finding.';

                trigger OnAction()
                var
                    Remediation: Codeunit "DH Generic Remediation";
                begin
                    Remediation.OpenHistory(Rec."Table ID", Rec."Record SystemId", Rec."Issue Code");
                end;
            }
        }
    }

    trigger OnOpenPage()
    begin
        ExplanationTxt := CorrectionExplanationLbl;
    end;

    trigger OnAfterGetRecord()
    begin
        UpdateStatus();
    end;

    var
        ExplanationTxt: Text[500];
        CurrentStatusTxt: Text[30];
        CurrentStatusStyle: Text[30];
        CorrectionExplanationLbl: Label 'Mark as Corrected is a persistent audit/documentation status. It does not suppress a finding and does not change the score by itself. Every future scan re-evaluates the actual Business Central data. Use Exclude from Analysis only for a deliberate persistent scan exception.';
        CorrectedLbl: Label 'Corrected';
        ReopenedLbl: Label 'Reopened';

    local procedure UpdateStatus()
    var
        Remediation: Codeunit "DH Generic Remediation";
    begin
        if Remediation.IsCorrectionActive(Rec."Table ID", Rec."Record SystemId", Rec."Issue Code") then begin
            CurrentStatusTxt := CorrectedLbl;
            CurrentStatusStyle := 'Favorable';
        end else begin
            CurrentStatusTxt := ReopenedLbl;
            CurrentStatusStyle := 'Ambiguous';
        end;
    end;
}
