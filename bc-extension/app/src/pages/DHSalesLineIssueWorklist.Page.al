page 53139 "DH Sales Line Issue Worklist"
{
    PageType = List;
    SourceTable = "Sales Line";
    ApplicationArea = All;
    UsageCategory = None;
    Caption = 'DH Sales Line Issue Worklist';
    Editable = false;

    layout
    {
        area(Content)
        {
            repeater(Lines)
            {
                field("Document Type"; Rec."Document Type")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Document Type.';
                }
                field("Document No."; Rec."Document No.")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Document No.';
                }
                field("Line No."; Rec."Line No.")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Line No.';
                }
                field(Type; Rec.Type)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Type.';
                }
                field("No."; Rec."No.")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies No.';
                }
                field(Description; Rec.Description)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Description.';
                }
                field(Quantity; Rec.Quantity)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Quantity.';
                }
                field("Unit Price"; Rec."Unit Price")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Unit Price.';
                }
                field("Shipment Date"; Rec."Shipment Date")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Shipment Date.';
                }
                field("Outstanding Quantity"; Rec."Outstanding Quantity")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Outstanding Quantity.';
                }
                field("Quantity Shipped"; Rec."Quantity Shipped")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Quantity Shipped.';
                }
                field("Quantity Invoiced"; Rec."Quantity Invoiced")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Quantity Invoiced.';
                }
                field("Line Discount %"; Rec."Line Discount %")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Line Discount %.';
                }
                field("Location Code"; Rec."Location Code")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Location Code.';
                }
                field("Shortcut Dimension 1 Code"; Rec."Shortcut Dimension 1 Code")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Shortcut Dimension 1 Code.';
                }
                field("Shortcut Dimension 2 Code"; Rec."Shortcut Dimension 2 Code")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Shortcut Dimension 2 Code.';
                }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(MarkIssueCorrected)
            {
                Caption = 'Mark as Corrected';
                ToolTip = 'Runs Mark as Corrected.';
                ApplicationArea = All;
                Image = EditLines;

                trigger OnAction()
                begin
                    MarkLinkedMasterRecordCorrected();
                end;
            }

            action(OpenDocument)
            {
                Caption = 'Correct Data';
                ToolTip = 'Runs Correct Data.';
                ApplicationArea = All;
                Image = EditLines;

                trigger OnAction()
                var
                    SalesHeader: Record "Sales Header";
                begin
                    if SalesHeader.Get(Rec."Document Type", Rec."Document No.") then
                        Page.Run(Page::"Sales Order", SalesHeader);
                end;
            }
        }
    }

    var
        CurrentIssueCode: Code[50];

    trigger OnOpenPage()
    begin
        ApplyIssueFilter();
    end;

    procedure SetIssueCode(IssueCode: Code[50])
    begin
        CurrentIssueCode := IssueCode;
    end;

    local procedure ApplyIssueFilter()
    begin
        Rec.FilterGroup(2);
        Rec.SetRange("Document Type", Rec."Document Type"::Order);

        case CurrentIssueCode of
            'SALES_LINES_ZERO_QUANTITY':
                Rec.SetRange(Quantity, 0);
            'SALES_LINES_ZERO_PRICE':
                Rec.SetRange("Unit Price", 0);
            'SALES_LINES_MISSING_NO':
                Rec.SetRange("No.", '');
            'SALES_LINES_MISSING_DIMENSIONS':
                begin
                    Rec.SetRange("Shortcut Dimension 1 Code", '');
                    Rec.SetRange("Shortcut Dimension 2 Code", '');
                end;
            'SALES_LINES_DISCOUNT_OVER_25':
                Rec.SetFilter("Line Discount %", '>%1', 25);
            'SALES_LINES_DISCOUNT_OVER_50':
                Rec.SetFilter("Line Discount %", '>%1', 50);
            'SALES_LINES_SHIPPED_NOT_INVOICED':
                Rec.SetFilter("Quantity Shipped", '>%1', 0);
            'SALES_LINES_OUTSTANDING_PAST_SHIPMENT_DATE':
                begin
                    Rec.SetFilter("Outstanding Quantity", '>%1', 0);
                    Rec.SetFilter("Shipment Date", '<>%1&<%2', 0D, Today);
                end;
            'SALES_LINES_MISSING_DESCRIPTION':
                Rec.SetRange(Description, '');
            'SALES_LINES_MISSING_LOCATION':
                Rec.SetRange("Location Code", '');
            'SALES_LINES_WITH_BLOCKED_ITEMS':
                MarkBlockedItemLines();
            'SALES_LINES_PRICE_BELOW_UNIT_COST':
                MarkBelowUnitCostLines();
        end;

        Rec.FilterGroup(0);
    end;


    local procedure MarkBlockedItemLines()
    var
        Item: Record Item;
    begin
        Rec.SetRange(Type, Rec.Type::Item);
        Rec.MarkedOnly(false);
        if Rec.FindSet() then
            repeat
                if (Rec."No." <> '') and Item.Get(Rec."No.") then
                    if Item.Blocked then
                        Rec.Mark(true);
            until Rec.Next() = 0;
        Rec.MarkedOnly(true);
    end;

    local procedure MarkBelowUnitCostLines()
    var
        Item: Record Item;
    begin
        Rec.SetRange(Type, Rec.Type::Item);
        Rec.MarkedOnly(false);
        if Rec.FindSet() then
            repeat
                if (Rec."No." <> '') and Item.Get(Rec."No.") then
                    if (Rec."Unit Price" > 0) and (Item."Unit Cost" > 0) and (Rec."Unit Price" < Item."Unit Cost") then
                        Rec.Mark(true);
            until Rec.Next() = 0;
        Rec.MarkedOnly(true);
    end;

    local procedure MarkLinkedMasterRecordCorrected()
    var
        Item: Record Item;
        ExceptionMgt: Codeunit "DH Exception Mgt.";
    begin
        if (Rec.Type = Rec.Type::Item) and (Rec."No." <> '') and Item.Get(Rec."No.") then begin
            ExceptionMgt.MarkItemCorrected(Item, CurrentIssueCode, 'Correction documented from the sales line worklist.');
            exit;
        end;

        Message('The correction was not logged because no master data record could be assigned.');
    end;

}

