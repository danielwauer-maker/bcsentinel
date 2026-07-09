page 53127 "DH Key Metrics Part"
{
    PageType = CardPart;
    SourceTable = "DH Scan Header";
    ApplicationArea = All;
    Caption = 'Key Metrics';
    Editable = false;
    UsageCategory = None;

    layout
    {
        area(Content)
        {
            cuegroup(KeyMetrics)
            {
                ShowCaption = false;

                field(DataScoreCue; Rec."Data Score")
                {
                    ApplicationArea = All;
                    Caption = 'Data Score';
                    ToolTip = 'Specifies Data Score.';
                    StyleExpr = DataScoreStyle;
                }

                field(TotalRecordsCue; Rec."Total Records")
                {
                    ApplicationArea = All;
                    Caption = 'Records';
                    ToolTip = 'Specifies Records.';
                    StyleExpr = RecordsStyle;
                }

                field(PremiumPriceCue; PremiumPriceTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Monitoring / Month';
                    ToolTip = 'Specifies the estimated monitoring amount per month in local currency.';
                    StyleExpr = PremiumPriceStyle;
                }

                field(EstimatedImpactCue; EstimatedImpactTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Estimated Impact';
                    ToolTip = 'Specifies the estimated impact in local currency.';
                    StyleExpr = LossStyle;
                }

                field(ROICue; ROITxt)
                {
                    ApplicationArea = All;
                    Caption = 'ROI';
                    ToolTip = 'Specifies ROI in local currency.';
                    StyleExpr = ROIStyle;
                }
            }
        }
    }

    trigger OnAfterGetRecord()
    begin
        BuildStyles();
    end;

    trigger OnOpenPage()
    begin
        BuildStyles();
    end;

    var
        DataScoreStyle: Text[30];
        RecordsStyle: Text[30];
        PremiumPriceStyle: Text[30];
        LossStyle: Text[30];
        ROIStyle: Text[30];
        EstimatedImpactTxt: Text[50];
        PremiumPriceTxt: Text[50];
        ROITxt: Text[50];

    local procedure BuildStyles()
    begin
        DataScoreStyle := GetScoreStyle(Rec."Data Score");
        RecordsStyle := 'StrongAccent';
        PremiumPriceStyle := 'Ambiguous';
        LossStyle := 'Unfavorable';
        ROIStyle := GetROIStyle(Rec."ROI");
        PremiumPriceTxt := GetLocalAmountText(Rec."Est. Premium Price");
        EstimatedImpactTxt := GetLocalAmountText(Rec."Estimated Loss (EUR)");
        ROITxt := GetLocalAmountText(Rec."ROI");
    end;

    local procedure GetScoreStyle(ScoreValue: Integer): Text
    begin
        if ScoreValue >= 86 then
            exit('Favorable');
        if ScoreValue >= 61 then
            exit('Ambiguous');
        exit('Unfavorable');
    end;

    local procedure GetROIStyle(ROIValue: Decimal): Text
    begin
        if ROIValue > 0 then
            exit('Favorable');
        if ROIValue < 0 then
            exit('Unfavorable');
        exit('Standard');
    end;

    local procedure GetLocalAmountText(Amount: Decimal): Text[50]
    var
        CurrencyMgt: Codeunit "DH Currency Mgt.";
    begin
        exit(CurrencyMgt.FormatLocalAmount(Amount));
    end;
}

