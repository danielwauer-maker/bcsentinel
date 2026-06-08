page 53158 "DH Deep Scan Monitor"
{
    PageType = Card;
    SourceTable = "DH Deep Scan Run";
    ApplicationArea = All;
    UsageCategory = None;
    Caption = 'BCSentinel Scan Monitor';
    DataCaptionExpression = Rec."Run ID";
    Editable = false;
    InsertAllowed = false;
    DeleteAllowed = false;
    ModifyAllowed = false;
    RefreshOnActivate = false;

    layout
    {
        area(Content)
        {
            group(Overview)
            {
                Caption = 'Overview';

                field(ScanStatus; ScanStatusTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Scan Status';
                    ToolTip = 'Specifies Scan Status.';
                    StyleExpr = ScanStatusStyle;
                }
                field("Current Module"; CurrentModuleTxt)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Current Module.';
                }
                field("Current Step"; CurrentStepTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Current Step';
                    ToolTip = 'Specifies Current Step.';
                    MultiLine = true;
                }
                field(OverallBar; OverallBarTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Overall Progress';
                    ToolTip = 'Specifies Overall Progress.';
                    StyleExpr = ProgressStyle;
                }
                field(ETA; ETATxt)
                {
                    ApplicationArea = All;
                    Caption = 'ETA';
                    ToolTip = 'Specifies ETA.';
                }
                field("Last Heartbeat"; LastHeartbeatValue)
                {
                    ApplicationArea = All;
                    Caption = 'Last Heartbeat';
                    ToolTip = 'Specifies Last Heartbeat.';
                }
                field("Estimated Remaining Time"; EstimatedRemainingTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Estimated Remaining Time';
                    ToolTip = 'Specifies Estimated Remaining Time.';
                }
                field("Started At"; StartedAtValue)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Started At.';
                }
                field("Finished At"; FinishedAtValue)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Finished At.';
                }
                field(Headline; HeadlineTxt)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Headline.';
                    MultiLine = true;
                }
            }
            group(StatusDetails)
            {
                Caption = 'Status Details';

                field(WarningMessage; WarningMessageTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Warning';
                    ToolTip = 'Specifies Warning.';
                    MultiLine = true;
                    StyleExpr = WarningStyle;
                }
                field(ErrorMessage; ErrorMessageTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Error';
                    ToolTip = 'Specifies Error.';
                    MultiLine = true;
                    StyleExpr = ErrorStyle;
                }
                field(RecentEvents; RecentEventsTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Recent Events';
                    ToolTip = 'Specifies Recent Events.';
                    MultiLine = true;
                }
            }
            /*part(KpiTiles; "DH Dashboard KPI Part")
            {
                ApplicationArea = All;
                Caption = 'Key Metrics';
                SubPageLink = "Entry No." = field("Entry No.");
            }*/

            group(OnlineDashboard)
            {
                Caption = 'Online';

                field(OpenExternalDashboardLink; OpenDashboardLinkTxt)
                {
                    ApplicationArea = All;
                    Caption = 'External Dashboard';
                    Editable = false;
                    DrillDown = true;
                    StyleExpr = OpenDashboardLinkStyle;
                    ToolTip = 'Open the external BCSentinel dashboard for this scan.';

                    trigger OnDrillDown()
                    begin
                        OpenAnalyticsDashboardForCurrentScan();
                    end;
                }
            }

            /*group(ScanResults)
            {
                Caption = 'Scan Results';

                field("Scanned Records"; ScannedRecordsValue)
                {
                    ApplicationArea = All;
                    Caption = 'Scanned Records';
                    ToolTip = 'Specifies Scanned Records.';
                }
                field("Affected Records Header"; AffectedRecordsValue)
                {
                    ApplicationArea = All;
                    Caption = 'Affected Records';
                    ToolTip = 'Specifies Affected Records.';
                }

                field("Estimated Loss"; EstimatedLossValue)
                {
                    ApplicationArea = All;
                    Caption = 'Estimated Loss';
                    ToolTip = 'Specifies Estimated Loss.';
                    StyleExpr = EstimatedLossStyle;
                }
                field("Potential Saving"; PotentialSavingValue)
                {
                    ApplicationArea = All;
                    Caption = 'Potential Saving';
                    ToolTip = 'Specifies Potential Saving.';
                    StyleExpr = PotentialSavingStyle;
                }
            }*/



            group(ModuleProgress)
            {
                Caption = 'Module Progress';

                field(SystemProgress; SystemProgressTxt)
                {
                    ApplicationArea = All;
                    Caption = 'System';
                    ToolTip = 'Specifies System.';
                    Visible = ShowSystem;
                    StyleExpr = SystemProgressStyle;
                }
                field(FinanceProgress; FinanceProgressTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Finance';
                    ToolTip = 'Specifies Finance.';
                    Visible = ShowFinance;
                    StyleExpr = FinanceProgressStyle;
                }
                field(SalesProgress; SalesProgressTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Sales';
                    ToolTip = 'Specifies Sales.';
                    Visible = ShowSales;
                    StyleExpr = SalesProgressStyle;
                }
                field(PurchasingProgress; PurchasingProgressTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Purchasing';
                    ToolTip = 'Specifies Purchasing.';
                    Visible = ShowPurchasing;
                    StyleExpr = PurchasingProgressStyle;
                }
                field(InventoryProgress; InventoryProgressTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Inventory';
                    ToolTip = 'Specifies Inventory.';
                    Visible = ShowInventory;
                    StyleExpr = InventoryProgressStyle;
                }
                field(CRMProgress; CRMProgressTxt)
                {
                    ApplicationArea = All;
                    Caption = 'CRM';
                    ToolTip = 'Specifies CRM.';
                    Visible = ShowCRM;
                    StyleExpr = CRMProgressStyle;
                }
                field(ManufacturingProgress; ManufacturingProgressTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Manufacturing';
                    ToolTip = 'Specifies Manufacturing.';
                    Visible = ShowManufacturing;
                    StyleExpr = ManufacturingProgressStyle;
                }
                field(ServiceProgress; ServiceProgressTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Service';
                    ToolTip = 'Specifies Service.';
                    Visible = ShowService;
                    StyleExpr = ServiceProgressStyle;
                }
                field(JobsProgress; JobsProgressTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Jobs';
                    ToolTip = 'Specifies Jobs.';
                    Visible = ShowJobs;
                    StyleExpr = JobsProgressStyle;
                }
                field(HRProgress; HRProgressTxt)
                {
                    ApplicationArea = All;
                    Caption = 'HR';
                    ToolTip = 'Specifies HR.';
                    Visible = ShowHR;
                    StyleExpr = HRProgressStyle;
                }
            }

            group(ModuleScores)
            {
                Caption = 'Module Scores';

                field("System Score"; SystemScoreValue)
                {
                    ApplicationArea = All;
                    Caption = 'System';
                    ToolTip = 'Specifies System.';
                    Visible = ShowSystem;
                    StyleExpr = SystemScoreStyle;
                }
                field("Finance Score"; FinanceScoreValue)
                {
                    ApplicationArea = All;
                    Caption = 'Finance';
                    ToolTip = 'Specifies Finance.';
                    Visible = ShowFinance;
                    StyleExpr = FinanceScoreStyle;
                }
                field("Sales Score"; SalesScoreValue)
                {
                    ApplicationArea = All;
                    Caption = 'Sales';
                    ToolTip = 'Specifies Sales.';
                    Visible = ShowSales;
                    StyleExpr = SalesScoreStyle;
                }
                field("Purchasing Score"; PurchasingScoreValue)
                {
                    ApplicationArea = All;
                    Caption = 'Purchasing';
                    ToolTip = 'Specifies Purchasing.';
                    Visible = ShowPurchasing;
                    StyleExpr = PurchasingScoreStyle;
                }
                field("Inventory Score"; InventoryScoreValue)
                {
                    ApplicationArea = All;
                    Caption = 'Inventory';
                    ToolTip = 'Specifies Inventory.';
                    Visible = ShowInventory;
                    StyleExpr = InventoryScoreStyle;
                }
                field("CRM Score"; CRMScoreValue)
                {
                    ApplicationArea = All;
                    Caption = 'CRM';
                    ToolTip = 'Specifies CRM.';
                    Visible = ShowCRM;
                    StyleExpr = CRMScoreStyle;
                }
                field("Manufacturing Score"; ManufacturingScoreValue)
                {
                    ApplicationArea = All;
                    Caption = 'Manufacturing';
                    ToolTip = 'Specifies Manufacturing.';
                    Visible = ShowManufacturing;
                    StyleExpr = ManufacturingScoreStyle;
                }
                field("Service Score"; ServiceScoreValue)
                {
                    ApplicationArea = All;
                    Caption = 'Service';
                    ToolTip = 'Specifies Service.';
                    Visible = ShowService;
                    StyleExpr = ServiceScoreStyle;
                }
                field("Jobs Score"; JobsScoreValue)
                {
                    ApplicationArea = All;
                    Caption = 'Jobs';
                    ToolTip = 'Specifies Jobs.';
                    Visible = ShowJobs;
                    StyleExpr = JobsScoreStyle;
                }
                field("HR Score"; HRScoreValue)
                {
                    ApplicationArea = All;
                    Caption = 'HR';
                    ToolTip = 'Specifies HR.';
                    Visible = ShowHR;
                    StyleExpr = HRScoreStyle;
                }
            }

            /*part(Findings; "DH Deep Scan Findings")
            {
                ApplicationArea = All;
                Caption = 'Issues';
                UpdatePropagation = Both;
                SubPageLink = "Deep Scan Entry No." = field("Entry No.");
            }*/
        }
    }

    actions
    {
        area(Processing)
        {
            action(RefreshProgress)
            {
                Caption = 'Refresh Status';
                ToolTip = 'Runs Refresh Status.';
                ApplicationArea = All;
                Image = Refresh;

                trigger OnAction()
                begin
                    ReloadMonitor();
                    CurrPage.Update(false);
                end;
            }

            action(OpenAllIssues)
            {
                Caption = 'Open Issues';
                ToolTip = 'Runs Open Issues.';
                ApplicationArea = All;
                Image = List;

                trigger OnAction()
                var
                    Finding: Record "DH Deep Scan Finding";
                begin
                    if Rec."Entry No." = 0 then
                        Error('No deep scan run is available.');

                    Finding.SetRange("Deep Scan Entry No.", Rec."Entry No.");
                    Page.Run(Page::"DH Deep Scan Findings List", Finding);
                end;
            }


            action(OpenExternalDashboard)
            {
                Caption = 'Open BCSentinel Dashboard';
                ApplicationArea = All;
                Image = View;
                ToolTip = 'Open the external BCSentinel dashboard for the current scan.';

                trigger OnAction()
                begin
                    OpenAnalyticsDashboardForCurrentScan();
                end;
            }

            action(OpenExecutiveReport)
            {
                Caption = 'Executive Report';
                ApplicationArea = All;
                Image = Report;
                ToolTip = 'Opens the executive management report for the completed scan.';

                trigger OnAction()
                begin
                    OpenExecutiveReportForCurrentScan(false);
                end;
            }

            action(OpenExecutivePdf)
            {
                Caption = 'Executive PDF';
                ApplicationArea = All;
                Image = Print;
                ToolTip = 'Opens the executive PDF report for the completed scan.';

                trigger OnAction()
                begin
                    OpenExecutiveReportForCurrentScan(true);
                end;
            }

            action(StartMonitoring)
            {
                Caption = 'Start Monitoring';
                ApplicationArea = All;
                Image = Add;
                ToolTip = 'Open the secure BCSentinel checkout for Monitoring Monthly.';

                trigger OnAction()
                var
                    Setup: Record "DH Setup";
                    ApiClient: Codeunit "DH API Client";
                begin
                    LoadSetupOrError(Setup);

                    if Setup."Monitoring Active" then begin
                        Message('Monitoring is already active.');
                        exit;
                    end;

                    ApiClient.OpenProductCheckout(Setup, 'monitoring_monthly');
                end;
            }

            action(RefreshLicenseStatus)
            {
                Caption = 'Refresh Product Access';
                ApplicationArea = All;
                Image = Refresh;
                ToolTip = 'Refresh scan credits, monitoring status, and product access from BCSentinel.';

                trigger OnAction()
                var
                    Setup: Record "DH Setup";
                    ApiClient: Codeunit "DH API Client";
                begin
                    LoadSetupOrError(Setup);
                    ApiClient.RefreshLicenseStatus(Setup);
                    Message('Product access refreshed.');
                end;
            }
        }
    }

    trigger OnOpenPage()
    begin
        UpdateModuleVisibility();
        ReloadDisplayValuesFromRec();
        LoadDashboardValues();
    end;

    trigger OnAfterGetRecord()
    begin
        ReloadDisplayValuesFromRec();
    end;

    trigger OnAfterGetCurrRecord()
    begin
        ReloadDisplayValuesFromRec();
    end;

    var
        BackendRefreshFailures: Integer;
        ShowSystem: Boolean;
        ShowFinance: Boolean;
        ShowSales: Boolean;
        ShowPurchasing: Boolean;
        ShowInventory: Boolean;
        ShowCRM: Boolean;
        ShowManufacturing: Boolean;
        ShowService: Boolean;
        ShowJobs: Boolean;
        ShowHR: Boolean;

        RunIdTxt: Code[50];
        CurrentModuleTxt: Text[50];
        CurrentStepTxt: Text[160];
        ProgressPct: Integer;
        OverallBarTxt: Text[50];
        ETATxt: Text[100];
        LastHeartbeatValue: DateTime;
        EstimatedRemainingTxt: Text[100];
        StartedAtValue: DateTime;
        FinishedAtValue: DateTime;
        HeadlineTxt: Text[250];
        WarningMessageTxt: Text[250];
        ErrorMessageTxt: Text[250];
        RecentEventsTxt: Text[500];
        ScanDateTimeValue: DateTime;
        ScanTypeTxt: Text[30];
        RatingTxt: Text[30];
        ScannedRecordsValue: Integer;
        EstimatedLossValue: Decimal;
        PotentialSavingValue: Decimal;
        EstimatedLossStyle: Text[30];
        PotentialSavingStyle: Text[30];
        OpenDashboardLinkTxt: Text[100];
        OpenDashboardLinkStyle: Text[30];
        DeepScoreValue: Integer;
        ChecksCountValue: Integer;
        IssuesCountValue: Integer;
        AffectedRecordsValue: Integer;
        SystemScoreValue: Integer;
        FinanceScoreValue: Integer;
        SalesScoreValue: Integer;
        PurchasingScoreValue: Integer;
        InventoryScoreValue: Integer;
        CRMScoreValue: Integer;
        ManufacturingScoreValue: Integer;
        ServiceScoreValue: Integer;
        JobsScoreValue: Integer;
        HRScoreValue: Integer;
        SystemProgressTxt: Text[60];
        FinanceProgressTxt: Text[60];
        SalesProgressTxt: Text[60];
        PurchasingProgressTxt: Text[60];
        InventoryProgressTxt: Text[60];
        CRMProgressTxt: Text[60];
        ManufacturingProgressTxt: Text[60];
        ServiceProgressTxt: Text[60];
        JobsProgressTxt: Text[60];
        HRProgressTxt: Text[60];
        ScanStatusTxt: Text[50];
        ScanStatusStyle: Text[30];
        ProgressStyle: Text[30];
        WarningStyle: Text[30];
        ErrorStyle: Text[30];
        ScoreStyle: Text[30];
        IssuesStyle: Text[30];
        RatingStyle: Text[30];
        SystemScoreStyle: Text[30];
        FinanceScoreStyle: Text[30];
        SalesScoreStyle: Text[30];
        PurchasingScoreStyle: Text[30];
        InventoryScoreStyle: Text[30];
        CRMScoreStyle: Text[30];
        ManufacturingScoreStyle: Text[30];
        ServiceScoreStyle: Text[30];
        JobsScoreStyle: Text[30];
        HRScoreStyle: Text[30];
        SystemProgressStyle: Text[30];
        FinanceProgressStyle: Text[30];
        SalesProgressStyle: Text[30];
        PurchasingProgressStyle: Text[30];
        InventoryProgressStyle: Text[30];
        CRMProgressStyle: Text[30];
        ManufacturingProgressStyle: Text[30];
        ServiceProgressStyle: Text[30];
        JobsProgressStyle: Text[30];
        HRProgressStyle: Text[30];

    local procedure ReloadMonitor()
    var
        DeepScanRun: Record "DH Deep Scan Run";
        Setup: Record "DH Setup";
        ApiClient: Codeunit "DH API Client";
    begin
        UpdateModuleVisibility();

        if DeepScanRun.Get(Rec."Entry No.") then begin
            if Setup.Get('SETUP') then begin
                if DeepScanRun."Run ID" <> '' then
                    if IsLocalTerminalStatus(DeepScanRun) and BackendStatusNeedsHealing(DeepScanRun) then
                        if not TrySyncLocalTerminalStatus(ApiClient, Setup, DeepScanRun) then begin
                            BackendRefreshFailures += 1;
                        end;

                if DeepScanRun."Run ID" <> '' then
                    if TryRefreshBackendStatus(ApiClient, Setup, DeepScanRun) then begin
                        BackendRefreshFailures := 0;
                        Commit();
                    end
                    else begin
                        BackendRefreshFailures += 1;
                        if BackendRefreshFailures >= 3 then begin
                            DeepScanRun."Warning Message" := CopyStr(GetBackendRefreshWarning(DeepScanRun), 1, MaxStrLen(DeepScanRun."Warning Message"));
                            DeepScanRun.Modify(true);
                            Commit();
                        end;
                    end;
            end;
            Rec := DeepScanRun;
            if (BackendRefreshFailures > 0) and (BackendRefreshFailures < 3) and (Rec."Backend Status" = '') then
                Rec."Current Step" := 'Waiting for backend status';
            ReloadDisplayValuesFromRec();
            LoadDashboardValues();
        end;
    end;

    local procedure ReloadDisplayValuesFromRec()
    begin
        RunIdTxt := Rec."Run ID";
        CurrentModuleTxt := GetCurrentModuleText();
        CurrentStepTxt := GetCurrentStepText();
        ProgressPct := GetDisplayProgressPercent();
        OverallBarTxt := BuildBar(ProgressPct);
        ETATxt := GetEtaText();
        LastHeartbeatValue := Rec."Last Heartbeat";
        EstimatedRemainingTxt := FormatRemainingSeconds(Rec."Estimated Remaining Seconds");
        StartedAtValue := Rec."Started At";
        FinishedAtValue := Rec."Finished At";
        HeadlineTxt := Rec.Headline;
        WarningMessageTxt := GetDisplayWarningText();
        ErrorMessageTxt := GetDisplayErrorText();
        RecentEventsTxt := Rec."Recent Events";

        DeepScoreValue := Rec."Deep Score";
        ChecksCountValue := Rec."Checks Count";
        IssuesCountValue := Rec."Issues Count";
        AffectedRecordsValue := Rec."Affected Records";

        SystemScoreValue := Rec."System Score";
        FinanceScoreValue := Rec."Finance Score";
        SalesScoreValue := Rec."Sales Score";
        PurchasingScoreValue := Rec."Purchasing Score";
        InventoryScoreValue := Rec."Inventory Score";
        CRMScoreValue := Rec."CRM Score";
        ManufacturingScoreValue := Rec."Manufacturing Score";
        ServiceScoreValue := Rec."Service Score";
        JobsScoreValue := Rec."Jobs Score";
        HRScoreValue := Rec."HR Score";

        SystemProgressTxt := BuildModuleText('System', Rec."System Progress %");
        FinanceProgressTxt := BuildModuleText('Finance', Rec."Finance Progress %");
        SalesProgressTxt := BuildModuleText('Sales', Rec."Sales Progress %");
        PurchasingProgressTxt := BuildModuleText('Purchasing', Rec."Purchasing Progress %");
        InventoryProgressTxt := BuildModuleText('Inventory', Rec."Inventory Progress %");
        CRMProgressTxt := BuildModuleText('CRM', Rec."CRM Progress %");
        ManufacturingProgressTxt := BuildModuleText('Manufacturing', Rec."Manufacturing Progress %");
        ServiceProgressTxt := BuildModuleText('Service', Rec."Service Progress %");
        JobsProgressTxt := BuildModuleText('Jobs', Rec."Jobs Progress %");
        HRProgressTxt := BuildModuleText('HR', Rec."HR Progress %");

        ScanStatusTxt := GetScanStatusText();
        ScanStatusStyle := GetScanStatusStyle();
        ProgressStyle := GetProgressStyle(ProgressPct);
        WarningStyle := GetWarningStyle();
        ErrorStyle := GetErrorStyle();
        ScoreStyle := GetScoreStyle(DeepScoreValue);
        IssuesStyle := GetIssuesStyle();
        EstimatedLossStyle := 'Unfavorable';
        PotentialSavingStyle := 'Strong';
        OpenDashboardLinkTxt := 'Open Analytics-Dashboard';
        OpenDashboardLinkStyle := 'Strong';

        SystemScoreStyle := GetScoreStyle(SystemScoreValue);
        FinanceScoreStyle := GetScoreStyle(FinanceScoreValue);
        SalesScoreStyle := GetScoreStyle(SalesScoreValue);
        PurchasingScoreStyle := GetScoreStyle(PurchasingScoreValue);
        InventoryScoreStyle := GetScoreStyle(InventoryScoreValue);
        CRMScoreStyle := GetScoreStyle(CRMScoreValue);
        ManufacturingScoreStyle := GetScoreStyle(ManufacturingScoreValue);
        ServiceScoreStyle := GetScoreStyle(ServiceScoreValue);
        JobsScoreStyle := GetScoreStyle(JobsScoreValue);
        HRScoreStyle := GetScoreStyle(HRScoreValue);

        SystemProgressStyle := GetProgressStyle(Rec."System Progress %");
        FinanceProgressStyle := GetProgressStyle(Rec."Finance Progress %");
        SalesProgressStyle := GetProgressStyle(Rec."Sales Progress %");
        PurchasingProgressStyle := GetProgressStyle(Rec."Purchasing Progress %");
        InventoryProgressStyle := GetProgressStyle(Rec."Inventory Progress %");
        CRMProgressStyle := GetProgressStyle(Rec."CRM Progress %");
        ManufacturingProgressStyle := GetProgressStyle(Rec."Manufacturing Progress %");
        ServiceProgressStyle := GetProgressStyle(Rec."Service Progress %");
        JobsProgressStyle := GetProgressStyle(Rec."Jobs Progress %");
        HRProgressStyle := GetProgressStyle(Rec."HR Progress %");
    end;

    [TryFunction]
    local procedure TryRefreshBackendStatus(var ApiClient: Codeunit "DH API Client"; var Setup: Record "DH Setup"; var DeepScanRun: Record "DH Deep Scan Run")
    begin
        ApiClient.RefreshScanStatus(Setup, DeepScanRun);
    end;

    [TryFunction]
    local procedure TrySyncLocalTerminalStatus(var ApiClient: Codeunit "DH API Client"; var Setup: Record "DH Setup"; var DeepScanRun: Record "DH Deep Scan Run")
    begin
        case DeepScanRun.Status of
            DeepScanRun.Status::Completed:
                begin
                    DeepScanRun."Progress %" := 100;
                    DeepScanRun."Current Module" := 'All modules completed';
                    DeepScanRun."Current Step" := 'Scan completed';
                    DeepScanRun."Warning Message" := '';
                    DeepScanRun."Error Message" := '';
                    ApiClient.UpdateScanProgress(Setup, DeepScanRun, 'completed', 'Scan completed', 'Scan completed');
                end;
            DeepScanRun.Status::Failed:
                begin
                    if DeepScanRun."Current Step" = '' then
                        DeepScanRun."Current Step" := 'Scan failed';
                    ApiClient.UpdateScanProgress(Setup, DeepScanRun, 'failed', 'Scan failed', 'Scan failed');
                end;
        end;
    end;

    local procedure LoadDashboardValues()
    begin
        ScanDateTimeValue := 0DT;
        ScanTypeTxt := '';
        RatingTxt := '';
        RatingStyle := 'Standard';
        ScannedRecordsValue := 0;
        EstimatedLossValue := 0;
        PotentialSavingValue := 0;

        if Rec."Run ID" = '' then
            exit;

        ScanDateTimeValue := Rec."Finished At";
        if ScanDateTimeValue = 0DT then
            ScanDateTimeValue := Rec."Requested At";

        ScanTypeTxt := 'Deep';
        RatingTxt := Rec.Rating;
        RatingStyle := GetRatingStyle(Rec.Rating);
        ScannedRecordsValue := Rec."Total Records";
        EstimatedLossValue := Rec."Estimated Loss (EUR)";
        PotentialSavingValue := Rec."Potential Saving (EUR)";

        if EstimatedLossValue < 0 then
            EstimatedLossValue := 0;

        if PotentialSavingValue < 0 then
            PotentialSavingValue := 0;

        if (EstimatedLossValue > 0) and (PotentialSavingValue > EstimatedLossValue) then
            PotentialSavingValue := EstimatedLossValue;

        if (DeepScoreValue = 0) and (Rec."Deep Score" <> 0) then
            DeepScoreValue := Rec."Deep Score";
        if (ChecksCountValue = 0) and (Rec."Checks Count" <> 0) then
            ChecksCountValue := Rec."Checks Count";
        if (IssuesCountValue = 0) and (Rec."Issues Count" <> 0) then
            IssuesCountValue := Rec."Issues Count";
        if (AffectedRecordsValue = 0) and (Rec."Affected Records" <> 0) then
            AffectedRecordsValue := Rec."Affected Records";
    end;

    local procedure UpdateModuleVisibility()
    var
        Setup: Record "DH Setup";
    begin
        ShowSystem := true;
        ShowFinance := true;
        ShowSales := true;
        ShowPurchasing := true;
        ShowInventory := true;
        ShowCRM := true;
        ShowManufacturing := true;
        ShowService := true;
        ShowJobs := true;
        ShowHR := true;

        if Setup.Get('SETUP') then begin
            Setup.ApplyDefaults();
            ShowSystem := Setup."Scan System Module";
            ShowFinance := Setup."Scan Finance Module";
            ShowSales := Setup."Scan Sales Module";
            ShowPurchasing := Setup."Scan Purchasing Module";
            ShowInventory := Setup."Scan Inventory Module";
            ShowCRM := Setup."Scan CRM Module";
            ShowManufacturing := Setup."Scan Manufacturing Module";
            ShowService := Setup."Scan Service Module";
            ShowJobs := Setup."Scan Jobs Module";
            ShowHR := Setup."Scan HR Module";
        end;
    end;

    local procedure BuildModuleText(ModuleName: Text; PercentValue: Integer): Text
    begin
        exit(StrSubstNo('%1  %2%  %3', ModuleName, PercentValue, BuildBar(PercentValue)));
    end;

    local procedure GetDisplayProgressPercent(): Integer
    begin
        if IsLocalCompleted() then
            exit(100);

        case LowerCase(Rec."Backend Status") of
            'queued', 'preparing':
                exit(0);
            'completed':
                exit(100);
        end;

        if Rec.Status = Rec.Status::Queued then
            exit(0);
        if Rec.Status = Rec.Status::Completed then
            exit(100);

        if Rec."Progress %" < 0 then
            exit(0);
        if Rec."Progress %" > 100 then
            exit(100);
        exit(Rec."Progress %");
    end;

    local procedure GetCurrentModuleText(): Text[50]
    begin
        if IsLocalCompleted() then
            exit('All modules completed');

        case LowerCase(Rec."Backend Status") of
            'queued', 'preparing':
                exit('Preparing');
            'completed':
                exit('All modules completed');
            'failed':
                begin
                    if Rec."Current Module" <> '' then
                        exit(CopyStr(StrSubstNo('Failed during %1', Rec."Current Module"), 1, 50));
                    exit('Failed');
                end;
        end;

        if Rec."Current Module" <> '' then
            exit(Rec."Current Module");

        exit('');
    end;

    local procedure GetCurrentStepText(): Text[160]
    begin
        if IsLocalCompleted() then
            exit('Scan completed');

        case LowerCase(Rec."Backend Status") of
            'queued':
                exit('Waiting for backend status');
            'preparing':
                exit('Preparing scan');
            'completed':
                exit('Scan completed');
            'failed':
                if Rec."Current Step" = '' then
                    exit('Scan failed');
        end;

        if Rec."Current Step" <> '' then
            exit(Rec."Current Step");

        if Rec.Status = Rec.Status::Queued then
            exit('Waiting for backend status');

        exit('');
    end;

    local procedure GetEtaText(): Text[100]
    begin
        if IsLocalCompleted() then
            exit('Completed');

        case LowerCase(Rec."Backend Status") of
            'completed':
                exit('Completed');
            'queued', 'preparing':
                exit('');
        end;

        exit(Rec."ETA Text");
    end;

    local procedure GetDisplayWarningText(): Text[250]
    begin
        if IsLocalCompleted() and IsBackendNonTerminal() then
            exit('Backend status is outdated. Local scan completed successfully.');

        if (BackendRefreshFailures > 0) and IsLocalCompleted() then
            exit('Backend status could not be refreshed. Local scan completed successfully.');

        if LowerCase(Rec."Backend Status") = 'completed' then
            exit('');

        exit(Rec."Warning Message");
    end;

    local procedure GetDisplayErrorText(): Text[250]
    begin
        if IsLocalCompleted() then
            exit('');

        if LowerCase(Rec."Backend Status") = 'completed' then
            exit('');

        exit(Rec."Error Message");
    end;

    local procedure BuildBar(PercentValue: Integer): Text
    var
        Filled: Integer;
        i: Integer;
        BarTxt: Text;
    begin
        if PercentValue < 0 then
            PercentValue := 0;
        if PercentValue > 100 then
            PercentValue := 100;

        Filled := PercentValue div 10;
        if (PercentValue mod 10) > 0 then
            Filled += 1;

        for i := 1 to 10 do
            if i <= Filled then
                BarTxt += '#'
            else
                BarTxt += '-';

        exit(BarTxt);
    end;

    local procedure GetProgressStyle(Value: Integer): Text
    begin
        if Value <= 0 then
            exit('Standard');
        if Value < 30 then
            exit('Unfavorable');
        if Value < 70 then
            exit('Ambiguous');
        if Value < 100 then
            exit('Favorable');
        exit('Strong');
    end;

    local procedure GetScoreStyle(Value: Integer): Text
    begin
        if Value <= 60 then
            exit('Unfavorable');
        if Value <= 75 then
            exit('Ambiguous');
        if Value <= 95 then
            exit('Favorable');
        exit('Strong');
    end;

    local procedure GetIssuesStyle(): Text
    begin
        if IssuesCountValue > 0 then
            exit('Attention');
        exit('Standard');
    end;

    local procedure GetRatingStyle(RatingValue: Code[20]): Text
    begin
        case LowerCase(Format(RatingValue)) of
            'critical':
                exit('Unfavorable');
            'warning', 'moderate':
                exit('Ambiguous');
            'good':
                exit('Favorable');
            'excellent':
                exit('Strong');
        end;

        exit('Standard');
    end;

    local procedure GetScanStatusText(): Text
    begin
        if IsLocalCompleted() then
            exit('Completed');

        if Rec.Status = Rec.Status::Failed then
            exit('Failed');
        if Rec.Status = Rec.Status::Canceled then
            exit('Cancelled');

        case LowerCase(Rec."Backend Status") of
            'queued':
                exit('Queued');
            'preparing':
                exit('Preparing');
            'running':
                exit('Running');
            'finalizing':
                exit('Finalizing');
            'completed':
                exit('Completed');
            'failed':
                exit('Failed');
            'stalled':
                exit('Possibly stalled');
            'cancelled':
                exit('Cancelled');
        end;

        case Rec.Status of
            Rec.Status::Queued:
                exit('Queued');
            Rec.Status::Running:
                exit('Running');
            Rec.Status::Completed:
                exit('Completed');
            Rec.Status::Failed:
                exit('Failed');
            Rec.Status::Canceled:
                exit('Cancelled');
        end;
        exit('Unknown');
    end;

    local procedure GetScanStatusStyle(): Text
    begin
        if IsLocalCompleted() then
            exit('Strong');

        if Rec.Status = Rec.Status::Failed then
            exit('Unfavorable');
        if Rec.Status = Rec.Status::Canceled then
            exit('Unfavorable');

        case LowerCase(Rec."Backend Status") of
            'queued', 'preparing', 'finalizing':
                exit('Ambiguous');
            'running':
                exit('Favorable');
            'completed':
                exit('Strong');
            'failed', 'stalled', 'cancelled':
                exit('Unfavorable');
        end;

        case Rec.Status of
            Rec.Status::Queued:
                exit('Ambiguous');
            Rec.Status::Running:
                exit('Favorable');
            Rec.Status::Completed:
                exit('Strong');
            Rec.Status::Failed, Rec.Status::Canceled:
                exit('Unfavorable');
        end;
        exit('Standard');
    end;

    local procedure FormatRemainingSeconds(RemainingSeconds: Integer): Text[100]
    var
        Minutes: Integer;
    begin
        if RemainingSeconds <= 0 then
            exit('');

        if RemainingSeconds < 60 then
            exit('Less than 1 minute');

        Minutes := (RemainingSeconds + 59) div 60;
        exit(StrSubstNo('%1 min remaining', Minutes));
    end;

    local procedure GetWarningStyle(): Text[30]
    begin
        if WarningMessageTxt <> '' then
            exit('Ambiguous');
        exit('Standard');
    end;

    local procedure GetErrorStyle(): Text[30]
    begin
        if ErrorMessageTxt <> '' then
            exit('Unfavorable');
        exit('Standard');
    end;

    local procedure IsLocalCompleted(): Boolean
    begin
        exit((Rec.Status = Rec.Status::Completed) or (Rec."Finished At" <> 0DT));
    end;

    local procedure IsLocalTerminalStatus(var DeepScanRun: Record "DH Deep Scan Run"): Boolean
    begin
        exit((DeepScanRun.Status = DeepScanRun.Status::Completed) or (DeepScanRun.Status = DeepScanRun.Status::Failed) or (DeepScanRun.Status = DeepScanRun.Status::Canceled));
    end;

    local procedure BackendStatusNeedsHealing(var DeepScanRun: Record "DH Deep Scan Run"): Boolean
    begin
        case LowerCase(DeepScanRun."Backend Status") of
            'completed', 'failed', 'cancelled', 'canceled':
                exit(false);
        end;

        exit(true);
    end;

    local procedure IsBackendNonTerminal(): Boolean
    begin
        case LowerCase(Rec."Backend Status") of
            'queued', 'preparing', 'running', 'finalizing':
                exit(true);
        end;

        exit(false);
    end;

    local procedure GetBackendRefreshWarning(var DeepScanRun: Record "DH Deep Scan Run"): Text
    begin
        if DeepScanRun.Status = DeepScanRun.Status::Completed then
            exit('Backend status could not be refreshed. Local scan completed successfully.');

        if DeepScanRun.Status = DeepScanRun.Status::Failed then
            exit('Backend status could not be refreshed. Local scan failed.');

        exit('Scan status could not be refreshed from the backend.');
    end;

    local procedure OpenAnalyticsDashboardForCurrentScan()
    var
        Setup: Record "DH Setup";
        ApiClient: Codeunit "DH API Client";
        Token: Text;
    begin
        LoadSetupOrError(Setup);

        Token := ApiClient.GetAnalyticsDashboardToken(Setup);

        if Token = '' then
            Error('No valid dashboard token was returned by the token service.');

        Hyperlink(GetDashboardUrl(Setup, Token));
    end;

    local procedure OpenExecutiveReportForCurrentScan(OpenPdf: Boolean)
    var
        Setup: Record "DH Setup";
        ReportUrl: Text;
        ReportType: Text;
    begin
        if not CanOpenExecutiveReport() then
            exit;

        LoadSetupOrError(Setup);

        if OpenPdf then
            ReportType := 'pdf'
        else
            ReportType := 'html';

        ReportUrl := GetExecutiveReportShareUrl(Setup, ReportType);

        Hyperlink(ReportUrl);
    end;

    local procedure CanOpenExecutiveReport(): Boolean
    begin
        if Rec."Entry No." = 0 then begin
            Message('No deep scan run is available.');
            exit(false);
        end;

        if Rec.Status <> Rec.Status::Completed then begin
            Message('The executive report is available after the deep scan is completed.');
            exit(false);
        end;

        if Rec."Run ID" = '' then begin
            Message('The completed scan does not have a backend scan ID yet.');
            exit(false);
        end;

        exit(true);
    end;

    local procedure LoadSetupOrError(var Setup: Record "DH Setup")
    begin
        if not Setup.Get('SETUP') then
            Error('DH Setup was not found.');

        if Setup."API Base URL" = '' then
            Error('Please enter the API Base URL in DH Setup first.');

        if Setup."Tenant ID" = '' then
            Error('Please register the tenant in DH Setup first.');

        if GetApiToken(Setup) = '' then
            Error('Please register the tenant in DH Setup first so that an API token is stored.');
    end;

    local procedure RequestDashboardToken(var Setup: Record "DH Setup"): Text
    var
        Client: HttpClient;
        Request: HttpRequestMessage;
        Headers: HttpHeaders;
        Response: HttpResponseMessage;
        ResponseText: Text;
        ApiClient: Codeunit "DH API Client";
    begin
        Request.Method := 'GET';
        Request.SetRequestUri(GetTokenUrl(Setup));
        Request.GetHeaders(Headers);
        Headers.Clear();
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', GetApiToken(Setup));

        if not Client.Send(Request, Response) then
            Error('The dashboard token service could not be reached.');

        Response.Content().ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error(
              'The dashboard token service returned an error. Status: %1. %2',
              Response.HttpStatusCode(),
              ApiClient.GetSafeBackendErrorText(ResponseText));

        exit(ResponseText);
    end;


    local procedure GetTokenUrl(var Setup: Record "DH Setup"): Text
    var
        BaseUrl: Text;
        CompanyValue: Text;
        EnvironmentValue: Text;
        TenantValue: Text;
        ScanModeValue: Text;
    begin
        BaseUrl := BuildUrl(Setup."API Base URL", '/analytics/get-token');
        CompanyValue := EncodeUrlValue(CompanyName());
        EnvironmentValue := EncodeUrlValue('BC Cloud');
        TenantValue := EncodeUrlValue(Setup."Tenant ID");
        ScanModeValue := EncodeUrlValue(GetScanModeQueryValue());

        exit(
          BaseUrl +
          '?company=' + CompanyValue +
          '&environment=' + EnvironmentValue +
          '&tenant_id=' + TenantValue +
          '&scan_mode=' + ScanModeValue +
          '&bc_issue_launch_url=' + EncodeUrlValue(GetIssueDrilldownLaunchUrl()));
    end;

    local procedure GetDashboardUrl(var Setup: Record "DH Setup"; Token: Text): Text
    var
        BaseUrl: Text;
    begin
        BaseUrl := BuildUrl(Setup."API Base URL", '/analytics/embed');
        exit(BaseUrl + '?embed_token=' + EncodeUrlValue(Token));
    end;

    local procedure GetExecutiveReportShareUrl(var Setup: Record "DH Setup"; ReportType: Text): Text
    var
        Client: HttpClient;
        Content: HttpContent;
        ContentHeaders: HttpHeaders;
        RequestHeaders: HttpHeaders;
        Response: HttpResponseMessage;
        RequestText: Text;
        ResponseText: Text;
        JsonRequest: JsonObject;
        ApiClient: Codeunit "DH API Client";
    begin
        JsonRequest.Add('report_type', ReportType);
        JsonRequest.WriteTo(RequestText);

        Content.WriteFrom(RequestText);
        Content.GetHeaders(ContentHeaders);
        ContentHeaders.Clear();
        ContentHeaders.Add('Content-Type', 'application/json');

        RequestHeaders := Client.DefaultRequestHeaders();
        if RequestHeaders.Contains('X-Tenant-Id') then
            RequestHeaders.Remove('X-Tenant-Id');
        if RequestHeaders.Contains('X-Api-Token') then
            RequestHeaders.Remove('X-Api-Token');
        RequestHeaders.Add('X-Tenant-Id', Setup."Tenant ID");
        RequestHeaders.Add('X-Api-Token', GetApiToken(Setup));

        if not Client.Post(BuildExecutiveShareLinkUrl(Setup), Content, Response) then
            Error('The executive report link service could not be reached.');

        Response.Content().ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error(
              'The executive report link service returned an error. Status: %1. %2',
              Response.HttpStatusCode(),
              ApiClient.GetSafeBackendErrorText(ResponseText));

        exit(ExtractUrlFromJson(ResponseText));
    end;

    local procedure BuildExecutiveShareLinkUrl(var Setup: Record "DH Setup"): Text
    begin
        exit(BuildUrl(Setup."API Base URL", '/reports/executive/' + EncodeUrlValue(Format(Rec."Run ID")) + '/share-link'));
    end;

    local procedure ExtractUrlFromJson(JsonText: Text): Text
    var
        JsonObj: JsonObject;
        JsonToken: JsonToken;
        Url: Text;
    begin
        if not JsonObj.ReadFrom(JsonText) then
            Error('The executive report link response is not valid JSON.');

        if not JsonObj.Get('url', JsonToken) then
            Error('The executive report link response does not contain a url.');

        Url := JsonToken.AsValue().AsText();
        if Url = '' then
            Error('The executive report link response contains an empty url.');

        exit(Url);
    end;

    local procedure GetIssueDrilldownLaunchUrl(): Text
    begin
        exit(GetUrl(ClientType::Web, CompanyName(), ObjectType::Page, Page::"DH Issue Drilldown Launch"));
    end;

    local procedure GetScanModeQueryValue(): Text
    begin
        if ScanTypeTxt <> '' then
            exit(LowerCase(ScanTypeTxt));

        exit('deep');
    end;

    local procedure ExtractTokenFromJson(JsonText: Text): Text
    var
        JsonObj: JsonObject;
        JsonToken: JsonToken;
    begin
        if not JsonObj.ReadFrom(JsonText) then
            Error('The token service response is not valid JSON.');

        if not JsonObj.Get('token', JsonToken) then
            Error('The field "token" is missing in the token service response.');

        exit(JsonToken.AsValue().AsText());
    end;

    local procedure BuildUrl(BaseUrl: Text; RelativePath: Text): Text
    begin
        exit(RemoveTrailingSlash(BaseUrl) + RelativePath);
    end;

    local procedure RemoveTrailingSlash(Value: Text): Text
    begin
        while (StrLen(Value) > 0) and (CopyStr(Value, StrLen(Value), 1) = '/') do
            Value := CopyStr(Value, 1, StrLen(Value) - 1);

        exit(Value);
    end;

    local procedure EncodeUrlValue(Value: Text): Text
    begin
        Value := Value.Replace('%', '%25');
        Value := Value.Replace(' ', '%20');
        Value := Value.Replace('&', '%26');
        Value := Value.Replace('?', '%3F');
        Value := Value.Replace('=', '%3D');
        Value := Value.Replace('#', '%23');
        Value := Value.Replace('+', '%2B');
        Value := Value.Replace('/', '%2F');
        exit(Value);
    end;

    local procedure GetApiToken(var Setup: Record "DH Setup"): Text
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        exit(SecretMgt.GetApiToken(Setup));
    end;
}

