page 53138 "DH Blocked Items Inv"
{
    PageType = List;
    SourceTable = Item;
    ApplicationArea = All;
    UsageCategory = None;
    Caption = 'DH Blocked Items With Inventory';
    SourceTableView = where(Blocked = const(true), Inventory = filter(<> 0));
    Editable = false;

    layout
    {
        area(Content)
        {
            repeater(General)
            {
                field("No."; Rec."No.")
                {
                    ApplicationArea = All;
                    Caption = 'Item No.';
                    ToolTip = 'Opens the original item card for the selected record.';

                    trigger OnDrillDown()
                    begin
                        Page.Run(Page::"Item Card", Rec);
                    end;
                }
                field(Description; Rec.Description)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the item description.';
                }
                field(Inventory; Rec.Inventory)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the inventory quantity.';
                }
                field(Blocked; Rec.Blocked)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies whether the item is blocked.';
                }
                field("Unit Cost"; Rec."Unit Cost")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the unit cost.';
                    AutoFormatType = 1;
                    AutoFormatExpression = GetLocalCurrencyCode();
                    DecimalPlaces = 2 : 2;
                }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(OpenItemCard)
            {
                Caption = 'Open Item Card';
                ToolTip = 'Opens the original Business Central item card for the selected record.';
                ApplicationArea = All;
                Image = Card;
                Promoted = true;
                PromotedCategory = Process;

                trigger OnAction()
                begin
                    Page.Run(Page::"Item Card", Rec);
                end;
            }
            action(ExcludeFromIssue)
            {
                Caption = 'Exclude from Analysis';
                ToolTip = 'Excludes the selected item from this BCSentinel check without requiring an issue code.';
                ApplicationArea = All;
                Image = Cancel;
                Promoted = true;
                PromotedCategory = Process;

                trigger OnAction()
                var
                    ExceptionMgt: Codeunit "DH Exception Mgt.";
                begin
                    ExceptionMgt.PromptAddItemException(Rec, 'BLOCKED_ITEMS_WITH_INVENTORY');
                    CurrPage.Update(false);
                end;
            }
            action(MarkCorrected)
            {
                Caption = 'Mark as Corrected';
                ToolTip = 'Documents the selected item as corrected for this BCSentinel check.';
                ApplicationArea = All;
                Image = Approve;
                Promoted = true;
                PromotedCategory = Process;

                trigger OnAction()
                var
                    ExceptionMgt: Codeunit "DH Exception Mgt.";
                begin
                    ExceptionMgt.MarkItemCorrected(Rec, 'BLOCKED_ITEMS_WITH_INVENTORY', 'Datensatz manuell als korrigiert markiert.');
                    CurrPage.Update(false);
                end;
            }
        }
    }

    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Access Guard";
    begin
        AccessGuard.EnsureIssuesAccess();
    end;

    local procedure GetLocalCurrencyCode(): Text
    var
        CurrencyMgt: Codeunit "DH Currency Mgt.";
    begin
        exit(CurrencyMgt.GetLocalCurrencyCode());
    end;
}
