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

                field(RatingDisplay; RatingTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Rating';
                    ToolTip = 'Specifies the rating.';
                    StyleExpr = RatingStyle;
                }

                field(ScoreDisplay; ScoreTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Score';
                    ToolTip = 'Specifies Score.';
                    StyleExpr = ScoreStyle;
                }

                field(ModulesDisplay; ModulesTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Modules';
                    ToolTip = 'Specifies completed modules compared with configured modules.';
                }

                field(ChecksDisplay; ChecksTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Checks';
                    ToolTip = 'Specifies Checks Count.';
                }

                field("Issues Count"; Rec."Issues Count")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Issues Count.';
                }

                field(ImpactDisplay; ImpactTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Impact';
                    ToolTip = 'Specifies the estimated business impact in local currency.';
                }

                field("Headline"; Rec."Headline")
                {
                    ApplicationArea = All;
                    Caption = 'Technical Message';
                    ToolTip = 'Specifies the technical backend message.';
                    Visible = false;
                }

                field(ResultDisplay; ResultTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Result';
                    ToolTip = 'Specifies the scan result.';
                    StyleExpr = ResultStyle;
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
                    AccessGuard: Codeunit "DH Access Guard";
                begin
                    AccessGuard.EnsureIssuesAccess();
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
        ScoreTxt := GetScoreText();
        ModulesTxt := GetModulesText();
        ChecksTxt := GetChecksText();
        ImpactTxt := GetImpactText();
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
        ChecksTxt: Text[30];
        ModulesTxt: Text[30];
        ImpactTxt: Text[50];
        RatingTxt: Text[30];
        ResultTxt: Text[30];
        ScoreTxt: Text[30];
        ScanTypeTxt: Text[50];

        SelectScanErr: Label 'Please select a scan first.';
        SetupNotFoundErr: Label 'BCSentinel setup was not found.';
        MonitorDeepOnlyErr: Label 'The scan monitor is only available for deep scans.';
        MonitorNotFoundErr: Label 'The scan monitor could not find details for scan %1.', Comment = '%1 = runtime value';
        DeleteOneQst: Label 'Do you want to delete scan %1?', Comment = '%1 = runtime value';
        DeleteManyQst: Label 'Do you want to delete %1 selected scans?', Comment = '%1 = runtime value';
        DeleteOneMsg: Label 'Scan deleted.';
        DeleteManyMsg: Label '%1 scan(s) deleted.', Comment = '%1 = runtime value';
        CompletedLbl: Label 'Completed';
        CriticalLbl: Label 'Critical';
        FailedLbl: Label 'Failed';
        FreeScanLbl: Label 'Free Scan';
        GoodLbl: Label 'Good';
        ManualScanLbl: Label 'Manual Scan';
        MediumLbl: Label 'Medium';
        MonitoringScanLbl: Label 'Monitoring Scan';
        ReconcileQst: Label 'This synchronizes the backend scan history with the current Business Central scan list and removes orphan backend scans. Continue?';
        ReconcileMsg: Label 'Scan history successfully synchronized with the backend.';
        RunningLbl: Label 'Running';
        UnknownLbl: Label 'Unknown';
        ValidationScanLbl: Label 'Validation Scan';

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

    local procedure GetScoreText(): Text[30]
    begin
        if Rec."Data Score" <= 0 then
            exit('');

        exit(CopyStr(StrSubstNo('%1 / 100', Rec."Data Score"), 1, 30));
    end;

    local procedure GetModulesText(): Text[30]
    var
        DeepScanRun: Record "DH Deep Scan Run";
        DisplayModules: Integer;
        HasDeepRun: Boolean;
        TotalModules: Integer;
    begin
        HasDeepRun := FindDeepScanRun(DeepScanRun);
        if HasDeepRun then begin
            DisplayModules := DeepScanRun."Completed Modules";
            if DisplayModules = 0 then
                DisplayModules := DeepScanRun."Total Modules";

            TotalModules := GetTotalDeepScanModules();
        end;

        if not HasDeepRun then
            exit('');

        if TotalModules = 0 then
            TotalModules := 10;

        if DisplayModules = 0 then
            if Rec."Scan Type" = Rec."Scan Type"::Quick then
                exit('');

        if (DisplayModules = 0) and (TotalModules = 0) then
            exit('');

        if TotalModules = 0 then
            exit(CopyStr(StrSubstNo('%1 / ?', DisplayModules), 1, 30));

        exit(CopyStr(StrSubstNo('%1 / %2', DisplayModules, TotalModules), 1, 30));
    end;

    local procedure GetChecksText(): Text[30]
    var
        Setup: Record "DH Setup";
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
        TotalChecks: Integer;
    begin
        if Rec."Checks Count" = 0 then
            exit('');

        if Setup.Get('SETUP') then
            TotalChecks := ScanCheckMgt.GetTotalModuleChecksCount(Setup);

        if TotalChecks = 0 then
            exit(CopyStr(StrSubstNo('%1 / ?', Rec."Checks Count"), 1, 30));

        if TotalChecks < Rec."Checks Count" then
            TotalChecks := Rec."Checks Count";

        exit(CopyStr(StrSubstNo('%1 / %2', Rec."Checks Count", TotalChecks), 1, 30));
    end;

    local procedure GetImpactText(): Text[50]
    var
        CurrencyMgt: Codeunit "DH Currency Mgt.";
    begin
        exit(CurrencyMgt.FormatLocalAmount(Rec."Estimated Loss (EUR)"));
    end;

    local procedure GetScanTypeText(): Text[50]
    var
        DeepScanRun: Record "DH Deep Scan Run";
        ScanMode: Text;
    begin
        if Rec."Scan Type" = Rec."Scan Type"::Quick then
            exit(CopyStr(FreeScanLbl, 1, 50));

        if FindDeepScanRun(DeepScanRun) then
            ScanMode := LowerCase(DeepScanRun."Scan Mode")
        else
            exit(CopyStr(ManualScanLbl, 1, 50));

        if HasMonitoringRunMarker(DeepScanRun) then
            exit(CopyStr(MonitoringScanLbl, 1, 50));

        case ScanMode of
            'data_health_score', 'free':
                exit(CopyStr(FreeScanLbl, 1, 50));
            'monitoring', 'scheduled':
                exit(CopyStr(MonitoringScanLbl, 1, 50));
            'validation', 'validation_scan', 'full_analysis', 'one_time', 'credit':
                exit(CopyStr(ValidationScanLbl, 1, 50));
            'deep':
                exit(CopyStr(ManualScanLbl, 1, 50));
        end;

        exit(CopyStr(ManualScanLbl, 1, 50));
    end;

    local procedure GetResultText(): Text[30]
    var
        DeepScanRun: Record "DH Deep Scan Run";
    begin
        if Rec."Scan Type" = Rec."Scan Type"::Quick then
            exit(CopyStr(CompletedLbl, 1, 30));

        if not FindDeepScanRun(DeepScanRun) then
            exit(CopyStr(UnknownLbl, 1, 30));

        if IsDeepScanFailed(DeepScanRun) then
            exit(CopyStr(FailedLbl, 1, 30));

        if IsDeepScanRunning(DeepScanRun) then
            exit(CopyStr(RunningLbl, 1, 30));

        if IsDeepScanCompleted(DeepScanRun) then
            exit(CopyStr(CompletedLbl, 1, 30));

        exit(CopyStr(UnknownLbl, 1, 30));
    end;

    local procedure GetResultStyle(): Text[30]
    var
        DeepScanRun: Record "DH Deep Scan Run";
    begin
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
                exit(CopyStr(GoodLbl, 1, 30));
            'medium', 'moderate', 'warning', 'high':
                exit(CopyStr(MediumLbl, 1, 30));
            'critical':
                exit(CopyStr(CriticalLbl, 1, 30));
        end;

        if RatingValue = '' then
            exit(CopyStr(UnknownLbl, 1, 30));

        exit(CopyStr(UnknownLbl, 1, 30));
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
            'completed', 'completed_with_warnings':
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

    local procedure HasMonitoringRunMarker(var DeepScanRun: Record "DH Deep Scan Run"): Boolean
    var
        RecentEvents: Text;
        ScanMode: Text;
    begin
        ScanMode := LowerCase(DeepScanRun."Scan Mode");
        if ScanMode in ['monitoring', 'scheduled'] then
            exit(true);

        RecentEvents := LowerCase(DeepScanRun."Recent Events");
        exit((StrPos(RecentEvents, 'monitoring') > 0) or (StrPos(RecentEvents, 'skipped checks') > 0));
    end;

    local procedure GetTotalDeepScanModules(): Integer
    begin
        exit(10);
    end;

    local procedure IsDeepScanFailed(var DeepScanRun: Record "DH Deep Scan Run"): Boolean
    begin
        if DeepScanRun.Status in [DeepScanRun.Status::Failed, DeepScanRun.Status::Canceled] then
            exit(true);

        case LowerCase(DeepScanRun."Backend Status") of
            'failed', 'error', 'stalled', 'expired', 'cancelled', 'canceled':
                exit(true);
        end;

        exit(false);
    end;

    local procedure HasApiToken(var Setup: Record "DH Setup"): Boolean
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        exit(SecretMgt.HasApiToken(Setup));
    end;
}

