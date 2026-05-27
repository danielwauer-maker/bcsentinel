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
                }
                field(Description; Rec.Description)
                {
                    ApplicationArea = All;
                }
                field("Location Filter"; Rec."Location Filter")
                {
                    ApplicationArea = All;
                    ToolTip = 'Optional FlowFilter to limit the view to one location.';
                }
                field(Inventory; Rec.Inventory)
                {
                    ApplicationArea = All;
                }
                field(Blocked; Rec.Blocked)
                {
                    ApplicationArea = All;
                }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(ExcludeFromIssue)
            {
                Caption = 'Exclude from Analysis';
                ApplicationArea = All;
                Image = Cancel;

                trigger OnAction()
                var
                    ExceptionMgt: Codeunit "DH Exception Mgt.";
                begin
                    ExceptionMgt.AddItemException(Rec, 'ITEMS_NEGATIVE_INVENTORY', StrSubstNo('Manually excluded from ITEMS_NEGATIVE_INVENTORY.', 'ITEMS_NEGATIVE_INVENTORY'));
                    CurrPage.Update(false);
                end;
            }
            action(MarkCorrected)
            {
                Caption = 'Mark as Corrected';
                ApplicationArea = All;
                Image = EditLines;

                trigger OnAction()
                var
                    ExceptionMgt: Codeunit "DH Exception Mgt.";
                begin
                    ExceptionMgt.MarkItemCorrected(Rec, 'ITEMS_NEGATIVE_INVENTORY', 'Datensatz manuell als korrigiert markiert.');
                    CurrPage.Update(false);
                end;
            }

            action(OpenItemCard)
            {
                Caption = 'Correct Data';
                ApplicationArea = All;
                Image = EditLines;

                trigger OnAction()
                begin
                    Page.Run(Page::"Item Card", Rec);
                end;
            }
            action(OpenLedgerEntries)
            {
                Caption = 'Show Issue';
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
}
