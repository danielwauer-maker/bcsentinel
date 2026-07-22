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
            group(OverviewStatus)
            {
                Caption = 'Overview and Status';

                field(ConnectionStatusDisplay; ConnectionStatusTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Connection Status';
                    Editable = false;
                    StyleExpr = ConnectionStatusStyle;
                    ToolTip = 'Shows whether the BCSentinel connection is configured. Use Test Connection to verify that the service is reachable.';
                }
                field(RegistrationStatusDisplay; RegistrationStatusTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Registration Status';
                    Editable = false;
                    StyleExpr = RegistrationStatusStyle;
                    ToolTip = 'Shows whether this Business Central company is registered with BCSentinel.';
                }
                field(CurrentProductPlanDisplay; ProductAccessTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Current Product Plan';
                    Editable = false;
                    ToolTip = 'Shows the current product access from the locally stored access snapshot.';
                }
                field(LatestDataHealthScoreDisplay; LastScanScoreTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Latest Data Health Score';
                    Editable = false;
                    StyleExpr = LastScanScoreStyle;
                    ToolTip = 'Shows the Data Health Score from the latest locally stored scan. No backend request is made when the page opens.';
                }
                field(LatestRatingDisplay; LatestRatingTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Rating';
                    Editable = false;
                    StyleExpr = LastScanScoreStyle;
                    ToolTip = 'Shows the rating derived from the latest locally stored Data Health Score.';
                }
                field(LatestScanDisplay; LastScanDateValue)
                {
                    ApplicationArea = All;
                    Caption = 'Last Scan';
                    Editable = false;
                    ToolTip = 'Shows when the latest locally stored scan was requested.';
                }
                field(LatestScanStatusDisplay; LastScanStatusTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Scan Status';
                    Editable = false;
                    StyleExpr = LastScanStatusStyle;
                    ToolTip = 'Shows the status of the latest locally stored scan.';
                }
                field(NextScheduledScanDisplay; Rec."Next Scheduled Scan")
                {
                    ApplicationArea = All;
                    Caption = 'Next Scheduled Scan';
                    Editable = false;
                    ToolTip = 'Shows the next scheduled scan. The value is empty when no run is scheduled.';
                }
                field(MonitoringEnabledDisplay; Rec."Monitoring Active")
                {
                    ApplicationArea = All;
                    Caption = 'Monitoring Enabled';
                    Editable = false;
                    StyleExpr = MonitoringStyle;
                    ToolTip = 'Shows whether the current product access includes Monitoring.';
                }
            }

            group(SubscriptionStatus)
            {
                Caption = 'Product and Access';

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
                field(FreeAssessmentStatus; FreeAssessmentStatusTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Free Data Health Score';
                    Editable = false;
                    ToolTip = 'Shows whether the one-time free Data Health Score is available or already used.';
                }
                field("Validation Credits Available"; Rec."Validation Credits Available")
                {
                    ApplicationArea = All;
                    Caption = 'Validation Credits';
                    Editable = false;
                    ToolTip = 'Shows the available Validation credits. Monitoring scans do not consume these credits under the current product model.';
                }
                field(ReportAccessDisplay; Rec.GetReportAccessDisplay())
                {
                    ApplicationArea = All;
                    Caption = 'Report Access';
                    Editable = false;
                    ToolTip = 'Shows whether Free Report access is unavailable, time-limited, or unlimited.';
                }
                field(DashboardAccessDisplay; Rec.GetDashboardAccessDisplay())
                {
                    ApplicationArea = All;
                    Caption = 'Dashboard Access';
                    ToolTip = 'Shows whether Free Dashboard access is unavailable, time-limited, or unlimited.';
                    Editable = false;
                }
                field(IssueAccessDisplay; Rec.GetIssueAccessDisplay())
                {
                    ApplicationArea = All;
                    Caption = 'Findings Access';
                    ToolTip = 'Shows whether Free Findings access is unavailable, time-limited, or unlimited.';
                    Editable = false;
                }
                field(PremiumUntil; Rec."Premium Until")
                {
                    ApplicationArea = All;
                    Caption = 'Product Access Until';
                    Editable = false;
                    ToolTip = 'Shows until when the current product access is valid.';
                }
                field(MonitoringUntil; Rec."Monitoring Until")
                {
                    ApplicationArea = All;
                    Caption = 'Monitoring Until';
                    Editable = false;
                    ToolTip = 'Shows until when Monitoring is active.';
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
                    ToolTip = 'Explains scheduler availability and how Business Central runs scheduled scans.';
                }
                field("Scheduled Scans Enabled"; Rec."Scheduled Scans Enabled")
                {
                    ApplicationArea = All;
                    Editable = CanUseScheduler;
                    ToolTip = 'Specifies whether scheduled scans are enabled.';

                    trigger OnValidate()
                    var
                        SchedulerMgt: Codeunit "DH Scan Scheduler Mgt.";
                    begin
                        if Rec."Scheduled Scans Enabled" then
                            SchedulerMgt.EnableScheduler(Rec)
                        else
                            SchedulerMgt.DisableScheduler(Rec);
                        UpdateActionState();
                        UpdateDisplayValues();
                        CurrPage.Update(false);
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
                        RescheduleEnabledScheduler();
                    end;
                }
                field("Schedule Time"; Rec."Schedule Time")
                {
                    ApplicationArea = All;
                    Editable = CanEditSchedulerDetails;
                    ToolTip = 'Specifies the local time for scheduled scans.';

                    trigger OnValidate()
                    begin
                        RescheduleEnabledScheduler();
                    end;
                }
                group(WeeklyDays)
                {
                    Caption = 'Weekly Days';
                    Visible = ShowWeeklySchedulerFields;

                    field("Schedule Monday"; Rec."Schedule Monday")
                    {
                        ApplicationArea = All;
                        Editable = CanEditSchedulerDetails;
                        ToolTip = 'Specifies whether scheduled Monitoring scans run on Monday.';

                        trigger OnValidate()
                        begin
                            RescheduleEnabledScheduler();
                        end;
                    }
                    field("Schedule Tuesday"; Rec."Schedule Tuesday")
                    {
                        ApplicationArea = All;
                        Editable = CanEditSchedulerDetails;
                        ToolTip = 'Specifies whether scheduled Monitoring scans run on Tuesday.';

                        trigger OnValidate()
                        begin
                            RescheduleEnabledScheduler();
                        end;
                    }
                    field("Schedule Wednesday"; Rec."Schedule Wednesday")
                    {
                        ApplicationArea = All;
                        Editable = CanEditSchedulerDetails;
                        ToolTip = 'Specifies whether scheduled Monitoring scans run on Wednesday.';

                        trigger OnValidate()
                        begin
                            RescheduleEnabledScheduler();
                        end;
                    }
                    field("Schedule Thursday"; Rec."Schedule Thursday")
                    {
                        ApplicationArea = All;
                        Editable = CanEditSchedulerDetails;
                        ToolTip = 'Specifies whether scheduled Monitoring scans run on Thursday.';

                        trigger OnValidate()
                        begin
                            RescheduleEnabledScheduler();
                        end;
                    }
                    field("Schedule Friday"; Rec."Schedule Friday")
                    {
                        ApplicationArea = All;
                        Editable = CanEditSchedulerDetails;
                        ToolTip = 'Specifies whether scheduled Monitoring scans run on Friday.';

                        trigger OnValidate()
                        begin
                            RescheduleEnabledScheduler();
                        end;
                    }
                    field("Schedule Saturday"; Rec."Schedule Saturday")
                    {
                        ApplicationArea = All;
                        Editable = CanEditSchedulerDetails;
                        ToolTip = 'Specifies whether scheduled Monitoring scans run on Saturday.';

                        trigger OnValidate()
                        begin
                            RescheduleEnabledScheduler();
                        end;
                    }
                    field("Schedule Sunday"; Rec."Schedule Sunday")
                    {
                        ApplicationArea = All;
                        Editable = CanEditSchedulerDetails;
                        ToolTip = 'Specifies whether scheduled Monitoring scans run on Sunday.';

                        trigger OnValidate()
                        begin
                            RescheduleEnabledScheduler();
                        end;
                    }
                }
                field("Monthly Schedule Day"; Rec."Monthly Schedule Day")
                {
                    ApplicationArea = All;
                    Editable = CanEditSchedulerDetails;
                    Visible = ShowMonthlySchedulerFields;
                    ToolTip = 'Specifies the day of month for monthly scheduled scans.';

                    trigger OnValidate()
                    begin
                        RescheduleEnabledScheduler();
                    end;
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
                field(LastScheduledScanResult; LastScheduledScanResultTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Last Scheduled Scan Result';
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
                field("Scheduled Scan Task ID"; Rec."Scheduled Scan Task ID")
                {
                    ApplicationArea = All;
                    Editable = false;
                    Visible = false;
                    ToolTip = 'Specifies the Business Central TaskScheduler task that will start the next scheduled scan.';
                }
            }

            group(Connection)
            {
                Caption = 'Connection and Registration';

                group(RegistrationPreparation)
                {
                    Caption = 'Prepare registration';
                    Visible = ShowRegistrationPreparation;

                    field(RegistrationPreparationMessage; RegistrationPreparationTxt)
                    {
                        ApplicationArea = All;
                        ShowCaption = false;
                        Editable = false;
                        MultiLine = true;
                        StyleExpr = RegistrationPreparationStyle;
                        ToolTip = 'Explains whether all requirements for BCSentinel registration have been completed.';
                    }
                    field(ContactEmailRequirement; ContactEmailRequirementTxt)
                    {
                        ApplicationArea = All;
                        Caption = 'Contact Email';
                        Editable = false;
                        StyleExpr = ContactEmailRequirementStyle;
                        ToolTip = 'Shows whether a valid contact email address has been entered for registration.';
                    }
                    field(PrivacyConsentRequirement; PrivacyConsentRequirementTxt)
                    {
                        ApplicationArea = All;
                        Caption = 'Privacy Consent';
                        Editable = false;
                        StyleExpr = PrivacyConsentRequirementStyle;
                        ToolTip = 'Shows whether the existing data processing consent has been accepted for registration.';
                    }
                }

                field("API Base URL"; Rec."API Base URL")
                {
                    ApplicationArea = All;
                    Editable = true;
                    ToolTip = 'Base URL of the BCSentinel API. Default is production.';

                    trigger OnValidate()
                    begin
                        UpdateActionState();
                        CurrPage.Update(false);
                    end;
                }

                field("Contact Email"; Rec."Contact Email")
                {
                    ApplicationArea = All;
                    ToolTip = 'Contact email used for BCSentinel onboarding and future dashboard login.';

                    trigger OnValidate()
                    begin
                        UpdateActionState();
                        CurrPage.Update(false);
                    end;
                }

                field("Tenant ID"; Rec."Tenant ID")
                {
                    ApplicationArea = All;
                    Caption = 'Tenant ID';
                    ToolTip = 'Specifies Tenant ID.';
                    Editable = false;
                    Visible = false;
                }

                field(ApiTokenConfigured; HasStoredApiToken())
                {
                    ApplicationArea = All;
                    Caption = 'API Token Configured';
                    Editable = false;
                    Visible = false;
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
                    Visible = false;
                }

                field("Data Processing Consent"; Rec."Data Processing Consent")
                {
                    ApplicationArea = All;
                    ToolTip = 'Confirms that BCSentinel may send tenant and company identifiers, metadata, configuration data, scan results, findings, and aggregated quality metrics for data health analysis, dashboards, executive reports, and product-access checks. API tokens are stored securely and are not included in reports or share URLs. Review the privacy policy and terms before enabling consent.';

                    trigger OnValidate()
                    begin
                        UpdateActionState();
                        CurrPage.Update(false);
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
                field(SystemModuleScore; SystemModuleScoreTxt) { ApplicationArea = All; Caption = 'System'; Editable = false; StyleExpr = SystemModuleScoreStyle; ToolTip = 'Shows the latest score for the System module.'; }
                field(FinanceModuleScore; FinanceModuleScoreTxt) { ApplicationArea = All; Caption = 'Finance'; Editable = false; StyleExpr = FinanceModuleScoreStyle; ToolTip = 'Shows the latest score for the Finance module.'; }
                field(SalesModuleScore; SalesModuleScoreTxt) { ApplicationArea = All; Caption = 'Sales'; Editable = false; StyleExpr = SalesModuleScoreStyle; ToolTip = 'Shows the latest score for the Sales module.'; }
                field(PurchasingModuleScore; PurchasingModuleScoreTxt) { ApplicationArea = All; Caption = 'Purchasing'; Editable = false; StyleExpr = PurchasingModuleScoreStyle; ToolTip = 'Shows the latest score for the Purchasing module.'; }
                field(InventoryModuleScore; InventoryModuleScoreTxt) { ApplicationArea = All; Caption = 'Inventory'; Editable = false; StyleExpr = InventoryModuleScoreStyle; ToolTip = 'Shows the latest score for the Inventory module.'; }
                field(CRMModuleScore; CRMModuleScoreTxt) { ApplicationArea = All; Caption = 'CRM'; Editable = false; StyleExpr = CRMModuleScoreStyle; ToolTip = 'Shows the latest score for the CRM module.'; }
                field(ManufacturingModuleScore; ManufacturingModuleScoreTxt) { ApplicationArea = All; Caption = 'Manufacturing'; Editable = false; StyleExpr = ManufacturingModuleScoreStyle; ToolTip = 'Shows the latest score for the Manufacturing module.'; }
                field(ServiceModuleScore; ServiceModuleScoreTxt) { ApplicationArea = All; Caption = 'Service'; Editable = false; StyleExpr = ServiceModuleScoreStyle; ToolTip = 'Shows the latest score for the Service module.'; }
                field(JobsModuleScore; JobsModuleScoreTxt) { ApplicationArea = All; Caption = 'Jobs'; Editable = false; StyleExpr = JobsModuleScoreStyle; ToolTip = 'Shows the latest score for the Jobs module.'; }
                field(HRModuleScore; HRModuleScoreTxt) { ApplicationArea = All; Caption = 'HR'; Editable = false; StyleExpr = HRModuleScoreStyle; ToolTip = 'Shows the latest score for the HR module.'; }
            }

            group(LastScan)
            {
                Caption = 'Last Scan';

                field(LastScanRunId; LastScanRunIdTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Last Scan ID';
                    Editable = false;
                    Visible = false;
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
                field(LastScanEstimatedImpact; LastScanEstimatedImpactTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Estimated Impact';
                    Editable = false;
                    StyleExpr = LastScanLossStyle;
                    ToolTip = 'Specifies the estimated impact from the last scan in local currency.';
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

            group(AdvancedInformation)
            {
                Caption = 'Advanced Information';

                field(EntraTenantIdDisplay; EntraTenantIdTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Entra Tenant ID';
                    Editable = false;
                    ToolTip = 'Shows the Entra tenant identifier used for support and tenant-binding diagnostics.';
                }
                field(EnvironmentNameDisplay; EnvironmentNameTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Environment Name';
                    Editable = false;
                    ToolTip = 'Shows the Business Central environment name used for support diagnostics.';
                }
                field(EnvironmentTypeDisplay; EnvironmentTypeTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Environment Type';
                    Editable = false;
                    ToolTip = 'Shows the Business Central environment type used for support diagnostics.';
                }
                field(CompanySystemIdDisplay; CompanySystemIdTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Company System ID';
                    Editable = false;
                    ToolTip = 'Shows the immutable Business Central company identifier used for support diagnostics.';
                }
                field(TenantIdDiagnostic; Rec."Tenant ID")
                {
                    ApplicationArea = All;
                    Caption = 'Registration Identifier';
                    Editable = false;
                    ToolTip = 'Shows the BCSentinel registration identifier for support and diagnostics.';
                }
                field(ApiTokenConfiguredDiagnostic; HasStoredApiToken())
                {
                    ApplicationArea = All;
                    Caption = 'API Token Configured';
                    Editable = false;
                    ToolTip = 'Shows whether an API token is stored securely. The token itself is never displayed.';
                }
                field(RegistrationDateDiagnostic; Rec."Registration Date")
                {
                    ApplicationArea = All;
                    Caption = 'Registration Date';
                    Editable = false;
                    ToolTip = 'Shows when the local registration was completed.';
                }
                field(ScheduledTaskIdDiagnostic; Rec."Scheduled Scan Task ID")
                {
                    ApplicationArea = All;
                    Caption = 'Scheduler Task ID';
                    Editable = false;
                    ToolTip = 'Shows the Business Central task identifier for support diagnostics.';
                }
                field(LastLicenseCheckDiagnostic; Rec."Last License Check")
                {
                    ApplicationArea = All;
                    Caption = 'Last Product Access Check';
                    Editable = false;
                    ToolTip = 'Shows when product access was last refreshed from BCSentinel.';
                }
                field(AccessSnapshotReceivedAtDiagnostic; Rec."Access Snapshot Received At")
                {
                    ApplicationArea = All;
                    Caption = 'Access Snapshot Received At';
                    Editable = false;
                    ToolTip = 'Shows when the current access snapshot was received for support diagnostics.';
                }
                field(AccessSnapshotExpiresAtDiagnostic; Rec."Access Snapshot Expires At")
                {
                    ApplicationArea = All;
                    Caption = 'Access Snapshot Expires At';
                    Editable = false;
                    ToolTip = 'Shows when the short-lived access snapshot expires.';
                }
                field(AccessSnapshotVersionDiagnostic; Rec."Access Snapshot Version")
                {
                    ApplicationArea = All;
                    Caption = 'Access Snapshot Version';
                    Editable = false;
                    ToolTip = 'Shows the access snapshot contract version for support diagnostics.';
                }
                field(AccessCorrelationIdDiagnostic; Rec."Access Correlation ID")
                {
                    ApplicationArea = All;
                    Caption = 'Correlation ID';
                    Editable = false;
                    ToolTip = 'Shows the latest access-request correlation identifier for support diagnostics.';
                }
                field(LastScanIdDiagnostic; LastScanRunIdTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Last Scan ID';
                    Editable = false;
                    ToolTip = 'Shows the latest local scan identifier for support diagnostics.';
                }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(StartScan)
            {
                Caption = 'Start Free Data Health Score';
                ToolTip = 'Starts the free BCSentinel Data Health Score and opens the scan monitor.';
                Image = Start;
                ApplicationArea = All;
                Enabled = CanStartFreeDataHealthScore;
                Visible = ShowStartFreeDataHealthScore;
                Promoted = true;
                PromotedCategory = Process;
                PromotedOnly = true;

                trigger OnAction()
                begin
                    StartAvailableScan();
                end;
            }

            action(StartScanCompleted)
            {
                Caption = 'Start Scan';
                ToolTip = 'Free Data Health Score already completed. Buy a Validation Check or start Monitoring to run another scan.';
                Image = Start;
                ApplicationArea = All;
                Enabled = false;
                Visible = ShowFreeDataHealthScoreCompleted and not ShowStartValidationCheck;
                Promoted = true;
                PromotedCategory = Process;
                PromotedOnly = true;
            }

            group(ConnectionActions)
            {
                Caption = 'Connection';
                Image = Link;

                action(TestConnection)
                {
                    Caption = 'Test BCSentinel Connection';
                    ToolTip = 'Tests the connection to the configured BCSentinel API.';
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
                    Caption = 'Register';
                    ToolTip = 'Registers this Business Central tenant with BCSentinel.';
                    ApplicationArea = All;
                    Image = Web;
                    Enabled = CanRegisterTenant;
                    Visible = ShowRegisterTenant;
                    Promoted = true;
                    PromotedCategory = Process;

                    trigger OnAction()
                    begin
                        RunTenantRegistration();
                    end;
                }

                action(ResetRegistration)
                {
                    Caption = 'Reset Registration';
                    ToolTip = 'Clears cached registration status while preserving the stable tenant binding, API token, purchases, and scan history.';
                    ApplicationArea = All;
                    Image = ResetStatus;
                    Enabled = CanResetRegistration;
                    Visible = false;

                    trigger OnAction()
                    begin
                        if not Confirm(ResetTheCachedBCSentinelRegistrationStatusThLbl, false) then
                            exit;

                        ResetLocalRegistrationState();
                        UpdateActionState();
                        UpdateDisplayValues();
                        CurrPage.Update(false);
                        Message(CachedRegistrationStatusWasResetWithoutChangLbl);
                    end;
                }

                action(RefreshLicenseStatus)
                {
                    Caption = 'Refresh Product Access';
                    ApplicationArea = All;
                    Image = Refresh;
                    ToolTip = 'Refreshes Validation Credits, Monitoring status, and product access from BCSentinel.';
                    Promoted = true;
                    PromotedCategory = Process;

                    trigger OnAction()
                    var
                        ApiClient: Codeunit "DH API Client";
                    begin
                        if Rec."Tenant ID" = '' then
                            Error(PleaseRegisterTheTenantFirstLbl);

                        ApiClient.RefreshLicenseStatus(Rec);
                        CurrPage.Update(false);
                        Message(ProductAccessRefreshedLbl);
                    end;
                }
            }

            group(SettingsActions)
            {
                Caption = 'Settings';
                Image = Setup;

                action(SelectModules)
                {
                    Caption = 'Select Modules';
                    ToolTip = 'Opens the BCSentinel scan module selection.';
                    Image = Setup;
                    ApplicationArea = All;

                    trigger OnAction()
                    begin
                        Page.Run(Page::"DH Scan Modules");
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

                    trigger OnAction()
                    begin
                        OpenChecksSelection();
                    end;
                }
            }

            group(ScanMenu)
            {
                Caption = 'Scan';
                Image = Start;

                action(StartScanFromMenu)
                {
                    Caption = 'Start Validation Check';
                    ToolTip = 'Uses one Validation Credit to start a new scan and opens the scan monitor.';
                    Image = Start;
                    ApplicationArea = All;
                    Enabled = CanStartValidationCheck;
                    Visible = ShowStartValidationCheck and not Rec."Monitoring Active";
                    Promoted = true;
                    PromotedCategory = Process;

                    trigger OnAction()
                    begin
                        StartAvailableScan();
                    end;
                }

                action(OpenLatestScanMonitor)
                {
                    Caption = 'Open Current Scan';
                    ToolTip = 'Opens the scan monitor for the latest deep scan.';
                    Image = ViewDetails;
                    ApplicationArea = All;
                    Enabled = CanOpenLatestMonitor;

                    trigger OnAction()
                    begin
                        OpenLatestMonitor();
                    end;
                }

                action(ViewScanHistory)
                {
                    Caption = 'Open Scan History';
                    ToolTip = 'Opens the BCSentinel scan history.';
                    Image = List;
                    ApplicationArea = All;
                    Promoted = true;
                    PromotedCategory = Process;

                    trigger OnAction()
                    begin
                        Page.Run(Page::"DH Deep Scan Runs");
                    end;
                }

                action(OpenDashboard)
                {
                    Caption = 'Open Analytics Dashboard';
                    ApplicationArea = All;
                    Image = View;
                    ToolTip = 'Opens the BCSentinel analytics dashboard for this tenant.';
                    Enabled = CanOpenDashboard;
                    Promoted = true;
                    PromotedCategory = Process;

                    trigger OnAction()
                    var
                        ApiClient: Codeunit "DH API Client";
                        AccessGuard: Codeunit "DH Access Guard";
                        Token: Text;
                        AccessError: Text;
                    begin
                        if not AccessGuard.TryEnsureDashboardAccess(AccessError) then begin
                            Message(AccessError);
                            exit;
                        end;
                        Token := ApiClient.GetAnalyticsDashboardToken(Rec);
                        Hyperlink(GetDashboardUrl(Rec, Token));
                    end;
                }

                action(StartMonitoringScan)
                {
                    Caption = 'Start Monitoring Scan';
                    ToolTip = 'Starts an available Monitoring scan and opens the scan monitor.';
                    Image = Start;
                    ApplicationArea = All;
                    Enabled = CanStartValidationCheck;
                    Visible = ShowStartValidationCheck and Rec."Monitoring Active";
                    Promoted = true;
                    PromotedCategory = Process;

                    trigger OnAction()
                    begin
                        StartAvailableScan();
                    end;
                }

                action(OpenLatestFindings)
                {
                    Caption = 'Open Findings';
                    ApplicationArea = All;
                    Image = List;
                    ToolTip = 'Opens the findings from the latest scan. Current product access is verified before details are shown.';
                    Enabled = CanOpenLatestMonitor;
                    Visible = ShowOpenLatestFindings;
                    Promoted = true;
                    PromotedCategory = Process;

                    trigger OnAction()
                    begin
                        OpenFindingsForLatestScan();
                    end;
                }

                action(OpenLatestReport)
                {
                    Caption = 'Open Latest Report';
                    ApplicationArea = All;
                    Image = Report;
                    ToolTip = 'Opens the Executive Report for the latest completed scan. Current report access is verified first.';
                    Enabled = CanOpenLatestReport;
                    Promoted = true;
                    PromotedCategory = Process;

                    trigger OnAction()
                    begin
                        OpenReportForLatestScan();
                    end;
                }
            }

            group(SchedulerActions)
            {
                Caption = 'Scheduler';
                Image = Calendar;

                action(EnableScheduler)
                {
                    Caption = 'Enable Scheduler';
                    ToolTip = 'Enables scheduled Monitoring scans and plans the next run.';
                    Image = Approve;
                    ApplicationArea = All;
                    Enabled = CanUseScheduler and not Rec."Scheduled Scans Enabled";
                    Promoted = true;
                    PromotedCategory = Process;

                    trigger OnAction()
                    var
                        SchedulerMgt: Codeunit "DH Scan Scheduler Mgt.";
                    begin
                        SchedulerMgt.EnableScheduler(Rec);
                        UpdateActionState();
                        UpdateDisplayValues();
                        CurrPage.Update(false);
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
                        Message(NextScheduledScan1Lbl, NextRun);
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

                action(RunScheduledScanNow)
                {
                    Caption = 'Run Now';
                    ToolTip = 'Starts a Monitoring scan immediately and opens the scan monitor.';
                    Image = Start;
                    ApplicationArea = All;
                    Enabled = CanUseScheduler;

                    trigger OnAction()
                    var
                        SchedulerMgt: Codeunit "DH Scan Scheduler Mgt.";
                        EntryNo: Integer;
                    begin
                        EntryNo := SchedulerMgt.RunNow(Rec);
                        if EntryNo = 0 then
                            exit;
                        Rec.Get('SETUP');
                        UpdateActionState();
                        UpdateDisplayValues();
                        CurrPage.Update(false);
                        Message(DataHealthScanStartedMsg);
                    end;
                }
            }

            group(AdministrativeActions)
            {
                Caption = 'Administrative Actions';
                Image = Administration;

                action(ResetRegistrationAdmin)
                {
                    Caption = 'Reset Cached Registration';
                    ToolTip = 'Clears only the local cached registration and access status. Tenant identity, API token, purchases, and scan history are preserved.';
                    ApplicationArea = All;
                    Image = ResetStatus;
                    Enabled = CanResetRegistration;

                    trigger OnAction()
                    begin
                        if not Confirm(ResetRegistrationQst, false) then
                            exit;

                        ResetLocalRegistrationState();
                        UpdateActionState();
                        UpdateDisplayValues();
                        CurrPage.Update(false);
                        Message(ResetRegistrationDoneMsg);
                    end;
                }
            }

            group(SubscriptionActions)
            {
                Caption = 'Subscription';
                Image = Payment;

                action(BuyFullAnalysis)
                {
                    Caption = 'Buy Full Analysis';
                    ApplicationArea = All;
                    Image = Add;
                    ToolTip = 'Opens the secure BCSentinel checkout for Full Analysis.';
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
                    Caption = 'Buy Validation Check';
                    ApplicationArea = All;
                    Image = Add;
                    ToolTip = 'Opens the secure BCSentinel checkout for a Validation Check follow-up scan.';
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
                    Caption = 'Buy Monitoring Monthly';
                    ApplicationArea = All;
                    Image = Add;
                    ToolTip = 'Opens the secure BCSentinel checkout for monthly monitoring.';
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
                    Caption = 'Buy Monitoring Annual';
                    ApplicationArea = All;
                    Image = Add;
                    ToolTip = 'Opens the secure BCSentinel checkout for annual monitoring.';
                    Visible = ShowStartMonitoring;

                    trigger OnAction()
                    var
                        ApiClient: Codeunit "DH API Client";
                    begin
                        ApiClient.OpenProductCheckout(Rec, 'monitoring_annual');
                    end;
                }
            }

        }
    }

    var
        CanRegisterTenant: Boolean;
        ShowRegisterTenant: Boolean;
        ShowRegistrationPreparation: Boolean;
        ShowOpenLatestFindings: Boolean;
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
        CanOpenLatestReport: Boolean;
        ShowBuyFullAnalysis: Boolean;
        ShowBuyValidationCheck: Boolean;
        ShowStartMonitoring: Boolean;
        ShowWeeklySchedulerFields: Boolean;
        ShowMonthlySchedulerFields: Boolean;
        ShowNoScanNotice: Boolean;
        DataProcessingNoticeTxt: Text[1024];
        RegistrationPreparationTxt: Text[250];
        ContactEmailRequirementTxt: Text[100];
        PrivacyConsentRequirementTxt: Text[100];
        InviteNoticeTxt: Text[512];
        SubscriptionStatusTxt: Text[100];
        ProductAccessTxt: Text[100];
        FreeAssessmentStatusTxt: Text[50];
        ActiveModulesTxt: Text[100];
        ActiveChecksTxt: Text[100];
        ScanConfigurationStatusTxt: Text[250];
        SchedulerNoticeTxt: Text[250];
        ModuleScoresNoticeTxt: Text[100];
        LastScheduledScanResultTxt: Text[100];
        LastScanRunIdTxt: Text[50];
        LastScanDateValue: DateTime;
        LastScanScoreTxt: Text[30];
        LastScanIssuesValue: Integer;
        LastScanEstimatedImpactTxt: Text[50];
        LastScanDurationTxt: Text[50];
        LastScanStatusTxt: Text[100];
        LatestRatingTxt: Text[50];
        ConnectionStatusTxt: Text[100];
        RegistrationStatusTxt: Text[100];
        EntraTenantIdTxt: Text[100];
        EnvironmentNameTxt: Text[100];
        EnvironmentTypeTxt: Text[20];
        CompanySystemIdTxt: Text[50];
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
        ConnectionStatusStyle: Text[30];
        RegistrationStatusStyle: Text[30];
        RegistrationPreparationStyle: Text[30];
        ContactEmailRequirementStyle: Text[30];
        PrivacyConsentRequirementStyle: Text[30];
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
        ConnectionConfiguredLbl: Label 'Configured';
        ConnectionNotConfiguredLbl: Label 'Not configured';
        RegisteredLbl: Label 'Registered';
        NotRegisteredLbl: Label 'Not registered';
        NoScanLbl: Label 'No scan yet';
        RatingExcellentLbl: Label 'Excellent';
        RatingGoodLbl: Label 'Good';
        RatingNeedsAttentionLbl: Label 'Needs attention';
        SchedulerJobQueueNoticeLbl: Label 'Scheduled scans are executed through the Business Central job queue. The user does not need to remain signed in.';
        RegistrationRequirementsPendingLbl: Label 'The following information is required before registration:';
        RegistrationRequirementsCompletedLbl: Label 'All registration requirements have been completed. You can now register BCSentinel.';
        EnterContactEmailAddressLbl: Label 'Enter a contact email address';
        ContactEmailAddressInvalidLbl: Label 'The contact email address is invalid.';
        ContactEmailEnteredLbl: Label 'Contact email entered';
        AcceptPrivacyConsentLbl: Label 'Accept the privacy consent';
        PrivacyConsentAcceptedLbl: Label 'Privacy consent accepted';
        DataHealthScanStartedMsg: Label 'The data health scan has been started.';
        ResetRegistrationQst: Label 'Reset the cached BCSentinel registration and access status? The tenant identity, API token, purchases, and scan history are preserved. This action cannot be undone locally. Do you want to continue?';
        ResetRegistrationDoneMsg: Label 'The cached registration and access status was reset. Tenant identity, API token, purchases, and scan history were preserved.';

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
        Rec.Registered := false;
        Rec."Registration Date" := 0DT;
        Rec."Can Run Data Health Score" := true;
        Rec."Data Health Score Completed" := false;
        Rec."Scan Credits Available" := 0;
        /*Rec."Assessment Credits Available" := 0;*/
        Rec."Validation Credits Available" := 0;
        Rec."Monitoring Active" := false;
        Rec."Dashboard Access Until" := '';
        Rec."Issue Access Until" := '';
        Rec."Can Run Deep Scan" := false;
        Rec."Can View Dashboard" := false;
        Rec."Can View Issue Details" := false;
        Rec."Product Access Model" := '';
        Rec.Modify(true);
    end;

    local procedure RunTenantRegistration()
    var
        RegistrationMessage: Text;
    begin
        if Rec.Registered then
            exit;

        if Rec."Contact Email" = '' then begin
            Message(PleaseEnterAContactEmailAddressFirstLbl);
            exit;
        end;

        Rec.EnsureValidContactEmail();

        ClearLastError();
        if not TryRegisterTenantAndRefresh(RegistrationMessage) then begin
            RegistrationMessage := GetLastErrorText();
            ClearLastError();
            UpdateActionState();
            UpdateDisplayValues();
            CurrPage.Update(false);
            if RegistrationMessage = '' then
                RegistrationMessage := RegistrationUnexpectedErrorLbl;
            Message(RegistrationMessage);
            exit;
        end;

        UpdateActionState();
        UpdateDisplayValues();
        CurrPage.Update(false);
        Message(RegistrationMessage);
    end;

    [TryFunction]
    local procedure TryRegisterTenantAndRefresh(var RegistrationMessage: Text)
    var
        ApiClient: Codeunit "DH API Client";
    begin
        RegistrationMessage := ApiClient.RegisterTenant(Rec);
        ApiClient.RefreshLicenseStatus(Rec);
    end;

    local procedure DeleteScanHistoryForReset()
    var
        ApiClient: Codeunit "DH API Client";
        ScanHeader: Record "DH Scan Header";
        DeepScanRun: Record "DH Deep Scan Run";
        ScanTrend: Record "DH Scan Trend";
    begin
        ApiClient.ClearBackendScanHistoryForReset(Rec);

        if not ScanHeader.IsEmpty() then
            ScanHeader.DeleteAll(true);

        if not DeepScanRun.IsEmpty() then
            DeepScanRun.DeleteAll(true);

        if not ScanTrend.IsEmpty() then
            ScanTrend.DeleteAll(true);

        Rec."Last Score" := 0;
        Rec."Last Scan Date" := 0DT;
        Rec."Data Health Score Completed" := false;
        Rec."Can Run Data Health Score" := true;
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
            Rec."Premium Enabled" or
            (LowerCase(Rec."Product Access Model") = 'one_time');
        CanRegisterTenant := Rec.IsRegistrationReady();
        ShowRegisterTenant := not Rec.Registered;
        ShowRegistrationPreparation := not Rec.Registered;
        ShowOpenLatestFindings := Rec.Registered;
        CanResetRegistration :=
            Rec.Registered or
            (Rec."Tenant ID" <> '') or
            (Rec."Registration Date" <> 0DT) or
            HasStoredApiToken();
        CanStartFreeDataHealthScore := (Rec."Tenant ID" <> '') and not HasCompletedFreeScore;
        ShowStartFreeDataHealthScore := not HasCompletedFreeScore;
        ShowFreeDataHealthScoreCompleted := HasCompletedFreeScore;
        CanStartValidationCheck :=
            (Rec."Tenant ID" <> '') and HasCompletedFreeScore and
            (Rec."Monitoring Active" or (Rec."Validation Credits Available" > 0));
        ShowStartValidationCheck := HasCompletedFreeScore;
        ShowValidationCheckRequiresFreeScore := not HasCompletedFreeScore;
        CanSelectScanChecks := (Rec."Tenant ID" <> '') and Rec."Monitoring Active";
        CanUseScheduler := (Rec."Tenant ID" <> '') and Rec."Monitoring Active";
        CanEditSchedulerDetails := CanUseScheduler and Rec."Scheduled Scans Enabled";
        CanOpenDashboard := (Rec."Tenant ID" <> '') and HasStoredApiToken();
        CanOpenLatestMonitor := LastDeepScanRunExists();
        CanOpenLatestReport := LatestCompletedScanExists();
        UpdateSchedulerVisibility();
        ShowBuyFullAnalysis := (Rec."Tenant ID" <> '') and not Rec."Monitoring Active" and not HasOneTimeAccess;
        ShowBuyValidationCheck := (Rec."Tenant ID" <> '') and not Rec."Monitoring Active" and HasCompletedFreeScore;
        ShowStartMonitoring := (Rec."Tenant ID" <> '') and not Rec."Monitoring Active";
        UpdateRegistrationGuidance();
    end;

    local procedure UpdateRegistrationGuidance()
    begin
        if Rec.Registered then begin
            RegistrationPreparationTxt := '';
            ContactEmailRequirementTxt := '';
            PrivacyConsentRequirementTxt := '';
            RegistrationPreparationStyle := 'Standard';
            ContactEmailRequirementStyle := 'Standard';
            PrivacyConsentRequirementStyle := 'Standard';
            exit;
        end;

        if Rec.IsRegistrationReady() then begin
            RegistrationPreparationTxt := RegistrationRequirementsCompletedLbl;
            RegistrationPreparationStyle := 'Favorable';
        end else begin
            RegistrationPreparationTxt := RegistrationRequirementsPendingLbl;
            RegistrationPreparationStyle := 'Ambiguous';
        end;

        if Rec."Contact Email" = '' then begin
            ContactEmailRequirementTxt := EnterContactEmailAddressLbl;
            ContactEmailRequirementStyle := 'Unfavorable';
        end else
            if Rec.HasValidContactEmail() then begin
                ContactEmailRequirementTxt := ContactEmailEnteredLbl;
                ContactEmailRequirementStyle := 'Favorable';
            end else begin
                ContactEmailRequirementTxt := ContactEmailAddressInvalidLbl;
                ContactEmailRequirementStyle := 'Unfavorable';
            end;

        if Rec."Data Processing Consent" then begin
            PrivacyConsentRequirementTxt := PrivacyConsentAcceptedLbl;
            PrivacyConsentRequirementStyle := 'Favorable';
        end else begin
            PrivacyConsentRequirementTxt := AcceptPrivacyConsentLbl;
            PrivacyConsentRequirementStyle := 'Unfavorable';
        end;
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
        DataProcessingNoticeTxt := BeforeRegistrationOrScansBCSentinelRequiresYLbl;

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
        UpdateCustomerStatusValues();
        SubscriptionStatusTxt := Rec.GetSubscriptionStatusDisplay();
        ProductAccessTxt := Rec.GetProductAccessDisplay();
        FreeAssessmentStatusTxt := Rec.GetFreeAssessmentDisplay();
        ActiveModulesTxt := SchedulerMgt.GetActiveModulesSummary(Rec);
        ActiveChecksTxt := SchedulerMgt.GetActiveChecksSummary(Rec);
        EnabledChecks := ScanCheckMgt.GetExpectedChecksCount(Rec);
        TotalChecks := ScanCheckMgt.GetTotalModuleChecksCount(Rec);

        if not Rec.HasAnyModuleEnabled() then begin
            ScanConfigurationStatusTxt := ScanNotPossibleAtLeastOneModuleLbl;
            ScanConfigurationStyle := 'Unfavorable';
        end else
            if Rec."Monitoring Active" and (EnabledChecks = 0) and (TotalChecks > 0) then begin
                ScanConfigurationStatusTxt := ScanNotPossibleAtLeastOneCheckLbl;
                ScanConfigurationStyle := 'Unfavorable';
            end else begin
                ScanConfigurationStatusTxt := ScanPossibleRequiredModulesAndChecksAreLbl;
                ScanConfigurationStyle := 'Favorable';
            end;

        if Rec."Monitoring Active" then
            SchedulerNoticeTxt := SchedulerJobQueueNoticeLbl
        else
            SchedulerNoticeTxt := Rec.GetScheduledScanAccessDisplay() + ' ' + SchedulerJobQueueNoticeLbl;

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
        LastScheduledScanResultTxt := GetScheduledScanResultDisplay();
        if Rec."Scheduled Scan Failure Count" > 0 then
            ScheduledFailureStyle := 'Unfavorable'
        else
            ScheduledFailureStyle := 'Standard';

        LoadLastScan(LastRun);
        UpdateLatestRating(LastRun);
        UpdateModuleScoreTexts(LastRun);
    end;

    local procedure UpdateCustomerStatusValues()
    var
        IdentityMgt: Codeunit "DH Tenant Identity Mgt.";
    begin
        if (Rec."API Base URL" <> '') and HasStoredApiToken() then begin
            ConnectionStatusTxt := ConnectionConfiguredLbl;
            ConnectionStatusStyle := 'Favorable';
        end else begin
            ConnectionStatusTxt := ConnectionNotConfiguredLbl;
            ConnectionStatusStyle := 'Unfavorable';
        end;

        if Rec.Registered and (Rec."Tenant ID" <> '') and HasStoredApiToken() then begin
            RegistrationStatusTxt := RegisteredLbl;
            RegistrationStatusStyle := 'Favorable';
        end else begin
            RegistrationStatusTxt := NotRegisteredLbl;
            RegistrationStatusStyle := 'Unfavorable';
        end;

        EntraTenantIdTxt := IdentityMgt.GetEntraTenantId();
        EnvironmentNameTxt := IdentityMgt.GetEnvironmentName();
        EnvironmentTypeTxt := IdentityMgt.GetEnvironmentType();
        CompanySystemIdTxt := IdentityMgt.GetCompanyId();
    end;

    local procedure UpdateLatestRating(var LastRun: Record "DH Deep Scan Run")
    begin
        if LastRun."Entry No." = 0 then begin
            LatestRatingTxt := NoScanLbl;
            exit;
        end;

        if LastRun."Deep Score" >= 90 then
            LatestRatingTxt := RatingExcellentLbl
        else
            if LastRun."Deep Score" >= 70 then
                LatestRatingTxt := RatingGoodLbl
            else
                LatestRatingTxt := RatingNeedsAttentionLbl;
    end;

    local procedure LatestCompletedScanExists(): Boolean
    var
        DeepScanRun: Record "DH Deep Scan Run";
    begin
        DeepScanRun.SetRange(Status, DeepScanRun.Status::Completed);
        DeepScanRun.SetFilter("Run ID", '<>%1', '');
        exit(not DeepScanRun.IsEmpty());
    end;

    local procedure OpenFindingsForLatestScan()
    var
        DeepScanRun: Record "DH Deep Scan Run";
        Finding: Record "DH Deep Scan Finding";
        AccessGuard: Codeunit "DH Access Guard";
    begin
        AccessGuard.EnsureIssuesAccess();
        DeepScanRun.SetCurrentKey("Requested At");
        DeepScanRun.Ascending(false);
        if not DeepScanRun.FindFirst() then
            Error(NoScanLbl);

        Finding.SetRange("Deep Scan Entry No.", DeepScanRun."Entry No.");
        Page.Run(Page::"DH Deep Scan Findings List", Finding);
    end;

    local procedure OpenReportForLatestScan()
    var
        DeepScanRun: Record "DH Deep Scan Run";
        DeepScanMonitor: Page "DH Deep Scan Monitor";
    begin
        DeepScanRun.SetCurrentKey("Requested At");
        DeepScanRun.SetRange(Status, DeepScanRun.Status::Completed);
        DeepScanRun.SetFilter("Run ID", '<>%1', '');
        DeepScanRun.Ascending(false);
        if not DeepScanRun.FindFirst() then
            Error(NoScanLbl);

        DeepScanMonitor.SetRecord(DeepScanRun);
        DeepScanMonitor.OpenExecutiveHtmlReport();
    end;

    local procedure UpdateSchedulerVisibility()
    begin
        ShowWeeklySchedulerFields := Rec."Schedule Frequency" = Rec."Schedule Frequency"::Weekly;
        ShowMonthlySchedulerFields := Rec."Schedule Frequency" = Rec."Schedule Frequency"::Monthly;
    end;

    local procedure RescheduleEnabledScheduler()
    var
        SchedulerMgt: Codeunit "DH Scan Scheduler Mgt.";
    begin
        if not Rec."Scheduled Scans Enabled" then
            exit;

        SchedulerMgt.RescheduleSilently(Rec);
        UpdateActionState();
        UpdateDisplayValues();
        CurrPage.Update(false);
    end;

    local procedure LoadLastScan(var LastRun: Record "DH Deep Scan Run")
    begin
        Clear(LastRun);
        LastScanRunIdTxt := '';
        LastScanDateValue := 0DT;
        LastScanScoreTxt := '';
        LastScanIssuesValue := 0;
        LastScanEstimatedImpactTxt := '';
        LastScanDurationTxt := '';
        LastScanStatusTxt := '';
        ShowNoScanNotice := true;
        ModuleScoresNoticeTxt := NoScanAvailableYetLbl;

        LastRun.Reset();
        LastRun.SetCurrentKey("Requested At");
        LastRun.Ascending(false);
        if not LastRun.FindFirst() then begin
            LastScanStatusTxt := NoScanAvailableYetLbl;
            LastScanStatusStyle := 'Standard';
            exit;
        end;

        ShowNoScanNotice := false;
        ModuleScoresNoticeTxt := '';
        LastScanRunIdTxt := LastRun."Run ID";
        LastScanDateValue := LastRun."Requested At";
        LastScanScoreTxt := StrSubstNo('%1 / 100', LastRun."Deep Score");
        LastScanIssuesValue := LastRun."Issues Count";
        LastScanEstimatedImpactTxt := GetLocalAmountText(LastRun."Estimated Loss (EUR)");
        LastScanDurationTxt := GetDurationText(LastRun);
        LastScanStatusTxt := GetDeepScanStatusDisplay(LastRun);
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

    local procedure GetLocalAmountText(Amount: Decimal): Text[50]
    var
        CurrencyMgt: Codeunit "DH Currency Mgt.";
    begin
        exit(CurrencyMgt.FormatLocalAmount(Amount));
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
            Rec."Last Scheduled Scan Result"::Disabled:
                exit('Standard');
        end;
        exit('Standard');
    end;

    local procedure GetScheduledScanResultDisplay(): Text[100]
    begin
        case Rec."Last Scheduled Scan Result" of
            Rec."Last Scheduled Scan Result"::None:
                exit(UnknownLbl);
            Rec."Last Scheduled Scan Result"::Queued:
                exit(WaitingLbl);
            Rec."Last Scheduled Scan Result"::Completed:
                exit(SuccessLbl);
            Rec."Last Scheduled Scan Result"::Failed:
                exit(FailedLbl);
            Rec."Last Scheduled Scan Result"::SkippedMonitoringInactive:
                exit(SkippedLbl);
            Rec."Last Scheduled Scan Result"::SkippedConfiguration:
                exit(SkippedLbl);
            Rec."Last Scheduled Scan Result"::Disabled:
                exit(DisabledLbl);
        end;

        exit(UnknownLbl);
    end;

    local procedure GetDeepScanStatusDisplay(var DeepScanRun: Record "DH Deep Scan Run"): Text[100]
    begin
        case DeepScanRun.Status of
            DeepScanRun.Status::Queued:
                exit(QueuedLbl);
            DeepScanRun.Status::Running:
                exit(RunningLbl);
            DeepScanRun.Status::Completed:
                exit(CompletedLbl);
            DeepScanRun.Status::Failed:
                exit(FailedLbl);
            DeepScanRun.Status::Canceled:
                exit(CanceledLbl);
        end;

        exit('');
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

    local procedure StartAvailableScan()
    var
        Setup: Record "DH Setup";
        DeepScanRun: Record "DH Deep Scan Run";
        DeepScanMgt: Codeunit "DH Deep Scan Mgt.";
        EntryNo: Integer;
    begin
        EnsureSetupExists();
        Setup := Rec;

        if ShowStartFreeDataHealthScore and CanStartFreeDataHealthScore then begin
            EntryNo := DeepScanMgt.QueueDataHealthScore(Setup);
            if EntryNo = 0 then
                exit;
            Rec.Get('SETUP');
            Rec."Data Health Score Completed" := true;
            Rec."Can Run Data Health Score" := false;
            Rec.Modify(true);
        end else begin
            EntryNo := DeepScanMgt.QueueDeepScan(Setup);
            if EntryNo = 0 then
                exit;
        end;

        UpdateActionState();
        UpdateDisplayValues();
        CurrPage.Update(false);
        if DeepScanRun.Get(EntryNo) then
            Page.Run(Page::"DH Deep Scan Monitor", DeepScanRun);
    end;

    local procedure OpenLatestMonitor()
    var
        DeepScanRun: Record "DH Deep Scan Run";
    begin
        DeepScanRun.Reset();
        DeepScanRun.SetCurrentKey("Requested At");
        DeepScanRun.Ascending(false);
        if not DeepScanRun.FindFirst() then
            Error(NoDeepScanRunIsAvailableLbl);

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
    var
        ApiUrlPolicy: Codeunit "DH API URL Policy";
        IdentityMgt: Codeunit "DH Tenant Identity Mgt.";
    begin
        if Setup."API Base URL" = '' then
            Error(PleaseConfigureTheAPIBaseURLFirstLbl);

        if Setup."Tenant ID" = '' then
            Error(TenantIsNotRegisteredYetLbl);

        exit(ApiUrlPolicy.BuildUrl(Setup."API Base URL", '/analytics/get-token') + '?company=' + EncodeUrlValue(CompanyName()) + '&environment=' + EncodeUrlValue(IdentityMgt.GetEnvironmentName()) + '&environment_type=' + EncodeUrlValue(IdentityMgt.GetEnvironmentType()) + '&entra_tenant_id=' + EncodeUrlValue(IdentityMgt.GetEntraTenantId()) + '&company_id=' + EncodeUrlValue(IdentityMgt.GetCompanyId()) + '&tenant_id=' + EncodeUrlValue(Setup."Tenant ID") + '&scan_mode=' + EncodeUrlValue(GetScanMode(Setup)) + '&bc_issue_launch_url=' + EncodeUrlValue(GetIssueDrilldownLaunchUrl()));
    end;

    local procedure GetScanMode(var Setup: Record "DH Setup"): Text
    begin
        if Setup."Premium Enabled" then
            exit('premium_deep');
        exit('free_deep');
    end;

    local procedure GetDashboardUrl(var Setup: Record "DH Setup"; Token: Text): Text
    var
        ApiUrlPolicy: Codeunit "DH API URL Policy";
    begin
        exit(ApiUrlPolicy.BuildUrl(Setup."API Base URL", '/analytics/embed') + '?embed_token=' + EncodeUrlValue(Token));
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
            Error(TheTokenResponseIsNotValidJSONLbl);

        if not JsonObj.Get('token', JsonToken) then
            Error(TheTokenFieldIsMissingInTheLbl);

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


    var
        PleaseEnterAContactEmailAddressFirstLbl: Label 'Please enter a contact email address first. It is required for dashboard access and important BCSentinel notifications.';
        BCSentinelRegistrationDataIsIncompleteRegistLbl: Label 'BCSentinel registration data is incomplete. Registration will request a fresh API token.';
        RegistrationUnexpectedErrorLbl: Label 'The registration could not be completed because of an unexpected error. Try again later or contact BCSentinel support.';
        ResetTheCachedBCSentinelRegistrationStatusThLbl: Label 'Reset the cached BCSentinel registration status? The stable tenant binding, API token, purchases, and scan history are preserved. Use Register afterwards to reconcile with the backend.';
        CachedRegistrationStatusWasResetWithoutChangLbl: Label 'Cached registration status was reset without changing the tenant identity. Please register again to reconcile.';
        PleaseRegisterTheTenantFirstLbl: Label 'Please register the tenant first.';
        ProductAccessRefreshedLbl: Label 'Product access refreshed.';
        NextScheduledScan1Lbl: Label 'Next scheduled scan: %1', Comment = '%1 = runtime value';
        BeforeRegistrationOrScansBCSentinelRequiresYLbl: Label 'Before registration or scans, BCSentinel requires your consent to send and process tenant and company identifiers, metadata, configuration data, scan results, findings, and aggregated quality metrics. The data is used for Data Health analysis, dashboards, executive reports, and license checks.';
        ScanNotPossibleAtLeastOneModuleLbl: Label 'Scan not possible. At least one module must be active.';
        ScanNotPossibleAtLeastOneCheckLbl: Label 'Scan not possible. At least one check must be active.';
        ScanPossibleRequiredModulesAndChecksAreLbl: Label 'Scan possible. Required modules and checks are available.';
        NoScanAvailableYetLbl: Label 'No scan available yet.';
        UnknownLbl: Label 'Unknown';
        WaitingLbl: Label 'Waiting';
        SuccessLbl: Label 'Success';
        FailedLbl: Label 'Failed';
        SkippedLbl: Label 'Skipped';
        DisabledLbl: Label 'Disabled';
        QueuedLbl: Label 'Queued';
        RunningLbl: Label 'Running';
        CompletedLbl: Label 'Completed';
        CanceledLbl: Label 'Canceled';
        NoDeepScanRunIsAvailableLbl: Label 'No deep scan run is available.';
        PleaseConfigureTheAPIBaseURLFirstLbl: Label 'Please configure the API Base URL first.';
        TenantIsNotRegisteredYetLbl: Label 'Tenant is not registered yet.';
        TheTokenResponseIsNotValidJSONLbl: Label 'The token response is not valid JSON.';
        TheTokenFieldIsMissingInTheLbl: Label 'The token field is missing in the response.';
}
