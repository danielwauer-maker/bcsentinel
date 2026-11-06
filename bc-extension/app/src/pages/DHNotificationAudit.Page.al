page 53176 "DH Notification Audit"
{
    PageType = List;
    SourceTable = "DH Notification Config Audit";
    ApplicationArea = All;
    UsageCategory = History;
    Caption = 'BCSentinel Notification Configuration Audit';
    Editable = false;
    InsertAllowed = false;
    ModifyAllowed = false;
    DeleteAllowed = false;

    layout
    {
        area(Content)
        {
            repeater(Audit)
            {
                field("Changed At UTC"; Rec."Changed At UTC") { ApplicationArea = All; }
                field("Object Type"; Rec."Object Type") { ApplicationArea = All; }
                field("Object Ref"; Rec."Object Ref") { ApplicationArea = All; }
                field("Changed Field"; Rec."Changed Field") { ApplicationArea = All; }
                field("Previous Value"; Rec."Previous Value") { ApplicationArea = All; }
                field("New Value"; Rec."New Value") { ApplicationArea = All; }
                field("Changed By"; Rec."Changed By") { ApplicationArea = All; }
            }
        }
    }
}
