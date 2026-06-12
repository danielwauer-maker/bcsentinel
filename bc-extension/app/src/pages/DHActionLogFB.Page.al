page 53155 "DH Action Log FB"
{
    PageType = ListPart;
    SourceTable = "DH Issue Action Log";
    ApplicationArea = All;
    Caption = 'DH Activity';
    Editable = false;
    SourceTableView = sorting("Table ID", "Record SystemId", "Action At") order(descending);

    layout
    {
        area(Content)
        {
            repeater(General)
            {
                field("Action At"; Rec."Action At")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Action At.';
                }
                field("Action Type"; Rec."Action Type")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Action Type.';
                }
                field("Issue Code"; Rec."Issue Code")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Issue Code.';
                }
                field("Action User"; Rec."Action User")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Action User.';
                }
            }
        }
    }
}

