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
                }
                field(Description; Rec.Description)
                {
                    ApplicationArea = All;
                }
                field(Inventory; Rec.Inventory)
                {
                    ApplicationArea = All;
                }
                field(Blocked; Rec.Blocked)
                {
                    ApplicationArea = All;
                }
                field("Unit Cost"; Rec."Unit Cost")
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
                    ExceptionMgt.AddItemException(Rec, 'BLOCKED_ITEMS_WITH_INVENTORY', StrSubstNo('Manually excluded from BLOCKED_ITEMS_WITH_INVENTORY.', 'BLOCKED_ITEMS_WITH_INVENTORY'));
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
                    ExceptionMgt.MarkItemCorrected(Rec, 'BLOCKED_ITEMS_WITH_INVENTORY', 'Datensatz manuell als korrigiert markiert.');
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
        }
    }
}
