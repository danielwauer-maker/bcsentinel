pageextension 53199 "DH Sales Line Correction Ext" extends "DH Sales Line Issue Worklist"
{
    layout
    {
        addfirst(Lines)
        {
            field(DHCorrectionStatus; CorrectionStatusTxt)
            {
                ApplicationArea = All;
                Caption = 'Korrekturstatus';
                Editable = false;
                StyleExpr = CorrectionStatusStyle;
                ToolTip = 'Zeigt, ob diese konkrete Verkaufszeile für die aktuelle DH-Prüfung als korrigiert dokumentiert wurde.';
            }
            field(DHCorrectedAt; CorrectedAtValue)
            {
                ApplicationArea = All;
                Caption = 'Korrigiert am';
                Editable = false;
                ToolTip = 'Zeigt Datum und Uhrzeit der letzten dokumentierten Korrektur.';
            }
            field(DHCorrectedBy; CorrectedByTxt)
            {
                ApplicationArea = All;
                Caption = 'Korrigiert von';
                Editable = false;
                ToolTip = 'Zeigt den Benutzer, der die Korrektur dokumentiert hat.';
            }
        }
    }

    actions
    {
        modify(MarkIssueCorrected)
        {
            Visible = false;
        }

        modify(OpenDocument)
        {
            Visible = false;
        }

        addfirst(Processing)
        {
            action(DHMarkSalesLineCorrected)
            {
                Caption = 'Als korrigiert markieren';
                ToolTip = 'Dokumentiert die ausgewählte Verkaufszeile für die aktuelle DH-Prüfung als korrigiert und schreibt einen nachvollziehbaren Historieneintrag.';
                ApplicationArea = All;
                Image = Approve;
                Promoted = true;
                PromotedCategory = Process;

                trigger OnAction()
                begin
                    MarkCurrentLineCorrected(true);
                end;
            }

            action(DHCorrectSalesLineData)
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

            action(DHOpenSalesLineCorrectionHistory)
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

    trigger OnAfterGetRecord()
    begin
        LoadCorrectionStatus();
    end;

    trigger OnAfterGetCurrRecord()
    begin
        LoadCorrectionStatus();
    end;

    var
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
}
