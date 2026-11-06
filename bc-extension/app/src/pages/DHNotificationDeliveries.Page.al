page 53174 "DH Notification Deliveries"
{
    PageType = List;
    SourceTable = "DH Notification Delivery";
    ApplicationArea = All;
    UsageCategory = History;
    Caption = 'BCSentinel Notification Delivery Log';
    Editable = false;
    InsertAllowed = false;
    ModifyAllowed = false;
    DeleteAllowed = false;

    layout
    {
        area(Content)
        {
            repeater(Deliveries)
            {
                field(Status; Rec.Status) { ApplicationArea = All; }
                field("Attempt No."; Rec."Attempt No.") { ApplicationArea = All; }
                field(Channel; Rec.Channel) { ApplicationArea = All; }
                field("Created At UTC"; Rec."Created At UTC") { ApplicationArea = All; }
                field("Sent At UTC"; Rec."Sent At UTC") { ApplicationArea = All; }
                field("Next Retry At UTC"; Rec."Next Retry At UTC") { ApplicationArea = All; }
                field("Error Code"; Rec."Error Code") { ApplicationArea = All; }
                field("Error Message Safe"; Rec."Error Message Safe") { ApplicationArea = All; }
                field("Suppression Reason"; Rec."Suppression Reason") { ApplicationArea = All; }
                field("Event ID"; Rec."Event ID") { ApplicationArea = All; }
                field("Recipient ID"; Rec."Recipient ID") { ApplicationArea = All; }
            }
        }
    }
}
