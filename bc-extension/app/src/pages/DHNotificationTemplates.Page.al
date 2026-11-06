page 53173 "DH Notification Templates"
{
    PageType = List;
    SourceTable = "DH Notification Template";
    ApplicationArea = All;
    UsageCategory = Administration;
    Caption = 'BCSentinel Notification Templates';

    layout
    {
        area(Content)
        {
            repeater(Templates)
            {
                field("Template Key"; Rec."Template Key") { ApplicationArea = All; }
                field("Event Type"; Rec."Event Type") { ApplicationArea = All; }
                field("Language Code"; Rec."Language Code") { ApplicationArea = All; }
                field("Subject Template"; Rec."Subject Template") { ApplicationArea = All; }
                field("Body Template"; Rec."Body Template") { ApplicationArea = All; MultiLine = true; }
                field("Template Version"; Rec."Template Version") { ApplicationArea = All; }
                field(Enabled; Rec.Enabled) { ApplicationArea = All; }
                field("Updated At UTC"; Rec."Updated At UTC") { ApplicationArea = All; Editable = false; }
            }
        }
    }
}
