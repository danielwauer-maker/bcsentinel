page 53172 "DH Scan Modules"
{
    PageType = Card;
    SourceTable = "DH Setup";
    Caption = 'BCSentinel Scan Modules';
    ApplicationArea = All;
    UsageCategory = Administration;

    layout
    {
        area(Content)
        {
            group(Summary)
            {
                Caption = 'Summary';

                field(ActiveModules; ActiveModulesTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Active Modules';
                    Editable = false;
                    StyleExpr = ActiveModulesStyle;
                    ToolTip = 'Shows how many scan modules are active.';
                }
                field(ActiveChecks; ActiveChecksTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Active Checks';
                    Editable = false;
                    StyleExpr = ActiveChecksStyle;
                    ToolTip = 'Shows how many checks are active for the current module selection.';
                }
                field(ModuleSelectionStatus; ModuleSelectionStatusTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Scan Status';
                    Editable = false;
                    MultiLine = true;
                    StyleExpr = ModuleSelectionStatusStyle;
                    ToolTip = 'Shows whether the module selection allows scans.';
                }
            }

            group(SystemModule)
            {
                Caption = 'System';

                field("Scan System Module"; Rec."Scan System Module")
                {
                    ApplicationArea = All;
                    Caption = 'Active';
                    ToolTip = 'Include system and setup checks in scans.';
                }
                field(SystemDescription; SystemDescriptionTxt) { ApplicationArea = All; Caption = 'Description'; Editable = false; MultiLine = true; }
                field(SystemChecks; SystemChecksTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Checks';
                    Editable = false;
                    DrillDown = true;

                    trigger OnDrillDown()
                    begin
                        OpenChecksForModule('SYSTEM');
                    end;
                }
                field(SystemScore; SystemScoreTxt) { ApplicationArea = All; Caption = 'Last Score'; Editable = false; StyleExpr = SystemScoreStyle; }
            }

            group(FinanceModule)
            {
                Caption = 'Finance';
                field("Scan Finance Module"; Rec."Scan Finance Module") { ApplicationArea = All; Caption = 'Active'; ToolTip = 'Include finance-related checks in scans.'; }
                field(FinanceDescription; FinanceDescriptionTxt) { ApplicationArea = All; Caption = 'Description'; Editable = false; MultiLine = true; }
                field(FinanceChecks; FinanceChecksTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Checks';
                    Editable = false;
                    DrillDown = true;

                    trigger OnDrillDown()
                    begin
                        OpenChecksForModule('FINANCE');
                    end;
                }
                field(FinanceScore; FinanceScoreTxt) { ApplicationArea = All; Caption = 'Last Score'; Editable = false; StyleExpr = FinanceScoreStyle; }
            }

            group(SalesModule)
            {
                Caption = 'Sales';
                field("Scan Sales Module"; Rec."Scan Sales Module") { ApplicationArea = All; Caption = 'Active'; ToolTip = 'Include sales-related checks in scans.'; }
                field(SalesDescription; SalesDescriptionTxt) { ApplicationArea = All; Caption = 'Description'; Editable = false; MultiLine = true; }
                field(SalesChecks; SalesChecksTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Checks';
                    Editable = false;
                    DrillDown = true;

                    trigger OnDrillDown()
                    begin
                        OpenChecksForModule('SALES');
                    end;
                }
                field(SalesScore; SalesScoreTxt) { ApplicationArea = All; Caption = 'Last Score'; Editable = false; StyleExpr = SalesScoreStyle; }
            }

            group(PurchasingModule)
            {
                Caption = 'Purchasing';
                field("Scan Purchasing Module"; Rec."Scan Purchasing Module") { ApplicationArea = All; Caption = 'Active'; ToolTip = 'Include purchasing-related checks in scans.'; }
                field(PurchasingDescription; PurchasingDescriptionTxt) { ApplicationArea = All; Caption = 'Description'; Editable = false; MultiLine = true; }
                field(PurchasingChecks; PurchasingChecksTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Checks';
                    Editable = false;
                    DrillDown = true;

                    trigger OnDrillDown()
                    begin
                        OpenChecksForModule('PURCHASING');
                    end;
                }
                field(PurchasingScore; PurchasingScoreTxt) { ApplicationArea = All; Caption = 'Last Score'; Editable = false; StyleExpr = PurchasingScoreStyle; }
            }

            group(InventoryModule)
            {
                Caption = 'Inventory';
                field("Scan Inventory Module"; Rec."Scan Inventory Module") { ApplicationArea = All; Caption = 'Active'; ToolTip = 'Include inventory-related checks in scans.'; }
                field(InventoryDescription; InventoryDescriptionTxt) { ApplicationArea = All; Caption = 'Description'; Editable = false; MultiLine = true; }
                field(InventoryChecks; InventoryChecksTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Checks';
                    Editable = false;
                    DrillDown = true;

                    trigger OnDrillDown()
                    begin
                        OpenChecksForModule('INVENTORY');
                    end;
                }
                field(InventoryScore; InventoryScoreTxt) { ApplicationArea = All; Caption = 'Last Score'; Editable = false; StyleExpr = InventoryScoreStyle; }
            }

            group(CRMModule)
            {
                Caption = 'CRM';
                field("Scan CRM Module"; Rec."Scan CRM Module") { ApplicationArea = All; Caption = 'Active'; ToolTip = 'Include CRM/contact-related checks in scans.'; }
                field(CRMDescription; CRMDescriptionTxt) { ApplicationArea = All; Caption = 'Description'; Editable = false; MultiLine = true; }
                field(CRMChecks; CRMChecksTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Checks';
                    Editable = false;
                    DrillDown = true;

                    trigger OnDrillDown()
                    begin
                        OpenChecksForModule('CRM');
                    end;
                }
                field(CRMScore; CRMScoreTxt) { ApplicationArea = All; Caption = 'Last Score'; Editable = false; StyleExpr = CRMScoreStyle; }
            }

            group(ManufacturingModule)
            {
                Caption = 'Manufacturing';
                field("Scan Manufacturing Module"; Rec."Scan Manufacturing Module") { ApplicationArea = All; Caption = 'Active'; ToolTip = 'Include manufacturing-related checks in scans.'; }
                field(ManufacturingDescription; ManufacturingDescriptionTxt) { ApplicationArea = All; Caption = 'Description'; Editable = false; MultiLine = true; }
                field(ManufacturingChecks; ManufacturingChecksTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Checks';
                    Editable = false;
                    DrillDown = true;

                    trigger OnDrillDown()
                    begin
                        OpenChecksForModule('MANUFACTURING');
                    end;
                }
                field(ManufacturingScore; ManufacturingScoreTxt) { ApplicationArea = All; Caption = 'Last Score'; Editable = false; StyleExpr = ManufacturingScoreStyle; }
            }

            group(ServiceModule)
            {
                Caption = 'Service';
                field("Scan Service Module"; Rec."Scan Service Module") { ApplicationArea = All; Caption = 'Active'; ToolTip = 'Include service-related checks in scans.'; }
                field(ServiceDescription; ServiceDescriptionTxt) { ApplicationArea = All; Caption = 'Description'; Editable = false; MultiLine = true; }
                field(ServiceChecks; ServiceChecksTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Checks';
                    Editable = false;
                    DrillDown = true;

                    trigger OnDrillDown()
                    begin
                        OpenChecksForModule('SERVICE');
                    end;
                }
                field(ServiceScore; ServiceScoreTxt) { ApplicationArea = All; Caption = 'Last Score'; Editable = false; StyleExpr = ServiceScoreStyle; }
            }

            group(JobsModule)
            {
                Caption = 'Jobs';
                field("Scan Jobs Module"; Rec."Scan Jobs Module") { ApplicationArea = All; Caption = 'Active'; ToolTip = 'Include jobs and project-related checks in scans.'; }
                field(JobsDescription; JobsDescriptionTxt) { ApplicationArea = All; Caption = 'Description'; Editable = false; MultiLine = true; }
                field(JobsChecks; JobsChecksTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Checks';
                    Editable = false;
                    DrillDown = true;

                    trigger OnDrillDown()
                    begin
                        OpenChecksForModule('JOB');
                    end;
                }
                field(JobsScore; JobsScoreTxt) { ApplicationArea = All; Caption = 'Last Score'; Editable = false; StyleExpr = JobsScoreStyle; }
            }

            group(HRModule)
            {
                Caption = 'HR';
                field("Scan HR Module"; Rec."Scan HR Module") { ApplicationArea = All; Caption = 'Active'; ToolTip = 'Include HR-related checks in scans.'; }
                field(HRDescription; HRDescriptionTxt) { ApplicationArea = All; Caption = 'Description'; Editable = false; MultiLine = true; }
                field(HRChecks; HRChecksTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Checks';
                    Editable = false;
                    DrillDown = true;

                    trigger OnDrillDown()
                    begin
                        OpenChecksForModule('HR');
                    end;
                }
                field(HRScore; HRScoreTxt) { ApplicationArea = All; Caption = 'Last Score'; Editable = false; StyleExpr = HRScoreStyle; }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(EnableAll)
            {
                Caption = 'Enable All';
                ToolTip = 'Enables all scan modules.';
                ApplicationArea = All;
                Image = Approve;
                Promoted = true;
                PromotedCategory = Process;

                trigger OnAction()
                begin
                    Rec.SetAllScanModules(true);
                    Rec.Modify(true);
                    UpdateDisplayValues();
                    CurrPage.Update(false);
                end;
            }
            action(DisableAll)
            {
                Caption = 'Disable All';
                ToolTip = 'Disables all scan modules. Scan start will be blocked until at least one module is active.';
                ApplicationArea = All;
                Image = Cancel;
                Promoted = true;
                PromotedCategory = Process;

                trigger OnAction()
                begin
                    Rec.SetAllScanModules(false);
                    Rec.Modify(true);
                    UpdateDisplayValues();
                    CurrPage.Update(false);
                end;
            }
            action(RestoreDefaults)
            {
                Caption = 'Restore Defaults';
                ToolTip = 'Restores the default scan module selection.';
                ApplicationArea = All;
                Image = Restore;
                Promoted = true;
                PromotedCategory = Process;

                trigger OnAction()
                begin
                    Rec.RestoreDefaultScanModules();
                    Rec.Modify(true);
                    UpdateDisplayValues();
                    CurrPage.Update(false);
                end;
            }
            action(SelectChecks)
            {
                Caption = 'Select Checks';
                ToolTip = 'Opens the Monitoring-only check selection.';
                ApplicationArea = All;
                Image = CheckList;

                trigger OnAction()
                begin
                    OpenChecks();
                end;
            }
        }
    }

    trigger OnOpenPage()
    begin
        if not Rec.Get('SETUP') then begin
            Rec.Init();
            Rec."Primary Key" := 'SETUP';
            Rec.Insert(true);
        end;
        UpdateDisplayValues();
    end;

    trigger OnAfterGetCurrRecord()
    begin
        UpdateDisplayValues();
    end;

    var
        ActiveModulesTxt: Text[100];
        ActiveChecksTxt: Text[100];
        ModuleSelectionStatusTxt: Text[250];
        ActiveModulesStyle: Text[30];
        ActiveChecksStyle: Text[30];
        ModuleSelectionStatusStyle: Text[30];
        SystemDescriptionTxt: Text[250];
        FinanceDescriptionTxt: Text[250];
        SalesDescriptionTxt: Text[250];
        PurchasingDescriptionTxt: Text[250];
        InventoryDescriptionTxt: Text[250];
        CRMDescriptionTxt: Text[250];
        ManufacturingDescriptionTxt: Text[250];
        ServiceDescriptionTxt: Text[250];
        JobsDescriptionTxt: Text[250];
        HRDescriptionTxt: Text[250];
        SystemChecksTxt: Text[50];
        FinanceChecksTxt: Text[50];
        SalesChecksTxt: Text[50];
        PurchasingChecksTxt: Text[50];
        InventoryChecksTxt: Text[50];
        CRMChecksTxt: Text[50];
        ManufacturingChecksTxt: Text[50];
        ServiceChecksTxt: Text[50];
        JobsChecksTxt: Text[50];
        HRChecksTxt: Text[50];
        SystemScoreTxt: Text[50];
        FinanceScoreTxt: Text[50];
        SalesScoreTxt: Text[50];
        PurchasingScoreTxt: Text[50];
        InventoryScoreTxt: Text[50];
        CRMScoreTxt: Text[50];
        ManufacturingScoreTxt: Text[50];
        ServiceScoreTxt: Text[50];
        JobsScoreTxt: Text[50];
        HRScoreTxt: Text[50];
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

    local procedure UpdateDisplayValues()
    var
        SchedulerMgt: Codeunit "DH Scan Scheduler Mgt.";
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
        LastRun: Record "DH Deep Scan Run";
        EnabledChecks: Integer;
    begin
        ActiveModulesTxt := SchedulerMgt.GetActiveModulesSummary(Rec);
        ActiveChecksTxt := SchedulerMgt.GetActiveChecksSummary(Rec);
        EnabledChecks := ScanCheckMgt.GetExpectedChecksCount(Rec);
        ActiveModulesStyle := GetOkStyle(Rec.HasAnyModuleEnabled());
        ActiveChecksStyle := GetOkStyle(EnabledChecks > 0);
        if not Rec.HasAnyModuleEnabled() then begin
            ModuleSelectionStatusTxt := 'Scan not possible. At least one module must be active.';
            ModuleSelectionStatusStyle := 'Unfavorable';
        end else
            if EnabledChecks = 0 then begin
                ModuleSelectionStatusTxt := 'Scan not possible. At least one check must be active.';
                ModuleSelectionStatusStyle := 'Unfavorable';
            end else begin
                ModuleSelectionStatusTxt := 'Scan possible. Required modules and checks are available.';
                ModuleSelectionStatusStyle := 'Favorable';
            end;

        SystemDescriptionTxt := 'System, setup, dimensions and core configuration.';
        FinanceDescriptionTxt := 'Finance, posting setup, VAT and ledger quality checks.';
        SalesDescriptionTxt := 'Sales master data and sales document quality checks.';
        PurchasingDescriptionTxt := 'Purchasing master data and purchase document quality checks.';
        InventoryDescriptionTxt := 'Inventory, item master data and stock value checks.';
        CRMDescriptionTxt := 'Contacts, relationships and CRM data quality checks.';
        ManufacturingDescriptionTxt := 'Manufacturing and production master data checks.';
        ServiceDescriptionTxt := 'Service management data quality checks.';
        JobsDescriptionTxt := 'Jobs and project-related planning checks.';
        HRDescriptionTxt := 'Employees and resources data quality checks.';

        SystemChecksTxt := GetModuleChecksText('SYSTEM');
        FinanceChecksTxt := GetModuleChecksText('FINANCE');
        SalesChecksTxt := GetModuleChecksText('SALES');
        PurchasingChecksTxt := GetModuleChecksText('PURCHASING');
        InventoryChecksTxt := GetModuleChecksText('INVENTORY');
        CRMChecksTxt := GetModuleChecksText('CRM');
        ManufacturingChecksTxt := GetModuleChecksText('MANUFACTURING');
        ServiceChecksTxt := GetModuleChecksText('SERVICE');
        JobsChecksTxt := GetModuleChecksText('JOB');
        HRChecksTxt := GetModuleChecksText('HR');

        LastRun.Reset();
        LastRun.SetCurrentKey("Requested At");
        LastRun.Ascending(false);
        if LastRun.FindFirst() then begin
            SystemScoreTxt := FormatScore(LastRun."System Score");
            FinanceScoreTxt := FormatScore(LastRun."Finance Score");
            SalesScoreTxt := FormatScore(LastRun."Sales Score");
            PurchasingScoreTxt := FormatScore(LastRun."Purchasing Score");
            InventoryScoreTxt := FormatScore(LastRun."Inventory Score");
            CRMScoreTxt := FormatScore(LastRun."CRM Score");
            ManufacturingScoreTxt := FormatScore(LastRun."Manufacturing Score");
            ServiceScoreTxt := FormatScore(LastRun."Service Score");
            JobsScoreTxt := FormatScore(LastRun."Jobs Score");
            HRScoreTxt := FormatScore(LastRun."HR Score");
            SystemScoreStyle := GetScoreStyle(LastRun."System Score");
            FinanceScoreStyle := GetScoreStyle(LastRun."Finance Score");
            SalesScoreStyle := GetScoreStyle(LastRun."Sales Score");
            PurchasingScoreStyle := GetScoreStyle(LastRun."Purchasing Score");
            InventoryScoreStyle := GetScoreStyle(LastRun."Inventory Score");
            CRMScoreStyle := GetScoreStyle(LastRun."CRM Score");
            ManufacturingScoreStyle := GetScoreStyle(LastRun."Manufacturing Score");
            ServiceScoreStyle := GetScoreStyle(LastRun."Service Score");
            JobsScoreStyle := GetScoreStyle(LastRun."Jobs Score");
            HRScoreStyle := GetScoreStyle(LastRun."HR Score");
        end else begin
            SystemScoreTxt := '-';
            FinanceScoreTxt := '-';
            SalesScoreTxt := '-';
            PurchasingScoreTxt := '-';
            InventoryScoreTxt := '-';
            CRMScoreTxt := '-';
            ManufacturingScoreTxt := '-';
            ServiceScoreTxt := '-';
            JobsScoreTxt := '-';
            HRScoreTxt := '-';
        end;
    end;

    local procedure GetModuleChecksText(ModuleName: Text[100]): Text[50]
    var
        ScanCheck: Record "DH Scan Check Selection";
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
        ActiveCount: Integer;
        TotalCount: Integer;
    begin
        ScanCheckMgt.EnsureDefaultChecks();
        ScanCheck.SetRange("Module", ModuleName);
        TotalCount := ScanCheck.Count();
        ScanCheck.SetRange(Enabled, true);
        ActiveCount := ScanCheck.Count();
        exit(StrSubstNo('%1 / %2 active', ActiveCount, TotalCount));
    end;

    local procedure OpenChecksForModule(ModuleName: Text[100])
    var
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
        ScanCheck: Record "DH Scan Check Selection";
    begin
        ScanCheckMgt.EnsureMonitoringAccess(true);
        ScanCheckMgt.EnsureDefaultChecks();
        ScanCheck.SetRange("Module", ModuleName);
        Page.Run(Page::"DH Scan Checks", ScanCheck);
    end;

    local procedure OpenChecks()
    var
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
    begin
        ScanCheckMgt.EnsureMonitoringAccess(true);
        Page.Run(Page::"DH Scan Checks");
    end;

    local procedure FormatScore(Score: Integer): Text[50]
    begin
        exit(StrSubstNo('%1 / 100', Score));
    end;

    local procedure GetOkStyle(IsOk: Boolean): Text[30]
    begin
        if IsOk then
            exit('Favorable');
        exit('Unfavorable');
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
}
