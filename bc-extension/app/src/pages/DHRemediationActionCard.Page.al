page 53195 "DH Remediation Action Card"
{
    PageType = Card;
    SourceTable = "DH Remediation Action";
    ApplicationArea = All;
    UsageCategory = None;
    Caption = 'BCSentinel Remediation Action';
    DeleteAllowed = false;

    layout
    {
        area(Content)
        {
            group(General)
            {
                field("Action ID"; Rec."Action ID") { ApplicationArea = All; Editable = false; }
                field(Title; Rec.Title) { ApplicationArea = All; }
                field("Finding Key"; Rec."Finding Key") { ApplicationArea = All; }
                field(Status; Rec.Status) { ApplicationArea = All; }
                field(Priority; Rec.Priority) { ApplicationArea = All; }
                field(Source; Rec.Source) { ApplicationArea = All; }
                field(Description; Rec.Description) { ApplicationArea = All; MultiLine = true; }
                field("Recommendation Ref"; Rec."Recommendation Ref") { ApplicationArea = All; }
            }
            group(Ownership)
            {
                field(Owner; Rec."Owner Principal ID")
                {
                    ApplicationArea = All;
                    ToolTip = 'Select the Business Central user responsible for this remediation action. The user security ID remains the stable identity reference.';
                }
                field("Owner Display Name"; Rec."Owner Display Name")
                {
                    ApplicationArea = All;
                    Editable = false;
                    ToolTip = 'Display name resolved automatically from the selected Business Central user.';
                }
                field("Due At UTC"; Rec."Due At UTC")
                {
                    ApplicationArea = All;
                    ToolTip = 'Due date for this action. Changes are written to the remediation audit trail.';
                }
                field("Blocked Reason"; Rec."Blocked Reason")
                {
                    ApplicationArea = All;
                    MultiLine = true;
                    ToolTip = 'Explain why the action is blocked. Changes are written to the remediation audit trail.';
                }
                field("Completion Note"; Rec."Completion Note")
                {
                    ApplicationArea = All;
                    MultiLine = true;
                    ToolTip = 'Record completion context or evidence. Changes are written to the remediation audit trail.';
                }
            }
            group(Validation)
            {
                field("Validation Result Ref"; Rec."Validation Result Ref") { ApplicationArea = All; ToolTip = 'Links evidence only. A validation result does not automatically change the remediation status.'; }
            }
            group(AuditMetadata)
            {
                field("Tenant ID"; Rec."Tenant ID") { ApplicationArea = All; }
                field("Company ID"; Rec."Company ID") { ApplicationArea = All; }
                field("Created At UTC"; Rec."Created At UTC") { ApplicationArea = All; }
                field("Updated At UTC"; Rec."Updated At UTC") { ApplicationArea = All; }
                field("Started At UTC"; Rec."Started At UTC") { ApplicationArea = All; }
                field("Completed At UTC"; Rec."Completed At UTC") { ApplicationArea = All; }
                field("Cancelled At UTC"; Rec."Cancelled At UTC") { ApplicationArea = All; }
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
