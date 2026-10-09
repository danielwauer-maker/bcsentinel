page 53194 "DH Remediation Actions"
{
    PageType = List;
    SourceTable = "DH Remediation Action";
    ApplicationArea = All;
    UsageCategory = Lists;
    Caption = 'BCSentinel Remediation Actions';
    CardPageId = "DH Remediation Action Card";
    InsertAllowed = true;
    DeleteAllowed = false;

    layout
    {
        area(Content)
        {
            repeater(Actions)
            {
                field(Title; Rec.Title) { ApplicationArea = All; }
                field("Finding Key"; Rec."Finding Key") { ApplicationArea = All; }
                field(Status; Rec.Status) { ApplicationArea = All; }
                field(Priority; Rec.Priority) { ApplicationArea = All; }
                field("Owner Display Name"; Rec."Owner Display Name") { ApplicationArea = All; }
                field("Due At UTC"; Rec."Due At UTC") { ApplicationArea = All; }
                field(Source; Rec.Source) { ApplicationArea = All; Editable = false; }
                field("Updated At UTC"; Rec."Updated At UTC") { ApplicationArea = All; Editable = false; }
            }
        }
    }

    actions
    {
        area(Navigation)
        {
            action(AuditTrail)
            {
                ApplicationArea = All;
                Caption = 'Audit Trail';
                Image = History;
                RunObject = page "DH Remediation Audit";
                RunPageLink = "Action ID" = field("Action ID");
            }
        }
    }
}
