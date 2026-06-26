page 53100 "DH Setup"
{
    PageType = Card;
    SourceTable = "DH Setup";
    Caption = 'BCSentinel Setup';
    ApplicationArea = All;
    UsageCategory = Administration;

    layout
    {
        area(Content)
        {
            group(SubscriptionStatus)
            {
                Caption = 'Subscription & Status';

                field(SubscriptionStatusDisplay; SubscriptionStatusTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Subscription Status';
                    Editable = false;
                    StyleExpr = SubscriptionStatusStyle;
                    ToolTip = 'Shows the current BCSentinel subscription and access status.';
                }
                field(ProductAccessDisplay; ProductAccessTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Product Access';
                    Editable = false;
                    ToolTip = 'Shows the readable product access level.';
                }
                field("Monitoring Active"; Rec."Monitoring Active")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Monitoring Active.';
                    Editable = false;
                    StyleExpr = MonitoringStyle;
                }
                field(ScheduledScanAccess; ScheduledScanAccessTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Scheduled Scans';
                    Editable = false;
                    StyleExpr = SchedulerAccessStyle;
                    ToolTip = 'Shows whether scheduled scans are available.';
                }
                field("Dashboard Access Until"; Rec."Dashboard Access Until")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Dashboard Access Until.';
                    Editable = false;
                }
                field("Issue Access Until"; Rec."Issue Access Until")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Issue Access Until.';
                    Editable = false;
                }
                field("Scan Credits Available"; Rec."Scan Credits Available")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Scan Credits Available.';
                    Editable = false;
                    StyleExpr = ScanCreditsStyle;
                }
                field("Last License Check"; Rec."Last License Check")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Last Product Access Check.';
                    Editable = false;
                }
            }

            group(ScanConfiguration)
            {
                Caption = 'Scan Configuration';

                field(ActiveModulesSummary; ActiveModulesTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Active Modules';
                    Editable = false;
                    DrillDown = true;
                    StyleExpr = ModuleConfigStyle;
                    ToolTip = 'Shows how many scan modules are active.';

                    trigger OnDrillDown()
                    begin
                        Page.Run(Page::"DH Scan Modules");
                    end;
                }
                field(ActiveChecksSummary; ActiveChecksTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Active Checks';
                    Editable = false;
                    DrillDown = true;
                    StyleExpr = ChecksConfigStyle;
                    ToolTip = 'Shows how many checks are active for the current module selection.';

                    trigger OnDrillDown()
                    begin
                        OpenChecksSelection();
                    end;
                }
                field(ScanConfigurationStatus; ScanConfigurationStatusTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Scan Status';
                    Editable = false;
                    MultiLine = true;
                    StyleExpr = ScanConfigurationStyle;
                    ToolTip = 'Shows whether the scan configuration is ready.';
                }
            }

            group(ScheduledScans)
            {
                Caption = 'Scheduled Scans';

                field(SchedulerNotice; SchedulerNoticeTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Scheduler Notice';
                    Editable = false;
                    MultiLine = true;
                    StyleExpr = SchedulerAccessStyle;
                    ToolTip = 'Shows scheduler availability.';
                }
                field("Scheduled Scans Enabled"; Rec."Scheduled Scans Enabled")
                {
                    ApplicationArea = All;
                    Editable = CanUseScheduler;
                    ToolTip = 'Specifies whether scheduled scans are enabled.';

                    trigger OnValidate()
                    begin
                        UpdateActionState();
                        UpdateDisplayValues();
                    end;
                }
                field("Schedule Frequency"; Rec."Schedule Frequency")
                {
                    ApplicationArea = All;
                    Editable = CanEditSchedulerDetails;
                    ToolTip = 'Specifies how often scheduled scans should run.';

                    trigger OnValidate()
                    begin
                        UpdateSchedulerVisibility();
                    end;
                }
                field("Schedule Time"; Rec."Schedule Time")
                {
                    ApplicationArea = All;
                    Editable = CanEditSchedulerDetails;
                    ToolTip = 'Specifies the local time for scheduled scans.';
                }
                group(WeeklyDays)
                {
                    Caption = 'Weekly Days';
                    Visible = ShowWeeklySchedulerFields;

                    field("Schedule Monday"; Rec."Schedule Monday") { ApplicationArea = All; Editable = CanEditSchedulerDetails; }
                    field("Schedule Tuesday"; Rec."Schedule Tuesday") { ApplicationArea = All; Editable = CanEditSchedulerDetails; }
                    field("Schedule Wednesday"; Rec."Schedule Wednesday") { ApplicationArea = All; Editable = CanEditSchedulerDetails; }
                    field("Schedule Thursday"; Rec."Schedule Thursday") { ApplicationArea = All; Editable = CanEditSchedulerDetails; }
                    field("Schedule Friday"; Rec."Schedule Friday") { ApplicationArea = All; Editable = CanEditSchedulerDetails; }
                    field("Schedule Saturday"; Rec."Schedule Saturday") { ApplicationArea = All; Editable = CanEditSchedulerDetails; }
                    field("Schedule Sunday"; Rec."Schedule Sunday") { ApplicationArea = All; Editable = CanEditSchedulerDetails; }
                }
                field("Monthly Schedule Day"; Rec."Monthly Schedule Day")
                {
                    ApplicationArea = All;
                    Editable = CanEditSchedulerDetails;
                    Visible = ShowMonthlySchedulerFields;
                    ToolTip = 'Specifies the day of month for monthly scheduled scans.';
                }
                field("Next Scheduled Scan"; Rec."Next Scheduled Scan")
                {
                    ApplicationArea = All;
                    Editable = false;
                    ToolTip = 'Specifies the next scheduled scan.';
                }
                field("Last Scheduled Scan"; Rec."Last Scheduled Scan")
                {
                    ApplicationArea = All;
                    Editable = false;
                    ToolTip = 'Specifies the last scheduled scan.';
                }
                field("Last Scheduled Scan Result"; Rec."Last Scheduled Scan Result")
                {
                    ApplicationArea = All;
                    Editable = false;
                    StyleExpr = LastScheduledResultStyle;
                    ToolTip = 'Specifies the last scheduled scan result.';
                }
                field("Last Scheduled Scan Duration"; Rec."Last Scheduled Scan Duration")
                {
                    ApplicationArea = All;
                    Editable = false;
                    ToolTip = 'Specifies the last scheduled scan duration.';
                }
                field("Scheduled Scan Failure Count"; Rec."Scheduled Scan Failure Count")
                {
                    ApplicationArea = All;
                    Editable = false;
                    StyleExpr = ScheduledFailureStyle;
                    ToolTip = 'Specifies the scheduled scan failure count.';
                }
                field("Last Scheduled Scan Error"; Rec."Last Scheduled Scan Error")
                {
                    ApplicationArea = All;
                    Editable = false;
                    MultiLine = true;
                    StyleExpr = ScheduledFailureStyle;
                    ToolTip = 'Specifies the last scheduled scan error.';
                }
            }

            group(Connection)
            {
                Caption = 'Connection';

                field("API Base URL"; Rec."API Base URL")
                {
                    ApplicationArea = All;
                    Editable = true;
                    ToolTip = 'Base URL of the BCSentinel API. Default is production.';

                    trigger OnValidate()
                    begin
                        UpdateActionState();
                    end;
                }

                field("Contact Email"; Rec."Contact Email")
                {
                    ApplicationArea = All;
                    ToolTip = 'Contact email used for BCSentinel onboarding and future dashboard login.';

                    trigger OnValidate()
                    begin
                        UpdateActionState();
                    end;
                }

                field("Tenant ID"; Rec."Tenant ID")
                {
                    ApplicationArea = All;
                    Caption = 'Tenant ID';
                    ToolTip = 'Specifies Tenant ID.';
                    Editable = false;
                }

                field(ApiTokenConfigured; HasStoredApiToken())
                {
                    ApplicationArea = All;
                    Caption = 'API Token Configured';
                    Editable = false;
                    ToolTip = 'Shows whether the API token is stored securely for this company. The token itself is not displayed.';
                }

                field("Registration Invite Code"; Rec."Registration Invite Code")
                {
                    ApplicationArea = All;
                    ExtendedDatatype = Masked;
                    ToolTip = 'Specifies the BCSentinel pilot invite code. Current backend registration requires this code; AppSource self-service signup is a follow-up backend task.';
                    Visible = false;
                }

                field(Registered; Rec.Registered)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Registered.';
                    Editable = false;
                }

                field("Registration Date"; Rec."Registration Date")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Registration Date.';
                    Editable = false;
                }

                field("Data Processing Consent"; Rec."Data Processing Consent")
                {
                    ApplicationArea = All;
                    ToolTip = 'Confirms that BCSentinel may send tenant and company identifiers, metadata, configuration data, scan results, findings, and aggregated quality metrics to BCSentinel for data health analysis, dashboards, executive reports, and license or credit checks. API tokens are stored securely and are not included in reports or share URLs. Review the privacy policy and terms before enabling consent.';

                    trigger OnValidate()
                    begin
                        UpdateActionState();
                    end;
                }

                field(DataProcessingNotice; DataProcessingNoticeTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Data Processing Notice';
                    Editable = false;
                    MultiLine = true;
                    ToolTip = 'Explains which data BCSentinel sends to the backend and why consent is required.';
                }

                field(InviteNotice; InviteNoticeTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Onboarding Notice';
                    Editable = false;
                    MultiLine = true;
                    ToolTip = 'Explains the current pilot invite requirement for tenant registration.';
                    Visible = false;
                }
            }

            group(ModuleHealthScores)
            {
                Caption = 'Module Health Scores (Last Scan)';

                field(ModuleScoresNotice; ModuleScoresNoticeTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Status';
                    Editable = false;
                    MultiLine = true;
                    Visible = ShowNoScanNotice;
                    ToolTip = 'Shows whether module scores are available.';
                }
                field(SystemModuleScore; SystemModuleScoreTxt) { ApplicationArea = All; Caption = 'System'; Editable = false; StyleExpr = SystemModuleScoreStyle; }
                field(FinanceModuleScore; FinanceModuleScoreTxt) { ApplicationArea = All; Caption = 'Finance'; Editable = false; StyleExpr = FinanceModuleScoreStyle; }
                field(SalesModuleScore; SalesModuleScoreTxt) { ApplicationArea = All; Caption = 'Sales'; Editable = false; StyleExpr = SalesModuleScoreStyle; }
                field(PurchasingModuleScore; PurchasingModuleScoreTxt) { ApplicationArea = All; Caption = 'Purchasing'; Editable = false; StyleExpr = PurchasingModuleScoreStyle; }
                field(InventoryModuleScore; InventoryModuleScoreTxt) { ApplicationArea = All; Caption = 'Inventory'; Editable = false; StyleExpr = InventoryModuleScoreStyle; }
                field(CRMModuleScore; CRMModuleScoreTxt) { ApplicationArea = All; Caption = 'CRM'; Editable = false; StyleExpr = CRMModuleScoreStyle; }
                field(ManufacturingModuleScore; ManufacturingModuleScoreTxt) { ApplicationArea = All; Caption = 'Manufacturing'; Editable = false; StyleExpr = ManufacturingModuleScoreStyle; }
                field(ServiceModuleScore; ServiceModuleScoreTxt) { ApplicationArea = All; Caption = 'Service'; Editable = false; StyleExpr = ServiceModuleScoreStyle; }
                field(JobsModuleScore; JobsModuleScoreTxt) { ApplicationArea = All; Caption = 'Jobs'; Editable = false; StyleExpr = JobsModuleScoreStyle; }
                field(HRModuleScore; HRModuleScoreTxt) { ApplicationArea = All; Caption = 'HR'; Editable = false; StyleExpr = HRModuleScoreStyle; }
            }

            group(LastScan)
            {
                Caption = 'Last Scan';

                field(LastScanRunId; LastScanRunIdTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Last Scan ID';
                    Editable = false;
                    ToolTip = 'Specifies the last scan ID.';
                }
                field(LastScanDate; LastScanDateValue)
                {
                    ApplicationArea = All;
                    Caption = 'Last Scan Date';
                    Editable = false;
                    ToolTip = 'Specifies the last scan date.';
                }
                field(LastScanScore; LastScanScoreTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Data Health Score';
                    Editable = false;
                    StyleExpr = LastScanScoreStyle;
                    ToolTip = 'Specifies the last data health score.';
                }
                field(LastScanIssues; LastScanIssuesValue)
                {
                    ApplicationArea = All;
                    Caption = 'Issues';
                    Editable = false;
                    StyleExpr = LastScanIssuesStyle;
                    ToolTip = 'Specifies the issue count from the last scan.';
                }
                field(LastScanEstimatedLoss; LastScanEstimatedLossValue)
                {
                    ApplicationArea = All;
                    Caption = 'Estimated Loss EUR';
                    Editable = false;
                    StyleExpr = LastScanLossStyle;
                    ToolTip = 'Specifies the estimated loss from the last scan.';
                }
                field(LastScanDuration; LastScanDurationTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Duration';
                    Editable = false;
                    ToolTip = 'Specifies the duration of the last scan.';
                }
                field(LastScanStatus; LastScanStatusTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Last Scan Status';
                    Editable = false;
                    StyleExpr = LastScanStatusStyle;
                    ToolTip = 'Specifies the last scan status.';
                }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(TestConnection)
            {
                Caption = 'Test BCSentinel Connection';
                ToolTip = 'Runs Test BCSentinel Connection.';
                ApplicationArea = All;
                Image = TestFile;

                trigger OnAction()
                var
                    ApiClient: Codeunit "DH API Client";
                begin
                    ApiClient.TestConnection(Rec);
                end;
            }

            action(RegisterTenant)
            {
                Caption = 'Register Tenant';
                ToolTip = 'Registers this Business Central tenant with BCSentinel.';
                ApplicationArea = All;
                Image = Web;
                Enabled = CanRegisterTenant;
                Visible = true;
                Promoted = true;
                PromotedCategory = Process;
                PromotedOnly = false;

                trigger OnAction()
                var
                    ApiClient: Codeunit "DH API Client";
                begin
                    if Rec."Tenant ID" <> '' then begin
                        Message('BCSentinel tenant is already registered.');
                        exit;
                    end;

                    Rec.EnsureValidContactEmail();

                    if Rec.Registered then begin
                        if HasStoredApiToken() then begin
                            Message('BCSentinel tenant is already registered.');
                            exit;
                        end;

                        Message('BCSentinel registration data is incomplete. Registration will request a fresh API token.');
                    end;

                    Message('BCSentinel tenant registration started.');
                    ApiClient.RegisterTenant(Rec);
                    ApiClient.RefreshLicenseStatus(Rec);
                    UpdateActionState();
                    CurrPage.Update(false);
                    Message('BCSentinel tenant registration completed.');
                end;
            }

            action(ResetRegistration)
            {
                Caption = 'Reset Registration';
                ToolTip = 'Clears only the local BCSentinel registration state and stored API token so the tenant can be registered again. Backend data is not deleted.';
                ApplicationArea = All;
                Image = ResetStatus;
                Enabled = CanResetRegistration;
                Visible = true;
                Promoted = true;
                PromotedCategory = Process;
                PromotedOnly = false;

                trigger OnAction()
                var
                    ResetRegistrationQst: Label 'Reset BCSentinel registration? This creates a new tenant identity. Existing purchases, credits, Full Analysis, Validation Check, and Monitoring will no longer be linked to this Business Central company. Continue only if you understand this.';
                begin
                    if not Confirm(ResetRegistrationQst, false) then
                        exit;

                    ResetLocalRegistrationState();
                    UpdateActionState();
                    CurrPage.Update(false);
                    Message('Local BCSentinel registration was reset. Please register again.');
                end;
            }

            action(RequestAccess)
            {
                Caption = 'Request Access';
                ToolTip = 'Opens the BCSentinel website to request onboarding access.';
                ApplicationArea = All;
                Image = LinkWeb;
                Visible = false;

                trigger OnAction()
                begin
                    Hyperlink('https://bcsentinel.com');
                end;
            }

            action(BuyFullAnalysis)
            {
                Caption = 'Buy Full Analysis';
                ApplicationArea = All;
                Image = Add;
                ToolTip = 'Open the secure BCSentinel checkout for Full Analysis.';
                Visible = ShowBuyFullAnalysis;

                trigger OnAction()
                var
                    ApiClient: Codeunit "DH API Client";
                begin
                    ApiClient.OpenProductCheckout(Rec, 'full_analysis');
                end;
            }

            action(BuyValidationCheck)
            {
                Caption = 'Buy Validation Check / New Credit';
                ApplicationArea = All;
                Image = Add;
                ToolTip = 'Open the secure BCSentinel checkout for a Validation Check follow-up scan.';
                Visible = ShowBuyValidationCheck;

                trigger OnAction()
                var
                    ApiClient: Codeunit "DH API Client";
                begin
                    ApiClient.OpenProductCheckout(Rec, 'validation_check');
                end;
            }

            action(StartMonitoringMonthly)
            {
                Caption = 'Start Monitoring Monthly';
                ApplicationArea = All;
                Image = Add;
                ToolTip = 'Open the secure BCSentinel checkout for monthly monitoring.';
                Visible = ShowStartMonitoring;

                trigger OnAction()
                var
                    ApiClient: Codeunit "DH API Client";
                begin
                    ApiClient.OpenProductCheckout(Rec, 'monitoring_monthly');
                end;
            }

            action(StartMonitoringAnnual)
            {
                Caption = 'Start Monitoring Annual';
                ApplicationArea = All;
                Image = Add;
                ToolTip = 'Open the secure BCSentinel checkout for annual monitoring.';
                Visible = ShowStartMonitoring;

                trigger OnAction()
                var
                    ApiClient: Codeunit "DH API Client";
                begin
                    ApiClient.OpenProductCheckout(Rec, 'monitoring_annual');
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
                    ApiClient: Codeunit "DH API Client";
                begin
                    if Rec."Tenant ID" = '' then
                        Error('Please register the tenant first.');

                    ApiClient.RefreshLicenseStatus(Rec);
                    CurrPage.Update(false);
                    Message('Product access refreshed.');
                end;
            }

            action(OpenDashboard)
            {
                Caption = 'Open Dashboard';
                ApplicationArea = All;
                Image = View;
                ToolTip = 'Opens the BCSentinel dashboard for this tenant.';
                Enabled = CanOpenDashboard;
                Promoted = true;
                PromotedCategory = Process;

                trigger OnAction()
                var
                    ApiClient: Codeunit "DH API Client";
                    Token: Text;
                begin
                    Token := ApiClient.GetAnalyticsDashboardToken(Rec);
                    Hyperlink(GetDashboardUrl(Rec, Token));
                end;
            }

            group(ScanMenu)
            {
                Caption = 'Scan';
                Image = Start;

                action(StartScan)
                {
                    Caption = 'Start Free Data Health Score';
                    ToolTip = 'Starts the free Data Health Score scan.';
                    Image = Start;
                    ApplicationArea = All;
                    Enabled = CanStartFreeDataHealthScore;
                    Visible = ShowStartFreeDataHealthScore;

                    trigger OnAction()
                    var
                        Setup: Record "DH Setup";
                        DeepScanRun: Record "DH Deep Scan Run";
                        DeepScanMgt: Codeunit "DH Deep Scan Mgt.";
                        EntryNo: Integer;
                        ConfirmStartScanQst: Label 'Do you want to start the free Data Health Score now? Performance may be affected during live operations. We recommend running the scan outside business hours.';
                    begin
                        EnsureSetupExists();
                        Setup := Rec;
                        if not Confirm(ConfirmStartScanQst, false) then
                            exit;

                        EntryNo := DeepScanMgt.QueueDataHealthScore(Setup);
                        Rec.Get('SETUP');
                        Rec."Data Health Score Completed" := true;
                        Rec."Can Run Data Health Score" := false;
                        Rec.Modify(true);
                        UpdateActionState();
                        CurrPage.Update(false);
                        if DeepScanRun.Get(EntryNo) then
                            Page.Run(Page::"DH Deep Scan Monitor", DeepScanRun);
                    end;
                }

                action(FreeDataHealthScoreCompleted)
                {
                    Caption = 'Start Free Data Health Score';
                    ToolTip = 'Free Data Health Score already completed.';
                    Image = Start;
                    ApplicationArea = All;
                    Enabled = false;
                    Visible = ShowFreeDataHealthScoreCompleted;
                }

                action(StartPaidDeepScan)
                {
                    Caption = 'Start Scan';
                    ToolTip = 'Starts a Validation Check follow-up scan using active access.';
                    Image = Start;
                    ApplicationArea = All;
                    Enabled = CanStartValidationCheck;
                    Visible = ShowStartValidationCheck;

                    trigger OnAction()
                    var
                        Setup: Record "DH Setup";
                        DeepScanRun: Record "DH Deep Scan Run";
                        ApiClient: Codeunit "DH API Client";
                        DeepScanMgt: Codeunit "DH Deep Scan Mgt.";
                        EntryNo: Integer;
                    begin
                        EnsureSetupExists();
                        Setup := Rec;
                        ApiClient.EnsureReadyForScan(Setup);
                        EntryNo := DeepScanMgt.QueueDeepScan(Setup);
                        CurrPage.Update(false);
                        if DeepScanRun.Get(EntryNo) then
                            Page.Run(Page::"DH Deep Scan Monitor", DeepScanRun);
                    end;
                }

                action(StartValidationCheckBeforeFreeScore)
                {
                    Caption = 'Start Validation Check';
                    ToolTip = 'Run the free Data Health Score first.';
                    Image = Start;
                    ApplicationArea = All;
                    Enabled = false;
                    Visible = ShowValidationCheckRequiresFreeScore;
                }

                action(ViewScanHistory)
                {
                    Caption = 'Scan History';
                    ToolTip = 'Runs Scan History.';
                    Image = List;
                    ApplicationArea = All;

                    trigger OnAction()
                    begin
                        Page.Run(Page::"DH Deep Scan Runs");
                    end;
                }

                action(OpenLatestScanMonitor)
                {
                    Caption = 'Open Scan Monitor';
                    ToolTip = 'Opens the scan monitor for the latest deep scan.';
                    Image = ViewDetails;
                    ApplicationArea = All;
                    Enabled = CanOpenLatestMonitor;

                    trigger OnAction()
                    begin
                        OpenLatestMonitor();
                    end;
                }

                action(SelectScanChecks)
                {
                    Caption = 'Select Checks';
                    ToolTip = 'Selects the checks that are included in Monitoring scans.';
                    Image = CheckList;
                    ApplicationArea = All;
                    Enabled = CanSelectScanChecks;
                    Visible = true;
                    Promoted = true;
                    PromotedCategory = Process;

                    trigger OnAction()
                    begin
                        OpenChecksSelection();
                    end;
                }

                action(ConfigureModules)
                {
                    Caption = 'Configure Modules';
                    ToolTip = 'Opens the BCSentinel scan module configuration.';
                    Image = Setup;
                    ApplicationArea = All;
                    Promoted = true;
                    PromotedCategory = Process;

                    trigger OnAction()
                    begin
                        Page.Run(Page::"DH Scan Modules");
                    end;
                }
            }

            group(SchedulerActions)
            {
                Caption = 'Scheduler';
                Image = Calendar;

                action(RunScheduledScanNow)
                {
                    Caption = 'Run now';
                    ToolTip = 'Starts a Monitoring scan immediately and opens the scan monitor.';
                    Image = Start;
                    ApplicationArea = All;
                    Enabled = CanUseScheduler;
                    Promoted = true;
                    PromotedCategory = Process;

                    trigger OnAction()
                    var
                        SchedulerMgt: Codeunit "DH Scan Scheduler Mgt.";
                        DeepScanRun: Record "DH Deep Scan Run";
                        EntryNo: Integer;
                    begin
                        EntryNo := SchedulerMgt.RunNow(Rec);
                        UpdateActionState();
                        UpdateDisplayValues();
                        CurrPage.Update(false);
                        if DeepScanRun.Get(EntryNo) then
                            Page.Run(Page::"DH Deep Scan Monitor", DeepScanRun);
                    end;
                }

                action(CalculateNextRun)
                {
                    Caption = 'Calculate Next Run';
                    ToolTip = 'Calculates the next scheduled scan date and time.';
                    Image = CalculateCalendar;
                    ApplicationArea = All;
                    Enabled = CanUseScheduler;

                    trigger OnAction()
                    var
                        SchedulerMgt: Codeunit "DH Scan Scheduler Mgt.";
                        NextRun: DateTime;
                    begin
                        NextRun := SchedulerMgt.CalculateNextRun(Rec);
                        UpdateDisplayValues();
                        CurrPage.Update(false);
                        Message('Next scheduled scan: %1', NextRun);
                    end;
                }

                action(RescheduleScheduler)
                {
                    Caption = 'Reschedule Scheduler';
                    ToolTip = 'Schedules the next Monitoring scan with the Business Central TaskScheduler.';
                    Image = Calendar;
                    ApplicationArea = All;
                    Enabled = CanEditSchedulerDetails;

                    trigger OnAction()
                    var
                        SchedulerMgt: Codeunit "DH Scan Scheduler Mgt.";
                    begin
                        SchedulerMgt.Reschedule(Rec);
                        UpdateDisplayValues();
                        CurrPage.Update(false);
                    end;
                }

                action(DisableScheduler)
                {
                    Caption = 'Disable Scheduler';
                    ToolTip = 'Disables scheduled scans.';
                    Image = Cancel;
                    ApplicationArea = All;
                    Enabled = Rec."Scheduled Scans Enabled";

                    trigger OnAction()
                    var
                        SchedulerMgt: Codeunit "DH Scan Scheduler Mgt.";
                    begin
                        SchedulerMgt.DisableScheduler(Rec);
                        UpdateActionState();
                        UpdateDisplayValues();
                        CurrPage.Update(false);
                    end;
                }
            }

            group(HelpSupport)
            {
                Caption = 'Help & Support';
                Image = Help;

                action(OpenDocumentation)
                {
                    Caption = 'Documentation';
                    ToolTip = 'Opens BCSentinel documentation.';
                    Image = Help;
                    ApplicationArea = All;

                    trigger OnAction()
                    begin
                        Hyperlink('https://bcsentinel.com/documentation');
                    end;
                }

                action(OpenSupport)
                {
                    Caption = 'Support';
                    ToolTip = 'Opens BCSentinel support.';
                    Image = Help;
                    ApplicationArea = All;

                    trigger OnAction()
                    begin
                        Hyperlink('https://bcsentinel.com/support');
                    end;
                }

                action(OpenPrivacySecurity)
                {
                    Caption = 'Privacy & Security';
                    ToolTip = 'Opens BCSentinel privacy and security information.';
                    Image = Lock;
                    ApplicationArea = All;

                    trigger OnAction()
                    begin
                        Hyperlink('https://bcsentinel.com/privacy.html');
                    end;
                }
            }
        }
    }

    var
        CanRegisterTenant: Boolean;
        CanResetRegistration: Boolean;
        CanStartFreeDataHealthScore: Boolean;
        CanStartValidationCheck: Boolean;
        ShowStartFreeDataHealthScore: Boolean;
        ShowFreeDataHealthScoreCompleted: Boolean;
        ShowStartValidationCheck: Boolean;
        ShowValidationCheckRequiresFreeScore: Boolean;
        CanSelectScanChecks: Boolean;
        CanUseScheduler: Boolean;
        CanEditSchedulerDetails: Boolean;
        CanOpenDashboard: Boolean;
        CanOpenLatestMonitor: Boolean;
        ShowBuyFullAnalysis: Boolean;
        ShowBuyValidationCheck: Boolean;
        ShowStartMonitoring: Boolean;
        ShowWeeklySchedulerFields: Boolean;
        ShowMonthlySchedulerFields: Boolean;
        ShowNoScanNotice: Boolean;
        DataProcessingNoticeTxt: Text[1024];
        InviteNoticeTxt: Text[512];
        SubscriptionStatusTxt: Text[100];
        ProductAccessTxt: Text[100];
        ScheduledScanAccessTxt: Text[100];
        ActiveModulesTxt: Text[100];
        ActiveChecksTxt: Text[100];
        ScanConfigurationStatusTxt: Text[250];
        SchedulerNoticeTxt: Text[250];
        ModuleScoresNoticeTxt: Text[100];
        LastScanRunIdTxt: Text[50];
        LastScanDateValue: DateTime;
        LastScanScoreTxt: Text[30];
        LastScanIssuesValue: Integer;
        LastScanEstimatedLossValue: Decimal;
        LastScanDurationTxt: Text[50];
        LastScanStatusTxt: Text[100];
        SystemModuleScoreTxt: Text[50];
        FinanceModuleScoreTxt: Text[50];
        SalesModuleScoreTxt: Text[50];
        PurchasingModuleScoreTxt: Text[50];
        InventoryModuleScoreTxt: Text[50];
        CRMModuleScoreTxt: Text[50];
        ManufacturingModuleScoreTxt: Text[50];
        ServiceModuleScoreTxt: Text[50];
        JobsModuleScoreTxt: Text[50];
        HRModuleScoreTxt: Text[50];
        SubscriptionStatusStyle: Text[30];
        MonitoringStyle: Text[30];
        SchedulerAccessStyle: Text[30];
        ScanCreditsStyle: Text[30];
        ModuleConfigStyle: Text[30];
        ChecksConfigStyle: Text[30];
        ScanConfigurationStyle: Text[30];
        LastScheduledResultStyle: Text[30];
        ScheduledFailureStyle: Text[30];
        LastScanScoreStyle: Text[30];
        LastScanIssuesStyle: Text[30];
        LastScanLossStyle: Text[30];
        LastScanStatusStyle: Text[30];
        SystemModuleScoreStyle: Text[30];
        FinanceModuleScoreStyle: Text[30];
        SalesModuleScoreStyle: Text[30];
        PurchasingModuleScoreStyle: Text[30];
        InventoryModuleScoreStyle: Text[30];
        CRMModuleScoreStyle: Text[30];
        ManufacturingModuleScoreStyle: Text[30];
        ServiceModuleScoreStyle: Text[30];
        JobsModuleScoreStyle: Text[30];
        HRModuleScoreStyle: Text[30];

    trigger OnOpenPage()
    begin
        EnsureSetupExists();
        UpdateActionState();
        UpdateNoticeTexts();
        UpdateDisplayValues();
        //RefreshLicenseSilently();
        CurrPage.Update(false);
    end;

    trigger OnAfterGetCurrRecord()
    begin
        UpdateActionState();
        UpdateNoticeTexts();
        UpdateDisplayValues();
    end;

    local procedure EnsureSetupExists()
    begin
        if not Rec.Get('SETUP') then begin
            Rec.Init();
            Rec."Primary Key" := 'SETUP';
            Rec.Insert(true);
        end;

        Rec.ApplyDefaults();
        Rec.Modify(true);
    end;

    local procedure HasStoredApiToken(): Boolean
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        exit(SecretMgt.HasApiToken(Rec));
    end;

    local procedure DeleteStoredApiToken()
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        SecretMgt.DeleteApiToken(Rec);
    end;

    local procedure ResetLocalRegistrationState()
    begin
        Rec."Tenant ID" := '';
        Rec.Registered := false;
        Rec."Registration Date" := 0DT;
        Rec."Can Run Data Health Score" := true;
        Rec."Data Health Score Completed" := false;
        Rec."Scan Credits Available" := 0;
        Rec."Monitoring Active" := false;
        Rec."Dashboard Access Until" := '';
        Rec."Issue Access Until" := '';
        Rec."Can Run Deep Scan" := false;
        Rec."Can View Dashboard" := false;
        Rec."Can View Issue Details" := false;
        Rec."Product Access Model" := '';
        DeleteStoredApiToken();
        Rec.Modify(true);
    end;

    local procedure RefreshLicenseSilently()
    var
        ApiClient: Codeunit "DH API Client";
    begin
        if Rec."Tenant ID" = '' then
            exit;

        ApiClient.RefreshLicenseStatus(Rec);
    end;

    local procedure UpdateActionState()
    var
        HasCompletedFreeScore: Boolean;
        HasOneTimeAccess: Boolean;
    begin
        HasCompletedFreeScore := HasCompletedDataHealthScore();
        HasOneTimeAccess :=
            Rec."Can View Issue Details" or
            Rec."Premium Enabled" or
            (LowerCase(Rec."Product Access Model") = 'one_time');
        CanRegisterTenant := (Rec."Tenant ID" = '') and Rec."Data Processing Consent" and (Rec."API Base URL" <> '') and Rec.HasValidContactEmail();
        CanResetRegistration :=
            Rec.Registered or
            (Rec."Tenant ID" <> '') or
            (Rec."Registration Date" <> 0DT) or
            HasStoredApiToken();
        CanStartFreeDataHealthScore := (Rec."Tenant ID" <> '') and not HasCompletedFreeScore;
        ShowStartFreeDataHealthScore := not HasCompletedFreeScore;
        ShowFreeDataHealthScoreCompleted := HasCompletedFreeScore;
        CanStartValidationCheck := (Rec."Tenant ID" <> '') and HasCompletedFreeScore;
        ShowStartValidationCheck := HasCompletedFreeScore;
        ShowValidationCheckRequiresFreeScore := not HasCompletedFreeScore;
        CanSelectScanChecks := (Rec."Tenant ID" <> '') and Rec."Monitoring Active";
        CanUseScheduler := (Rec."Tenant ID" <> '') and Rec."Monitoring Active";
        CanEditSchedulerDetails := CanUseScheduler and Rec."Scheduled Scans Enabled";
        CanOpenDashboard := (Rec."Tenant ID" <> '') and HasStoredApiToken();
        CanOpenLatestMonitor := LastDeepScanRunExists();
        UpdateSchedulerVisibility();
        ShowBuyFullAnalysis := (Rec."Tenant ID" <> '') and not Rec."Monitoring Active" and not HasOneTimeAccess;
        ShowBuyValidationCheck := (Rec."Tenant ID" <> '') and not Rec."Monitoring Active" and HasOneTimeAccess;
        ShowStartMonitoring := (Rec."Tenant ID" <> '') and not Rec."Monitoring Active";
    end;

    local procedure HasCompletedDataHealthScore(): Boolean
    var
        DeepScanRun: Record "DH Deep Scan Run";
    begin
        if Rec."Data Health Score Completed" then
            exit(true);

        DeepScanRun.Reset();
        DeepScanRun.SetRange("Scan Mode", 'data_health_score');
        DeepScanRun.SetRange(Status, DeepScanRun.Status::Completed);
        exit(not DeepScanRun.IsEmpty());
    end;

    local procedure UpdateNoticeTexts()
    begin
        DataProcessingNoticeTxt :=
            'Before registration or scans, BCSentinel requires consent to send tenant and company identifiers, metadata, configuration data, scan results, findings, and aggregated quality metrics to BCSentinel. The data is used for Data Health analysis, dashboards, executive reports, and license or credit checks. API tokens are stored securely and are not included in reports or share URLs. Review the privacy policy and terms before enabling consent.';

        InviteNoticeTxt := '';
    end;

    local procedure UpdateDisplayValues()
    var
        SchedulerMgt: Codeunit "DH Scan Scheduler Mgt.";
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
        LastRun: Record "DH Deep Scan Run";
        EnabledChecks: Integer;
        TotalChecks: Integer;
    begin
        Rec.EnsureSchedulerDefaults();
        SubscriptionStatusTxt := Rec.GetSubscriptionStatusDisplay();
        ProductAccessTxt := Rec.GetProductAccessDisplay();
        ScheduledScanAccessTxt := Rec.GetScheduledScanAccessDisplay();
        ActiveModulesTxt := SchedulerMgt.GetActiveModulesSummary(Rec);
        ActiveChecksTxt := SchedulerMgt.GetActiveChecksSummary(Rec);
        EnabledChecks := ScanCheckMgt.GetExpectedChecksCount(Rec);
        TotalChecks := ScanCheckMgt.GetTotalModuleChecksCount(Rec);

        if not Rec.HasAnyModuleEnabled() then begin
            ScanConfigurationStatusTxt := 'Scan not possible. At least one module must be active.';
            ScanConfigurationStyle := 'Unfavorable';
        end else
            if Rec."Monitoring Active" and (EnabledChecks = 0) and (TotalChecks > 0) then begin
                ScanConfigurationStatusTxt := 'Scan not possible. At least one check must be active.';
                ScanConfigurationStyle := 'Unfavorable';
            end else begin
                ScanConfigurationStatusTxt := 'Scan possible. Required modules and checks are available.';
                ScanConfigurationStyle := 'Favorable';
            end;

        if Rec."Monitoring Active" then
            SchedulerNoticeTxt := 'Scheduled scans are available with active Monitoring.'
        else
            SchedulerNoticeTxt := 'Scheduled scans require an active Monitoring subscription.';

        SubscriptionStatusStyle := GetAccessStyle(Rec."Monitoring Active" or Rec."Can View Issue Details" or Rec."Premium Enabled");
        MonitoringStyle := GetAccessStyle(Rec."Monitoring Active");
        SchedulerAccessStyle := GetAccessStyle(Rec."Monitoring Active");
        if Rec."Scan Credits Available" > 0 then
            ScanCreditsStyle := 'Favorable'
        else
            ScanCreditsStyle := 'Standard';

        ModuleConfigStyle := GetAccessStyle(Rec.HasAnyModuleEnabled());
        ChecksConfigStyle := GetAccessStyle(EnabledChecks > 0);
        LastScheduledResultStyle := GetScheduledResultStyle();
        if Rec."Scheduled Scan Failure Count" > 0 then
            ScheduledFailureStyle := 'Unfavorable'
        else
            ScheduledFailureStyle := 'Standard';

        LoadLastScan(LastRun);
        UpdateModuleScoreTexts(LastRun);
    end;

    local procedure UpdateSchedulerVisibility()
    begin
        ShowWeeklySchedulerFields := Rec."Schedule Frequency" = Rec."Schedule Frequency"::Weekly;
        ShowMonthlySchedulerFields := Rec."Schedule Frequency" = Rec."Schedule Frequency"::Monthly;
    end;

    local procedure LoadLastScan(var LastRun: Record "DH Deep Scan Run")
    begin
        Clear(LastRun);
        LastScanRunIdTxt := '';
        LastScanDateValue := 0DT;
        LastScanScoreTxt := '';
        LastScanIssuesValue := 0;
        LastScanEstimatedLossValue := 0;
        LastScanDurationTxt := '';
        LastScanStatusTxt := '';
        ShowNoScanNotice := true;
        ModuleScoresNoticeTxt := 'No scan available yet.';

        LastRun.Reset();
        LastRun.SetCurrentKey("Requested At");
        LastRun.Ascending(false);
        if not LastRun.FindFirst() then begin
            LastScanStatusTxt := 'No scan available yet.';
            LastScanStatusStyle := 'Standard';
            exit;
        end;

        ShowNoScanNotice := false;
        ModuleScoresNoticeTxt := '';
        LastScanRunIdTxt := LastRun."Run ID";
        LastScanDateValue := LastRun."Requested At";
        LastScanScoreTxt := StrSubstNo('%1 / 100', LastRun."Deep Score");
        LastScanIssuesValue := LastRun."Issues Count";
        LastScanEstimatedLossValue := LastRun."Estimated Loss (EUR)";
        LastScanDurationTxt := GetDurationText(LastRun);
        LastScanStatusTxt := Format(LastRun.Status);
        LastScanScoreStyle := GetScoreStyle(LastRun."Deep Score");
        LastScanIssuesStyle := GetIssueStyle(LastRun."Issues Count");
        LastScanLossStyle := GetAmountStyle(LastRun."Estimated Loss (EUR)");
        LastScanStatusStyle := GetRunStatusStyle(LastRun);
    end;

    local procedure UpdateModuleScoreTexts(var LastRun: Record "DH Deep Scan Run")
    begin
        SystemModuleScoreTxt := FormatModuleScore(LastRun."System Score");
        FinanceModuleScoreTxt := FormatModuleScore(LastRun."Finance Score");
        SalesModuleScoreTxt := FormatModuleScore(LastRun."Sales Score");
        PurchasingModuleScoreTxt := FormatModuleScore(LastRun."Purchasing Score");
        InventoryModuleScoreTxt := FormatModuleScore(LastRun."Inventory Score");
        CRMModuleScoreTxt := FormatModuleScore(LastRun."CRM Score");
        ManufacturingModuleScoreTxt := FormatModuleScore(LastRun."Manufacturing Score");
        ServiceModuleScoreTxt := FormatModuleScore(LastRun."Service Score");
        JobsModuleScoreTxt := FormatModuleScore(LastRun."Jobs Score");
        HRModuleScoreTxt := FormatModuleScore(LastRun."HR Score");

        SystemModuleScoreStyle := GetScoreStyle(LastRun."System Score");
        FinanceModuleScoreStyle := GetScoreStyle(LastRun."Finance Score");
        SalesModuleScoreStyle := GetScoreStyle(LastRun."Sales Score");
        PurchasingModuleScoreStyle := GetScoreStyle(LastRun."Purchasing Score");
        InventoryModuleScoreStyle := GetScoreStyle(LastRun."Inventory Score");
        CRMModuleScoreStyle := GetScoreStyle(LastRun."CRM Score");
        ManufacturingModuleScoreStyle := GetScoreStyle(LastRun."Manufacturing Score");
        ServiceModuleScoreStyle := GetScoreStyle(LastRun."Service Score");
        JobsModuleScoreStyle := GetScoreStyle(LastRun."Jobs Score");
        HRModuleScoreStyle := GetScoreStyle(LastRun."HR Score");
    end;

    local procedure FormatModuleScore(Score: Integer): Text[50]
    begin
        if ShowNoScanNotice then
            exit('-');

        exit(StrSubstNo('%1 / 100', Score));
    end;

    local procedure GetAccessStyle(IsAvailable: Boolean): Text[30]
    begin
        if IsAvailable then
            exit('Favorable');

        exit('Standard');
    end;

    local procedure GetScoreStyle(Score: Integer): Text[30]
    begin
        if Score >= 90 then
            exit('Favorable');
        if Score >= 70 then
            exit('Ambiguous');
        if Score > 0 then
            exit('Unfavorable');
        exit('Standard');
    end;

    local procedure GetIssueStyle(IssueCount: Integer): Text[30]
    begin
        if IssueCount > 0 then
            exit('Unfavorable');
        exit('Favorable');
    end;

    local procedure GetAmountStyle(Amount: Decimal): Text[30]
    begin
        if Amount > 0 then
            exit('Unfavorable');
        exit('Standard');
    end;

    local procedure GetRunStatusStyle(var DeepScanRun: Record "DH Deep Scan Run"): Text[30]
    begin
        case DeepScanRun.Status of
            DeepScanRun.Status::Completed:
                exit('Favorable');
            DeepScanRun.Status::Failed, DeepScanRun.Status::Canceled:
                exit('Unfavorable');
            DeepScanRun.Status::Queued, DeepScanRun.Status::Running:
                exit('Ambiguous');
        end;
        exit('Standard');
    end;

    local procedure GetDurationText(var DeepScanRun: Record "DH Deep Scan Run"): Text[50]
    var
        DurationValue: Duration;
    begin
        if (DeepScanRun."Started At" = 0DT) or (DeepScanRun."Finished At" = 0DT) then
            exit('');

        DurationValue := DeepScanRun."Finished At" - DeepScanRun."Started At";
        exit(Format(DurationValue));
    end;

    local procedure GetScheduledResultStyle(): Text[30]
    begin
        case Rec."Last Scheduled Scan Result" of
            Rec."Last Scheduled Scan Result"::Completed, Rec."Last Scheduled Scan Result"::Queued:
                exit('Favorable');
            Rec."Last Scheduled Scan Result"::Failed, Rec."Last Scheduled Scan Result"::SkippedConfiguration, Rec."Last Scheduled Scan Result"::SkippedMonitoringInactive:
                exit('Unfavorable');
        end;
        exit('Standard');
    end;

    local procedure LastDeepScanRunExists(): Boolean
    var
        DeepScanRun: Record "DH Deep Scan Run";
    begin
        DeepScanRun.Reset();
        DeepScanRun.SetCurrentKey("Requested At");
        DeepScanRun.Ascending(false);
        exit(DeepScanRun.FindFirst());
    end;

    local procedure OpenLatestMonitor()
    var
        DeepScanRun: Record "DH Deep Scan Run";
    begin
        DeepScanRun.Reset();
        DeepScanRun.SetCurrentKey("Requested At");
        DeepScanRun.Ascending(false);
        if not DeepScanRun.FindFirst() then
            Error('No deep scan run is available.');

        Page.Run(Page::"DH Deep Scan Monitor", DeepScanRun);
    end;

    local procedure OpenChecksSelection()
    var
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
    begin
        EnsureSetupExists();
        ScanCheckMgt.EnsureMonitoringAccess(true);
        Page.Run(Page::"DH Scan Checks");
        if Rec.Get('SETUP') then begin
            UpdateActionState();
            UpdateDisplayValues();
            CurrPage.Update(false);
        end;
    end;

    local procedure GetTokenUrl(var Setup: Record "DH Setup"): Text
    begin
        if Setup."API Base URL" = '' then
            Error('Please configure the API Base URL first.');

        if Setup."Tenant ID" = '' then
            Error('Tenant is not registered yet.');

        exit(RemoveTrailingSlash(Setup."API Base URL") + '/analytics/get-token?company=' + EncodeUrlValue(CompanyName()) + '&environment=' + EncodeUrlValue('BC Cloud') + '&tenant_id=' + EncodeUrlValue(Setup."Tenant ID") + '&scan_mode=' + EncodeUrlValue(GetScanMode(Setup)) + '&bc_issue_launch_url=' + EncodeUrlValue(GetIssueDrilldownLaunchUrl()));
    end;

    local procedure GetScanMode(var Setup: Record "DH Setup"): Text
    begin
        if Setup."Premium Enabled" then
            exit('premium_deep');
        exit('free_deep');
    end;

    local procedure GetDashboardUrl(var Setup: Record "DH Setup"; Token: Text): Text
    begin
        exit(RemoveTrailingSlash(Setup."API Base URL") + '/analytics/embed?embed_token=' + EncodeUrlValue(Token));
    end;

    local procedure GetIssueDrilldownLaunchUrl(): Text
    begin
        exit(GetUrl(ClientType::Web, CompanyName(), ObjectType::Page, Page::"DH Issue Drilldown Launch"));
    end;

    local procedure ExtractTokenFromJson(JsonText: Text): Text
    var
        JsonObj: JsonObject;
        JsonToken: JsonToken;
    begin
        if not JsonObj.ReadFrom(JsonText) then
            Error('The token response is not valid JSON.');

        if not JsonObj.Get('token', JsonToken) then
            Error('The token field is missing in the response.');

        exit(JsonToken.AsValue().AsText());
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
}

