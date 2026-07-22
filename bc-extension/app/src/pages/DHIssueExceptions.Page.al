page 53153 "DH Issue Exceptions"
{
    PageType = List;
    SourceTable = "DH Issue Exception";
    ApplicationArea = All;
    UsageCategory = Lists;
    Caption = 'DH Exceptions';
    InsertAllowed = false;
    ModifyAllowed = false;
    DeleteAllowed = false;

    layout
    {
        area(Content)
        {
            group(EmptyState)
            {
                ShowCaption = false;
                Visible = EmptyStateVisible;
                field(EmptyStateText; EmptyStateTxt)
                {
                    ApplicationArea = All;
                    ShowCaption = false;
                    Editable = false;
                    MultiLine = true;
                    ToolTip = 'Explains that no DH exceptions match the current view.';
                }
            }
            repeater(General)
            {
                field(Active; Rec.Active) { ApplicationArea = All; ToolTip = 'Specifies whether the exception currently excludes the record from score calculation.'; }
                field(RecordType; RecordTypeTxt) { ApplicationArea = All; Caption = 'Record Type'; Editable = false; ToolTip = 'Specifies whether the exception belongs to a customer, vendor, or item.'; }
                field("Record No."; Rec."Record No.") { ApplicationArea = All; ToolTip = 'Specifies the number of the affected record.'; }
                field("Record Caption"; Rec."Record Caption") { ApplicationArea = All; ToolTip = 'Specifies the caption of the affected record.'; }
                field("Issue Code"; Rec."Issue Code") { ApplicationArea = All; ToolTip = 'Specifies the check to which the exception applies.'; }
                field(Reason; Rec.Reason) { ApplicationArea = All; ToolTip = 'Specifies why the record is excluded from this check.'; }
                field("Created By User"; Rec."Created By User") { ApplicationArea = All; ToolTip = 'Specifies who created the exception.'; }
                field("Created At"; Rec."Created At") { ApplicationArea = All; ToolTip = 'Specifies when the exception was created.'; }
                field("Deactivated By User"; Rec."Deactivated By User") { ApplicationArea = All; ToolTip = 'Specifies who last deactivated the exception.'; }
                field("Deactivated At"; Rec."Deactivated At") { ApplicationArea = All; ToolTip = 'Specifies when the exception was last deactivated.'; }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(CreateException)
            {
                Caption = 'Create Exception';
                ToolTip = 'Creates an exception for the current customer, vendor, or item and check.';
                ApplicationArea = All;
                Image = New;
                AccessByPermission = tabledata "DH Issue Exception" = I;
                Visible = ContextTableId <> 0;
                trigger OnAction()
                begin
                    RunExceptionDialog(false);
                end;
            }
            action(ActivateException)
            {
                Caption = 'Activate';
                ToolTip = 'Reactivates the selected exception and excludes the record from the next score calculation.';
                ApplicationArea = All;
                Image = Approve;
                AccessByPermission = tabledata "DH Issue Exception" = M;
                Enabled = not Rec.Active;
                trigger OnAction()
                begin
                    RunExceptionDialog(true);
                end;
            }
            action(DeactivateException)
            {
                Caption = 'Deactivate';
                ToolTip = 'Deactivates the selected exception and includes the record in the next score calculation.';
                ApplicationArea = All;
                Image = Cancel;
                AccessByPermission = tabledata "DH Issue Exception" = M;
                Enabled = Rec.Active;
                trigger OnAction()
                var
                    ExceptionMgt: Codeunit "DH Exception Mgt.";
                begin
                    if not Confirm(DeactivateConfirmQst, false, Rec."Record No.", Rec."Issue Code") then
                        exit;
                    ExceptionMgt.DeactivateExceptionEntry(Rec);
                    CurrPage.Update(false);
                end;
            }
            action(OpenRecord)
            {
                Caption = 'Open Record';
                ToolTip = 'Opens the affected Business Central record.';
                ApplicationArea = All;
                Image = View;
                trigger OnAction()
                var
                    Customer: Record Customer;
                    Vendor: Record Vendor;
                    Item: Record Item;
                begin
                    case Rec."Table ID" of
                        Database::Customer:
                            if Customer.GetBySystemId(Rec."Record SystemId") then begin
                                Page.Run(Page::"Customer Card", Customer);
                                exit;
                            end;
                        Database::Vendor:
                            if Vendor.GetBySystemId(Rec."Record SystemId") then begin
                                Page.Run(Page::"Vendor Card", Vendor);
                                exit;
                            end;
                        Database::Item:
                            if Item.GetBySystemId(Rec."Record SystemId") then begin
                                Page.Run(Page::"Item Card", Item);
                                exit;
                            end;
                    end;
                    Error(RecordNotFoundErr);
                end;
            }
            action(ShowHistory)
            {
                Caption = 'Show History';
                ToolTip = 'Shows the activation, reactivation, deactivation, and correction history for the selected record and check.';
                ApplicationArea = All;
                Image = History;
                trigger OnAction()
                var
                    ActionLog: Record "DH Issue Action Log";
                begin
                    ActionLog.SetRange("Table ID", Rec."Table ID");
                    ActionLog.SetRange("Record SystemId", Rec."Record SystemId");
                    ActionLog.SetRange("Issue Code", Rec."Issue Code");
                    Page.Run(Page::"DH Issue Action Log", ActionLog);
                end;
            }
        }
        area(Navigation)
        {
            group(Views)
            {
                Caption = 'Views';
                action(ShowActive)
                {
                    Caption = 'Active'; ApplicationArea = All;
                    trigger OnAction()
                    begin
                        Rec.SetRange(Active, true);
                        CurrPage.Update(false);
                    end;
                }
                action(ShowInactive)
                {
                    Caption = 'Inactive'; ApplicationArea = All;
                    trigger OnAction()
                    begin
                        Rec.SetRange(Active, false);
                        CurrPage.Update(false);
                    end;
                }
                action(ShowAll)
                {
                    Caption = 'All'; ApplicationArea = All;
                    trigger OnAction()
                    begin
                        Rec.SetRange(Active);
                        Rec.SetRange("Table ID");
                        CurrPage.Update(false);
                    end;
                }
                action(ShowCustomers)
                {
                    Caption = 'Customers'; ApplicationArea = All;
                    trigger OnAction()
                    begin
                        Rec.SetRange("Table ID", Database::Customer);
                        CurrPage.Update(false);
                    end;
                }
                action(ShowVendors)
                {
                    Caption = 'Vendors'; ApplicationArea = All;
                    trigger OnAction()
                    begin
                        Rec.SetRange("Table ID", Database::Vendor);
                        CurrPage.Update(false);
                    end;
                }
                action(ShowItems)
                {
                    Caption = 'Items'; ApplicationArea = All;
                    trigger OnAction()
                    begin
                        Rec.SetRange("Table ID", Database::Item);
                        CurrPage.Update(false);
                    end;
                }
            }
        }
    }

    trigger OnOpenPage()
    begin
        if ContextTableId <> 0 then begin
            Rec.SetRange("Table ID", ContextTableId);
            Rec.SetRange("Record SystemId", ContextSystemId);
        end;
        UpdateEmptyState();
    end;

    trigger OnAfterGetRecord()
    begin
        RecordTypeTxt := GetRecordType(Rec."Table ID");
        EmptyStateVisible := false;
    end;

    procedure SetContext(TableId: Integer; RecordSystemId: Guid; RecordNo: Code[20]; RecordCaption: Text[100])
    begin
        ContextTableId := TableId;
        ContextSystemId := RecordSystemId;
        ContextRecordNo := RecordNo;
        ContextRecordCaption := RecordCaption;
    end;

    local procedure RunExceptionDialog(IsReactivation: Boolean)
    var
        Customer: Record Customer;
        Vendor: Record Vendor;
        Item: Record Item;
        ExceptionMgt: Codeunit "DH Exception Mgt.";
        ExceptionDialog: Page "DH Exception Dialog";
        IssueCode: Code[50];
        Reason: Text[250];
    begin
        if IsReactivation then
            ExceptionDialog.SetContext(Rec."Record No.", Rec."Record Caption", Rec."Issue Code", Rec.Reason)
        else
            ExceptionDialog.SetContext(ContextRecordNo, ContextRecordCaption, '', '');
        if ExceptionDialog.RunModal() <> Action::OK then
            exit;
        ExceptionDialog.GetValues(IssueCode, Reason);
        if IsReactivation then
            ExceptionMgt.ReactivateExceptionEntry(Rec, Reason)
        else
            case ContextTableId of
                Database::Customer:
                    begin
                        Customer.GetBySystemId(ContextSystemId);
                        ExceptionMgt.AddCustomerException(Customer, IssueCode, Reason);
                    end;
                Database::Vendor:
                    begin
                        Vendor.GetBySystemId(ContextSystemId);
                        ExceptionMgt.AddVendorException(Vendor, IssueCode, Reason);
                    end;
                Database::Item:
                    begin
                        Item.GetBySystemId(ContextSystemId);
                        ExceptionMgt.AddItemException(Item, IssueCode, Reason);
                    end;
                else
                    Error(UnsupportedRecordTypeErr);
            end;
        CurrPage.Update(false);
    end;

    local procedure UpdateEmptyState()
    begin
        EmptyStateTxt := NoExceptionsLbl;
        EmptyStateVisible := Rec.IsEmpty();
    end;

    local procedure GetRecordType(TableId: Integer): Text[30]
    begin
        case TableId of
            Database::Customer: exit(CustomerLbl);
            Database::Vendor: exit(VendorLbl);
            Database::Item: exit(ItemLbl);
        end;
        exit(StrSubstNo(TableLbl, TableId));
    end;

    var
        ContextTableId: Integer;
        ContextSystemId: Guid;
        ContextRecordNo: Code[20];
        ContextRecordCaption: Text[100];
        RecordTypeTxt: Text[30];
        EmptyStateTxt: Text[150];
        EmptyStateVisible: Boolean;
        NoExceptionsLbl: Label 'No DH exceptions match the current view.';
        CustomerLbl: Label 'Customer';
        VendorLbl: Label 'Vendor';
        ItemLbl: Label 'Item';
        TableLbl: Label 'Table %1', Comment = '%1 = table ID';
        DeactivateConfirmQst: Label 'Deactivate the DH exception for record %1 and issue %2? The record will be included in the next score calculation.', Comment = '%1 = record number, %2 = issue code';
        RecordNotFoundErr: Label 'The affected record no longer exists or cannot be opened.';
        UnsupportedRecordTypeErr: Label 'Exceptions can only be created here for customers, vendors, and items.';
}
