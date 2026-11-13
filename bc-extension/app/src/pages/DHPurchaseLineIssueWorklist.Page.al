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
                    ToolTip = 'Opens the original purchase order for the affected line.';
                    DrillDown = true;

                    trigger OnDrillDown()
                    begin
                        OpenPurchaseOrder();
                    end;
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
                    AutoFormatType = 1;
                    AutoFormatExpression = GetLocalCurrencyCode();
                    DecimalPlaces = 2 : 2;
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
            action(OpenDocument)
            {
                Caption = 'Correct Data';
                ApplicationArea = All;
                Image = EditLines;
                Promoted = true;
                PromotedCategory = Process;
                ToolTip = 'Opens the original purchase order for the selected finding line.';

                trigger OnAction()
                begin
                    OpenPurchaseOrder();
                end;
            }
            action(ExcludeFinding)
            {
                Caption = 'Exclude from Analysis';
                ApplicationArea = All;
                Image = Cancel;
                Promoted = true;
                PromotedCategory = Process;
                ToolTip = 'Creates a persistent issue-specific exclusion for this purchase line.';

                trigger OnAction()
                var
                    Remediation: Codeunit "DH Generic Remediation";
                begin
                    EnsureIssueContext();
                    Remediation.PromptExclude(Database::"Purchase Line", Rec.SystemId, BuildRecordNo(), BuildRecordCaption());
                end;
            }
            action(MarkIssueCorrected)
            {
                Caption = 'Mark as Corrected';
                ApplicationArea = All;
                Image = Approve;
                Promoted = true;
                PromotedCategory = Process;
                ToolTip = 'Records the correction for this purchase line and its exact finding code; future scans still evaluate BC data.';

                trigger OnAction()
                var
                    Remediation: Codeunit "DH Generic Remediation";
                begin
                    EnsureIssueContext();
                    Remediation.MarkCorrected(Database::"Purchase Line", Rec.SystemId, BuildRecordNo(), BuildRecordCaption());
                end;
            }
            action(OpenCorrectionHistory)
            {
                Caption = 'Open Correction History';
                ApplicationArea = All;
                Image = History;

                trigger OnAction()
                var
                    Remediation: Codeunit "DH Generic Remediation";
                begin
                    EnsureIssueContext();
                    Remediation.OpenHistory(Database::"Purchase Line", Rec.SystemId, CurrentIssueCode);
                end;
            }
        }
    }

    var
        CurrentIssueCode: Code[50];
        IssueContextMissingErr: Label 'Open this purchase line from a BCSentinel finding to provide the exact issue code.';
        PurchaseDocumentNotFoundErr: Label 'Purchase order %1 was not found.', Comment = '%1 = order number';

    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Access Guard";
    begin
        AccessGuard.EnsureIssuesAccess();
        EnsureIssueContext();
        ApplyIssueFilter();
    end;

    procedure SetIssueCode(IssueCode: Code[50])
    begin
        CurrentIssueCode := IssueCode;
    end;

    local procedure EnsureIssueContext()
    var
        Context: Codeunit "DH Remediation Context";
    begin
        if CurrentIssueCode = '' then
            Error(IssueContextMissingErr);
        Context.SetIssueCode(CurrentIssueCode);
    end;

    local procedure BuildRecordNo(): Text
    begin
        exit(Rec."Document No.");
    end;

    local procedure BuildRecordCaption(): Text
    begin
        exit(StrSubstNo('%1 / line %2: %3', Rec."Document No.", Rec."Line No.", Rec.Description));
    end;

    local procedure OpenPurchaseOrder()
    var
        PurchaseHeader: Record "Purchase Header";
    begin
        EnsureIssueContext();
        if not PurchaseHeader.Get(Rec."Document Type", Rec."Document No.") then
            Error(PurchaseDocumentNotFoundErr, Rec."Document No.");
        Page.Run(Page::"Purchase Order", PurchaseHeader);
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

    local procedure GetLocalCurrencyCode(): Text
    var
        CurrencyMgt: Codeunit "DH Currency Mgt.";
    begin
        exit(CurrencyMgt.GetLocalCurrencyCode());
    end;
}
