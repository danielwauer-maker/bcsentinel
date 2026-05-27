pageextension 53161 "DH Cust List Ext" extends "Customer List"
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
                trigger OnAction()
                var
                    ExceptionMgt: Codeunit "DH Exception Mgt.";
                begin
                    ExceptionMgt.OpenCustomerExceptions(Rec);
                end;
            }
        }
    }
}
