page 53171 "DH Notification Recipients"
{
    PageType = List;
    SourceTable = "DH Notification Recipient";
    ApplicationArea = All;
    UsageCategory = Administration;
    Caption = 'BCSentinel Notification Recipients';

    layout
    {
        area(Content)
        {
            repeater(Recipients)
            {
                field("Display Name"; Rec."Display Name") { ApplicationArea = All; }
                field("Email Address"; Rec."Email Address") { ApplicationArea = All; }
                field(Enabled; Rec.Enabled) { ApplicationArea = All; }
                field("Language Code"; Rec."Language Code") { ApplicationArea = All; }
                field("Recipient Role"; Rec."Recipient Role") { ApplicationArea = All; }
                field("Principal ID"; Rec."Principal ID") { ApplicationArea = All; }
                field("Updated At UTC"; Rec."Updated At UTC") { ApplicationArea = All; Editable = false; }
            }
        }
    }
}
