pageextension 53163 "DH Item List Ext" extends "Item List"
{
    actions
    {
        addlast(Processing)
        {
            action(DHOpenExceptions)
            {
                Caption = 'DH Exceptions';
                ApplicationArea = All;
                Image = View;
                ToolTip = 'Opens active BCSentinel exceptions for the selected item.';
                trigger OnAction()
                var
                    ExceptionMgt: Codeunit "DH Exception Mgt.";
                begin
                    ExceptionMgt.OpenItemExceptions(Rec);
                end;
            }
        }
    }
}
