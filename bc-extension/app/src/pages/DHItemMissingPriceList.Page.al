page 53148 "DH Item Missing Price List"
{
    PageType = List;
    SourceTable = Item;
    ApplicationArea = All;
    UsageCategory = None;
    Caption = 'DH Item Missing Price List';
    SourceTableView = where("Unit Price" = const(0));

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
                    Editable = false;

                    trigger OnDrillDown()
                    begin
                        Page.Run(Page::"Item Card", Rec);
                    end;
                }
                field(Description; Rec.Description)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the item description.';
                    Editable = false;
                }
                field("Unit Price"; Rec."Unit Price")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the unit price.';
                    AutoFormatType = 1;
                    AutoFormatExpression = GetLocalCurrencyCode();
                    DecimalPlaces = 2 : 2;
                }
                field("Unit Cost"; Rec."Unit Cost")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the unit cost.';
                    Editable = false;
                    AutoFormatType = 1;
                    AutoFormatExpression = GetLocalCurrencyCode();
                    DecimalPlaces = 2 : 2;
                }
                field(Inventory; Rec.Inventory)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the inventory quantity.';
                    Editable = false;
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
                    ExceptionMgt.PromptAddItemException(Rec, 'ITEMS_WITHOUT_UNIT_PRICE');
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
                    ExceptionMgt.MarkItemCorrected(Rec, 'ITEMS_WITHOUT_UNIT_PRICE', 'Datensatz manuell als korrigiert markiert.');
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
