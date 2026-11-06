page 53175 "DH Notification Events"
{
    PageType = List;
    SourceTable = "DH Notification Event";
    ApplicationArea = All;
    UsageCategory = History;
    Caption = 'BCSentinel Notification Event Log';
    Editable = false;
    InsertAllowed = false;
    ModifyAllowed = false;
    DeleteAllowed = false;

    layout
    {
        area(Content)
        {
            repeater(Events)
            {
                field("Occurred At UTC"; Rec."Occurred At UTC") { ApplicationArea = All; }
                field("Event Type"; Rec."Event Type") { ApplicationArea = All; }
                field(Summary; Rec.Summary) { ApplicationArea = All; }
                field(Severity; Rec.Severity) { ApplicationArea = All; }
                field("Source Ref"; Rec."Source Ref") { ApplicationArea = All; }
                field("Correlation Key"; Rec."Correlation Key") { ApplicationArea = All; }
                field("Finding Key"; Rec."Finding Key") { ApplicationArea = All; }
                field("Scan ID"; Rec."Scan ID") { ApplicationArea = All; }
                field("Validation Ref"; Rec."Validation Ref") { ApplicationArea = All; }
                field("Action ID"; Rec."Action ID") { ApplicationArea = All; }
            }
        }
    }
}
