page 53136 "DH Item Neg. Inventory"
{
    PageType = List;
    SourceTable = Item;
    ApplicationArea = All;
    UsageCategory = None;
    Caption = 'DH Item Negative Inventory List';
    SourceTableView = where(Inventory = filter(< 0));
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
                field("Location Filter"; Rec."Location Filter")
                {
                    ApplicationArea = All;
                    ToolTip = 'Optional FlowFilter to limit the view to one location.';
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
                    ExceptionMgt.PromptAddItemException(Rec, 'ITEMS_NEGATIVE_INVENTORY');
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
                    ExceptionMgt.MarkItemCorrected(Rec, 'ITEMS_NEGATIVE_INVENTORY', 'Datensatz manuell als korrigiert markiert.');
                    CurrPage.Update(false);
                end;
            }
            action(OpenLedgerEntries)
            {
                Caption = 'Show Ledger Entries';
                ToolTip = 'Opens item ledger entries for the selected item.';
                ApplicationArea = All;
                Image = LedgerEntries;

                trigger OnAction()
                var
                    ItemLedgerEntry: Record "Item Ledger Entry";
                begin
                    ItemLedgerEntry.SetRange("Item No.", Rec."No.");
                    Page.Run(Page::"Item Ledger Entries", ItemLedgerEntry);
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
}
