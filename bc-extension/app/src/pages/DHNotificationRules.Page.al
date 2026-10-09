page 53172 "DH Notification Rules"
{
    PageType = List;
    SourceTable = "DH Notification Rule";
    ApplicationArea = All;
    UsageCategory = Administration;
    Caption = 'BCSentinel Notification Rules';

    layout
    {
        area(Content)
        {
            repeater(Rules)
            {
                field("Event Type"; Rec."Event Type") { ApplicationArea = All; }
                field(Enabled; Rec.Enabled) { ApplicationArea = All; }
                field(Channel; Rec.Channel) { ApplicationArea = All; Editable = false; }
                field("Template Key"; Rec."Template Key") { ApplicationArea = All; }
                field("Minimum Severity"; Rec."Minimum Severity") { ApplicationArea = All; }
                field("Module Scope"; Rec."Module Scope") { ApplicationArea = All; }
                field("Business Area"; Rec."Business Area") { ApplicationArea = All; }
                field("Quiet Hours Policy"; Rec."Quiet Hours Policy") { ApplicationArea = All; }
                field("Digest Policy"; Rec."Digest Policy") { ApplicationArea = All; }
                field("Updated At UTC"; Rec."Updated At UTC") { ApplicationArea = All; Editable = false; }
            }
        }
    }
}
