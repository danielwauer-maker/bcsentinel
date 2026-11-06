page 53196 "DH Remediation Audit"
{
    PageType = List;
    SourceTable = "DH Remediation Audit";
    ApplicationArea = All;
    UsageCategory = None;
    Caption = 'BCSentinel Remediation Audit';
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
                field("Changed Field or Status"; Rec."Changed Field or Status") { ApplicationArea = All; }
                field("Previous Value"; Rec."Previous Value") { ApplicationArea = All; }
                field("New Value"; Rec."New Value") { ApplicationArea = All; }
                field("Changed By Principal ID"; Rec."Changed By Principal ID") { ApplicationArea = All; }
                field("Tenant ID"; Rec."Tenant ID") { ApplicationArea = All; }
                field("Company ID"; Rec."Company ID") { ApplicationArea = All; }
            }
        }
    }
}
