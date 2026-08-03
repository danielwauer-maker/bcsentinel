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
                field(CorrectionStatus; CorrectionStatusTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Korrekturstatus';
                    Editable = false;
                    StyleExpr = CorrectionStatusStyle;
                    ToolTip = 'Zeigt, ob diese konkrete Verkaufszeile für die aktuelle DH-Prüfung als korrigiert dokumentiert wurde.';
                }
                field(CorrectedAt; CorrectedAtValue)
                {
                    ApplicationArea = All;
                    Caption = 'Korrigiert am';
                    Editable = false;
                    ToolTip = 'Zeigt Datum und Uhrzeit der letzten dokumentierten Korrektur.';
                }
                field(CorrectedBy; CorrectedByTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Korrigiert von';
                    Editable = false;
                    ToolTip = 'Zeigt den Benutzer, der die Korrektur dokumentiert hat.';
                }
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
                    AutoFormatType = 1;
                    AutoFormatExpression = GetLocalCurrencyCode();
                    DecimalPlaces = 2 : 2;
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
                Caption = 'Als korrigiert markieren';
                ToolTip = 'Dokumentiert die ausgewählte Verkaufszeile für die aktuelle DH-Prüfung als korrigiert.';
                ApplicationArea = All;
                Image = Approve;
                Promoted = true;
                PromotedCategory = Process;

                trigger OnAction()
                begin
                    MarkCurrentLineCorrected(true);
                end;
            }

            action(OpenDocument)
            {
                Caption = 'Daten korrigieren';
                ToolTip = 'Öffnet den zugehörigen Verkaufsauftrag. Nach dem Schließen kann die ausgewählte Zeile direkt als korrigiert dokumentiert werden.';
                ApplicationArea = All;
                Image = EditLines;
                Promoted = true;
                PromotedCategory = Process;

                trigger OnAction()
                var
                    SalesHeader: Record "Sales Header";
                begin
                    if not SalesHeader.Get(Rec."Document Type", Rec."Document No.") then
                        Error(SalesDocumentNotFoundErr, Rec."Document No.");

                    Page.RunModal(Page::"Sales Order", SalesHeader);

                    if Confirm(MarkAfterEditingQst, false, Rec."Document No.", Rec."Line No.") then
                        MarkCurrentLineCorrected(false)
                    else begin
                        LoadCorrectionStatus();
                        CurrPage.Update(false);
                    end;
                end;
            }

            action(OpenCorrectionHistory)
            {
                Caption = 'Korrekturhistorie öffnen';
                ToolTip = 'Öffnet alle dokumentierten DH-Aktionen für die ausgewählte Verkaufszeile und die aktuelle Prüfung.';
                ApplicationArea = All;
                Image = History;

                trigger OnAction()
                var
                    IssueActionLog: Record "DH Issue Action Log";
                begin
                    EnsureIssueContext();
                    IssueActionLog.SetRange("Table ID", Database::"Sales Line");
                    IssueActionLog.SetRange("Record SystemId", Rec.SystemId);
                    IssueActionLog.SetRange("Issue Code", CurrentIssueCode);
                    Page.Run(Page::"DH Issue Action Log", IssueActionLog);
                end;
            }
        }
    }

    var
        CurrentIssueCode: Code[50];
        CorrectionStatusTxt: Text[30];
        CorrectionStatusStyle: Text[30];
        CorrectedAtValue: DateTime;
        CorrectedByTxt: Text[50];
        CorrectedLbl: Label 'Korrigiert';
        OpenLbl: Label 'Offen';
        MarkCorrectionQst: Label 'Soll die Verkaufszeile %1 / %2 für die Prüfung %3 als korrigiert dokumentiert werden?', Comment = '%1 = document no., %2 = line no., %3 = issue code';
        MarkAfterEditingQst: Label 'Wurden die Daten im Auftrag %1 für Zeile %2 korrigiert und soll die Korrektur jetzt dokumentiert werden?', Comment = '%1 = document no., %2 = line no.';
        CorrectionRecordedMsg: Label 'Die Verkaufszeile %1 / %2 wurde als korrigiert dokumentiert. Der Eintrag ist in der Korrekturhistorie sichtbar.', Comment = '%1 = document no., %2 = line no.';
        CorrectionAlreadyRecordedMsg: Label 'Diese Verkaufszeile ist für die aktuelle Prüfung bereits als korrigiert dokumentiert.';
        CorrectionCommentLbl: Label 'Korrektur der Verkaufszeile aus der DH-Problemliste dokumentiert.';
        IssueContextMissingErr: Label 'Für diese Problemliste wurde kein DH-Prüfcode übergeben. Die Korrektur kann nicht revisionssicher dokumentiert werden.';
        SalesDocumentNotFoundErr: Label 'Der Verkaufsauftrag %1 wurde nicht gefunden.', Comment = '%1 = document no.';

    trigger OnOpenPage()
    var
        AccessGuard: Codeunit "DH Access Guard";
    begin
        AccessGuard.EnsureIssuesAccess();
        ApplyIssueFilter();
    end;

    trigger OnAfterGetRecord()
    begin
        LoadCorrectionStatus();
    end;

    trigger OnAfterGetCurrRecord()
    begin
        LoadCorrectionStatus();
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

    local procedure MarkCurrentLineCorrected(AskForConfirmation: Boolean)
    var
        IssueActionLog: Record "DH Issue Action Log";
    begin
        EnsureIssueContext();

        if IsCurrentLineCorrected(IssueActionLog) then begin
            Message(CorrectionAlreadyRecordedMsg);
            LoadCorrectionStatus();
            CurrPage.Update(false);
            exit;
        end;

        if AskForConfirmation then
            if not Confirm(MarkCorrectionQst, false, Rec."Document No.", Rec."Line No.", CurrentIssueCode) then
                exit;

        IssueActionLog.Init();
        IssueActionLog."Table ID" := Database::"Sales Line";
        IssueActionLog."Record SystemId" := Rec.SystemId;
        IssueActionLog."Record No." := CopyStr(Rec."Document No.", 1, MaxStrLen(IssueActionLog."Record No."));
        IssueActionLog."Record Caption" := CopyStr(BuildRecordCaption(), 1, MaxStrLen(IssueActionLog."Record Caption"));
        IssueActionLog."Issue Code" := CurrentIssueCode;
        IssueActionLog."Action Type" := 'CORRECTED';
        IssueActionLog.Comment := CopyStr(CorrectionCommentLbl, 1, MaxStrLen(IssueActionLog.Comment));
        IssueActionLog.Insert(true);
        Commit();

        LoadCorrectionStatus();
        CurrPage.Update(false);
        Message(CorrectionRecordedMsg, Rec."Document No.", Rec."Line No.");
    end;

    local procedure LoadCorrectionStatus()
    var
        IssueActionLog: Record "DH Issue Action Log";
    begin
        CorrectionStatusTxt := OpenLbl;
        CorrectionStatusStyle := 'Unfavorable';
        CorrectedAtValue := 0DT;
        CorrectedByTxt := '';

        if CurrentIssueCode = '' then
            exit;

        if not IsCurrentLineCorrected(IssueActionLog) then
            exit;

        CorrectionStatusTxt := CorrectedLbl;
        CorrectionStatusStyle := 'Favorable';
        CorrectedAtValue := IssueActionLog."Action At";
        CorrectedByTxt := IssueActionLog."Action User";
    end;

    local procedure IsCurrentLineCorrected(var IssueActionLog: Record "DH Issue Action Log"): Boolean
    begin
        IssueActionLog.Reset();
        IssueActionLog.SetCurrentKey("Table ID", "Record SystemId", "Action At");
        IssueActionLog.SetRange("Table ID", Database::"Sales Line");
        IssueActionLog.SetRange("Record SystemId", Rec.SystemId);
        IssueActionLog.SetRange("Issue Code", CurrentIssueCode);
        IssueActionLog.SetRange("Action Type", 'CORRECTED');
        IssueActionLog.Ascending(false);
        exit(IssueActionLog.FindFirst());
    end;

    local procedure BuildRecordCaption(): Text[100]
    begin
        exit(CopyStr(StrSubstNo('%1, Zeile %2: %3', Rec."Document No.", Rec."Line No.", Rec.Description), 1, 100));
    end;

    local procedure EnsureIssueContext()
    begin
        if CurrentIssueCode = '' then
            Error(IssueContextMissingErr);
    end;

    local procedure GetLocalCurrencyCode(): Text
    var
        CurrencyMgt: Codeunit "DH Currency Mgt.";
    begin
        exit(CurrencyMgt.GetLocalCurrencyCode());
    end;
}
