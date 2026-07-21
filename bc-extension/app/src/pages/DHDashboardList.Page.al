page 53124 "DH Dashboard List"
{
    PageType = List;
    SourceTable = "DH Scan Header";
    ApplicationArea = All;
    UsageCategory = Lists;
    Caption = 'BCSentinel Dashboards';
    CardPageId = "DH Deep Scan Monitor";
    Editable = false;
    InsertAllowed = false;
    DeleteAllowed = false;
    ModifyAllowed = false;

    layout
    {
        area(Content)
        {
            group(EmptyState)
            {
                ShowCaption = false;
                Visible = EmptyStateVisible;
                field(EmptyStateText; EmptyStateTxt)
                {
                    ApplicationArea = All;
                    ShowCaption = false;
                    Editable = false;
                    MultiLine = true;
                    ToolTip = 'Explains that no scan results are available.';
                }
            }
            repeater(Entries)
            {
                field(DisplayRunId; Rec.GetDisplayRunId())
                {
                    ApplicationArea = All;
                    Caption = 'Run ID';
                    ToolTip = 'Specifies Run ID.';
                }

                field("Scan Type"; Rec."Scan Type")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Scan Type.';
                }

                field("Scan DateTime"; Rec."Scan DateTime")
                {
                    ApplicationArea = All;
                    Caption = 'Scan Date';
                    ToolTip = 'Specifies Scan Date.';
                }

                field("Data Score"; Rec."Data Score")
                {
                    ApplicationArea = All;
                    Caption = 'Score';
                    ToolTip = 'Specifies Score.';
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

                field(MonitoringAmountDisplay; MonitoringAmountTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Monitoring / Month';
                    ToolTip = 'Specifies the estimated monitoring amount per month in local currency.';
                }

                field(ImpactDisplay; ImpactTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Impact';
                    ToolTip = 'Specifies the estimated impact in local currency.';
                }

                field(ROIDisplay; ROITxt)
                {
                    ApplicationArea = All;
                    Caption = 'ROI';
                    ToolTip = 'Specifies ROI in local currency.';
                }

                field("Headline"; Rec."Headline")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Headline.';
                }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(OpenDashboardCard)
            {
                Caption = 'Open Dashboard';
                ToolTip = 'Runs Open Dashboard.';
                ApplicationArea = All;
                Image = Navigate;

                trigger OnAction()
                begin
                    Page.Run(Page::"DH Deep Scan Monitor", Rec);
                end;
            }

            action(RunQuickScan)
            {
                Caption = 'Run Scan';
                ToolTip = 'Runs Run Scan.';
                ApplicationArea = All;
                Image = Calculate;

                trigger OnAction()
                var
                    Setup: Record "DH Setup";
                    QuickScanMgt: Codeunit "DH QuickScan Mgt.";
                begin
                    if not Setup.Get('SETUP') then
                        Error(SetupNotFoundErr);

                    QuickScanMgt.RunQuickScanAndOpenDashboard(Setup);
                    CurrPage.Update(false);
                end;
            }

            action(DeleteSelectedDashboard)
            {
                Caption = 'Delete Selected Dashboard';
                ToolTip = 'Runs Delete Selected Dashboard.';
                ApplicationArea = All;
                Image = Delete;

                trigger OnAction()
                var
                    Setup: Record "DH Setup";
                    ApiClient: Codeunit "DH API Client";
                    BackendDeleteId: Code[50];
                begin
                    if Rec."Entry No." = 0 then
                        Error(SelectDashboardEntryErr);

                    if Confirm(DeleteDashboardQst, false, Format(Rec."Scan DateTime")) then begin
                        BackendDeleteId := GetBackendDeleteId();

                        if Setup.Get('SETUP') then
                            if (Setup."Tenant ID" <> '') and HasApiToken(Setup) and (BackendDeleteId <> '') then
                                ApiClient.DeleteScanFromBackend(Setup, BackendDeleteId);

                        Rec.Delete(true);
                        CurrPage.Update(false);
                    end;
                end;
            }

            action(ReconcileScanHistory)
            {
                Caption = 'Reconcile Scan History';
                ToolTip = 'Runs Reconcile Scan History.';
                ApplicationArea = All;
                Image = RefreshLines;

                trigger OnAction()
                var
                    Setup: Record "DH Setup";
                    ApiClient: Codeunit "DH API Client";
                begin
                    if not Setup.Get('SETUP') then
                        Error(SetupNotFoundErr);

                    if not Confirm(ReconcileScanHistoryQst, false) then
                        exit;

                    ApiClient.ReconcileScansWithBackend(Setup);
                    Message(ScanHistorySynchronizedMsg);
                    CurrPage.Update(false);
                end;
            }

            action(OpenSetup)
            {
                Caption = 'Open Setup';
                ToolTip = 'Runs Open Setup.';
                ApplicationArea = All;
                Image = Setup;
                RunObject = page "DH Setup";
            }

            action(UpgradeToPremium)
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
                    if not Setup.Get('SETUP') then
                        Error(SetupNotFoundErr);

                    if Setup."Premium Enabled" then begin
                        Message(MonitoringAlreadyActiveMsg);
                        exit;
                    end;

                    ApiClient.OpenProductCheckout(Setup, 'monitoring_monthly');
                end;
            }
        }

        area(Promoted)
        {
            group(Process)
            {
                actionref(OpenDashboardCard_Promoted; OpenDashboardCard)
                {
                }
                actionref(RunQuickScan_Promoted; RunQuickScan)
                {
                }
                actionref(DeleteSelectedDashboard_Promoted; DeleteSelectedDashboard)
                {
                }
                actionref(ReconcileScanHistory_Promoted; ReconcileScanHistory)
                {
                }
                actionref(UpgradeToPremium_Promoted; UpgradeToPremium)
                {
                }
            }
        }
    }

    trigger OnOpenPage()
    begin
        Rec.SetCurrentKey("Scan DateTime");
        Rec.Ascending(false);
        EmptyStateTxt := NoScanResultsLbl;
        EmptyStateVisible := Rec.IsEmpty();
    end;

    trigger OnAfterGetRecord()
    begin
        EmptyStateVisible := false;
        MonitoringAmountTxt := GetLocalAmountText(Rec."Est. Premium Price");
        ImpactTxt := GetLocalAmountText(Rec."Estimated Loss (EUR)");
        ROITxt := GetLocalAmountText(Rec."ROI");
    end;

    var
        EmptyStateTxt: Text[100];
        EmptyStateVisible: Boolean;
        ImpactTxt: Text[50];
        MonitoringAmountTxt: Text[50];
        ROITxt: Text[50];
        DeleteDashboardQst: Label 'Do you want to delete the selected dashboard from %1?', Comment = '%1 = scan date and time';
        MonitoringAlreadyActiveMsg: Label 'Monitoring is already active.';
        NoScanResultsLbl: Label 'No scan results are available yet.';
        ReconcileScanHistoryQst: Label 'This aligns the BCSentinel scan history with the current Business Central scan list and removes orphaned backend scans. Do you want to continue?';
        ScanHistorySynchronizedMsg: Label 'Scan history successfully synchronized.';
        SelectDashboardEntryErr: Label 'Select a dashboard entry first.';
        SetupNotFoundErr: Label 'BCSentinel setup was not found.';

    local procedure GetBackendDeleteId(): Code[50]
    begin
        if Rec."Backend Scan Id" <> '' then
            exit(Rec."Backend Scan Id");

        exit(Rec.GetDisplayRunId());
    end;

    local procedure HasApiToken(var Setup: Record "DH Setup"): Boolean
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        exit(SecretMgt.HasApiToken(Setup));
    end;

    local procedure GetLocalAmountText(Amount: Decimal): Text[50]
    var
        CurrencyMgt: Codeunit "DH Currency Mgt.";
    begin
        exit(CurrencyMgt.FormatLocalAmount(Amount));
    end;
}
