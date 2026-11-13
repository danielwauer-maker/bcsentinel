pageextension 53201 "DH Setup Effective Access" extends "DH Setup"
{
    layout
    {
        modify(PremiumUntil)
        {
            Visible = false;
        }

        addafter(PremiumUntil)
        {
            field(EffectiveProductAccessUntil; EffectiveProductAccessUntilTxt)
            {
                ApplicationArea = All;
                Caption = 'Product Access Until';
                Editable = false;
                ToolTip = 'Shows the effective product entitlement expiry: active Monitoring takes precedence over the earlier Full Analysis end date.';
            }
            field(FullAnalysisAccessUntil; Rec."Premium Until")
            {
                ApplicationArea = All;
                Caption = 'Full Analysis Access Until';
                Editable = false;
                ToolTip = 'Shows the separately granted Full Analysis access end. This can differ from an active Monitoring subscription expiry.';
            }
        }
    }

    trigger OnAfterGetRecord()
    begin
        UpdateEffectiveProductAccessUntil();
    end;

    trigger OnAfterGetCurrRecord()
    begin
        UpdateEffectiveProductAccessUntil();
    end;

    var
        EffectiveProductAccessUntilTxt: Text[50];

    local procedure UpdateEffectiveProductAccessUntil()
    begin
        if Rec."Monitoring Active" and (Rec."Monitoring Until" <> '') then
            EffectiveProductAccessUntilTxt := Rec."Monitoring Until"
        else
            EffectiveProductAccessUntilTxt := Rec."Premium Until";
    end;
}
