pageextension 53162 "DH Vend List Ext" extends "Vendor List"
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
                ToolTip = 'Opens active BCSentinel exceptions for the selected vendor.';
                trigger OnAction()
                var
                    ExceptionMgt: Codeunit "DH Exception Mgt.";
                begin
                    ExceptionMgt.OpenVendorExceptions(Rec);
                end;
            }
        }
    }
}
