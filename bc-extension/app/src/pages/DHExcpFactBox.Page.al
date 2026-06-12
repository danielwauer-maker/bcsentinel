page 53154 "DH Excp. FactBox"
{
    PageType = ListPart;
    SourceTable = "DH Issue Exception";
    ApplicationArea = All;
    Caption = 'DH Exceptions';
    Editable = false;

    layout
    {
        area(Content)
        {
            repeater(General)
            {
                field("Issue Code"; Rec."Issue Code")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Issue Code.';
                }
                field(Reason; Rec.Reason)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Reason.';
                }
                field("Created By User"; Rec."Created By User")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Created By User.';
                }
            }
        }
    }
}

