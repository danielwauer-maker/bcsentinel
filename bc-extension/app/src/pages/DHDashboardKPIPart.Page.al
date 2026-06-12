page 53142 "DH Dashboard KPI Part"
{
    PageType = CardPart;
    SourceTable = "DH Deep Scan Run";
    ApplicationArea = All;
    Caption = 'Key Metrics';
    Editable = false;
    InsertAllowed = false;
    DeleteAllowed = false;
    ModifyAllowed = false;

    layout
    {
        area(Content)
        {
            cuegroup(KPIs)
            {
                ShowCaption = false;

                field("Data Score"; Rec."Deep Score")
                {
                    ApplicationArea = All;
                    Caption = 'Data Health Score';
                    StyleExpr = DataScoreStyle;
                    ToolTip = 'Assessment of data quality.';
                }

                /*field("Estimated Loss"; Rec."Estimated Loss (EUR)")
                {
                    ApplicationArea = All;
                    Caption = 'Potential Loss';
                    StyleExpr = EstimatedLossStyle;
                    ToolTip = 'Estimated potential loss caused by poor data quality.';
                }*/

                field("Checks Count"; Rec."Checks Count")
                {
                    ApplicationArea = All;
                    Caption = 'Checks';
                    StyleExpr = ChecksStyle;
                    ToolTip = 'Number of checks run.';
                }

                field("Issues Count"; Rec."Issues Count")
                {
                    ApplicationArea = All;
                    Caption = 'Different Issues';
                    StyleExpr = IssuesStyle;
                    ToolTip = 'Number of issues found.';
                }

                /*field("Affected Records"; Rec."Affected Records")
                {
                    ApplicationArea = All;
                    Caption = 'Affected';
                    StyleExpr = IssuesStyle;
                    ToolTip = 'Total affected records across all findings.';
                }*/
            }
        }
    }

    trigger OnAfterGetRecord()
    begin
        UpdateStyles();
    end;

    trigger OnOpenPage()
    begin
        UpdateStyles();
    end;

    var
        DataScoreStyle: Text[30];
        EstimatedLossStyle: Text[30];
        ChecksStyle: Text[30];
        IssuesStyle: Text[30];

    local procedure UpdateStyles()
    begin
        DataScoreStyle := GetDataScoreStyle();
        EstimatedLossStyle := GetEstimatedLossStyle();
        ChecksStyle := GetChecksStyle();
        IssuesStyle := GetIssuesStyle();
    end;

    local procedure GetDataScoreStyle(): Text[30]
    begin
        if Rec."Deep Score" >= 86 then
            exit('Favorable');

        if Rec."Deep Score" >= 61 then
            exit('Ambiguous');

        if Rec."Deep Score" >= 1 then
            exit('Unfavorable');

        exit('Unfavorable');
    end;

    local procedure GetEstimatedLossStyle(): Text[30]
    begin
        if Rec."Estimated Loss (EUR)" > 0 then
            exit('Unfavorable');

        exit('Standard');
    end;

    local procedure GetChecksStyle(): Text[30]
    begin
        if Rec."Checks Count" > 0 then
            exit('Strong');

        exit('Standard');
    end;

    local procedure GetIssuesStyle(): Text[30]
    begin
        if (Rec."Issues Count" > 0) or (Rec."Affected Records" > 0) then
            exit('Attention');

        exit('Standard');
    end;


    procedure SetDeepScanRunEntryNo(DeepScanRunEntryNo: Integer)
    begin
        if DeepScanRunEntryNo <= 0 then begin
            Rec.Reset();
            Rec.SetRange("Entry No.", -1);
            if Rec.FindFirst() then;
            CurrPage.Update(false);
            exit;
        end;

        Rec.Reset();
        Rec.SetRange("Entry No.", DeepScanRunEntryNo);
        if Rec.FindFirst() then;
        CurrPage.Update(false);
    end;
}
