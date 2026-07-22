page 53174 "DH Issue Action Log"
{
    PageType = List;
    SourceTable = "DH Issue Action Log";
    SourceTableView = sorting("Table ID", "Record SystemId", "Action At") order(descending);
    ApplicationArea = All;
    UsageCategory = History;
    Caption = 'DH Exception History';
    InsertAllowed = false;
    ModifyAllowed = false;
    DeleteAllowed = false;

    layout
    {
        area(Content)
        {
            repeater(General)
            {
                field("Action At"; Rec."Action At") { ApplicationArea = All; ToolTip = 'Specifies when the action occurred.'; }
                field("Action Type"; Rec."Action Type") { ApplicationArea = All; ToolTip = 'Specifies EXCLUDED for activation, INCLUDED for deactivation, or CORRECTED for a separately documented correction.'; }
                field("Record No."; Rec."Record No.") { ApplicationArea = All; ToolTip = 'Specifies the affected record.'; }
                field("Record Caption"; Rec."Record Caption") { ApplicationArea = All; ToolTip = 'Specifies the affected record caption.'; }
                field("Issue Code"; Rec."Issue Code") { ApplicationArea = All; ToolTip = 'Specifies the affected check.'; }
                field(Comment; Rec.Comment) { ApplicationArea = All; ToolTip = 'Specifies the reason or comment recorded for the action.'; }
                field("Action User"; Rec."Action User") { ApplicationArea = All; ToolTip = 'Specifies who performed the action.'; }
            }
        }
    }
}
