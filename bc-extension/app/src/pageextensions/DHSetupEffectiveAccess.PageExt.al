pageextension 53200 "DH Setup Effective Access" extends "DH Setup"
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
                ToolTip = 'Shows the effective end of the currently active product access. When Monitoring is active, the Monitoring end date is authoritative.';
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
