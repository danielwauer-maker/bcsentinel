page 53130 "DH Deep Scan Runs"
{
    PageType = List;
    SourceTable = "DH Scan Header";
    ApplicationArea = All;
    UsageCategory = Administration;
    Caption = 'BCSentinel Scan History';
    Editable = false;
    InsertAllowed = false;
    DeleteAllowed = false;
    ModifyAllowed = false;

    layout
    {
        area(Content)
        {
            repeater(Runs)
            {
                field(DisplayRunId; Rec.GetDisplayRunId())
                {
                    ApplicationArea = All;
                    Caption = 'Run ID';
                    ToolTip = 'Specifies Run ID.';
                    StyleExpr = RunIdStyle;

                    trigger OnDrillDown()
                    begin
                        OpenMonitorForCurrentScan();
                    end;
                }

                /*field("Scan Type"; Rec."Scan Type")
                {
                    ApplicationArea = All;
                }*/

                field("Scan DateTime"; Rec."Scan DateTime")
                {
                    ApplicationArea = All;
                    Caption = 'Scan Date';
                    ToolTip = 'Specifies Scan Date.';
                }

                field(ScanTypeDisplay; ScanTypeTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Scan Type';
                    ToolTip = 'Specifies the customer-facing scan type.';
                }

                field(ResultDisplay; ResultTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Result';
                    ToolTip = 'Specifies the scan result.';
                    StyleExpr = ResultStyle;
                }

                field(RatingDisplay; RatingTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Rating';
                    ToolTip = 'Specifies the rating.';
                    StyleExpr = RatingStyle;
                }

                field("Data Score"; Rec."Data Score")
                {
                    ApplicationArea = All;
                    Caption = 'Score';
                    ToolTip = 'Specifies Score.';
                    StyleExpr = ScoreStyle;
                }

                field("Checks Count"; Rec."Checks Count")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Checks Count.';
                }

                field("Issues Count"; Rec."Issues Count")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Issues Count.';
                }

                field("Est. Loss"; Rec."Estimated Loss (EUR)")
                {
                    ApplicationArea = All;
                    Caption = 'Impact LCY';
                    ToolTip = 'Specifies the estimated business impact in local currency.';
                }

                field("Headline"; Rec."Headline")
                {
                    ApplicationArea = All;
                    Caption = 'Technical Message';
                    ToolTip = 'Specifies the technical backend message.';
                }

                /*field("Premium"; GetIsPremiumRun())
                {
                    ApplicationArea = All;
                    Caption = 'Paid Access';
                }*/
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(OpenDashboardAction)
            {
                Caption = 'Open Scan';
                ToolTip = 'Opens the selected scan.';
                ApplicationArea = All;
                Image = Navigate;

                trigger OnAction()
                begin
                    OpenMonitorForCurrentScan();
                end;
            }

            action(OpenAllIssues)
            {
                Caption = 'Open Issues';
                ToolTip = 'Opens issues for the selected scan.';
                ApplicationArea = All;
                Image = List;

                trigger OnAction()
                var
                    DashboardIssue: Record "DH Dashboard Issue";
                    DashboardMgt: Codeunit "DH Dashboard Mgt.";
                begin
                    DashboardMgt.RefreshDashboardIssueCache(Rec);
                    DashboardIssue.SetRange("Dashboard Scan Entry No.", Rec."Entry No.");
                    Page.Run(Page::"DH Dashboard Issues List", DashboardIssue);
                end;
            }

            action(OpenMonitor)
            {
                Caption = 'Open Scan Monitor';
                ToolTip = 'Opens the scan monitor for the selected run.';
                ApplicationArea = All;
                Image = ViewDetails;

                trigger OnAction()
                var
                    DeepScanRun: Record "DH Deep Scan Run";
                begin
                    if Rec."Scan Type" <> Rec."Scan Type"::Deep then
                        Error(MonitorDeepOnlyErr);

                    DeepScanRun.SetRange("Run ID", Rec.GetDisplayRunId());
                    if not DeepScanRun.FindFirst() then
                        Error(MonitorNotFoundErr, Rec.GetDisplayRunId());

                    Page.Run(Page::"DH Deep Scan Monitor", DeepScanRun);
                end;
            }

            action(DeleteSelectedScan)
            {
                Caption = 'Delete Selected Scan(s)';
                ToolTip = 'Deletes the selected scan history entries after confirmation.';
                ApplicationArea = All;
                Image = Delete;
                Scope = Repeater;

                trigger OnAction()
                begin
                    DeleteSelectedScans();
                end;
            }

            action(DeleteCurrentScan)
            {
                Caption = 'Delete This Scan';
                ToolTip = 'Deletes the current scan history entry after confirmation.';
                ApplicationArea = All;
                Image = Delete;
                Scope = Repeater;

                trigger OnAction()
                var
                    Setup: Record "DH Setup";
                    ApiClient: Codeunit "DH API Client";
                begin
                    if Rec."Entry No." = 0 then
                        Error(SelectScanErr);

                    if not Confirm(DeleteOneQst, false, Rec.GetDisplayRunId()) then
                        exit;

                    DeleteSingleScan(Rec, Setup, ApiClient);
                    CurrPage.Update(false);
                    Message(DeleteOneMsg);
                end;
            }

            action(ReconcileScanHistory)
            {
                Caption = 'Reconcile Scan History';
                ToolTip = 'Synchronizes the Business Central scan history with the backend.';
                ApplicationArea = All;
                Image = RefreshLines;

                trigger OnAction()
                var
                    Setup: Record "DH Setup";
                    ApiClient: Codeunit "DH API Client";
                begin
                    if not Setup.Get('SETUP') then
                        Error(SetupNotFoundErr);

                    if not Confirm(ReconcileQst, false) then
                        exit;

                    ApiClient.ReconcileScansWithBackend(Setup);
                    Message(ReconcileMsg);
                    CurrPage.Update(false);
                end;
            }

            action(Refresh)
            {
                Caption = 'Refresh';
                ToolTip = 'Refreshes the scan history.';
                ApplicationArea = All;
                Image = Refresh;

                trigger OnAction()
                begin
                    CurrPage.Update(false);
                end;
            }
        }
    }

    trigger OnOpenPage()
    begin
        Rec.SetCurrentKey("Scan DateTime");
        Rec.Ascending(false);
    end;

    trigger OnAfterGetRecord()
    begin
        ScoreStyle := GetScoreStyle();
        ResultTxt := GetResultText();
        ResultStyle := GetResultStyle();
        RatingTxt := GetRatingText(Rec."Rating");
        RatingStyle := GetRatingStyle(Rec."Rating");
        ScanTypeTxt := GetScanTypeText();
        RunIdStyle := 'Strong';
    end;

    var
        ScoreStyle: Text[30];
        ResultStyle: Text[30];
        RatingStyle: Text[30];
        RunIdStyle: Text[30];
        ResultTxt: Text[80];
        RatingTxt: Text[30];
        ScanTypeTxt: Text[50];

        SelectScanErr: Label 'Please select a scan first.', Comment = 'DEU="Bitte wählen Sie zuerst einen Scan aus."';
        SetupNotFoundErr: Label 'BCSentinel setup was not found.', Comment = 'DEU="Die BCSentinel Einrichtung wurde nicht gefunden."';
        MonitorDeepOnlyErr: Label 'The scan monitor is only available for deep scans.', Comment = 'DEU="Der Scan-Monitor ist nur für Deep-Scans verfügbar."';
        MonitorNotFoundErr: Label 'The scan monitor could not find details for scan %1.', Comment = 'DEU="Der Scan-Monitor konnte keine Details für Scan %1 finden."';
        DeleteOneQst: Label 'Do you want to delete scan %1?', Comment = 'DEU="Möchten Sie Scan %1 löschen?"';
        DeleteManyQst: Label 'Do you want to delete %1 selected scans?', Comment = 'DEU="Möchten Sie %1 ausgewählte Scans löschen?"';
        DeleteOneMsg: Label 'Scan deleted.', Comment = 'DEU="Scan gelöscht."';
        DeleteManyMsg: Label '%1 scan(s) deleted.', Comment = 'DEU="%1 Scan(s) gelöscht."';
        ReconcileQst: Label 'This synchronizes the backend scan history with the current Business Central scan list and removes orphan backend scans. Continue?', Comment = 'DEU="Dies gleicht die Backend-Scan-Historie mit der aktuellen Business-Central-Scanliste ab und entfernt verwaiste Backend-Scans. Fortfahren?"';
        ReconcileMsg: Label 'Scan history successfully synchronized with the backend.', Comment = 'DEU="Scan-Historie erfolgreich mit dem Backend abgeglichen."';

    local procedure OpenMonitorForCurrentScan()
    var
        DeepScanRun: Record "DH Deep Scan Run";
    begin
        if Rec."Scan Type" <> Rec."Scan Type"::Deep then
            Error(MonitorDeepOnlyErr);

        DeepScanRun.SetRange("Run ID", Rec.GetDisplayRunId());
        if not DeepScanRun.FindFirst() then
            Error(MonitorNotFoundErr, Rec.GetDisplayRunId());

        Page.Run(Page::"DH Deep Scan Monitor", DeepScanRun);
    end;

    local procedure DeleteSingleScan(var ScanHeader: Record "DH Scan Header"; var Setup: Record "DH Setup"; var ApiClient: Codeunit "DH API Client")
    var
        BackendDeleteId: Code[50];
    begin
        BackendDeleteId := GetBackendDeleteIdFor(ScanHeader);

        if Setup.Get('SETUP') then
            if (Setup."Tenant ID" <> '') and HasApiToken(Setup) and (BackendDeleteId <> '') then
                ApiClient.DeleteScanFromBackend(Setup, BackendDeleteId);

        DeleteLinkedDeepRunIfNeededFor(ScanHeader);
        ScanHeader.Delete(true);
    end;

    local procedure DeleteSelectedScans()
    var
        Setup: Record "DH Setup";
        SelectedScans: Record "DH Scan Header";
        ApiClient: Codeunit "DH API Client";
        TotalToDelete: Integer;
        DeletedCount: Integer;
    begin
        CurrPage.SetSelectionFilter(SelectedScans);
        if SelectedScans.IsEmpty() then
            Error(SelectScanErr);

        TotalToDelete := SelectedScans.Count();
        if TotalToDelete = 1 then begin
            if not SelectedScans.FindFirst() then
                exit;

            if not Confirm(DeleteOneQst, false, SelectedScans.GetDisplayRunId()) then
                exit;
        end else
            if not Confirm(DeleteManyQst, false, TotalToDelete) then
                exit;

        if SelectedScans.FindSet() then
            repeat
                DeleteSingleScan(SelectedScans, Setup, ApiClient);
                DeletedCount += 1;
            until SelectedScans.Next() = 0;

        CurrPage.Update(false);
        Message(DeleteManyMsg, DeletedCount);
    end;

    local procedure DeleteLinkedDeepRunIfNeededFor(var ScanHeader: Record "DH Scan Header")
    var
        DeepScanRun: Record "DH Deep Scan Run";
    begin
        if ScanHeader."Scan Type" <> ScanHeader."Scan Type"::Deep then
            exit;

        if ScanHeader.GetDisplayRunId() = '' then
            exit;

        DeepScanRun.SetRange("Run ID", ScanHeader.GetDisplayRunId());
        if DeepScanRun.FindFirst() then
            DeepScanRun.Delete(true);
    end;

    local procedure GetBackendDeleteIdFor(var ScanHeader: Record "DH Scan Header"): Code[50]
    begin
        if ScanHeader."Backend Scan Id" <> '' then
            exit(ScanHeader."Backend Scan Id");

        exit(ScanHeader.GetDisplayRunId());
    end;

    local procedure GetScoreStyle(): Text[30]
    begin
        if Rec."Data Score" >= 86 then
            exit('Favorable');

        if Rec."Data Score" >= 61 then
            exit('Ambiguous');

        if Rec."Data Score" > 0 then
            exit('Unfavorable');

        exit('Standard');
    end;

    local procedure GetScanTypeText(): Text[50]
    var
        DeepScanRun: Record "DH Deep Scan Run";
        ScanMode: Text;
    begin
        if Rec."Scan Type" = Rec."Scan Type"::Quick then
            exit(CopyStr(LocalizeText('Free Scan', 'Kostenloser Scan'), 1, 50));

        if FindDeepScanRun(DeepScanRun) then
            ScanMode := LowerCase(DeepScanRun."Scan Mode")
        else
            exit(CopyStr(LocalizeText('Manual Scan', 'Manueller Scan'), 1, 50));

        case ScanMode of
            'data_health_score', 'free':
                exit(CopyStr(LocalizeText('Free Scan', 'Kostenloser Scan'), 1, 50));
            'monitoring', 'scheduled':
                exit(CopyStr(LocalizeText('Monitoring Scan', 'Monitoring-Scan'), 1, 50));
            'deep', 'validation', 'full_analysis', 'one_time':
                exit(CopyStr(LocalizeText('Validation Scan', 'Validierungs-Scan'), 1, 50));
        end;

        if Rec."Scan Type" = Rec."Scan Type"::Deep then
            exit(CopyStr(LocalizeText('Validation Scan', 'Validierungs-Scan'), 1, 50));

        exit(CopyStr(LocalizeText('Manual Scan', 'Manueller Scan'), 1, 50));
    end;

    local procedure GetResultText(): Text[80]
    var
        DeepScanRun: Record "DH Deep Scan Run";
    begin
        if Rec."Scan Type" = Rec."Scan Type"::Quick then begin
            if HasCriticalFindings() then
                exit(CopyStr(LocalizeText('Completed with critical findings', 'Abgeschlossen mit kritischen Befunden'), 1, 80));

            exit(CopyStr(LocalizeText('Completed', 'Abgeschlossen'), 1, 80));
        end;

        if not FindDeepScanRun(DeepScanRun) then
            exit(CopyStr(LocalizeText('Unknown', 'Unbekannt'), 1, 80));

        if IsDeepScanFailed(DeepScanRun) then
            exit(CopyStr(LocalizeText('Failed', 'Fehlgeschlagen'), 1, 80));

        if IsDeepScanRunning(DeepScanRun) then
            exit(CopyStr(LocalizeText('Running', 'Wird ausgeführt'), 1, 80));

        if IsDeepScanCompleted(DeepScanRun) then begin
            if HasCriticalFindings() then
                exit(CopyStr(LocalizeText('Completed with critical findings', 'Abgeschlossen mit kritischen Befunden'), 1, 80));

            exit(CopyStr(LocalizeText('Completed', 'Abgeschlossen'), 1, 80));
        end;

        exit(CopyStr(LocalizeText('Unknown', 'Unbekannt'), 1, 80));
    end;

    local procedure GetResultStyle(): Text[30]
    var
        DeepScanRun: Record "DH Deep Scan Run";
    begin
        if HasCriticalFindings() then
            exit('Unfavorable');

        if Rec."Scan Type" = Rec."Scan Type"::Quick then
            exit('Favorable');

        if not FindDeepScanRun(DeepScanRun) then
            exit('Standard');

        if IsDeepScanFailed(DeepScanRun) then
            exit('Unfavorable');

        if IsDeepScanRunning(DeepScanRun) then
            exit('Ambiguous');

        if IsDeepScanCompleted(DeepScanRun) then
            exit('Favorable');

        exit('Standard');
    end;

    local procedure GetRatingText(RatingValue: Code[20]): Text[30]
    begin
        case LowerCase(Format(RatingValue)) of
            'good', 'excellent':
                exit(CopyStr(LocalizeText('Good', 'Gut'), 1, 30));
            'medium', 'moderate', 'warning', 'high':
                exit(CopyStr(LocalizeText('Medium', 'Mittel'), 1, 30));
            'critical':
                exit(CopyStr(LocalizeText('Critical', 'Kritisch'), 1, 30));
        end;

        if RatingValue = '' then
            exit(CopyStr(LocalizeText('Unknown', 'Unbekannt'), 1, 30));

        exit(CopyStr(LocalizeText('Unknown', 'Unbekannt'), 1, 30));
    end;

    local procedure GetRatingStyle(RatingValue: Code[20]): Text[30]
    begin
        case LowerCase(Format(RatingValue)) of
            'good', 'excellent':
                exit('Favorable');
            'medium', 'moderate', 'warning', 'high':
                exit('Ambiguous');
            'critical':
                exit('Unfavorable');
        end;

        exit('Standard');
    end;

    local procedure HasCriticalFindings(): Boolean
    var
        DashboardIssue: Record "DH Dashboard Issue";
        DeepScanFinding: Record "DH Deep Scan Finding";
        DeepScanRun: Record "DH Deep Scan Run";
    begin
        if LowerCase(Format(Rec."Rating")) = 'critical' then
            exit(true);

        DashboardIssue.SetRange("Dashboard Scan Entry No.", Rec."Entry No.");
        DashboardIssue.SetFilter(Severity, '%1|%2', 'critical', 'CRITICAL');
        if not DashboardIssue.IsEmpty() then
            exit(true);

        if FindDeepScanRun(DeepScanRun) then begin
            DeepScanFinding.SetRange("Deep Scan Entry No.", DeepScanRun."Entry No.");
            DeepScanFinding.SetFilter(Severity, '%1|%2', 'critical', 'CRITICAL');
            if not DeepScanFinding.IsEmpty() then
                exit(true);
        end;

        exit(false);
    end;

    local procedure FindDeepScanRun(var DeepScanRun: Record "DH Deep Scan Run"): Boolean
    begin
        if Rec.GetDisplayRunId() = '' then
            exit(false);

        DeepScanRun.Reset();
        DeepScanRun.SetRange("Run ID", Rec.GetDisplayRunId());
        exit(DeepScanRun.FindFirst());
    end;

    local procedure IsDeepScanCompleted(var DeepScanRun: Record "DH Deep Scan Run"): Boolean
    begin
        if DeepScanRun.Status = DeepScanRun.Status::Completed then
            exit(true);

        case LowerCase(DeepScanRun."Backend Status") of
            'completed':
                exit(true);
        end;

        exit(DeepScanRun."Finished At" <> 0DT);
    end;

    local procedure IsDeepScanRunning(var DeepScanRun: Record "DH Deep Scan Run"): Boolean
    begin
        if DeepScanRun.Status in [DeepScanRun.Status::Queued, DeepScanRun.Status::Running] then
            exit(true);

        case LowerCase(DeepScanRun."Backend Status") of
            'queued', 'preparing', 'running', 'finalizing':
                exit(true);
        end;

        exit(false);
    end;

    local procedure IsDeepScanFailed(var DeepScanRun: Record "DH Deep Scan Run"): Boolean
    begin
        if DeepScanRun.Status in [DeepScanRun.Status::Failed, DeepScanRun.Status::Canceled] then
            exit(true);

        case LowerCase(DeepScanRun."Backend Status") of
            'failed', 'error', 'stalled', 'cancelled', 'canceled':
                exit(true);
        end;

        exit(false);
    end;

    local procedure LocalizeText(EnglishText: Text; GermanText: Text): Text
    begin
        if IsGermanLanguage() then
            exit(GermanText);

        exit(EnglishText);
    end;

    local procedure IsGermanLanguage(): Boolean
    begin
        case GlobalLanguage() of
            1031, 2055, 3079, 4103, 5127:
                exit(true);
        end;

        exit(false);
    end;

    local procedure GetIsPremiumRun(): Boolean
    begin
        exit(Rec."Scan Type" = Rec."Scan Type"::Deep);
    end;

    local procedure HasApiToken(var Setup: Record "DH Setup"): Boolean
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        exit(SecretMgt.HasApiToken(Setup));
    end;
}

