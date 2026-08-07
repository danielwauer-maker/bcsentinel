pageextension 53163 "DH Item List Ext" extends "Item List"
{
    actions
    {
        addlast(Processing)
        {
            action(DHOpenItemCard)
            {
                Caption = 'Open Item Card';
                ApplicationArea = All;
                Image = Card;
                ToolTip = 'Opens the original Business Central item card for the selected item.';

                trigger OnAction()
                begin
                    Page.Run(Page::"Item Card", Rec);
                end;
            }
            action(DHExcludeFromAnalysis)
            {
                Caption = 'Exclude from Analysis';
                ApplicationArea = All;
                Image = Cancel;
                ToolTip = 'Excludes the selected item from the active BCSentinel finding without requiring a manually entered issue code.';

                trigger OnAction()
                var
                    ExceptionMgt: Codeunit "DH Exception Mgt.";
                    IssueCode: Code[50];
                begin
                    IssueCode := ResolveIssueCodeFromFilters();
                    EnsureRemediationContext(IssueCode);
                    ExceptionMgt.PromptAddItemException(Rec, IssueCode);
                end;
            }
            action(DHMarkCorrected)
            {
                Caption = 'Mark as Corrected';
                ApplicationArea = All;
                Image = Approve;
                ToolTip = 'Documents the selected item as corrected for the active BCSentinel finding.';

                trigger OnAction()
                var
                    ExceptionMgt: Codeunit "DH Exception Mgt.";
                    IssueCode: Code[50];
                begin
                    IssueCode := ResolveIssueCodeFromFilters();
                    EnsureRemediationContext(IssueCode);
                    ExceptionMgt.MarkItemCorrected(Rec, IssueCode, 'Datensatz manuell als korrigiert markiert.');
                end;
            }
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

    local procedure ResolveIssueCodeFromFilters(): Code[50]
    begin
        if Rec.GetFilter(Description) <> '' then
            exit('ITEMS_MISSING_DESCRIPTION');
        if Rec.GetFilter("Item Category Code") <> '' then
            exit('ITEMS_MISSING_CATEGORY');
        if Rec.GetFilter("Base Unit of Measure") <> '' then
            exit('ITEMS_MISSING_BASE_UOM');
        if Rec.GetFilter("Gen. Prod. Posting Group") <> '' then
            exit('ITEMS_MISSING_GEN_PROD_POSTING_GROUP');
        if Rec.GetFilter("Inventory Posting Group") <> '' then
            exit('ITEMS_MISSING_INVENTORY_POSTING_GROUP');
        if Rec.GetFilter("VAT Prod. Posting Group") <> '' then
            exit('ITEMS_MISSING_VAT_PROD_POSTING_GROUP');
        if Rec.GetFilter("Vendor No.") <> '' then
            exit('ITEMS_MISSING_VENDOR_NO');
        if Rec.GetFilter("Shelf No.") <> '' then
            exit('ITEMS_MISSING_SHELF_NO');
        if Rec.GetFilter("Tariff No.") <> '' then
            exit('ITEMS_MISSING_TARIFF_NO');
        if Rec.GetFilter("Standard Cost") <> '' then
            exit('ITEMS_STANDARD_COST_ZERO');
        if Rec.GetFilter("Last Direct Cost") <> '' then
            exit('ITEMS_LAST_DIRECT_COST_ZERO');
        if Rec.GetFilter("Safety Stock Quantity") <> '' then
            exit('ITEMS_SAFETY_STOCK_ZERO');
        if Rec.GetFilter("Reorder Point") <> '' then
            exit('ITEMS_REORDER_POINT_ZERO');
        if Rec.GetFilter("Maximum Inventory") <> '' then
            exit('ITEMS_MAX_INVENTORY_ZERO');
        if Rec.GetFilter("Minimum Order Quantity") <> '' then
            exit('ITEMS_MIN_ORDER_QTY_ZERO');
        if Rec.GetFilter("Order Multiple") <> '' then
            exit('ITEMS_ORDER_MULTIPLE_ZERO');
        if Rec.GetFilter("Gross Weight") <> '' then
            exit('ITEMS_GROSS_WEIGHT_ZERO');
        if Rec.GetFilter("Net Weight") <> '' then
            exit('ITEMS_NET_WEIGHT_ZERO');
        if Rec.GetFilter("Unit Volume") <> '' then
            exit('ITEMS_UNIT_VOLUME_ZERO');
        if Rec.GetFilter("Unit Cost") <> '' then
            exit('ITEMS_WITHOUT_UNIT_COST');
        if Rec.GetFilter("Unit Price") <> '' then
            exit('ITEMS_WITHOUT_UNIT_PRICE');
        if Rec.GetFilter(Blocked) <> '' then
            exit('BLOCKED_ITEMS_WITH_INVENTORY');

        exit('');
    end;

    local procedure EnsureRemediationContext(IssueCode: Code[50])
    begin
        if IssueCode = '' then
            Error(RemediationContextMissingErr);
    end;

    var
        RemediationContextMissingErr: Label 'BCSentinel could not determine the finding context for this standard Business Central list. Open the record from the BCSentinel finding again so the exception or correction can be assigned automatically.';
}
