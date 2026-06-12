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
                    ToolTip = 'Specifies Item No..';
                    Editable = false;
                }
                field(Description; Rec.Description)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Description.';
                    Editable = false;
                }
                field("Unit Price"; Rec."Unit Price")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Unit Price.';
                }
                field("Unit Cost"; Rec."Unit Cost")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Unit Cost.';
                    Editable = false;
                }
                field(Inventory; Rec.Inventory)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Inventory.';
                    Editable = false;
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
                ToolTip = 'Runs Exclude from Analysis.';
                ApplicationArea = All;
                Image = Cancel;

                trigger OnAction()
                var
                    ExceptionMgt: Codeunit "DH Exception Mgt.";
                begin
                    ExceptionMgt.AddItemException(Rec, 'ITEMS_WITHOUT_UNIT_PRICE', StrSubstNo('Manually excluded from ITEMS_WITHOUT_UNIT_PRICE.', 'ITEMS_WITHOUT_UNIT_PRICE'));
                    CurrPage.Update(false);
                end;
            }
            action(MarkCorrected)
            {
                Caption = 'Mark as Corrected';
                ToolTip = 'Runs Mark as Corrected.';
                ApplicationArea = All;
                Image = EditLines;

                trigger OnAction()
                var
                    ExceptionMgt: Codeunit "DH Exception Mgt.";
                begin
                    ExceptionMgt.MarkItemCorrected(Rec, 'ITEMS_WITHOUT_UNIT_PRICE', 'Datensatz manuell als korrigiert markiert.');
                    CurrPage.Update(false);
                end;
            }

            action(OpenItemCard)
            {
                Caption = 'Open List';
                ToolTip = 'Runs Open List.';
                ApplicationArea = All;
                Image = Card;

                trigger OnAction()
                begin
                    Page.Run(Page::"Item Card", Rec);
                end;
            }
        }
    }
}

