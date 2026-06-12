page 53144 "DH Purch. Line Worklist"
{
    PageType = List;
    SourceTable = "Purchase Line";
    ApplicationArea = All;
    UsageCategory = None;
    Caption = 'DH Purchase Line Issue Worklist';
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
                field("Direct Unit Cost"; Rec."Direct Unit Cost")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Direct Unit Cost.';
                }
                field("Expected Receipt Date"; Rec."Expected Receipt Date")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Expected Receipt Date.';
                }
                field("Outstanding Quantity"; Rec."Outstanding Quantity")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Outstanding Quantity.';
                }
                field("Quantity Received"; Rec."Quantity Received")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Quantity Received.';
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
                    PurchaseHeader: Record "Purchase Header";
                begin
                    if PurchaseHeader.Get(Rec."Document Type", Rec."Document No.") then
                        Page.Run(Page::"Purchase Order", PurchaseHeader);
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
            'PURCHASE_LINES_ZERO_QUANTITY':
                Rec.SetRange(Quantity, 0);
            'PURCHASE_LINES_ZERO_COST':
                Rec.SetRange("Direct Unit Cost", 0);
            'PURCHASE_LINES_MISSING_NO':
                Rec.SetRange("No.", '');
            'PURCHASE_LINES_MISSING_DIMENSIONS':
                begin
                    Rec.SetRange("Shortcut Dimension 1 Code", '');
                    Rec.SetRange("Shortcut Dimension 2 Code", '');
                end;
            'PURCHASE_LINES_DISCOUNT_OVER_25':
                Rec.SetFilter("Line Discount %", '>%1', 25);
            'PURCHASE_LINES_DISCOUNT_OVER_50':
                Rec.SetFilter("Line Discount %", '>%1', 50);
            'PURCHASE_LINES_RECEIVED_NOT_INVOICED':
                Rec.SetFilter("Quantity Received", '>%1', 0);
            'PURCHASE_LINES_OUTSTANDING_PAST_RECEIPT_DATE':
                begin
                    Rec.SetFilter("Outstanding Quantity", '>%1', 0);
                    Rec.SetFilter("Expected Receipt Date", '<>%1&<%2', 0D, Today);
                end;
            'PURCHASE_LINES_MISSING_DESCRIPTION':
                Rec.SetRange(Description, '');
            'PURCHASE_LINES_MISSING_LOCATION':
                Rec.SetRange("Location Code", '');
            'PURCHASE_LINES_WITH_BLOCKED_ITEMS':
                MarkBlockedItemLines();
            'PURCHASE_LINES_COST_BELOW_LAST_DIRECT_COST':
                MarkBelowLastDirectCostLines();
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

    local procedure MarkBelowLastDirectCostLines()
    var
        Item: Record Item;
    begin
        Rec.SetRange(Type, Rec.Type::Item);
        Rec.MarkedOnly(false);
        if Rec.FindSet() then
            repeat
                if (Rec."No." <> '') and Item.Get(Rec."No.") then
                    if (Rec."Direct Unit Cost" > 0) and (Item."Last Direct Cost" > 0) and (Rec."Direct Unit Cost" < Item."Last Direct Cost") then
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
            ExceptionMgt.MarkItemCorrected(Item, CurrentIssueCode, 'Correction documented from the purchase line worklist.');
            exit;
        end;

        Message('The correction was not logged because no master data record could be assigned.');
    end;

}

