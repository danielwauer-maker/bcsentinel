pageextension 53159 "DH Vend Card Ext" extends "Vendor Card"
{
    layout
    {
        addlast(FactBoxes)
        {
            part(DHExceptions; "DH Excp. FactBox")
            {
                ApplicationArea = All;
                SubPageLink = "Table ID" = const(23), "Record SystemId" = field(SystemId), Active = const(true);
            }
            part(DHActivity; "DH Action Log FB")
            {
                ApplicationArea = All;
                SubPageLink = "Table ID" = const(23), "Record SystemId" = field(SystemId);
            }
        }
    }

    actions
    {
        addlast(Processing)
        {
            action(DHOpenExceptions)
            {
                Caption = 'DH Exceptions';
                ApplicationArea = All;
                Image = View;
                ToolTip = 'Opens active BCSentinel exceptions for this vendor.';
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
