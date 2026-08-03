codeunit 53128 "DH Deep Scan Runner"
{
    TableNo = "DH Deep Scan Run";

    trigger OnRun()
    var
        DeepScanFailure: Codeunit "DH Deep Scan Failure";
        FailureText: Text;
    begin
        if TryProcessRun(Rec) then
            exit;

        FailureText := GetLastErrorText();
        ClearLastError();
        DeepScanFailure.MarkRunAsFailed(Rec, FailureText);
    end;

    [TryFunction]
    local procedure TryProcessRun(var DeepScanRun: Record "DH Deep Scan Run")
    begin
        ProcessRun(DeepScanRun);
    end;

    procedure RunSynchronously(var DeepScanRun: Record "DH Deep Scan Run")
    begin
        ProcessRun(DeepScanRun);
    end;

    local procedure ProcessRun(var DeepScanRun: Record "DH Deep Scan Run")
    var
        Score: Integer;
        ChecksCount: Integer;
        IssuesCount: Integer;
        Setup: Record "DH Setup";
        ApiClient: Codeunit "DH API Client";
        RequestText: Text;
        SyncResponseText: Text;
        SyncFailureMessage: Text;
        SyncSucceeded: Boolean;
        LeaseRejected: Boolean;
    begin
        DeepScanRun.LockTable();
        if not DeepScanRun.Get(DeepScanRun."Entry No.") then
            exit;

        if DeepScanRun.Status <> DeepScanRun.Status::Queued then
            exit;

        DeepScanRun.Status := DeepScanRun.Status::Running;
        DeepScanRun."Started At" := CurrentDateTime();
        DeepScanRun."Finished At" := 0DT;
        DeepScanRun."Error Message" := '';
        DeepScanRun."Headline" := CopyStr(GetRunningHeadline(DeepScanRun), 1, MaxStrLen(DeepScanRun."Headline"));
        DeepScanRun."Current Module" := 'Initializing';
        DeepScanRun."Progress %" := 0;
        DeepScanRun."Completed Modules" := 0;
        DeepScanRun."ETA Text" := 'Calculating...';
        DeepScanRun.Modify(true);
        Commit();
        TryUpdateBackendProgress(DeepScanRun, 'running', 'Preparing scan checks', GetStartedEventMessage(DeepScanRun));

        ExceptionMgt.BeginExceptionTracking();
        RunChecks(DeepScanRun, Score, ChecksCount, IssuesCount);

        DeepScanRun.Get(DeepScanRun."Entry No.");
        RecalculateScoreMetrics(DeepScanRun, Score);
        ClearDeepScanCommercials(DeepScanRun);
        DeepScanRun."Deep Score" := Score;
        DeepScanRun."Checks Count" := ChecksCount;
        DeepScanRun."Issues Count" := IssuesCount;
        DeepScanRun."Applied Exception Count" := ExceptionMgt.GetAppliedExceptionCount();
        DeepScanRun."Rating" := CopyStr(GetRating(Score), 1, MaxStrLen(DeepScanRun."Rating"));
        DeepScanRun."Headline" := CopyStr(GetHeadline(Score, IssuesCount), 1, MaxStrLen(DeepScanRun."Headline"));
        DeepScanRun.Status := DeepScanRun.Status::Running;
        DeepScanRun."Finished At" := 0DT;
        DeepScanRun."Current Module" := 'Finalizing';
        DeepScanRun."Current Step" := 'Persisting scan result';
        DeepScanRun."Progress %" := 99;
        DeepScanRun."Completed Modules" := DeepScanRun."Total Modules";
        DeepScanRun."ETA Text" := 'Finalizing';
        DeepScanRun."System Progress %" := 100;
        DeepScanRun."Finance Progress %" := 100;
        DeepScanRun."Sales Progress %" := 100;
        DeepScanRun."Purchasing Progress %" := 100;
        DeepScanRun."Inventory Progress %" := 100;
        DeepScanRun."CRM Progress %" := 100;
        DeepScanRun."Manufacturing Progress %" := 100;
        DeepScanRun."Service Progress %" := 100;
        DeepScanRun."Jobs Progress %" := 100;
        DeepScanRun."HR Progress %" := 100;
        DeepScanRun.Modify(true);
        Commit();

        if not Setup.Get('SETUP') then
            Error(SetupMissingForPersistenceErr);

        DeepScanRun.Get(DeepScanRun."Entry No.");
        if DeepScanRun."Backend Sync Status" = DeepScanRun."Backend Sync Status"::Failed then begin
            MarkLocalCompletionWithSyncFailure(DeepScanRun, DeepScanRun."Backend Sync Error", true);
            exit;
        end;

        RequestText := BuildSyncPayload(Setup, DeepScanRun);
        if not TrySynchronizeScan(Setup, RequestText, SyncResponseText, SyncFailureMessage, LeaseRejected, SyncSucceeded) then begin
            SyncFailureMessage := GetLastErrorText();
            if SyncFailureMessage = '' then
                SyncFailureMessage := SyncUnexpectedFailureLbl;
            MarkLocalCompletionWithSyncFailure(DeepScanRun, SyncFailureMessage, false);
            exit;
        end;
        if not SyncSucceeded then begin
            MarkLocalCompletionWithSyncFailure(DeepScanRun, SyncFailureMessage, LeaseRejected);
            exit;
        end;

        DeepScanRun.Get(DeepScanRun."Entry No.");
        ApiClient.ApplyScanSyncLifecycleResponse(SyncResponseText, DeepScanRun);
        DeepScanRun.Status := DeepScanRun.Status::Completed;
        if DeepScanRun."Finished At" = 0DT then
            DeepScanRun."Finished At" := CurrentDateTime();
        DeepScanRun."Current Module" := 'Completed';
        DeepScanRun."Current Step" := 'Scan completed';
        DeepScanRun."Progress %" := 100;
        DeepScanRun."ETA Text" := 'Completed';
        DeepScanRun."Backend Sync Status" := DeepScanRun."Backend Sync Status"::Synchronized;
        DeepScanRun."Backend Status" := 'completed';
        DeepScanRun."Backend Sync Error" := '';
        DeepScanRun."Warning Message" := '';
        DeepScanRun."Error Message" := '';
        DeepScanRun.Modify(true);
        EnsureDashboardHeaderForDeepScan(DeepScanRun);
        Commit();
        if not TryApplySyncPostprocessing(DeepScanRun, SyncResponseText) then begin
            DeepScanRun.Get(DeepScanRun."Entry No.");
            DeepScanRun."Warning Message" := CopyStr(PostprocessingRefreshFailedLbl, 1, MaxStrLen(DeepScanRun."Warning Message"));
            DeepScanRun.Modify(true);
            Commit();
        end;
        TryRefreshLicenseAfterCompletion(Setup);
    end;

    [TryFunction]
    local procedure TrySynchronizeScan(var Setup: Record "DH Setup"; RequestText: Text; var SyncResponseText: Text; var FailureMessage: Text; var LeaseRejected: Boolean; var SyncSucceeded: Boolean)
    var
        ApiClient: Codeunit "DH API Client";
    begin
        SyncSucceeded := ApiClient.TrySyncScanToBackendAndGetResponse(Setup, RequestText, SyncResponseText, FailureMessage, LeaseRejected);
    end;

    local procedure MarkLocalCompletionWithSyncFailure(var DeepScanRun: Record "DH Deep Scan Run"; FailureMessage: Text; LeaseRejected: Boolean)
    begin
        DeepScanRun.Get(DeepScanRun."Entry No.");
        DeepScanRun.Status := DeepScanRun.Status::Completed;
        DeepScanRun."Finished At" := CurrentDateTime();
        DeepScanRun."Current Module" := 'Completed';
        DeepScanRun."Current Step" := CopyStr(LocalCompleteSyncFailedLbl, 1, MaxStrLen(DeepScanRun."Current Step"));
        DeepScanRun."Progress %" := 100;
        DeepScanRun."ETA Text" := 'Completed locally';
        if LeaseRejected then
            DeepScanRun."Backend Sync Status" := DeepScanRun."Backend Sync Status"::Failed
        else
            DeepScanRun."Backend Sync Status" := DeepScanRun."Backend Sync Status"::RetryRequired;
        DeepScanRun."Backend Sync Error" := CopyStr(FailureMessage, 1, MaxStrLen(DeepScanRun."Backend Sync Error"));
        DeepScanRun."Warning Message" := CopyStr(FailureMessage, 1, MaxStrLen(DeepScanRun."Warning Message"));
        DeepScanRun."Error Message" := '';
        DeepScanRun.Modify(true);
        EnsureDashboardHeaderForDeepScan(DeepScanRun);
        Commit();
    end;

    [TryFunction]
    local procedure TryApplySyncPostprocessing(var DeepScanRun: Record "DH Deep Scan Run"; SyncResponseText: Text)
    begin
        ApplySyncCommercials(DeepScanRun, SyncResponseText);
        ApplySyncFindingImpacts(DeepScanRun, SyncResponseText);
        EnsureDashboardHeaderForDeepScan(DeepScanRun);
        Commit();
    end;

    [TryFunction]
    local procedure TryRefreshLicenseAfterCompletion(var Setup: Record "DH Setup")
    var
        ApiClient: Codeunit "DH API Client";
    begin
        ApiClient.RefreshLicenseStatus(Setup);
    end;

    local procedure RunChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        Setup: Record "DH Setup";
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
        ModuleNo: Integer;
        TotalModules: Integer;
    begin
        Score := 100;
        ChecksCount := 0;
        IssuesCount := 0;
        ModuleNo := 0;

        if Setup.Get('SETUP') then
            Setup.ApplyDefaults()
        else begin
            Setup.Init();
            Setup."Scan System Module" := true;
            Setup."Scan Finance Module" := true;
            Setup."Scan Sales Module" := true;
            Setup."Scan Purchasing Module" := true;
            Setup."Scan Inventory Module" := true;
            Setup."Scan CRM Module" := true;
            Setup."Scan Manufacturing Module" := true;
            Setup."Scan Service Module" := true;
            Setup."Scan Jobs Module" := true;
            Setup."Scan HR Module" := true;
        end;

        ScanCheckMgt.RequireEnabledChecksForMonitoring();

        TotalModules := GetEnabledModuleCount(Setup);
        InitializeProgress(DeepScanRun, TotalModules);

        if IsModuleEnabled(Setup, 'System') then begin
            ModuleNo += 1;
            StartModule(DeepScanRun, 'System', ModuleNo);
            RunSystemConfigurationChecks(DeepScanRun, Score, ChecksCount, IssuesCount);
            CompleteModule(DeepScanRun, 'System', ModuleNo);
        end;

        if IsModuleEnabled(Setup, 'Finance') then begin
            ModuleNo += 1;
            StartModule(DeepScanRun, 'Finance', ModuleNo);
            RunCustomerMasterDataChecks(DeepScanRun, Score, ChecksCount, IssuesCount);
            RunVendorMasterDataChecks(DeepScanRun, Score, ChecksCount, IssuesCount);
            RunCustomerDuplicateEmailCheck(DeepScanRun, Score, ChecksCount, IssuesCount);
            RunVendorDuplicateEmailCheck(DeepScanRun, Score, ChecksCount, IssuesCount);
            RunCustomerDuplicateVatCheck(DeepScanRun, Score, ChecksCount, IssuesCount);
            RunVendorDuplicateVatCheck(DeepScanRun, Score, ChecksCount, IssuesCount);
            RunCustomerDuplicateNamePostCodeCityCheck(DeepScanRun, Score, ChecksCount, IssuesCount);
            RunVendorDuplicateNamePostCodeCityCheck(DeepScanRun, Score, ChecksCount, IssuesCount);
            RunLedgerAgingChecks(DeepScanRun, Score, ChecksCount, IssuesCount);
            RunFinanceCommercialChecks(DeepScanRun, Score, ChecksCount, IssuesCount);
            CompleteModule(DeepScanRun, 'Finance', ModuleNo);
        end;

        if IsModuleEnabled(Setup, 'Sales') then begin
            ModuleNo += 1;
            StartModule(DeepScanRun, 'Sales', ModuleNo);
            RunSalesDocumentQualityChecks(DeepScanRun, Score, ChecksCount, IssuesCount);
            RunSalesExecutionChecks(DeepScanRun, Score, ChecksCount, IssuesCount);
            CompleteModule(DeepScanRun, 'Sales', ModuleNo);
        end;

        if IsModuleEnabled(Setup, 'Purchasing') then begin
            ModuleNo += 1;
            StartModule(DeepScanRun, 'Purchasing', ModuleNo);
            RunPurchaseDocumentQualityChecks(DeepScanRun, Score, ChecksCount, IssuesCount);
            RunPurchaseExecutionChecks(DeepScanRun, Score, ChecksCount, IssuesCount);
            CompleteModule(DeepScanRun, 'Purchasing', ModuleNo);
        end;

        if IsModuleEnabled(Setup, 'Inventory') then begin
            ModuleNo += 1;
            StartModule(DeepScanRun, 'Inventory', ModuleNo);
            RunItemMasterDataChecks(DeepScanRun, Score, ChecksCount, IssuesCount);
            RunInventoryValueChecks(DeepScanRun, Score, ChecksCount, IssuesCount);
            CompleteModule(DeepScanRun, 'Inventory', ModuleNo);
        end;

        if IsModuleEnabled(Setup, 'CRM') then begin
            ModuleNo += 1;
            StartModule(DeepScanRun, 'CRM', ModuleNo);
            RunCRMContactChecks(DeepScanRun, Score, ChecksCount, IssuesCount);
            CompleteModule(DeepScanRun, 'CRM', ModuleNo);
        end;

        if IsModuleEnabled(Setup, 'Manufacturing') then begin
            ModuleNo += 1;
            StartModule(DeepScanRun, 'Manufacturing', ModuleNo);
            RunManufacturingChecks(DeepScanRun, Score, ChecksCount, IssuesCount);
            CompleteModule(DeepScanRun, 'Manufacturing', ModuleNo);
        end;

        if IsModuleEnabled(Setup, 'Service') then begin
            ModuleNo += 1;
            StartModule(DeepScanRun, 'Service', ModuleNo);
            RunServiceChecks(DeepScanRun, Score, ChecksCount, IssuesCount);
            CompleteModule(DeepScanRun, 'Service', ModuleNo);
        end;

        if IsModuleEnabled(Setup, 'Jobs') then begin
            ModuleNo += 1;
            StartModule(DeepScanRun, 'Jobs', ModuleNo);
            RunJobsChecks(DeepScanRun, Score, ChecksCount, IssuesCount);
            CompleteModule(DeepScanRun, 'Jobs', ModuleNo);
        end;

        if IsModuleEnabled(Setup, 'HR') then begin
            ModuleNo += 1;
            StartModule(DeepScanRun, 'HR', ModuleNo);
            RunHRChecks(DeepScanRun, Score, ChecksCount, IssuesCount);
            CompleteModule(DeepScanRun, 'HR', ModuleNo);
        end;

        ChecksCount := ScanCheckMgt.GetExpectedChecksCount(Setup);

        if Score < 0 then
            Score := 0;
    end;

    local procedure RunCustomerMasterDataChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        Customer: Record Customer;
        MissingName: Integer;
        MissingSearchName: Integer;
        MissingAddress: Integer;
        MissingCity: Integer;
        MissingPostCode: Integer;
        MissingCountryCode: Integer;
        MissingEmail: Integer;
        MissingPhone: Integer;
        MissingPaymentTerms: Integer;
        MissingPaymentMethod: Integer;
        MissingCustomerPostingGroup: Integer;
        MissingGenBusPostingGroup: Integer;
        MissingVatBusPostingGroup: Integer;
        MissingCreditLimit: Integer;
        BlockedWithOpenSalesDocs: Integer;
        BlockedWithOpenLedgerEntries: Integer;
    begin
        ChecksCount += 16;

        Customer.Reset();
        if Customer.FindSet() then
            repeat
                if (Customer.Name = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_NAME') then
                    MissingName += 1;
                if (Customer."Search Name" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_SEARCH_NAME') then
                    MissingSearchName += 1;
                if (Customer.Address = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_ADDRESS') then
                    MissingAddress += 1;
                if (Customer.City = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_CITY') then
                    MissingCity += 1;
                if (Customer."Post Code" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_POST_CODE') then
                    MissingPostCode += 1;
                if (Customer."Country/Region Code" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_COUNTRY') then
                    MissingCountryCode += 1;
                if (Customer."E-Mail" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_EMAIL') then
                    MissingEmail += 1;
                if (Customer."Phone No." = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_PHONE') then
                    MissingPhone += 1;
                if (Customer."Payment Terms Code" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_PAYMENT_TERMS') then
                    MissingPaymentTerms += 1;
                if (Customer."Payment Method Code" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_PAYMENT_METHOD') then
                    MissingPaymentMethod += 1;
                if (Customer."Customer Posting Group" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_POSTING_GROUP') then
                    MissingCustomerPostingGroup += 1;
                if (Customer."Gen. Bus. Posting Group" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_GEN_BUS_POSTING') then
                    MissingGenBusPostingGroup += 1;
                if (Customer."VAT Bus. Posting Group" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_VAT_BUS_POSTING') then
                    MissingVatBusPostingGroup += 1;
                if (Customer."Credit Limit (LCY)" = 0) and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_CREDIT_LIMIT') then
                    MissingCreditLimit += 1;

                if Customer.Blocked <> Customer.Blocked::" " then begin
                    if HasOpenSalesDocumentsForCustomer(Customer."No.") and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'BLOCKED_CUSTOMERS_WITH_OPEN_SALES_DOCS') then
                        BlockedWithOpenSalesDocs += 1;
                    if HasOpenCustomerLedgerEntries(Customer."No.") and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'BLOCKED_CUSTOMERS_WITH_OPEN_LEDGER') then
                        BlockedWithOpenLedgerEntries += 1;
                end;
            until Customer.Next() = 0;

        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CUSTOMER', 'CUSTOMERS_MISSING_NAME', 'high', MissingName, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CUSTOMER', 'CUSTOMERS_MISSING_SEARCH_NAME', 'low', MissingSearchName, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CUSTOMER', 'CUSTOMERS_MISSING_ADDRESS', 'high', MissingAddress, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CUSTOMER', 'CUSTOMERS_MISSING_CITY', 'medium', MissingCity, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CUSTOMER', 'CUSTOMERS_MISSING_POST_CODE', 'medium', MissingPostCode, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CUSTOMER', 'CUSTOMERS_MISSING_COUNTRY', 'medium', MissingCountryCode, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CUSTOMER', 'CUSTOMERS_MISSING_EMAIL', 'medium', MissingEmail, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CUSTOMER', 'CUSTOMERS_MISSING_PHONE', 'low', MissingPhone, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CUSTOMER', 'CUSTOMERS_MISSING_PAYMENT_TERMS', 'high', MissingPaymentTerms, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CUSTOMER', 'CUSTOMERS_MISSING_PAYMENT_METHOD', 'medium', MissingPaymentMethod, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CUSTOMER', 'CUSTOMERS_MISSING_POSTING_GROUP', 'high', MissingCustomerPostingGroup, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CUSTOMER', 'CUSTOMERS_MISSING_GEN_BUS_POSTING', 'high', MissingGenBusPostingGroup, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CUSTOMER', 'CUSTOMERS_MISSING_VAT_BUS_POSTING', 'high', MissingVatBusPostingGroup, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CUSTOMER', 'CUSTOMERS_MISSING_CREDIT_LIMIT', 'low', MissingCreditLimit, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CUSTOMER', 'BLOCKED_CUSTOMERS_WITH_OPEN_SALES_DOCS', 'high', BlockedWithOpenSalesDocs, 7);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CUSTOMER', 'BLOCKED_CUSTOMERS_WITH_OPEN_LEDGER', 'high', BlockedWithOpenLedgerEntries, 7);
    end;

    local procedure RunVendorMasterDataChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        Vendor: Record Vendor;
        MissingName: Integer;
        MissingSearchName: Integer;
        MissingAddress: Integer;
        MissingCity: Integer;
        MissingPostCode: Integer;
        MissingCountryCode: Integer;
        MissingEmail: Integer;
        MissingPhone: Integer;
        MissingPaymentTerms: Integer;
        MissingPaymentMethod: Integer;
        MissingVendorPostingGroup: Integer;
        MissingGenBusPostingGroup: Integer;
        MissingVatBusPostingGroup: Integer;
        MissingBankAccount: Integer;
        BlockedWithOpenPurchaseDocs: Integer;
        BlockedWithOpenLedgerEntries: Integer;
    begin
        ChecksCount += 16;

        Vendor.Reset();
        if Vendor.FindSet() then
            repeat
                if (Vendor.Name = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_NAME') then
                    MissingName += 1;
                if (Vendor."Search Name" = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_SEARCH_NAME') then
                    MissingSearchName += 1;
                if (Vendor.Address = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_ADDRESS') then
                    MissingAddress += 1;
                if (Vendor.City = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_CITY') then
                    MissingCity += 1;
                if (Vendor."Post Code" = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_POST_CODE') then
                    MissingPostCode += 1;
                if (Vendor."Country/Region Code" = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_COUNTRY') then
                    MissingCountryCode += 1;
                if (Vendor."E-Mail" = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_EMAIL') then
                    MissingEmail += 1;
                if (Vendor."Phone No." = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_PHONE') then
                    MissingPhone += 1;
                if (Vendor."Payment Terms Code" = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_PAYMENT_TERMS') then
                    MissingPaymentTerms += 1;
                if (Vendor."Payment Method Code" = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_PAYMENT_METHOD') then
                    MissingPaymentMethod += 1;
                if (Vendor."Vendor Posting Group" = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_POSTING_GROUP') then
                    MissingVendorPostingGroup += 1;
                if (Vendor."Gen. Bus. Posting Group" = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_GEN_BUS_POSTING') then
                    MissingGenBusPostingGroup += 1;
                if (Vendor."VAT Bus. Posting Group" = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_VAT_BUS_POSTING') then
                    MissingVatBusPostingGroup += 1;
                if (Vendor."Preferred Bank Account Code" = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_BANK_ACCOUNT') then
                    MissingBankAccount += 1;

                if Vendor.Blocked <> Vendor.Blocked::" " then begin
                    if HasOpenPurchaseDocumentsForVendor(Vendor."No.") and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'BLOCKED_VENDORS_WITH_OPEN_PURCHASE_DOCS') then
                        BlockedWithOpenPurchaseDocs += 1;
                    if HasOpenVendorLedgerEntries(Vendor."No.") and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'BLOCKED_VENDORS_WITH_OPEN_LEDGER') then
                        BlockedWithOpenLedgerEntries += 1;
                end;
            until Vendor.Next() = 0;

        AddCountFinding(DeepScanRun, Score, IssuesCount, 'VENDOR', 'VENDORS_MISSING_NAME', 'high', MissingName, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'VENDOR', 'VENDORS_MISSING_SEARCH_NAME', 'low', MissingSearchName, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'VENDOR', 'VENDORS_MISSING_ADDRESS', 'high', MissingAddress, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'VENDOR', 'VENDORS_MISSING_CITY', 'medium', MissingCity, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'VENDOR', 'VENDORS_MISSING_POST_CODE', 'medium', MissingPostCode, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'VENDOR', 'VENDORS_MISSING_COUNTRY', 'medium', MissingCountryCode, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'VENDOR', 'VENDORS_MISSING_EMAIL', 'medium', MissingEmail, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'VENDOR', 'VENDORS_MISSING_PHONE', 'low', MissingPhone, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'VENDOR', 'VENDORS_MISSING_PAYMENT_TERMS', 'high', MissingPaymentTerms, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'VENDOR', 'VENDORS_MISSING_PAYMENT_METHOD', 'medium', MissingPaymentMethod, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'VENDOR', 'VENDORS_MISSING_POSTING_GROUP', 'high', MissingVendorPostingGroup, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'VENDOR', 'VENDORS_MISSING_GEN_BUS_POSTING', 'high', MissingGenBusPostingGroup, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'VENDOR', 'VENDORS_MISSING_VAT_BUS_POSTING', 'high', MissingVatBusPostingGroup, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'VENDOR', 'VENDORS_MISSING_BANK_ACCOUNT', 'medium', MissingBankAccount, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'VENDOR', 'BLOCKED_VENDORS_WITH_OPEN_PURCHASE_DOCS', 'high', BlockedWithOpenPurchaseDocs, 7);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'VENDOR', 'BLOCKED_VENDORS_WITH_OPEN_LEDGER', 'high', BlockedWithOpenLedgerEntries, 7);
    end;

    local procedure RunCustomerDuplicateEmailCheck(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        EmailQuery: Query "DH Customer Duplicate Email";
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
        DuplicateCount: Integer;
        LastFindingCount: Integer;
        Email: Text[100];
    begin
        if not ScanCheckMgt.IsCheckEnabled('CUSTOMERS_DUPLICATE_EMAIL') then
            exit;

        ChecksCount += 1;

        EmailQuery.SetFilter(EmailFilter, '<>%1', '');
        EmailQuery.Open();

        while EmailQuery.Read() do begin
            Email := CopyStr(EmailQuery.Email, 1, MaxStrLen(Email));
            DuplicateCount := CountCustomersByEmail(Email, 'CUSTOMERS_DUPLICATE_EMAIL');
            if DuplicateCount > LastFindingCount then
                LastFindingCount := DuplicateCount;

            if DuplicateCount > 1 then begin
                InsertFinding(
                    DeepScanRun."Entry No.",
                    'CUSTOMER',
                    'CUSTOMERS_DUPLICATE_EMAIL',
                    'high',
                    DuplicateCount);

                IssuesCount += 1;
                ApplyPenalty(Score, 8);
            end;
        end;

        EmailQuery.Close();
        ScanCheckMgt.UpdateLastRun('CUSTOMERS_DUPLICATE_EMAIL', LastFindingCount);
    end;

    local procedure RunVendorDuplicateEmailCheck(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        EmailQuery: Query "DH Vendor Duplicate Email";
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
        DuplicateCount: Integer;
        LastFindingCount: Integer;
        Email: Text[100];
    begin
        if not ScanCheckMgt.IsCheckEnabled('VENDORS_DUPLICATE_EMAIL') then
            exit;

        ChecksCount += 1;

        EmailQuery.SetFilter(EmailFilter, '<>%1', '');
        EmailQuery.Open();

        while EmailQuery.Read() do begin
            Email := CopyStr(EmailQuery.Email, 1, MaxStrLen(Email));
            DuplicateCount := CountVendorsByEmail(Email, 'VENDORS_DUPLICATE_EMAIL');
            if DuplicateCount > LastFindingCount then
                LastFindingCount := DuplicateCount;

            if DuplicateCount > 1 then begin
                InsertFinding(
                    DeepScanRun."Entry No.",
                    'VENDOR',
                    'VENDORS_DUPLICATE_EMAIL',
                    'high',
                    DuplicateCount);

                IssuesCount += 1;
                ApplyPenalty(Score, 8);
            end;
        end;

        EmailQuery.Close();
        ScanCheckMgt.UpdateLastRun('VENDORS_DUPLICATE_EMAIL', LastFindingCount);
    end;

    local procedure RunCustomerDuplicateVatCheck(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        Customer: Record Customer;
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
        DuplicateCount: Integer;
        LastFindingCount: Integer;
    begin
        if not ScanCheckMgt.IsCheckEnabled('CUSTOMERS_DUPLICATE_VAT') then
            exit;

        ChecksCount += 1;

        Customer.Reset();
        Customer.SetFilter("VAT Registration No.", '<>%1', '');

        if Customer.FindSet() then
            repeat
                if not IsCustomerDuplicateExcluded(Customer, 'CUSTOMERS_DUPLICATE_VAT') then
                    if not FindingExists(DeepScanRun."Entry No.", 'CUSTOMERS_DUPLICATE_VAT', Customer."VAT Registration No.") then begin
                        DuplicateCount := CountCustomersByVat(Customer."VAT Registration No.", 'CUSTOMERS_DUPLICATE_VAT');
                        if DuplicateCount > LastFindingCount then
                            LastFindingCount := DuplicateCount;

                        if DuplicateCount > 1 then begin
                            InsertFinding(
                                DeepScanRun."Entry No.",
                                'CUSTOMER',
                                'CUSTOMERS_DUPLICATE_VAT',
                                'high',
                                DuplicateCount);

                            IssuesCount += 1;
                            ApplyPenalty(Score, 8);
                        end;
                    end;
            until Customer.Next() = 0;

        ScanCheckMgt.UpdateLastRun('CUSTOMERS_DUPLICATE_VAT', LastFindingCount);
    end;

    local procedure RunVendorDuplicateVatCheck(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        Vendor: Record Vendor;
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
        DuplicateCount: Integer;
        LastFindingCount: Integer;
    begin
        if not ScanCheckMgt.IsCheckEnabled('VENDORS_DUPLICATE_VAT') then
            exit;

        ChecksCount += 1;

        Vendor.Reset();
        Vendor.SetFilter("VAT Registration No.", '<>%1', '');

        if Vendor.FindSet() then
            repeat
                if not IsVendorDuplicateExcluded(Vendor, 'VENDORS_DUPLICATE_VAT') then
                    if not FindingExists(DeepScanRun."Entry No.", 'VENDORS_DUPLICATE_VAT', Vendor."VAT Registration No.") then begin
                        DuplicateCount := CountVendorsByVat(Vendor."VAT Registration No.", 'VENDORS_DUPLICATE_VAT');
                        if DuplicateCount > LastFindingCount then
                            LastFindingCount := DuplicateCount;

                        if DuplicateCount > 1 then begin
                            InsertFinding(
                                DeepScanRun."Entry No.",
                                'VENDOR',
                                'VENDORS_DUPLICATE_VAT',
                                'high',
                                DuplicateCount);

                            IssuesCount += 1;
                            ApplyPenalty(Score, 8);
                        end;
                    end;
            until Vendor.Next() = 0;

        ScanCheckMgt.UpdateLastRun('VENDORS_DUPLICATE_VAT', LastFindingCount);
    end;

    local procedure RunCustomerDuplicateNamePostCodeCityCheck(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        Customer: Record Customer;
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
        DuplicateCount: Integer;
        LastFindingCount: Integer;
        Marker: Text[250];
    begin
        if not ScanCheckMgt.IsCheckEnabled('CUSTOMERS_DUPLICATE_NAME_POST_CITY') then
            exit;

        ChecksCount += 1;

        Customer.Reset();
        Customer.SetFilter(Name, '<>%1', '');
        Customer.SetFilter("Post Code", '<>%1', '');
        Customer.SetFilter(City, '<>%1', '');

        if Customer.FindSet() then
            repeat
                if not IsCustomerDuplicateExcluded(Customer, 'CUSTOMERS_DUPLICATE_NAME_POST_CITY') then begin
                    Marker := CopyStr(Customer.Name + '|' + Customer."Post Code" + '|' + Customer.City, 1, MaxStrLen(Marker));
                    if not FindingExists(DeepScanRun."Entry No.", 'CUSTOMERS_DUPLICATE_NAME_POST_CITY', Marker) then begin
                        DuplicateCount := CountCustomersByNamePostCity(Customer.Name, Customer."Post Code", Customer.City, 'CUSTOMERS_DUPLICATE_NAME_POST_CITY');
                        if DuplicateCount > LastFindingCount then
                            LastFindingCount := DuplicateCount;

                        if DuplicateCount > 1 then begin
                            InsertFinding(
                                DeepScanRun."Entry No.",
                                'CUSTOMER',
                                'CUSTOMERS_DUPLICATE_NAME_POST_CITY',
                                'high',
                                DuplicateCount);

                            IssuesCount += 1;
                            ApplyPenalty(Score, 8);
                        end;
                    end;
                end;
            until Customer.Next() = 0;

        ScanCheckMgt.UpdateLastRun('CUSTOMERS_DUPLICATE_NAME_POST_CITY', LastFindingCount);
    end;

    local procedure RunVendorDuplicateNamePostCodeCityCheck(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        Vendor: Record Vendor;
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
        DuplicateCount: Integer;
        LastFindingCount: Integer;
        Marker: Text[250];
    begin
        if not ScanCheckMgt.IsCheckEnabled('VENDORS_DUPLICATE_NAME_POST_CITY') then
            exit;

        ChecksCount += 1;

        Vendor.Reset();
        Vendor.SetFilter(Name, '<>%1', '');
        Vendor.SetFilter("Post Code", '<>%1', '');
        Vendor.SetFilter(City, '<>%1', '');

        if Vendor.FindSet() then
            repeat
                if not IsVendorDuplicateExcluded(Vendor, 'VENDORS_DUPLICATE_NAME_POST_CITY') then begin
                    Marker := CopyStr(Vendor.Name + '|' + Vendor."Post Code" + '|' + Vendor.City, 1, MaxStrLen(Marker));
                    if not FindingExists(DeepScanRun."Entry No.", 'VENDORS_DUPLICATE_NAME_POST_CITY', Marker) then begin
                        DuplicateCount := CountVendorsByNamePostCity(Vendor.Name, Vendor."Post Code", Vendor.City, 'VENDORS_DUPLICATE_NAME_POST_CITY');
                        if DuplicateCount > LastFindingCount then
                            LastFindingCount := DuplicateCount;

                        if DuplicateCount > 1 then begin
                            InsertFinding(
                                DeepScanRun."Entry No.",
                                'VENDOR',
                                'VENDORS_DUPLICATE_NAME_POST_CITY',
                                'high',
                                DuplicateCount);

                            IssuesCount += 1;
                            ApplyPenalty(Score, 8);
                        end;
                    end;
                end;
            until Vendor.Next() = 0;

        ScanCheckMgt.UpdateLastRun('VENDORS_DUPLICATE_NAME_POST_CITY', LastFindingCount);
    end;

    local procedure RunItemMasterDataChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        Item: Record Item;
        MissingDescription: Integer;
        MissingBaseUom: Integer;
        MissingItemCategory: Integer;
        MissingGenProdPostingGroup: Integer;
        MissingInventoryPostingGroup: Integer;
        MissingVendorNo: Integer;
        MissingUnitCost: Integer;
        MissingUnitPrice: Integer;
        NegativeInventory: Integer;
        BlockedWithInventory: Integer;
    begin
        ChecksCount += 10;

        Item.Reset();
        if Item.FindSet() then
            repeat
                Item.CalcFields(Inventory);

                if (Item.Description = '') and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_MISSING_DESCRIPTION') then
                    MissingDescription += 1;
                if (Item."Base Unit of Measure" = '') and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_MISSING_BASE_UOM') then
                    MissingBaseUom += 1;
                if (Item."Item Category Code" = '') and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_MISSING_CATEGORY') then
                    MissingItemCategory += 1;
                if (Item."Gen. Prod. Posting Group" = '') and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_MISSING_GEN_PROD_POSTING') then
                    MissingGenProdPostingGroup += 1;
                if (Item."Inventory Posting Group" = '') and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_MISSING_INVENTORY_POSTING') then
                    MissingInventoryPostingGroup += 1;
                if (Item."Vendor No." = '') and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_WITHOUT_VENDOR_NO') then
                    MissingVendorNo += 1;
                if (Item."Unit Cost" = 0) and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_WITHOUT_UNIT_COST') then
                    MissingUnitCost += 1;
                if (Item."Unit Price" = 0) and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_WITHOUT_UNIT_PRICE') then
                    MissingUnitPrice += 1;
                if (Item.Inventory < 0) and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_NEGATIVE_INVENTORY') then
                    NegativeInventory += 1;
                if Item.Blocked and (Item.Inventory <> 0) and not ExceptionMgt.IsItemIssueExcluded(Item, 'BLOCKED_ITEMS_WITH_INVENTORY') then
                    BlockedWithInventory += 1;
            until Item.Next() = 0;

        AddCountFinding(DeepScanRun, Score, IssuesCount, 'ITEM', 'ITEMS_MISSING_DESCRIPTION', 'high', MissingDescription, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'ITEM', 'ITEMS_MISSING_BASE_UOM', 'high', MissingBaseUom, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'ITEM', 'ITEMS_MISSING_CATEGORY', 'medium', MissingItemCategory, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'ITEM', 'ITEMS_MISSING_GEN_PROD_POSTING', 'high', MissingGenProdPostingGroup, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'ITEM', 'ITEMS_MISSING_INVENTORY_POSTING', 'high', MissingInventoryPostingGroup, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'ITEM', 'ITEMS_WITHOUT_VENDOR_NO', 'medium', MissingVendorNo, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'ITEM', 'ITEMS_WITHOUT_UNIT_COST', 'high', MissingUnitCost, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'ITEM', 'ITEMS_WITHOUT_UNIT_PRICE', 'medium', MissingUnitPrice, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'ITEM', 'ITEMS_NEGATIVE_INVENTORY', 'high', NegativeInventory, 8);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'ITEM', 'BLOCKED_ITEMS_WITH_INVENTORY', 'medium', BlockedWithInventory, 4);
    end;

    local procedure RunSalesDocumentQualityChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        SalesHeader: Record "Sales Header";
        SalesLine: Record "Sales Line";
        Customer: Record Customer;
        Item: Record Item;
        MissingShipmentDate: Integer;
        OldOrders: Integer;
        MissingNoOnLine: Integer;
        ZeroQuantity: Integer;
        ZeroPrice: Integer;
        MissingDimensions: Integer;
        BlockedCustomersOnDocs: Integer;
        BlockedItemsOnDocs: Integer;
        ThresholdDate: Date;
    begin
        ChecksCount += 8;

        ThresholdDate := CalcDate('<-30D>', Today());

        SalesHeader.Reset();
        SalesHeader.SetRange("Document Type", SalesHeader."Document Type"::Order);
        if SalesHeader.FindSet() then
            repeat
                if SalesHeader."Shipment Date" = 0D then
                    MissingShipmentDate += 1;
                if SalesHeader."Document Date" <> 0D then
                    if SalesHeader."Document Date" <= ThresholdDate then
                        OldOrders += 1;

                if Customer.Get(SalesHeader."Sell-to Customer No.") then
                    if Customer.Blocked <> Customer.Blocked::" " then
                        BlockedCustomersOnDocs += 1;
            until SalesHeader.Next() = 0;

        SalesLine.Reset();
        SalesLine.SetRange("Document Type", SalesLine."Document Type"::Order);
        if SalesLine.FindSet() then
            repeat
                if ((SalesLine.Type = SalesLine.Type::Item) or (SalesLine.Type = SalesLine.Type::"G/L Account")) and (SalesLine."No." = '') then
                    MissingNoOnLine += 1;

                if (SalesLine.Type = SalesLine.Type::Item) or (SalesLine.Type = SalesLine.Type::"G/L Account") then
                    if SalesLine.Quantity = 0 then
                        ZeroQuantity += 1;

                if SalesLine.Type = SalesLine.Type::Item then
                    if SalesLine."Unit Price" = 0 then
                        ZeroPrice += 1;

                if ((SalesLine.Type = SalesLine.Type::Item) or (SalesLine.Type = SalesLine.Type::"G/L Account")) and
                   (SalesLine."Shortcut Dimension 1 Code" = '') and
                   (SalesLine."Shortcut Dimension 2 Code" = '')
                then
                    MissingDimensions += 1;

                if (SalesLine.Type = SalesLine.Type::Item) and (SalesLine."No." <> '') then
                    if Item.Get(SalesLine."No.") then
                        if Item.Blocked then
                            BlockedItemsOnDocs += 1;
            until SalesLine.Next() = 0;

        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_ORDERS_MISSING_SHIPMENT_DATE', 'medium', MissingShipmentDate, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_ORDERS_OLD_OPEN', 'medium', OldOrders, 4);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_LINES_MISSING_NO', 'high', MissingNoOnLine, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_LINES_ZERO_QUANTITY', 'medium', ZeroQuantity, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_LINES_ZERO_PRICE', 'high', ZeroPrice, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_LINES_MISSING_DIMENSIONS', 'high', MissingDimensions, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_DOCS_WITH_BLOCKED_CUSTOMERS', 'high', BlockedCustomersOnDocs, 7);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_LINES_WITH_BLOCKED_ITEMS', 'high', BlockedItemsOnDocs, 7);
    end;

    local procedure RunPurchaseDocumentQualityChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        PurchaseHeader: Record "Purchase Header";
        PurchaseLine: Record "Purchase Line";
        Vendor: Record Vendor;
        Item: Record Item;
        MissingExpectedReceiptDate: Integer;
        OldOrders: Integer;
        MissingNoOnLine: Integer;
        ZeroQuantity: Integer;
        ZeroCost: Integer;
        MissingDimensions: Integer;
        BlockedVendorsOnDocs: Integer;
        BlockedItemsOnDocs: Integer;
        ThresholdDate: Date;
    begin
        ChecksCount += 8;

        ThresholdDate := CalcDate('<-30D>', Today());

        PurchaseHeader.Reset();
        PurchaseHeader.SetRange("Document Type", PurchaseHeader."Document Type"::Order);
        if PurchaseHeader.FindSet() then
            repeat
                if PurchaseHeader."Expected Receipt Date" = 0D then
                    MissingExpectedReceiptDate += 1;
                if PurchaseHeader."Document Date" <> 0D then
                    if PurchaseHeader."Document Date" <= ThresholdDate then
                        OldOrders += 1;

                if Vendor.Get(PurchaseHeader."Buy-from Vendor No.") then
                    if Vendor.Blocked <> Vendor.Blocked::" " then
                        BlockedVendorsOnDocs += 1;
            until PurchaseHeader.Next() = 0;

        PurchaseLine.Reset();
        PurchaseLine.SetRange("Document Type", PurchaseLine."Document Type"::Order);
        if PurchaseLine.FindSet() then
            repeat
                if ((PurchaseLine.Type = PurchaseLine.Type::Item) or (PurchaseLine.Type = PurchaseLine.Type::"G/L Account")) and (PurchaseLine."No." = '') then
                    MissingNoOnLine += 1;

                if (PurchaseLine.Type = PurchaseLine.Type::Item) or (PurchaseLine.Type = PurchaseLine.Type::"G/L Account") then
                    if PurchaseLine.Quantity = 0 then
                        ZeroQuantity += 1;

                if PurchaseLine.Type = PurchaseLine.Type::Item then
                    if PurchaseLine."Direct Unit Cost" = 0 then
                        ZeroCost += 1;

                if ((PurchaseLine.Type = PurchaseLine.Type::Item) or (PurchaseLine.Type = PurchaseLine.Type::"G/L Account")) and
                   (PurchaseLine."Shortcut Dimension 1 Code" = '') and
                   (PurchaseLine."Shortcut Dimension 2 Code" = '')
                then
                    MissingDimensions += 1;

                if (PurchaseLine.Type = PurchaseLine.Type::Item) and (PurchaseLine."No." <> '') then
                    if Item.Get(PurchaseLine."No.") then
                        if Item.Blocked then
                            BlockedItemsOnDocs += 1;
            until PurchaseLine.Next() = 0;

        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_ORDERS_MISSING_EXPECTED_DATE', 'medium', MissingExpectedReceiptDate, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_ORDERS_OLD_OPEN', 'medium', OldOrders, 4);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_LINES_MISSING_NO', 'high', MissingNoOnLine, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_LINES_ZERO_QUANTITY', 'medium', ZeroQuantity, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_LINES_ZERO_COST', 'high', ZeroCost, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_LINES_MISSING_DIMENSIONS', 'high', MissingDimensions, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_DOCS_WITH_BLOCKED_VENDORS', 'high', BlockedVendorsOnDocs, 7);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_LINES_WITH_BLOCKED_ITEMS', 'high', BlockedItemsOnDocs, 7);
    end;

    local procedure RunLedgerAgingChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        CustLedgerEntry: Record "Cust. Ledger Entry";
        VendorLedgerEntry: Record "Vendor Ledger Entry";
        OverdueCustomerEntries: Integer;
        OverdueVendorEntries: Integer;
        ThresholdDate: Date;
    begin
        ChecksCount += 2;

        ThresholdDate := CalcDate('<-30D>', Today());

        CustLedgerEntry.Reset();
        CustLedgerEntry.SetRange(Open, true);
        CustLedgerEntry.SetFilter("Due Date", '<>%1&<=%2', 0D, ThresholdDate);
        OverdueCustomerEntries := CustLedgerEntry.Count();

        VendorLedgerEntry.Reset();
        VendorLedgerEntry.SetRange(Open, true);
        VendorLedgerEntry.SetFilter("Due Date", '<>%1&<=%2', 0D, ThresholdDate);
        OverdueVendorEntries := VendorLedgerEntry.Count();

        AddCountFinding(DeepScanRun, Score, IssuesCount, 'LEDGER', 'CUSTOMER_LEDGER_OVERDUE_30', 'high', OverdueCustomerEntries, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'LEDGER', 'VENDOR_LEDGER_OVERDUE_30', 'medium', OverdueVendorEntries, 4);
    end;

    local procedure RunSystemConfigurationChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        GLEntry: Record "G/L Entry";
        GLAccount: Record "G/L Account";
        Customer: Record Customer;
        Vendor: Record Vendor;
        Item: Record Item;
        MissingDim1: Integer;
        MissingDim2: Integer;
        MissingBothDims: Integer;
        AccountsBlockedButUsed: Integer;
        AccountsWithoutDirectPostingButUsed: Integer;
        CustomersWithoutGenBusPosting: Integer;
        CustomersWithoutVatBusPosting: Integer;
        VendorsWithoutGenBusPosting: Integer;
        VendorsWithoutVatBusPosting: Integer;
        ItemsWithoutGenProdPosting: Integer;
        ItemsWithoutInventoryPosting: Integer;
        CustLedgerWithoutDueDate: Integer;
        VendLedgerWithoutDueDate: Integer;
        CustLedgerEntry: Record "Cust. Ledger Entry";
        VendorLedgerEntry: Record "Vendor Ledger Entry";
    begin
        ChecksCount += 14;

        GLEntry.Reset();
        if GLEntry.FindSet() then
            repeat
                if GLEntry."Global Dimension 1 Code" = '' then
                    MissingDim1 += 1;
                if GLEntry."Global Dimension 2 Code" = '' then
                    MissingDim2 += 1;
                if (GLEntry."Global Dimension 1 Code" = '') and (GLEntry."Global Dimension 2 Code" = '') then
                    MissingBothDims += 1;
            until GLEntry.Next() = 0;

        GLAccount.Reset();
        if GLAccount.FindSet() then
            repeat
                if GLAccount.Blocked and HasGLEntriesForAccount(GLAccount."No.") then
                    AccountsBlockedButUsed += 1;
                if (not GLAccount."Direct Posting") and HasGLEntriesForAccount(GLAccount."No.") then
                    AccountsWithoutDirectPostingButUsed += 1;
            until GLAccount.Next() = 0;

        Customer.Reset();
        if Customer.FindSet() then
            repeat
                if (Customer."Gen. Bus. Posting Group" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'SYSTEM_CUSTOMERS_MISSING_GEN_BUS_POSTING') then
                    CustomersWithoutGenBusPosting += 1;
                if (Customer."VAT Bus. Posting Group" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'SYSTEM_CUSTOMERS_MISSING_VAT_BUS_POSTING') then
                    CustomersWithoutVatBusPosting += 1;
            until Customer.Next() = 0;

        Vendor.Reset();
        if Vendor.FindSet() then
            repeat
                if (Vendor."Gen. Bus. Posting Group" = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'SYSTEM_VENDORS_MISSING_GEN_BUS_POSTING') then
                    VendorsWithoutGenBusPosting += 1;
                if (Vendor."VAT Bus. Posting Group" = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'SYSTEM_VENDORS_MISSING_VAT_BUS_POSTING') then
                    VendorsWithoutVatBusPosting += 1;
            until Vendor.Next() = 0;

        Item.Reset();
        if Item.FindSet() then
            repeat
                if (Item."Gen. Prod. Posting Group" = '') and not ExceptionMgt.IsItemIssueExcluded(Item, 'SYSTEM_ITEMS_MISSING_GEN_PROD_POSTING') then
                    ItemsWithoutGenProdPosting += 1;
                if (Item."Inventory Posting Group" = '') and not ExceptionMgt.IsItemIssueExcluded(Item, 'SYSTEM_ITEMS_MISSING_INVENTORY_POSTING') then
                    ItemsWithoutInventoryPosting += 1;
            until Item.Next() = 0;

        CustLedgerEntry.SetRange(Open, true);
        CustLedgerEntry.SetRange("Due Date", 0D);
        CustLedgerWithoutDueDate := CustLedgerEntry.Count();

        VendorLedgerEntry.SetRange(Open, true);
        VendorLedgerEntry.SetRange("Due Date", 0D);
        VendLedgerWithoutDueDate := VendorLedgerEntry.Count();

        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SYSTEM', 'GL_ENTRIES_MISSING_DIM1', 'medium', MissingDim1, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SYSTEM', 'GL_ENTRIES_MISSING_DIM2', 'medium', MissingDim2, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SYSTEM', 'GL_ENTRIES_MISSING_BOTH_DIMS', 'high', MissingBothDims, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SYSTEM', 'GL_ACCOUNTS_BLOCKED_BUT_USED', 'high', AccountsBlockedButUsed, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SYSTEM', 'GL_ACCOUNTS_NO_DIRECT_POSTING_BUT_USED', 'medium', AccountsWithoutDirectPostingButUsed, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SYSTEM', 'SYSTEM_CUSTOMERS_MISSING_GEN_BUS_POSTING', 'high', CustomersWithoutGenBusPosting, 4);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SYSTEM', 'SYSTEM_CUSTOMERS_MISSING_VAT_BUS_POSTING', 'high', CustomersWithoutVatBusPosting, 4);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SYSTEM', 'SYSTEM_VENDORS_MISSING_GEN_BUS_POSTING', 'high', VendorsWithoutGenBusPosting, 4);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SYSTEM', 'SYSTEM_VENDORS_MISSING_VAT_BUS_POSTING', 'high', VendorsWithoutVatBusPosting, 4);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SYSTEM', 'SYSTEM_ITEMS_MISSING_GEN_PROD_POSTING', 'high', ItemsWithoutGenProdPosting, 4);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SYSTEM', 'SYSTEM_ITEMS_MISSING_INVENTORY_POSTING', 'high', ItemsWithoutInventoryPosting, 4);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SYSTEM', 'CUSTOMER_LEDGER_MISSING_DUE_DATE', 'medium', CustLedgerWithoutDueDate, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SYSTEM', 'VENDOR_LEDGER_MISSING_DUE_DATE', 'medium', VendLedgerWithoutDueDate, 3);
    end;

    local procedure RunFinanceCommercialChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        Customer: Record Customer;
        Vendor: Record Vendor;
        CustLedgerEntry: Record "Cust. Ledger Entry";
        VendorLedgerEntry: Record "Vendor Ledger Entry";
        CustomerMissingVat: Integer;
        CustomerMissingSalesperson: Integer;
        CustomerMissingPriceGroup: Integer;
        CustomerMissingDiscGroup: Integer;
        CustomerMissingReminderTerms: Integer;
        CustomerMissingFinChargeTerms: Integer;
        CustomerMissingContact: Integer;
        CustomerMissingHomePage: Integer;
        VendorMissingVat: Integer;
        VendorMissingPurchaser: Integer;
        VendorMissingContact: Integer;
        VendorMissingHomePage: Integer;
        CustomerOverdue60: Integer;
        CustomerOverdue90: Integer;
        VendorOverdue60: Integer;
        VendorOverdue90: Integer;
    begin
        ChecksCount += 16;

        if Customer.FindSet() then
            repeat
                if (Customer."VAT Registration No." = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_VAT_REG_NO') then
                    CustomerMissingVat += 1;
                if (Customer."Salesperson Code" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_SALESPERSON') then
                    CustomerMissingSalesperson += 1;
                if (Customer."Customer Price Group" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_PRICE_GROUP') then
                    CustomerMissingPriceGroup += 1;
                if (Customer."Customer Disc. Group" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_DISC_GROUP') then
                    CustomerMissingDiscGroup += 1;
                if (Customer."Reminder Terms Code" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_REMINDER_TERMS') then
                    CustomerMissingReminderTerms += 1;
                if (Customer."Fin. Charge Terms Code" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_FIN_CHARGE_TERMS') then
                    CustomerMissingFinChargeTerms += 1;
                if (Customer.Contact = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_CONTACT') then
                    CustomerMissingContact += 1;
                if (Customer."Home Page" = '') and not ExceptionMgt.IsCustomerIssueExcluded(Customer, 'CUSTOMERS_MISSING_HOME_PAGE') then
                    CustomerMissingHomePage += 1;
            until Customer.Next() = 0;

        if Vendor.FindSet() then
            repeat
                if (Vendor."VAT Registration No." = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_VAT_REG_NO') then
                    VendorMissingVat += 1;
                if (Vendor."Purchaser Code" = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_PURCHASER') then
                    VendorMissingPurchaser += 1;
                if (Vendor.Contact = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_CONTACT') then
                    VendorMissingContact += 1;
                if (Vendor."Home Page" = '') and not ExceptionMgt.IsVendorIssueExcluded(Vendor, 'VENDORS_MISSING_HOME_PAGE') then
                    VendorMissingHomePage += 1;
            until Vendor.Next() = 0;

        CustLedgerEntry.SetRange(Open, true);
        CustLedgerEntry.SetFilter("Due Date", '<>%1&<=%2', 0D, CalcDate('<-60D>', Today()));
        CustomerOverdue60 := CustLedgerEntry.Count();
        CustLedgerEntry.SetRange("Due Date");
        CustLedgerEntry.SetFilter("Due Date", '<>%1&<=%2', 0D, CalcDate('<-90D>', Today()));
        CustomerOverdue90 := CustLedgerEntry.Count();

        VendorLedgerEntry.SetRange(Open, true);
        VendorLedgerEntry.SetFilter("Due Date", '<>%1&<=%2', 0D, CalcDate('<-60D>', Today()));
        VendorOverdue60 := VendorLedgerEntry.Count();
        VendorLedgerEntry.SetRange("Due Date");
        VendorLedgerEntry.SetFilter("Due Date", '<>%1&<=%2', 0D, CalcDate('<-90D>', Today()));
        VendorOverdue90 := VendorLedgerEntry.Count();

        AddCountFinding(DeepScanRun, Score, IssuesCount, 'FINANCE', 'CUSTOMERS_MISSING_VAT_REG_NO', 'medium', CustomerMissingVat, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'FINANCE', 'CUSTOMERS_MISSING_SALESPERSON', 'low', CustomerMissingSalesperson, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'FINANCE', 'CUSTOMERS_MISSING_PRICE_GROUP', 'medium', CustomerMissingPriceGroup, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'FINANCE', 'CUSTOMERS_MISSING_DISC_GROUP', 'medium', CustomerMissingDiscGroup, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'FINANCE', 'CUSTOMERS_MISSING_REMINDER_TERMS', 'medium', CustomerMissingReminderTerms, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'FINANCE', 'CUSTOMERS_MISSING_FIN_CHARGE_TERMS', 'low', CustomerMissingFinChargeTerms, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'FINANCE', 'CUSTOMERS_MISSING_CONTACT', 'low', CustomerMissingContact, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'FINANCE', 'CUSTOMERS_MISSING_HOME_PAGE', 'low', CustomerMissingHomePage, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'FINANCE', 'VENDORS_MISSING_VAT_REG_NO', 'medium', VendorMissingVat, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'FINANCE', 'VENDORS_MISSING_PURCHASER', 'low', VendorMissingPurchaser, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'FINANCE', 'VENDORS_MISSING_CONTACT', 'low', VendorMissingContact, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'FINANCE', 'VENDORS_MISSING_HOME_PAGE', 'low', VendorMissingHomePage, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'FINANCE', 'CUSTOMER_LEDGER_OVERDUE_60', 'high', CustomerOverdue60, 4);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'FINANCE', 'CUSTOMER_LEDGER_OVERDUE_90', 'high', CustomerOverdue90, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'FINANCE', 'VENDOR_LEDGER_OVERDUE_60', 'medium', VendorOverdue60, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'FINANCE', 'VENDOR_LEDGER_OVERDUE_90', 'medium', VendorOverdue90, 4);
    end;

    local procedure RunSalesExecutionChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        SalesHeader: Record "Sales Header";
        SalesLine: Record "Sales Line";
        Item: Record Item;
        MissingPaymentTerms: Integer;
        MissingPaymentMethod: Integer;
        MissingRequestedDeliveryDate: Integer;
        MissingShipmentMethod: Integer;
        MissingExternalDocumentNo: Integer;
        PastDueRequestedDeliveryDate: Integer;
        DiscountAbove25: Integer;
        DiscountAbove50: Integer;
        BelowUnitCost: Integer;
        ShippedNotInvoiced: Integer;
        OutstandingPastShipmentDate: Integer;
        MissingDescription: Integer;
        MissingLocationCode: Integer;
    begin
        ChecksCount += 13;

        SalesHeader.SetRange("Document Type", SalesHeader."Document Type"::Order);
        if SalesHeader.FindSet() then
            repeat
                if SalesHeader."Payment Terms Code" = '' then
                    MissingPaymentTerms += 1;
                if SalesHeader."Payment Method Code" = '' then
                    MissingPaymentMethod += 1;
                if SalesHeader."Requested Delivery Date" = 0D then
                    MissingRequestedDeliveryDate += 1;
                if SalesHeader."Shipment Method Code" = '' then
                    MissingShipmentMethod += 1;
                if SalesHeader."External Document No." = '' then
                    MissingExternalDocumentNo += 1;
                if (SalesHeader."Requested Delivery Date" <> 0D) and (SalesHeader."Requested Delivery Date" < Today()) then
                    PastDueRequestedDeliveryDate += 1;
            until SalesHeader.Next() = 0;

        SalesLine.SetRange("Document Type", SalesLine."Document Type"::Order);
        if SalesLine.FindSet() then
            repeat
                if SalesLine."Line Discount %" > 25 then
                    DiscountAbove25 += 1;
                if SalesLine."Line Discount %" > 50 then
                    DiscountAbove50 += 1;
                if (SalesLine.Type = SalesLine.Type::Item) and (SalesLine."No." <> '') then begin
                    if Item.Get(SalesLine."No.") then
                        if SalesLine."Unit Price" < Item."Unit Cost" then
                            BelowUnitCost += 1;
                end;
                if SalesLine."Quantity Shipped" > SalesLine."Quantity Invoiced" then
                    ShippedNotInvoiced += 1;
                if (SalesLine."Outstanding Quantity" > 0) and (SalesLine."Shipment Date" <> 0D) and (SalesLine."Shipment Date" < Today()) then
                    OutstandingPastShipmentDate += 1;
                if SalesLine.Description = '' then
                    MissingDescription += 1;
                if SalesLine."Location Code" = '' then
                    MissingLocationCode += 1;
            until SalesLine.Next() = 0;

        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_HEADERS_MISSING_PAYMENT_TERMS', 'medium', MissingPaymentTerms, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_HEADERS_MISSING_PAYMENT_METHOD', 'medium', MissingPaymentMethod, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_HEADERS_MISSING_REQUESTED_DELIVERY_DATE', 'medium', MissingRequestedDeliveryDate, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_HEADERS_MISSING_SHIPMENT_METHOD', 'low', MissingShipmentMethod, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_HEADERS_MISSING_EXTERNAL_DOC_NO', 'low', MissingExternalDocumentNo, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_HEADERS_PAST_REQUESTED_DELIVERY_DATE', 'high', PastDueRequestedDeliveryDate, 4);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_LINES_DISCOUNT_OVER_25', 'medium', DiscountAbove25, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_LINES_DISCOUNT_OVER_50', 'high', DiscountAbove50, 4);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_LINES_PRICE_BELOW_UNIT_COST', 'high', BelowUnitCost, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_LINES_SHIPPED_NOT_INVOICED', 'high', ShippedNotInvoiced, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_LINES_OUTSTANDING_PAST_SHIPMENT_DATE', 'medium', OutstandingPastShipmentDate, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_LINES_MISSING_DESCRIPTION', 'low', MissingDescription, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SALES', 'SALES_LINES_MISSING_LOCATION', 'medium', MissingLocationCode, 2);
    end;

    local procedure RunPurchaseExecutionChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        PurchaseHeader: Record "Purchase Header";
        PurchaseLine: Record "Purchase Line";
        Item: Record Item;
        MissingPaymentTerms: Integer;
        MissingPaymentMethod: Integer;
        MissingPurchaserCode: Integer;
        MissingVendorInvoiceNo: Integer;
        PastExpectedReceiptDate: Integer;
        DiscountAbove25: Integer;
        DiscountAbove50: Integer;
        ReceivedNotInvoiced: Integer;
        OutstandingPastReceiptDate: Integer;
        MissingDescription: Integer;
        MissingLocationCode: Integer;
        CostBelowItemCost: Integer;
    begin
        ChecksCount += 12;

        PurchaseHeader.SetRange("Document Type", PurchaseHeader."Document Type"::Order);
        if PurchaseHeader.FindSet() then
            repeat
                if PurchaseHeader."Payment Terms Code" = '' then
                    MissingPaymentTerms += 1;
                if PurchaseHeader."Payment Method Code" = '' then
                    MissingPaymentMethod += 1;
                if PurchaseHeader."Purchaser Code" = '' then
                    MissingPurchaserCode += 1;
                if PurchaseHeader."Vendor Invoice No." = '' then
                    MissingVendorInvoiceNo += 1;
                if (PurchaseHeader."Expected Receipt Date" <> 0D) and (PurchaseHeader."Expected Receipt Date" < Today()) then
                    PastExpectedReceiptDate += 1;
            until PurchaseHeader.Next() = 0;

        PurchaseLine.SetRange("Document Type", PurchaseLine."Document Type"::Order);
        if PurchaseLine.FindSet() then
            repeat
                if PurchaseLine."Line Discount %" > 25 then
                    DiscountAbove25 += 1;
                if PurchaseLine."Line Discount %" > 50 then
                    DiscountAbove50 += 1;
                if PurchaseLine."Quantity Received" > PurchaseLine."Quantity Invoiced" then
                    ReceivedNotInvoiced += 1;
                if (PurchaseLine."Outstanding Quantity" > 0) and (PurchaseLine."Expected Receipt Date" <> 0D) and (PurchaseLine."Expected Receipt Date" < Today()) then
                    OutstandingPastReceiptDate += 1;
                if PurchaseLine.Description = '' then
                    MissingDescription += 1;
                if PurchaseLine."Location Code" = '' then
                    MissingLocationCode += 1;
                if (PurchaseLine.Type = PurchaseLine.Type::Item) and (PurchaseLine."No." <> '') then
                    if Item.Get(PurchaseLine."No.") then
                        if (PurchaseLine."Direct Unit Cost" > 0) and (Item."Last Direct Cost" > 0) and (PurchaseLine."Direct Unit Cost" < Item."Last Direct Cost") then
                            CostBelowItemCost += 1;
            until PurchaseLine.Next() = 0;

        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_HEADERS_MISSING_PAYMENT_TERMS', 'medium', MissingPaymentTerms, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_HEADERS_MISSING_PAYMENT_METHOD', 'medium', MissingPaymentMethod, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_HEADERS_MISSING_PURCHASER', 'low', MissingPurchaserCode, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_HEADERS_MISSING_VENDOR_INVOICE_NO', 'low', MissingVendorInvoiceNo, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_HEADERS_PAST_EXPECTED_RECEIPT_DATE', 'high', PastExpectedReceiptDate, 4);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_LINES_DISCOUNT_OVER_25', 'low', DiscountAbove25, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_LINES_DISCOUNT_OVER_50', 'medium', DiscountAbove50, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_LINES_RECEIVED_NOT_INVOICED', 'medium', ReceivedNotInvoiced, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_LINES_OUTSTANDING_PAST_RECEIPT_DATE', 'medium', OutstandingPastReceiptDate, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_LINES_MISSING_DESCRIPTION', 'low', MissingDescription, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_LINES_MISSING_LOCATION', 'medium', MissingLocationCode, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'PURCHASE', 'PURCHASE_LINES_COST_BELOW_LAST_DIRECT_COST', 'low', CostBelowItemCost, 1);
    end;

    local procedure RunInventoryValueChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        Item: Record Item;
        LastMovementDate: Date;
        PriceBelowUnitCost: Integer;
        PriceBelowStandardCost: Integer;
        StandardCostZero: Integer;
        LastDirectCostZero: Integer;
        MissingLeadTime: Integer;
        SafetyStockZero: Integer;
        ReorderPointZero: Integer;
        MaxInventoryZero: Integer;
        MinOrderQtyZero: Integer;
        OrderMultipleZero: Integer;
        MissingShelfNo: Integer;
        MissingTariffNo: Integer;
        GrossWeightZero: Integer;
        NetWeightZero: Integer;
        UnitVolumeZero: Integer;
        DeadStock90: Integer;
        DeadStock180: Integer;
        DeadStock365: Integer;
        InventoryWithoutUnitCost: Integer;
    begin
        ChecksCount += 21;

        if Item.FindSet() then
            repeat
                Item.CalcFields(Inventory);
                if (Item."Unit Price" > 0) and (Item."Unit Cost" > 0) and (Item."Unit Price" < Item."Unit Cost") and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_PRICE_BELOW_UNIT_COST') then
                    PriceBelowUnitCost += 1;
                if (Item."Unit Price" > 0) and (Item."Standard Cost" > 0) and (Item."Unit Price" < Item."Standard Cost") and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_PRICE_BELOW_STANDARD_COST') then
                    PriceBelowStandardCost += 1;
                if (Item."Standard Cost" = 0) and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_STANDARD_COST_ZERO') then
                    StandardCostZero += 1;
                if (Item."Last Direct Cost" = 0) and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_LAST_DIRECT_COST_ZERO') then
                    LastDirectCostZero += 1;
                if (Format(Item."Lead Time Calculation") = '') and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_MISSING_LEAD_TIME') then
                    MissingLeadTime += 1;
                if (Item."Safety Stock Quantity" = 0) and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_SAFETY_STOCK_ZERO') then
                    SafetyStockZero += 1;
                if (Item."Reorder Point" = 0) and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_REORDER_POINT_ZERO') then
                    ReorderPointZero += 1;
                if (Item."Maximum Inventory" = 0) and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_MAX_INVENTORY_ZERO') then
                    MaxInventoryZero += 1;
                if (Item."Minimum Order Quantity" = 0) and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_MIN_ORDER_QTY_ZERO') then
                    MinOrderQtyZero += 1;
                if (Item."Order Multiple" = 0) and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_ORDER_MULTIPLE_ZERO') then
                    OrderMultipleZero += 1;
                if (Item."Shelf No." = '') and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_MISSING_SHELF_NO') then
                    MissingShelfNo += 1;
                if (Item."Tariff No." = '') and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_MISSING_TARIFF_NO') then
                    MissingTariffNo += 1;
                if (Item."Gross Weight" = 0) and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_GROSS_WEIGHT_ZERO') then
                    GrossWeightZero += 1;
                if (Item."Net Weight" = 0) and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_NET_WEIGHT_ZERO') then
                    NetWeightZero += 1;
                if (Item."Unit Volume" = 0) and not ExceptionMgt.IsItemIssueExcluded(Item, 'ITEMS_UNIT_VOLUME_ZERO') then
                    UnitVolumeZero += 1;
                if (Item.Inventory > 0) and (Item."Unit Cost" = 0) and not ExceptionMgt.IsItemIssueExcluded(Item, 'INVENTORY_WITHOUT_UNIT_COST') then
                    InventoryWithoutUnitCost += 1;

                LastMovementDate := GetLastItemMovementDate(Item."No.");
                if (Item.Inventory > 0) and (LastMovementDate <> 0D) and (LastMovementDate <= CalcDate('<-90D>', Today())) and not ExceptionMgt.IsItemIssueExcluded(Item, 'DEAD_STOCK_90') then
                    DeadStock90 += 1;
                if (Item.Inventory > 0) and (LastMovementDate <> 0D) and (LastMovementDate <= CalcDate('<-180D>', Today())) and not ExceptionMgt.IsItemIssueExcluded(Item, 'DEAD_STOCK_180') then
                    DeadStock180 += 1;
                if (Item.Inventory > 0) and (LastMovementDate <> 0D) and (LastMovementDate <= CalcDate('<-365D>', Today())) and not ExceptionMgt.IsItemIssueExcluded(Item, 'DEAD_STOCK_365') then
                    DeadStock365 += 1;
            until Item.Next() = 0;

        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'ITEMS_PRICE_BELOW_UNIT_COST', 'high', PriceBelowUnitCost, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'ITEMS_PRICE_BELOW_STANDARD_COST', 'high', PriceBelowStandardCost, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'ITEMS_STANDARD_COST_ZERO', 'medium', StandardCostZero, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'ITEMS_LAST_DIRECT_COST_ZERO', 'medium', LastDirectCostZero, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'ITEMS_MISSING_LEAD_TIME', 'medium', MissingLeadTime, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'ITEMS_SAFETY_STOCK_ZERO', 'low', SafetyStockZero, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'ITEMS_REORDER_POINT_ZERO', 'low', ReorderPointZero, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'ITEMS_MAX_INVENTORY_ZERO', 'low', MaxInventoryZero, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'ITEMS_MIN_ORDER_QTY_ZERO', 'low', MinOrderQtyZero, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'ITEMS_ORDER_MULTIPLE_ZERO', 'low', OrderMultipleZero, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'ITEMS_MISSING_SHELF_NO', 'low', MissingShelfNo, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'ITEMS_MISSING_TARIFF_NO', 'low', MissingTariffNo, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'ITEMS_GROSS_WEIGHT_ZERO', 'low', GrossWeightZero, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'ITEMS_NET_WEIGHT_ZERO', 'low', NetWeightZero, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'ITEMS_UNIT_VOLUME_ZERO', 'low', UnitVolumeZero, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'DEAD_STOCK_90', 'medium', DeadStock90, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'DEAD_STOCK_180', 'medium', DeadStock180, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'DEAD_STOCK_365', 'high', DeadStock365, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'INVENTORY', 'INVENTORY_WITHOUT_UNIT_COST', 'high', InventoryWithoutUnitCost, 5);
    end;

    local procedure RunCRMContactChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        Contact: Record Contact;
        MissingName: Integer;
        MissingEmail: Integer;
        MissingPhone: Integer;
        MissingMobilePhone: Integer;
        MissingCompanyNo: Integer;
        MissingAddress: Integer;
        MissingCity: Integer;
        MissingPostCode: Integer;
        MissingCountryCode: Integer;
    begin
        ChecksCount += 9;

        if Contact.FindSet() then
            repeat
                if Contact.Name = '' then
                    MissingName += 1;
                if Contact."E-Mail" = '' then
                    MissingEmail += 1;
                if Contact."Phone No." = '' then
                    MissingPhone += 1;
                if Contact."Mobile Phone No." = '' then
                    MissingMobilePhone += 1;
                if (Contact.Type = Contact.Type::Person) and (Contact."Company No." = '') then
                    MissingCompanyNo += 1;
                if Contact.Address = '' then
                    MissingAddress += 1;
                if Contact.City = '' then
                    MissingCity += 1;
                if Contact."Post Code" = '' then
                    MissingPostCode += 1;
                if Contact."Country/Region Code" = '' then
                    MissingCountryCode += 1;
            until Contact.Next() = 0;

        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CRM', 'CONTACTS_MISSING_NAME', 'medium', MissingName, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CRM', 'CONTACTS_MISSING_EMAIL', 'medium', MissingEmail, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CRM', 'CONTACTS_MISSING_PHONE', 'low', MissingPhone, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CRM', 'CONTACTS_MISSING_MOBILE_PHONE', 'low', MissingMobilePhone, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CRM', 'CONTACTS_PERSONS_MISSING_COMPANY', 'medium', MissingCompanyNo, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CRM', 'CONTACTS_MISSING_ADDRESS', 'low', MissingAddress, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CRM', 'CONTACTS_MISSING_CITY', 'low', MissingCity, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CRM', 'CONTACTS_MISSING_POST_CODE', 'low', MissingPostCode, 1);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'CRM', 'CONTACTS_MISSING_COUNTRY', 'low', MissingCountryCode, 1);
    end;


    local procedure RunManufacturingChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        ProdBOMHeader: Record "Production BOM Header";
        ProdBOMLine: Record "Production BOM Line";
        RoutingHeader: Record "Routing Header";
        RoutingLine: Record "Routing Line";
        WorkCenter: Record "Work Center";
        MachineCenter: Record "Machine Center";
        Item: Record Item;
        MissingBOMDescription: Integer;
        BOMNotCertified: Integer;
        BOMLinesMissingNo: Integer;
        BOMLinesZeroQty: Integer;
        RoutingMissingDescription: Integer;
        RoutingNotCertified: Integer;
        RoutingLinesMissingNo: Integer;
        RoutingLinesZeroSetupTime: Integer;
        RoutingLinesZeroRunTime: Integer;
        WorkCentersBlocked: Integer;
        WorkCentersMissingName: Integer;
        WorkCentersZeroCost: Integer;
        MachineCentersBlocked: Integer;
        MachineCentersMissingName: Integer;
        MachineCentersZeroCost: Integer;
        ItemsMissingProdBomNo: Integer;
        ItemsMissingRoutingNo: Integer;
    begin
        ChecksCount += 17;

        if ProdBOMHeader.FindSet() then
            repeat
                if ProdBOMHeader.Description = '' then
                    MissingBOMDescription += 1;
                if ProdBOMHeader.Status <> ProdBOMHeader.Status::Certified then
                    BOMNotCertified += 1;
            until ProdBOMHeader.Next() = 0;

        if ProdBOMLine.FindSet() then
            repeat
                if (Format(ProdBOMLine.Type) <> '') and (ProdBOMLine."No." = '') then
                    BOMLinesMissingNo += 1;
                if ProdBOMLine.Quantity = 0 then
                    BOMLinesZeroQty += 1;
            until ProdBOMLine.Next() = 0;

        if RoutingHeader.FindSet() then
            repeat
                if RoutingHeader.Description = '' then
                    RoutingMissingDescription += 1;
                if RoutingHeader.Status <> RoutingHeader.Status::Certified then
                    RoutingNotCertified += 1;
            until RoutingHeader.Next() = 0;

        if RoutingLine.FindSet() then
            repeat
                if (Format(RoutingLine.Type) <> '') and (RoutingLine."No." = '') then
                    RoutingLinesMissingNo += 1;
                if RoutingLine."Setup Time" = 0 then
                    RoutingLinesZeroSetupTime += 1;
                if RoutingLine."Run Time" = 0 then
                    RoutingLinesZeroRunTime += 1;
            until RoutingLine.Next() = 0;

        if WorkCenter.FindSet() then
            repeat
                if WorkCenter.Blocked then
                    WorkCentersBlocked += 1;
                if WorkCenter.Name = '' then
                    WorkCentersMissingName += 1;
                if WorkCenter."Unit Cost" = 0 then
                    WorkCentersZeroCost += 1;
            until WorkCenter.Next() = 0;

        if MachineCenter.FindSet() then
            repeat
                if MachineCenter.Blocked then
                    MachineCentersBlocked += 1;
                if MachineCenter.Name = '' then
                    MachineCentersMissingName += 1;
                if MachineCenter."Unit Cost" = 0 then
                    MachineCentersZeroCost += 1;
            until MachineCenter.Next() = 0;

        if Item.FindSet() then
            repeat
                if (Item."Production BOM No." <> '') and (Item."Routing No." = '') and not ExceptionMgt.IsItemIssueExcluded(Item, 'MFG_ITEMS_MISSING_ROUTING_NO') then
                    ItemsMissingRoutingNo += 1;
                if (Item."Routing No." <> '') and (Item."Production BOM No." = '') and not ExceptionMgt.IsItemIssueExcluded(Item, 'MFG_ITEMS_MISSING_PROD_BOM_NO') then
                    ItemsMissingProdBomNo += 1;
            until Item.Next() = 0;

        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_BOM_MISSING_DESCRIPTION', 'medium', MissingBOMDescription, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_BOM_NOT_CERTIFIED', 'high', BOMNotCertified, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_BOM_LINES_MISSING_NO', 'high', BOMLinesMissingNo, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_BOM_LINES_ZERO_QTY', 'high', BOMLinesZeroQty, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_ROUTING_MISSING_DESCRIPTION', 'low', RoutingMissingDescription, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_ROUTING_NOT_CERTIFIED', 'high', RoutingNotCertified, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_ROUTING_LINES_MISSING_NO', 'high', RoutingLinesMissingNo, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_ROUTING_LINES_ZERO_SETUP', 'medium', RoutingLinesZeroSetupTime, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_ROUTING_LINES_ZERO_RUN', 'high', RoutingLinesZeroRunTime, 4);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_WORK_CENTERS_BLOCKED', 'medium', WorkCentersBlocked, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_WORK_CENTERS_MISSING_NAME', 'low', WorkCentersMissingName, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_WORK_CENTERS_ZERO_COST', 'medium', WorkCentersZeroCost, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_MACHINE_CENTERS_BLOCKED', 'medium', MachineCentersBlocked, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_MACHINE_CENTERS_MISSING_NAME', 'low', MachineCentersMissingName, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_MACHINE_CENTERS_ZERO_COST', 'medium', MachineCentersZeroCost, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_ITEMS_MISSING_PROD_BOM_NO', 'high', ItemsMissingProdBomNo, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'MANUFACTURING', 'MFG_ITEMS_MISSING_ROUTING_NO', 'high', ItemsMissingRoutingNo, 5);
    end;

    local procedure RunServiceChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        ServiceItem: Record "Service Item";
        ServiceHeader: Record "Service Header";
        ServiceLine: Record "Service Line";
        MissingServiceItemDescription: Integer;
        MissingServiceItemCustomer: Integer;
        MissingServiceItemItemNo: Integer;
        MissingServiceItemSerialNo: Integer;
        MissingHeaderCustomer: Integer;
        MissingHeaderBillToCustomer: Integer;
        MissingHeaderDescription: Integer;
        MissingHeaderAssignedUser: Integer;
        MissingLineNo: Integer;
        MissingLineDescription: Integer;
        ZeroLineQuantity: Integer;
        ZeroLineUnitPrice: Integer;
    begin
        ChecksCount += 12;

        if ServiceItem.FindSet() then
            repeat
                if ServiceItem.Description = '' then
                    MissingServiceItemDescription += 1;
                if ServiceItem."Customer No." = '' then
                    MissingServiceItemCustomer += 1;
                if ServiceItem."Item No." = '' then
                    MissingServiceItemItemNo += 1;
                if ServiceItem."Serial No." = '' then
                    MissingServiceItemSerialNo += 1;
            until ServiceItem.Next() = 0;

        if ServiceHeader.FindSet() then
            repeat
                if ServiceHeader."Customer No." = '' then
                    MissingHeaderCustomer += 1;
                if ServiceHeader."Bill-to Customer No." = '' then
                    MissingHeaderBillToCustomer += 1;
                if ServiceHeader.Description = '' then
                    MissingHeaderDescription += 1;
                if ServiceHeader."Assigned User ID" = '' then
                    MissingHeaderAssignedUser += 1;
            until ServiceHeader.Next() = 0;

        if ServiceLine.FindSet() then
            repeat
                if (Format(ServiceLine.Type) <> '') and (ServiceLine."No." = '') then
                    MissingLineNo += 1;
                if (Format(ServiceLine.Type) <> '') and (ServiceLine.Description = '') then
                    MissingLineDescription += 1;
                if (Format(ServiceLine.Type) <> '') and (ServiceLine.Quantity = 0) then
                    ZeroLineQuantity += 1;
                if (Format(ServiceLine.Type) <> '') and (ServiceLine."Unit Price" = 0) then
                    ZeroLineUnitPrice += 1;
            until ServiceLine.Next() = 0;

        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SERVICE', 'SERVICE_ITEMS_MISSING_DESCRIPTION', 'medium', MissingServiceItemDescription, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SERVICE', 'SERVICE_ITEMS_MISSING_CUSTOMER', 'high', MissingServiceItemCustomer, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SERVICE', 'SERVICE_ITEMS_MISSING_ITEM_NO', 'high', MissingServiceItemItemNo, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SERVICE', 'SERVICE_ITEMS_MISSING_SERIAL_NO', 'medium', MissingServiceItemSerialNo, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SERVICE', 'SERVICE_ORDERS_MISSING_CUSTOMER', 'high', MissingHeaderCustomer, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SERVICE', 'SERVICE_ORDERS_MISSING_BILL_TO', 'high', MissingHeaderBillToCustomer, 6);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SERVICE', 'SERVICE_ORDERS_MISSING_DESCRIPTION', 'medium', MissingHeaderDescription, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SERVICE', 'SERVICE_ORDERS_MISSING_ASSIGNED_USER', 'medium', MissingHeaderAssignedUser, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SERVICE', 'SERVICE_LINES_MISSING_NO', 'high', MissingLineNo, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SERVICE', 'SERVICE_LINES_MISSING_DESCRIPTION', 'medium', MissingLineDescription, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SERVICE', 'SERVICE_LINES_ZERO_QTY', 'medium', ZeroLineQuantity, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'SERVICE', 'SERVICE_LINES_ZERO_UNIT_PRICE', 'high', ZeroLineUnitPrice, 5);
    end;

    local procedure RunJobsChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        JobRec: Record Job;
        JobTask: Record "Job Task";
        JobPlanningLine: Record "Job Planning Line";
        MissingJobDescription: Integer;
        MissingBillToCustomer: Integer;
        MissingPersonResponsible: Integer;
        MissingJobPostingGroup: Integer;
        MissingTaskDescription: Integer;
        MissingPlanningLineNo: Integer;
        MissingPlanningDescription: Integer;
        ZeroPlanningQuantity: Integer;
        ZeroUnitCost: Integer;
        ZeroUnitPrice: Integer;
    begin
        ChecksCount += 10;

        if JobRec.FindSet() then
            repeat
                if JobRec.Description = '' then
                    MissingJobDescription += 1;
                if JobRec."Bill-to Customer No." = '' then
                    MissingBillToCustomer += 1;
                if JobRec."Person Responsible" = '' then
                    MissingPersonResponsible += 1;
                if JobRec."Job Posting Group" = '' then
                    MissingJobPostingGroup += 1;
            until JobRec.Next() = 0;

        if JobTask.FindSet() then
            repeat
                if JobTask.Description = '' then
                    MissingTaskDescription += 1;
            until JobTask.Next() = 0;

        if JobPlanningLine.FindSet() then
            repeat
                if (Format(JobPlanningLine.Type) <> '') and (JobPlanningLine."No." = '') then
                    MissingPlanningLineNo += 1;
                if (Format(JobPlanningLine.Type) <> '') and (JobPlanningLine.Description = '') then
                    MissingPlanningDescription += 1;
                if (Format(JobPlanningLine.Type) <> '') and (JobPlanningLine.Quantity = 0) then
                    ZeroPlanningQuantity += 1;
                if (Format(JobPlanningLine.Type) <> '') and (JobPlanningLine."Unit Cost" = 0) then
                    ZeroUnitCost += 1;
                if (Format(JobPlanningLine.Type) <> '') and (JobPlanningLine."Unit Price" = 0) then
                    ZeroUnitPrice += 1;
            until JobPlanningLine.Next() = 0;

        AddCountFinding(DeepScanRun, Score, IssuesCount, 'JOB', 'JOBS_MISSING_DESCRIPTION', 'medium', MissingJobDescription, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'JOB', 'JOBS_MISSING_BILL_TO_CUSTOMER', 'high', MissingBillToCustomer, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'JOB', 'JOBS_MISSING_RESPONSIBLE', 'medium', MissingPersonResponsible, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'JOB', 'JOBS_MISSING_POSTING_GROUP', 'high', MissingJobPostingGroup, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'JOB', 'JOB_TASKS_MISSING_DESCRIPTION', 'medium', MissingTaskDescription, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'JOB', 'JOB_PLANNING_LINES_MISSING_NO', 'high', MissingPlanningLineNo, 5);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'JOB', 'JOB_PLANNING_LINES_MISSING_DESCRIPTION', 'medium', MissingPlanningDescription, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'JOB', 'JOB_PLANNING_LINES_ZERO_QTY', 'medium', ZeroPlanningQuantity, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'JOB', 'JOB_PLANNING_LINES_ZERO_UNIT_COST', 'high', ZeroUnitCost, 4);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'JOB', 'JOB_PLANNING_LINES_ZERO_UNIT_PRICE', 'high', ZeroUnitPrice, 4);
    end;

    local procedure RunHRChecks(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var ChecksCount: Integer; var IssuesCount: Integer)
    var
        Employee: Record Employee;
        ResourceRec: Record Resource;
        MissingFirstName: Integer;
        MissingLastName: Integer;
        MissingSearchName: Integer;
        MissingEmail: Integer;
        MissingPhone: Integer;
        MissingCountryCode: Integer;
        MissingResourceNo: Integer;
        MissingJobTitle: Integer;
        ResourcesMissingName: Integer;
        ResourcesZeroUnitCost: Integer;
        ResourcesZeroUnitPrice: Integer;
        ResourcesMissingBaseUOM: Integer;
    begin
        ChecksCount += 12;

        if Employee.FindSet() then
            repeat
                if Employee."First Name" = '' then
                    MissingFirstName += 1;
                if Employee."Last Name" = '' then
                    MissingLastName += 1;
                if Employee."Search Name" = '' then
                    MissingSearchName += 1;
                if Employee."E-Mail" = '' then
                    MissingEmail += 1;
                if Employee."Phone No." = '' then
                    MissingPhone += 1;
                if Employee."Country/Region Code" = '' then
                    MissingCountryCode += 1;
                if Employee."Resource No." = '' then
                    MissingResourceNo += 1;
                if Employee."Job Title" = '' then
                    MissingJobTitle += 1;
            until Employee.Next() = 0;

        if ResourceRec.FindSet() then
            repeat
                if ResourceRec.Name = '' then
                    ResourcesMissingName += 1;
                if ResourceRec."Unit Cost" = 0 then
                    ResourcesZeroUnitCost += 1;
                if ResourceRec."Unit Price" = 0 then
                    ResourcesZeroUnitPrice += 1;
                if ResourceRec."Base Unit of Measure" = '' then
                    ResourcesMissingBaseUOM += 1;
            until ResourceRec.Next() = 0;

        AddCountFinding(DeepScanRun, Score, IssuesCount, 'HR', 'EMPLOYEES_MISSING_FIRST_NAME', 'low', MissingFirstName, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'HR', 'EMPLOYEES_MISSING_LAST_NAME', 'medium', MissingLastName, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'HR', 'EMPLOYEES_MISSING_SEARCH_NAME', 'low', MissingSearchName, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'HR', 'EMPLOYEES_MISSING_EMAIL', 'medium', MissingEmail, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'HR', 'EMPLOYEES_MISSING_PHONE', 'low', MissingPhone, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'HR', 'EMPLOYEES_MISSING_COUNTRY', 'low', MissingCountryCode, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'HR', 'EMPLOYEES_MISSING_RESOURCE_NO', 'medium', MissingResourceNo, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'HR', 'EMPLOYEES_MISSING_JOB_TITLE', 'low', MissingJobTitle, 2);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'HR', 'RESOURCES_MISSING_NAME', 'medium', ResourcesMissingName, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'HR', 'RESOURCES_ZERO_UNIT_COST', 'medium', ResourcesZeroUnitCost, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'HR', 'RESOURCES_ZERO_UNIT_PRICE', 'medium', ResourcesZeroUnitPrice, 3);
        AddCountFinding(DeepScanRun, Score, IssuesCount, 'HR', 'RESOURCES_MISSING_BASE_UOM', 'low', ResourcesMissingBaseUOM, 2);
    end;

    local procedure GetEnabledModuleCount(var Setup: Record "DH Setup"): Integer
    var
        EnabledCount: Integer;
    begin
        if Setup.GetEnabledDeepScanModuleCount() > 0 then
            exit(Setup.GetEnabledDeepScanModuleCount());

        exit(10);
    end;

    local procedure IsModuleEnabled(var Setup: Record "DH Setup"; ModuleName: Text): Boolean
    begin
        case ModuleName of
            'System':
                exit(Setup."Scan System Module");
            'Finance':
                exit(Setup."Scan Finance Module");
            'Sales':
                exit(Setup."Scan Sales Module");
            'Purchasing':
                exit(Setup."Scan Purchasing Module");
            'Inventory':
                exit(Setup."Scan Inventory Module");
            'CRM':
                exit(Setup."Scan CRM Module");
            'Manufacturing':
                exit(Setup."Scan Manufacturing Module");
            'Service':
                exit(Setup."Scan Service Module");
            'Jobs':
                exit(Setup."Scan Jobs Module");
            'HR':
                exit(Setup."Scan HR Module");
        end;

        exit(true);
    end;

    local procedure InitializeProgress(var DeepScanRun: Record "DH Deep Scan Run"; TotalModules: Integer)
    begin
        DeepScanRun.Get(DeepScanRun."Entry No.");
        DeepScanRun."Current Module" := 'Initializing';
        DeepScanRun."Progress %" := 0;
        DeepScanRun."Completed Modules" := 0;
        DeepScanRun."Total Modules" := TotalModules;
        DeepScanRun."ETA Text" := 'Calculating...';
        DeepScanRun."System Progress %" := 0;
        DeepScanRun."Finance Progress %" := 0;
        DeepScanRun."Sales Progress %" := 0;
        DeepScanRun."Purchasing Progress %" := 0;
        DeepScanRun."Inventory Progress %" := 0;
        DeepScanRun."CRM Progress %" := 0;
        DeepScanRun."Manufacturing Progress %" := 0;
        DeepScanRun."Service Progress %" := 0;
        DeepScanRun."Jobs Progress %" := 0;
        DeepScanRun."HR Progress %" := 0;
        DeepScanRun.Modify(true);
        Commit();
        TryUpdateBackendProgress(DeepScanRun, 'running', 'Initializing module progress', 'Scan preparation started');
    end;

    local procedure StartModule(var DeepScanRun: Record "DH Deep Scan Run"; ModuleName: Text[50]; ModuleNo: Integer)
    begin
        DeepScanRun.Get(DeepScanRun."Entry No.");
        DeepScanRun."Current Module" := ModuleName;
        SetModuleProgress(DeepScanRun, ModuleName, 10);
        if DeepScanRun."Total Modules" > 0 then
            DeepScanRun."Progress %" := ((ModuleNo - 1) * 100) div DeepScanRun."Total Modules";
        DeepScanRun."ETA Text" := GetEtaText(DeepScanRun, ModuleNo - 1);
        DeepScanRun.Modify(true);
        Commit();
        TryUpdateBackendProgress(DeepScanRun, 'running', StrSubstNo('%1 checks started', ModuleName), StrSubstNo('%1 checks started', ModuleName));
    end;

    local procedure CompleteModule(var DeepScanRun: Record "DH Deep Scan Run"; ModuleName: Text[50]; ModuleNo: Integer)
    begin
        DeepScanRun.Get(DeepScanRun."Entry No.");
        SetModuleProgress(DeepScanRun, ModuleName, 100);
        DeepScanRun."Completed Modules" := ModuleNo;
        if DeepScanRun."Total Modules" > 0 then
            DeepScanRun."Progress %" := (ModuleNo * 100) div DeepScanRun."Total Modules";
        if ModuleNo >= DeepScanRun."Total Modules" then begin
            DeepScanRun."Current Module" := 'Finalizing';
            DeepScanRun."ETA Text" := 'Less than 1 minute';
        end else
            DeepScanRun."ETA Text" := GetEtaText(DeepScanRun, ModuleNo);
        DeepScanRun.Modify(true);
        Commit();
        TryUpdateBackendProgress(DeepScanRun, 'running', StrSubstNo('%1 checks completed', ModuleName), StrSubstNo('%1 checks completed', ModuleName));
    end;

    local procedure TryUpdateBackendProgress(var DeepScanRun: Record "DH Deep Scan Run"; StatusValue: Text; CurrentStep: Text; EventMessage: Text)
    begin
        if DeepScanRun."Backend Sync Status" = DeepScanRun."Backend Sync Status"::Failed then
            exit;
        if not SendBackendProgress(DeepScanRun, StatusValue, CurrentStep, EventMessage) then;
    end;

    [TryFunction]
    local procedure SendBackendProgress(var DeepScanRun: Record "DH Deep Scan Run"; StatusValue: Text; CurrentStep: Text; EventMessage: Text)
    var
        Setup: Record "DH Setup";
        ApiClient: Codeunit "DH API Client";
        FailureMessage: Text;
        LeaseRejected: Boolean;
    begin
        if not Setup.Get('SETUP') then
            exit;

        if (Setup."Tenant ID" = '') or (GetApiToken(Setup) = '') or (Setup."API Base URL" = '') then
            exit;

        if StatusValue = 'completed' then begin
            DeepScanRun.Status := DeepScanRun.Status::Completed;
            DeepScanRun."Progress %" := 100;
            DeepScanRun."Current Module" := 'All modules completed';
            DeepScanRun."Current Step" := 'Scan completed';
            DeepScanRun."Warning Message" := '';
            DeepScanRun."Error Message" := '';
        end else
            if StatusValue = 'failed' then begin
                DeepScanRun.Status := DeepScanRun.Status::Failed;
                DeepScanRun."Current Step" := 'Scan failed';
            end;

        DeepScanRun."Current Step" := CopyStr(CurrentStep, 1, MaxStrLen(DeepScanRun."Current Step"));
        DeepScanRun."Last Heartbeat" := CurrentDateTime();
        DeepScanRun.Modify(true);
        if not ApiClient.TryUpdateScanProgress(Setup, DeepScanRun, StatusValue, CurrentStep, EventMessage, FailureMessage, LeaseRejected) then begin
            DeepScanRun.Get(DeepScanRun."Entry No.");
            if LeaseRejected then
                DeepScanRun."Backend Sync Status" := DeepScanRun."Backend Sync Status"::Failed
            else
                DeepScanRun."Backend Sync Status" := DeepScanRun."Backend Sync Status"::RetryRequired;
            DeepScanRun."Backend Sync Error" := CopyStr(FailureMessage, 1, MaxStrLen(DeepScanRun."Backend Sync Error"));
            DeepScanRun."Warning Message" := CopyStr(FailureMessage, 1, MaxStrLen(DeepScanRun."Warning Message"));
            DeepScanRun.Modify(true);
            Commit();
            exit;
        end;

        DeepScanRun.Get(DeepScanRun."Entry No.");
        if DeepScanRun."Backend Sync Status" = DeepScanRun."Backend Sync Status"::RetryRequired then begin
            DeepScanRun."Backend Sync Status" := DeepScanRun."Backend Sync Status"::Pending;
            DeepScanRun."Backend Sync Error" := '';
        end;
        DeepScanRun.Modify(true);
        Commit();
    end;

    local procedure SetModuleProgress(var DeepScanRun: Record "DH Deep Scan Run"; ModuleName: Text; PercentValue: Integer)
    begin
        case ModuleName of
            'System':
                DeepScanRun."System Progress %" := PercentValue;
            'Finance':
                DeepScanRun."Finance Progress %" := PercentValue;
            'Sales':
                DeepScanRun."Sales Progress %" := PercentValue;
            'Purchasing':
                DeepScanRun."Purchasing Progress %" := PercentValue;
            'Inventory':
                DeepScanRun."Inventory Progress %" := PercentValue;
            'CRM':
                DeepScanRun."CRM Progress %" := PercentValue;
            'Manufacturing':
                DeepScanRun."Manufacturing Progress %" := PercentValue;
            'Service':
                DeepScanRun."Service Progress %" := PercentValue;
            'Jobs':
                DeepScanRun."Jobs Progress %" := PercentValue;
            'HR':
                DeepScanRun."HR Progress %" := PercentValue;
        end;
    end;

    local procedure GetEtaText(var DeepScanRun: Record "DH Deep Scan Run"; CompletedModules: Integer): Text[100]
    var
        ElapsedSeconds: Integer;
        RemainingSeconds: Integer;
        RemainingMinutes: Integer;
    begin
        if (CompletedModules <= 0) or (DeepScanRun."Started At" = 0DT) or (DeepScanRun."Total Modules" <= 0) then
            exit('Calculating...');

        ElapsedSeconds := GetElapsedSeconds(DeepScanRun."Started At", CurrentDateTime());
        RemainingSeconds := (ElapsedSeconds div CompletedModules) * (DeepScanRun."Total Modules" - CompletedModules);
        if RemainingSeconds < 60 then
            exit('Less than 1 minute');

        RemainingMinutes := (RemainingSeconds + 59) div 60;
        exit(StrSubstNo('%1 min remaining', RemainingMinutes));
    end;

    local procedure GetElapsedSeconds(StartDateTime: DateTime; EndDateTime: DateTime): Integer
    begin
        exit((EndDateTime - StartDateTime) div 1000);
    end;

    local procedure GetLastItemMovementDate(ItemNo: Code[20]): Date
    var
        ItemLedgerEntry: Record "Item Ledger Entry";
    begin
        ItemLedgerEntry.SetCurrentKey("Item No.", "Posting Date");
        ItemLedgerEntry.SetRange("Item No.", ItemNo);
        if ItemLedgerEntry.FindLast() then
            exit(ItemLedgerEntry."Posting Date");

        exit(0D);
    end;

    local procedure HasGLEntriesForAccount(GLAccountNo: Code[20]): Boolean
    var
        GLEntry: Record "G/L Entry";
    begin
        GLEntry.SetRange("G/L Account No.", GLAccountNo);
        exit(not GLEntry.IsEmpty());
    end;

    local procedure CountCustomersByEmail(Email: Text[100]; IssueCode: Code[50]): Integer
    var
        Customer: Record Customer;
        Count: Integer;
    begin
        Customer.SetRange("E-Mail", Email);
        if Customer.FindSet() then
            repeat
                if not IsCustomerDuplicateExcluded(Customer, IssueCode) then
                    Count += 1;
            until Customer.Next() = 0;

        exit(Count);
    end;

    local procedure CountVendorsByEmail(Email: Text[100]; IssueCode: Code[50]): Integer
    var
        Vendor: Record Vendor;
        Count: Integer;
    begin
        Vendor.SetRange("E-Mail", Email);
        if Vendor.FindSet() then
            repeat
                if not IsVendorDuplicateExcluded(Vendor, IssueCode) then
                    Count += 1;
            until Vendor.Next() = 0;

        exit(Count);
    end;

    local procedure CountCustomersByVat(VatRegNo: Code[20]; IssueCode: Code[50]): Integer
    var
        Customer: Record Customer;
        Count: Integer;
    begin
        Customer.SetRange("VAT Registration No.", VatRegNo);
        if Customer.FindSet() then
            repeat
                if not IsCustomerDuplicateExcluded(Customer, IssueCode) then
                    Count += 1;
            until Customer.Next() = 0;

        exit(Count);
    end;

    local procedure CountVendorsByVat(VatRegNo: Code[20]; IssueCode: Code[50]): Integer
    var
        Vendor: Record Vendor;
        Count: Integer;
    begin
        Vendor.SetRange("VAT Registration No.", VatRegNo);
        if Vendor.FindSet() then
            repeat
                if not IsVendorDuplicateExcluded(Vendor, IssueCode) then
                    Count += 1;
            until Vendor.Next() = 0;

        exit(Count);
    end;

    local procedure CountCustomersByNamePostCity(NameValue: Text[100]; PostCode: Code[20]; CityValue: Text[30]; IssueCode: Code[50]): Integer
    var
        Customer: Record Customer;
        Count: Integer;
    begin
        Customer.SetRange(Name, NameValue);
        Customer.SetRange("Post Code", PostCode);
        Customer.SetRange(City, CityValue);
        if Customer.FindSet() then
            repeat
                if not IsCustomerDuplicateExcluded(Customer, IssueCode) then
                    Count += 1;
            until Customer.Next() = 0;

        exit(Count);
    end;

    local procedure CountVendorsByNamePostCity(NameValue: Text[100]; PostCode: Code[20]; CityValue: Text[30]; IssueCode: Code[50]): Integer
    var
        Vendor: Record Vendor;
        Count: Integer;
    begin
        Vendor.SetRange(Name, NameValue);
        Vendor.SetRange("Post Code", PostCode);
        Vendor.SetRange(City, CityValue);
        if Vendor.FindSet() then
            repeat
                if not IsVendorDuplicateExcluded(Vendor, IssueCode) then
                    Count += 1;
            until Vendor.Next() = 0;

        exit(Count);
    end;

    local procedure IsCustomerDuplicateExcluded(var Customer: Record Customer; IssueCode: Code[50]): Boolean
    begin
        exit(ExceptionMgt.IsCustomerIssueExcluded(Customer, IssueCode));
    end;

    local procedure IsVendorDuplicateExcluded(var Vendor: Record Vendor; IssueCode: Code[50]): Boolean
    begin
        exit(ExceptionMgt.IsVendorIssueExcluded(Vendor, IssueCode));
    end;

    local procedure AddCountFinding(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer; var IssuesCount: Integer; Category: Code[30]; IssueCode: Code[50]; Severity: Code[20]; AffectedCount: Integer; PenaltyPoints: Integer)
    var
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
    begin
        if not ScanCheckMgt.IsCheckEnabled(IssueCode) then
            exit;

        ScanCheckMgt.UpdateLastRun(IssueCode, AffectedCount);

        if AffectedCount <= 0 then
            exit;

        Severity := ResolveImpactSeverity(IssueCode, Severity, AffectedCount, PenaltyPoints);

        InsertFinding(
            DeepScanRun."Entry No.",
            Category,
            IssueCode,
            Severity,
            AffectedCount);

        IssuesCount += 1;
        ApplyPenalty(Score, PenaltyPoints);
    end;

    local procedure ApplyPenalty(var Score: Integer; PenaltyPoints: Integer)
    begin
        Score -= PenaltyPoints;
        if Score < 0 then
            Score := 0;
    end;

    local procedure HasOpenSalesDocumentsForCustomer(CustomerNo: Code[20]): Boolean
    var
        SalesHeader: Record "Sales Header";
    begin
        SalesHeader.Reset();
        SalesHeader.SetRange("Sell-to Customer No.", CustomerNo);
        SalesHeader.SetFilter("Document Type", '%1|%2|%3', SalesHeader."Document Type"::Quote, SalesHeader."Document Type"::Order, SalesHeader."Document Type"::Invoice);
        exit(not SalesHeader.IsEmpty());
    end;

    local procedure HasOpenPurchaseDocumentsForVendor(VendorNo: Code[20]): Boolean
    var
        PurchaseHeader: Record "Purchase Header";
    begin
        PurchaseHeader.Reset();
        PurchaseHeader.SetRange("Buy-from Vendor No.", VendorNo);
        PurchaseHeader.SetFilter("Document Type", '%1|%2|%3', PurchaseHeader."Document Type"::Quote, PurchaseHeader."Document Type"::Order, PurchaseHeader."Document Type"::Invoice);
        exit(not PurchaseHeader.IsEmpty());
    end;

    local procedure HasOpenCustomerLedgerEntries(CustomerNo: Code[20]): Boolean
    var
        CustLedgerEntry: Record "Cust. Ledger Entry";
    begin
        CustLedgerEntry.Reset();
        CustLedgerEntry.SetRange("Customer No.", CustomerNo);
        CustLedgerEntry.SetRange(Open, true);
        exit(not CustLedgerEntry.IsEmpty());
    end;

    local procedure HasOpenVendorLedgerEntries(VendorNo: Code[20]): Boolean
    var
        VendorLedgerEntry: Record "Vendor Ledger Entry";
    begin
        VendorLedgerEntry.Reset();
        VendorLedgerEntry.SetRange("Vendor No.", VendorNo);
        VendorLedgerEntry.SetRange(Open, true);
        exit(not VendorLedgerEntry.IsEmpty());
    end;

    local procedure RecalculateScoreMetrics(var DeepScanRun: Record "DH Deep Scan Run"; var Score: Integer)
    var
        Finding: Record "DH Deep Scan Finding";
        Setup: Record "DH Setup";
        WeightedScoreTotal: Integer;
        EnabledWeightTotal: Integer;
        AffectedRecords: Integer;
        ModuleName: Text[30];
    begin
        ClearRunScoreMetrics(DeepScanRun);

        Finding.SetRange("Deep Scan Entry No.", DeepScanRun."Entry No.");
        if Finding.FindSet() then
            repeat
                AffectedRecords += Finding."Affected Count";
                ModuleName := ResolveModuleFromCategory(Finding.Category);
                AddPenaltyToModule(DeepScanRun, ModuleName, GetSeverityPenalty(Finding.Severity) + GetAffectedPenalty(Finding."Affected Count"));
            until Finding.Next() = 0;

        DeepScanRun."Affected Records" := AffectedRecords;
        DeepScanRun."System Score" := NormalizeModuleScore(DeepScanRun."System Score");
        DeepScanRun."Finance Score" := NormalizeModuleScore(DeepScanRun."Finance Score");
        DeepScanRun."Sales Score" := NormalizeModuleScore(DeepScanRun."Sales Score");
        DeepScanRun."Purchasing Score" := NormalizeModuleScore(DeepScanRun."Purchasing Score");
        DeepScanRun."Inventory Score" := NormalizeModuleScore(DeepScanRun."Inventory Score");
        DeepScanRun."CRM Score" := NormalizeModuleScore(DeepScanRun."CRM Score");
        DeepScanRun."Manufacturing Score" := NormalizeModuleScore(DeepScanRun."Manufacturing Score");
        DeepScanRun."Service Score" := NormalizeModuleScore(DeepScanRun."Service Score");
        DeepScanRun."Jobs Score" := NormalizeModuleScore(DeepScanRun."Jobs Score");
        DeepScanRun."HR Score" := NormalizeModuleScore(DeepScanRun."HR Score");

        if Setup.Get('SETUP') then
            Setup.ApplyDefaults()
        else begin
            Setup.Init();
            Setup."Scan System Module" := true;
            Setup."Scan Finance Module" := true;
            Setup."Scan Sales Module" := true;
            Setup."Scan Purchasing Module" := true;
            Setup."Scan Inventory Module" := true;
            Setup."Scan CRM Module" := true;
            Setup."Scan Manufacturing Module" := true;
            Setup."Scan Service Module" := true;
            Setup."Scan Jobs Module" := true;
            Setup."Scan HR Module" := true;
        end;

        AddWeightedModuleScore(Setup."Scan System Module", 15, DeepScanRun."System Score", WeightedScoreTotal, EnabledWeightTotal);
        AddWeightedModuleScore(Setup."Scan Finance Module", 20, DeepScanRun."Finance Score", WeightedScoreTotal, EnabledWeightTotal);
        AddWeightedModuleScore(Setup."Scan Sales Module", 15, DeepScanRun."Sales Score", WeightedScoreTotal, EnabledWeightTotal);
        AddWeightedModuleScore(Setup."Scan Purchasing Module", 10, DeepScanRun."Purchasing Score", WeightedScoreTotal, EnabledWeightTotal);
        AddWeightedModuleScore(Setup."Scan Inventory Module", 15, DeepScanRun."Inventory Score", WeightedScoreTotal, EnabledWeightTotal);
        AddWeightedModuleScore(Setup."Scan CRM Module", 5, DeepScanRun."CRM Score", WeightedScoreTotal, EnabledWeightTotal);
        AddWeightedModuleScore(Setup."Scan Manufacturing Module", 10, DeepScanRun."Manufacturing Score", WeightedScoreTotal, EnabledWeightTotal);
        AddWeightedModuleScore(Setup."Scan Service Module", 5, DeepScanRun."Service Score", WeightedScoreTotal, EnabledWeightTotal);
        AddWeightedModuleScore(Setup."Scan Jobs Module", 3, DeepScanRun."Jobs Score", WeightedScoreTotal, EnabledWeightTotal);
        AddWeightedModuleScore(Setup."Scan HR Module", 2, DeepScanRun."HR Score", WeightedScoreTotal, EnabledWeightTotal);

        if EnabledWeightTotal > 0 then
            Score := (WeightedScoreTotal + (EnabledWeightTotal div 2)) div EnabledWeightTotal
        else
            Score := 100;

        DeepScanRun."Deep Score" := Score;
        DeepScanRun.Modify(true);
    end;

    local procedure ClearRunScoreMetrics(var DeepScanRun: Record "DH Deep Scan Run")
    begin
        DeepScanRun."Affected Records" := 0;
        DeepScanRun."System Score" := 0;
        DeepScanRun."Finance Score" := 0;
        DeepScanRun."Sales Score" := 0;
        DeepScanRun."Purchasing Score" := 0;
        DeepScanRun."Inventory Score" := 0;
        DeepScanRun."CRM Score" := 0;
        DeepScanRun."Manufacturing Score" := 0;
        DeepScanRun."Service Score" := 0;
        DeepScanRun."Jobs Score" := 0;
        DeepScanRun."HR Score" := 0;
    end;

    local procedure ResolveModuleFromCategory(Category: Code[30]): Text[30]
    begin
        case UpperCase(Format(Category)) of
            'SYSTEM':
                exit('System');
            'FINANCE', 'CUSTOMER', 'VENDOR', 'LEDGER':
                exit('Finance');
            'SALES':
                exit('Sales');
            'PURCHASE':
                exit('Purchasing');
            'INVENTORY', 'ITEM':
                exit('Inventory');
            'CRM':
                exit('CRM');
            'MANUFACTURING':
                exit('Manufacturing');
            'SERVICE':
                exit('Service');
            'JOB':
                exit('Jobs');
            'HR':
                exit('HR');
        end;

        exit('System');
    end;

    local procedure AddPenaltyToModule(var DeepScanRun: Record "DH Deep Scan Run"; ModuleName: Text[30]; PenaltyPoints: Integer)
    begin
        case ModuleName of
            'System':
                DeepScanRun."System Score" += PenaltyPoints;
            'Finance':
                DeepScanRun."Finance Score" += PenaltyPoints;
            'Sales':
                DeepScanRun."Sales Score" += PenaltyPoints;
            'Purchasing':
                DeepScanRun."Purchasing Score" += PenaltyPoints;
            'Inventory':
                DeepScanRun."Inventory Score" += PenaltyPoints;
            'CRM':
                DeepScanRun."CRM Score" += PenaltyPoints;
            'Manufacturing':
                DeepScanRun."Manufacturing Score" += PenaltyPoints;
            'Service':
                DeepScanRun."Service Score" += PenaltyPoints;
            'Jobs':
                DeepScanRun."Jobs Score" += PenaltyPoints;
            'HR':
                DeepScanRun."HR Score" += PenaltyPoints;
        end;
    end;

    local procedure GetSeverityPenalty(Severity: Code[20]): Integer
    begin
        case LowerCase(Format(Severity)) of
            'critical':
                exit(10);
            'high':
                exit(6);
            'medium':
                exit(3);
            'low':
                exit(1);
        end;

        exit(2);
    end;

    local procedure ResolveImpactSeverity(IssueCode: Code[50]; Severity: Code[20]; AffectedCount: Integer; PenaltyPoints: Integer): Code[20]
    var
        IssueCodeUpper: Text;
    begin
        IssueCodeUpper := UpperCase(Format(IssueCode));

        if LowerCase(Format(Severity)) <> 'high' then
            exit(Severity);

        if IsCriticalImpactIssue(IssueCodeUpper) then
            exit('critical');

        if (PenaltyPoints >= 7) and (AffectedCount >= 10) then
            exit('critical');

        if AffectedCount >= 1000 then
            exit('critical');

        exit(Severity);
    end;

    local procedure IsCriticalImpactIssue(IssueCodeUpper: Text): Boolean
    begin
        if StrPos(IssueCodeUpper, 'BLOCKED') > 0 then
            exit(true);
        if StrPos(IssueCodeUpper, 'OPEN_LEDGER') > 0 then
            exit(true);
        if StrPos(IssueCodeUpper, 'POSTING_GROUP') > 0 then
            exit(true);
        if StrPos(IssueCodeUpper, 'VAT_BUS_POSTING') > 0 then
            exit(true);
        if StrPos(IssueCodeUpper, 'NEGATIVE_INVENTORY') > 0 then
            exit(true);
        if StrPos(IssueCodeUpper, 'WITHOUT_UNIT_COST') > 0 then
            exit(true);
        if StrPos(IssueCodeUpper, 'INVENTORY_WITHOUT_UNIT_COST') > 0 then
            exit(true);
        if StrPos(IssueCodeUpper, 'PRICE_BELOW_UNIT_COST') > 0 then
            exit(true);
        if StrPos(IssueCodeUpper, 'DEAD_STOCK_365') > 0 then
            exit(true);
        if StrPos(IssueCodeUpper, 'MISSING_DIMENSIONS') > 0 then
            exit(true);
        if StrPos(IssueCodeUpper, 'LINES_MISSING_NO') > 0 then
            exit(true);
        if StrPos(IssueCodeUpper, 'ZERO_UNIT_PRICE') > 0 then
            exit(true);
        if StrPos(IssueCodeUpper, 'ZERO_UNIT_COST') > 0 then
            exit(true);

        exit(false);
    end;

    local procedure GetAffectedPenalty(AffectedCount: Integer): Integer
    begin
        if AffectedCount <= 0 then
            exit(0);
        if AffectedCount >= 5000 then
            exit(8);
        if AffectedCount >= 1000 then
            exit(6);
        if AffectedCount >= 250 then
            exit(4);
        if AffectedCount >= 50 then
            exit(2);
        exit(1);
    end;

    local procedure NormalizeModuleScore(PenaltyTotal: Integer): Integer
    begin
        if PenaltyTotal <= 0 then
            exit(100);

        exit(100 - ((PenaltyTotal * 100) div (PenaltyTotal + 40)));
    end;

    local procedure AddWeightedModuleScore(IsEnabled: Boolean; Weight: Integer; ModuleScore: Integer; var WeightedScoreTotal: Integer; var EnabledWeightTotal: Integer)
    begin
        if not IsEnabled then
            exit;

        WeightedScoreTotal += ModuleScore * Weight;
        EnabledWeightTotal += Weight;
    end;

    local procedure EnsureDashboardHeaderForDeepScan(var DeepScanRun: Record "DH Deep Scan Run")
    var
        ScanHeader: Record "DH Scan Header";
        Setup: Record "DH Setup";
    begin
        ScanHeader.Reset();
        ScanHeader.SetRange("Scan Type", ScanHeader."Scan Type"::Deep);
        ScanHeader.SetRange("Run ID", DeepScanRun."Run ID");

        if not ScanHeader.FindFirst() then begin
            ScanHeader.Reset();
            ScanHeader.SetRange("Scan Type", ScanHeader."Scan Type"::Deep);
            ScanHeader.SetRange("Backend Scan Id", DeepScanRun."Run ID");

            if not ScanHeader.FindFirst() then begin
                ScanHeader.Init();
                ScanHeader."Entry No." := GetNextHeaderEntryNo();
                ScanHeader."Scan Type" := ScanHeader."Scan Type"::Deep;
                ScanHeader."Run ID" := DeepScanRun."Run ID";
                ScanHeader."Backend Scan Id" := DeepScanRun."Run ID";
                ScanHeader.Insert();
            end;
        end;

        if ScanHeader."Run ID" = '' then
            ScanHeader."Run ID" := DeepScanRun."Run ID";

        if DeepScanRun."Finished At" <> 0DT then
            ScanHeader."Scan DateTime" := DeepScanRun."Finished At"
        else
            ScanHeader."Scan DateTime" := DeepScanRun."Requested At";

        ScanHeader."Data Score" := DeepScanRun."Deep Score";
        ScanHeader."Checks Count" := DeepScanRun."Checks Count";
        ScanHeader."Issues Count" := DeepScanRun."Issues Count";
        ScanHeader."Affected Records" := DeepScanRun."Affected Records";
        ScanHeader."System Score" := DeepScanRun."System Score";
        ScanHeader."Finance Score" := DeepScanRun."Finance Score";
        ScanHeader."Sales Score" := DeepScanRun."Sales Score";
        ScanHeader."Purchasing Score" := DeepScanRun."Purchasing Score";
        ScanHeader."Inventory Score" := DeepScanRun."Inventory Score";
        ScanHeader."CRM Score" := DeepScanRun."CRM Score";
        ScanHeader."Manufacturing Score" := DeepScanRun."Manufacturing Score";
        ScanHeader."Service Score" := DeepScanRun."Service Score";
        ScanHeader."Jobs Score" := DeepScanRun."Jobs Score";
        ScanHeader."HR Score" := DeepScanRun."HR Score";
        ScanHeader."Applied Exception Count" := DeepScanRun."Applied Exception Count";
        ScanHeader."Estimated Loss (EUR)" := DeepScanRun."Estimated Loss (EUR)";
        ScanHeader."Potential Saving (EUR)" := DeepScanRun."Potential Saving (EUR)";
        ScanHeader."Est. Loss" := DeepScanRun."Estimated Loss (EUR)";
        ScanHeader."Potential Saving" := DeepScanRun."Potential Saving (EUR)";
        ScanHeader."Total Records" := DeepScanRun."Total Records";
        ScanHeader."Est. Premium Price" := DeepScanRun."Est. Premium Price";
        ScanHeader."ROI" := DeepScanRun."ROI";
        ScanHeader."Headline" := CopyStr(DeepScanRun."Headline", 1, MaxStrLen(ScanHeader."Headline"));
        ScanHeader."Rating" := CopyStr(DeepScanRun."Rating", 1, MaxStrLen(ScanHeader."Rating"));
        if Setup.Get('SETUP') then
            ScanHeader."Premium Available" := IsPremiumAvailableForRun(Setup, DeepScanRun)
        else
            ScanHeader."Premium Available" := false;
        ScanHeader.Modify(true);
    end;

    local procedure ApplySyncCommercials(var DeepScanRun: Record "DH Deep Scan Run"; SyncResponseText: Text)
    var
        JsonObj: JsonObject;
        CommercialsToken: JsonToken;
        CommercialsObj: JsonObject;
        Token: JsonToken;
        ScanHeader: Record "DH Scan Header";
    begin
        if SyncResponseText = '' then
            exit;

        if not JsonObj.ReadFrom(SyncResponseText) then
            exit;

        if not JsonObj.Get('commercials', CommercialsToken) then
            exit;

        CommercialsObj := CommercialsToken.AsObject();

        if CommercialsObj.Get('estimated_loss_eur', Token) then
            DeepScanRun."Estimated Loss (EUR)" := ReadJsonDecimal(Token);

        if CommercialsObj.Get('potential_saving_eur', Token) then
            DeepScanRun."Potential Saving (EUR)" := ReadJsonDecimal(Token);

        if CommercialsObj.Get('total_records', Token) then
            DeepScanRun."Total Records" := Token.AsValue().AsInteger();

        if CommercialsObj.Get('premium_price_per_month', Token) then
            DeepScanRun."Est. Premium Price" := ReadJsonDecimal(Token)
        else
            if CommercialsObj.Get('estimated_premium_price_monthly', Token) then
                DeepScanRun."Est. Premium Price" := ReadJsonDecimal(Token);

        if CommercialsObj.Get('roi_eur', Token) then
            DeepScanRun."ROI" := ReadJsonDecimal(Token);

        DeepScanRun.Modify(true);

        ScanHeader.Reset();
        ScanHeader.SetRange("Scan Type", ScanHeader."Scan Type"::Deep);
        ScanHeader.SetRange("Run ID", DeepScanRun."Run ID");
        if not ScanHeader.FindFirst() then begin
            ScanHeader.Reset();
            ScanHeader.SetRange("Scan Type", ScanHeader."Scan Type"::Deep);
            ScanHeader.SetRange("Backend Scan Id", DeepScanRun."Run ID");
            if not ScanHeader.FindFirst() then
                exit;
        end;

        ScanHeader."Total Records" := DeepScanRun."Total Records";
        ScanHeader."Estimated Loss (EUR)" := DeepScanRun."Estimated Loss (EUR)";
        ScanHeader."Potential Saving (EUR)" := DeepScanRun."Potential Saving (EUR)";
        ScanHeader."Est. Loss" := DeepScanRun."Estimated Loss (EUR)";
        ScanHeader."Potential Saving" := DeepScanRun."Potential Saving (EUR)";
        ScanHeader."Est. Premium Price" := DeepScanRun."Est. Premium Price";
        ScanHeader."ROI" := DeepScanRun."ROI";

        ScanHeader.Modify(true);
    end;

    local procedure ApplySyncFindingImpacts(var DeepScanRun: Record "DH Deep Scan Run"; SyncResponseText: Text)
    var
        JsonObj: JsonObject;
        IssuesToken: JsonToken;
        IssuesArray: JsonArray;
        IssueToken: JsonToken;
        IssueObj: JsonObject;
        Finding: Record "DH Deep Scan Finding";
        i: Integer;
        CodeTxt: Text;
    begin
        if SyncResponseText = '' then
            exit;

        if not JsonObj.ReadFrom(SyncResponseText) then
            exit;

        if not JsonObj.Get('issues', IssuesToken) then
            exit;

        IssuesArray := IssuesToken.AsArray();

        for i := 0 to IssuesArray.Count() - 1 do begin
            IssuesArray.Get(i, IssueToken);
            IssueObj := IssueToken.AsObject();
            CodeTxt := GetJsonText(IssueObj, 'code');

            Finding.Reset();
            Finding.SetRange("Deep Scan Entry No.", DeepScanRun."Entry No.");
            Finding.SetRange("Issue Code", CopyStr(CodeTxt, 1, MaxStrLen(Finding."Issue Code")));
            if Finding.FindFirst() then begin
                if GetJsonText(IssueObj, 'severity') <> '' then begin
                    Finding.Severity := CopyStr(GetJsonText(IssueObj, 'severity'), 1, MaxStrLen(Finding.Severity));
                    Finding."Severity Sort Order" := GetSeveritySortOrder(Finding.Severity);
                end;
                Finding."Estimated Impact (EUR)" := ReadJsonDecimalFromObject(IssueObj, 'estimated_impact_eur');
                Finding.Modify(true);
            end;
        end;
    end;

    local procedure GetJsonText(var JsonObj: JsonObject; FieldName: Text): Text
    var
        Token: JsonToken;
    begin
        if JsonObj.Get(FieldName, Token) then
            if not IsJsonNull(Token) then
                exit(Token.AsValue().AsText());

        exit('');
    end;

    local procedure ReadJsonDecimalFromObject(var JsonObj: JsonObject; FieldName: Text): Decimal
    var
        Token: JsonToken;
    begin
        if JsonObj.Get(FieldName, Token) then
            if not IsJsonNull(Token) then
                exit(ReadJsonDecimal(Token));

        exit(0);
    end;

    local procedure ReadJsonDecimal(Token: JsonToken): Decimal
    var
        ValueText: Text;
        ValueDecimal: Decimal;
    begin
        if IsJsonNull(Token) then
            exit(0);

        ValueText := DelChr(Token.AsValue().AsText(), '=', ' ');
        if ValueText = '' then
            exit(0);

        // JSON uses invariant number formatting:
        // decimal separator = "."
        // no locale-dependent parsing here
        if Evaluate(ValueDecimal, ValueText, 9) then
            exit(ValueDecimal);

        // Fallback for already localized values, just in case
        if TryEvaluateDecimal(ValueText, ValueDecimal) then
            exit(ValueDecimal);

        Error(BackendDecimalInvalidErr, Token.AsValue().AsText());
    end;

    [TryFunction]
    local procedure TryEvaluateDecimal(ValueText: Text; var ValueDecimal: Decimal)
    begin
        Evaluate(ValueDecimal, ValueText);
    end;

    local procedure IsJsonNull(Token: JsonToken): Boolean
    var
        JsonValueText: Text;
    begin
        JsonValueText := LowerCase(Format(Token));
        exit((JsonValueText = 'null') or (JsonValueText = '<null>'));
    end;

    local procedure GetApiToken(var Setup: Record "DH Setup"): Text
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        exit(SecretMgt.GetApiToken(Setup));
    end;

    local procedure GetRunScanMode(var DeepScanRun: Record "DH Deep Scan Run"): Text
    begin
        if LowerCase(DeepScanRun."Scan Mode") = 'data_health_score' then
            exit('data_health_score');

        if LowerCase(DeepScanRun."Scan Mode") = 'monitoring' then
            exit('monitoring');

        exit('deep');
    end;

    local procedure IsDataHealthScoreRun(var DeepScanRun: Record "DH Deep Scan Run"): Boolean
    begin
        exit(GetRunScanMode(DeepScanRun) = 'data_health_score');
    end;

    local procedure GetRunningHeadline(var DeepScanRun: Record "DH Deep Scan Run"): Text
    begin
        if IsDataHealthScoreRun(DeepScanRun) then
            exit(DataHealthScoreRunningLbl);

        exit(ValidationCheckRunningLbl);
    end;

    local procedure GetStartedEventMessage(var DeepScanRun: Record "DH Deep Scan Run"): Text
    begin
        if IsDataHealthScoreRun(DeepScanRun) then
            exit(DataHealthScoreStartedLbl);

        exit(ValidationCheckStartedLbl);
    end;

    local procedure IsPremiumAvailableForRun(var Setup: Record "DH Setup"; var DeepScanRun: Record "DH Deep Scan Run"): Boolean
    begin
        if IsDataHealthScoreRun(DeepScanRun) then
            exit(false);

        exit(Setup."Premium Enabled");
    end;

    local procedure BuildSyncPayload(var Setup: Record "DH Setup"; var DeepScanRun: Record "DH Deep Scan Run"): Text
    var
        Finding: Record "DH Deep Scan Finding";
        Payload: JsonObject;
        IssuesArray: JsonArray;
        IssueObject: JsonObject;
        ScanDateTime: DateTime;
        RequestText: Text;
        DataProfilingMgt: Codeunit "DH Data Profiling Mgt.";
        ModuleScores: JsonObject;
        EnabledModules: JsonArray;
    begin
        if DeepScanRun."Finished At" <> 0DT then
            ScanDateTime := DeepScanRun."Finished At"
        else
            ScanDateTime := DeepScanRun."Requested At";

        Payload.Add('tenant_id', Setup."Tenant ID");
        Payload.Add('preferred_language', GetPreferredLanguage());
        Payload.Add('scan_id', Format(DeepScanRun."Run ID"));
        Payload.Add('bc_run_id', DeepScanRun."Run ID");
        Payload.Add('execution_token', Format(DeepScanRun."Execution Token"));
        Payload.Add('worker_id', Format(DeepScanRun."Client Request ID"));
        Payload.Add('correlation_id', DeepScanRun."Correlation ID");
        Payload.Add('scan_type', GetRunScanMode(DeepScanRun));
        Payload.Add('generated_at_utc', Format(ScanDateTime, 0, 9));
        Payload.Add('data_score', DeepScanRun."Deep Score");
        Payload.Add('checks_count', DeepScanRun."Checks Count");
        Payload.Add('issues_count', DeepScanRun."Issues Count");
        Payload.Add('applied_exception_count', DeepScanRun."Applied Exception Count");
        Payload.Add('premium_available', IsPremiumAvailableForRun(Setup, DeepScanRun));
        Payload.Add('data_profile', DataProfilingMgt.BuildDataProfile());

        ModuleScores.Add('system', DeepScanRun."System Score");
        ModuleScores.Add('finance', DeepScanRun."Finance Score");
        ModuleScores.Add('sales', DeepScanRun."Sales Score");
        ModuleScores.Add('purchasing', DeepScanRun."Purchasing Score");
        ModuleScores.Add('inventory', DeepScanRun."Inventory Score");
        ModuleScores.Add('crm', DeepScanRun."CRM Score");
        ModuleScores.Add('manufacturing', DeepScanRun."Manufacturing Score");
        ModuleScores.Add('service', DeepScanRun."Service Score");
        ModuleScores.Add('jobs', DeepScanRun."Jobs Score");
        ModuleScores.Add('hr', DeepScanRun."HR Score");
        Payload.Add('module_scores', ModuleScores);

        AddEnabledModules(Setup, EnabledModules);
        Payload.Add('enabled_modules', EnabledModules);

        Payload.Add('headline', DeepScanRun."Headline");
        Payload.Add('rating', DeepScanRun."Rating");

        Finding.Reset();
        Finding.SetRange("Deep Scan Entry No.", DeepScanRun."Entry No.");
        if Finding.FindSet() then
            repeat
                Clear(IssueObject);
                IssueObject.Add('code', Format(Finding."Issue Code"));
                IssueObject.Add('category', Format(Finding.Category));
                IssueObject.Add('title', Finding.Title);
                IssueObject.Add('severity', LowerCase(Format(Finding.Severity)));
                IssueObject.Add('affected_count', Finding."Affected Count");
                IssueObject.Add('premium_only', Finding."Premium Only");
                IssueObject.Add('recommendation_preview', Finding."Recommendation Preview");
                IssuesArray.Add(IssueObject);
            until Finding.Next() = 0;

        Payload.Add('issues', IssuesArray);
        Payload.WriteTo(RequestText);
        exit(RequestText);
    end;

    local procedure GetPreferredLanguage(): Text
    var
        LanguageId: Integer;
    begin
        LanguageId := GlobalLanguage();

        case LanguageId of
            1031, 2055, 3079, 4103, 5127:
                exit('de');
            else
                exit('en');
        end;
    end;

    local procedure AddEnabledModules(var Setup: Record "DH Setup"; var EnabledModules: JsonArray)
    begin
        if Setup."Scan System Module" then
            EnabledModules.Add('System');
        if Setup."Scan Finance Module" then
            EnabledModules.Add('Finance');
        if Setup."Scan Sales Module" then
            EnabledModules.Add('Sales');
        if Setup."Scan Purchasing Module" then
            EnabledModules.Add('Purchasing');
        if Setup."Scan Inventory Module" then
            EnabledModules.Add('Inventory');
        if Setup."Scan CRM Module" then
            EnabledModules.Add('CRM');
        if Setup."Scan Manufacturing Module" then
            EnabledModules.Add('Manufacturing');
        if Setup."Scan Service Module" then
            EnabledModules.Add('Service');
        if Setup."Scan Jobs Module" then
            EnabledModules.Add('Jobs');
        if Setup."Scan HR Module" then
            EnabledModules.Add('HR');
    end;

    local procedure InsertFinding(DeepScanEntryNo: Integer; Category: Code[30]; IssueCode: Code[50]; Severity: Code[20]; AffectedCount: Integer)
    var
        Finding: Record "DH Deep Scan Finding";
    begin
        Finding.Init();
        Finding."Entry No." := GetNextFindingEntryNo();
        Finding."Deep Scan Entry No." := DeepScanEntryNo;
        Finding.Category := Category;
        Finding."Issue Code" := IssueCode;
        Finding.Title := CopyStr(IssueCode, 1, MaxStrLen(Finding.Title));
        Finding.Severity := Severity;
        Finding."Severity Sort Order" := GetSeveritySortOrder(Finding.Severity);
        Finding."Affected Count" := AffectedCount;
        Finding."Affected Count Sort Value" := -AffectedCount;
        Finding."Recommendation Preview" := CopyStr(IssueCode, 1, MaxStrLen(Finding."Recommendation Preview"));
        Finding."Premium Only" := true;
        Finding."Estimated Impact (EUR)" := 0;
        Finding.Insert(true);
    end;

    local procedure ClearDeepScanCommercials(var DeepScanRun: Record "DH Deep Scan Run")
    begin
        DeepScanRun."Estimated Loss (EUR)" := 0;
        DeepScanRun."Potential Saving (EUR)" := 0;
    end;

    local procedure FindingExists(DeepScanEntryNo: Integer; IssueCode: Code[50]; ValueMarker: Text): Boolean
    var
        Finding: Record "DH Deep Scan Finding";
    begin
        Finding.SetRange("Deep Scan Entry No.", DeepScanEntryNo);
        Finding.SetRange("Issue Code", IssueCode);
        Finding.SetFilter(Title, '*%1*', ValueMarker);
        exit(not Finding.IsEmpty());
    end;

    local procedure GetNextFindingEntryNo(): Integer
    var
        Finding: Record "DH Deep Scan Finding";
    begin
        if Finding.FindLast() then
            exit(Finding."Entry No." + 1);

        exit(1);
    end;

    local procedure GetNextHeaderEntryNo(): Integer
    var
        ScanHeader: Record "DH Scan Header";
    begin
        if ScanHeader.FindLast() then
            exit(ScanHeader."Entry No." + 1);

        exit(1);
    end;

    local procedure GetRating(Score: Integer): Text
    begin
        if Score >= 90 then
            exit('good');

        if Score >= 75 then
            exit('fair');

        exit('critical');
    end;

    local procedure GetHeadline(Score: Integer; IssuesCount: Integer): Text
    begin
        if IssuesCount = 0 then
            exit(ScanCompletedWithoutFindingsLbl);

        if Score >= 90 then
            exit(ScanCompletedMinorFindingsLbl);

        if Score >= 75 then
            exit(ScanCompletedImprovementPotentialLbl);

        exit(ScanCompletedCriticalFindingsLbl);
    end;


    local procedure GetSeveritySortOrder(SeverityValue: Code[20]): Integer
    begin
        case LowerCase(SeverityValue) of
            'critical':
                exit(0);
            'high':
                exit(1);
            'medium':
                exit(2);
            'low':
                exit(3);
        end;

        exit(99);
    end;

    var
        ExceptionMgt: Codeunit "DH Exception Mgt.";
        BackendDecimalInvalidErr: Label 'The decimal value from the backend response could not be parsed: %1', Comment = '%1 = backend value';
        DataHealthScoreRunningLbl: Label 'Data Health Score is running';
        DataHealthScoreStartedLbl: Label 'Data Health Score started';
        DuplicateCustomerAddressLbl: Label 'Multiple customers with the same name, post code, and city: %1 | %2 %3', Comment = '%1 = customer name, %2 = post code, %3 = city';
        DuplicateCustomerEmailLbl: Label 'Multiple customers with the same email: %1', Comment = '%1 = email address';
        DuplicateCustomerVatNoLbl: Label 'Multiple customers with the same VAT registration number: %1', Comment = '%1 = VAT registration number';
        DuplicateVendorAddressLbl: Label 'Multiple vendors with the same name, post code, and city: %1 | %2 %3', Comment = '%1 = vendor name, %2 = post code, %3 = city';
        DuplicateVendorEmailLbl: Label 'Multiple vendors with the same email: %1', Comment = '%1 = email address';
        DuplicateVendorVatNoLbl: Label 'Multiple vendors with the same VAT registration number: %1', Comment = '%1 = VAT registration number';
        LocalCompleteSyncFailedLbl: Label 'Scan completed locally; backend synchronization failed.';
        PostprocessingRefreshFailedLbl: Label 'The scan completed, but local postprocessing could not be refreshed. Refresh the scan status later.';
        ScanCompletedCriticalFindingsLbl: Label 'Validation Check completed with critical findings.';
        ScanCompletedImprovementPotentialLbl: Label 'Validation Check completed with relevant improvement potential.';
        ScanCompletedMinorFindingsLbl: Label 'Validation Check completed with minor findings.';
        ScanCompletedWithoutFindingsLbl: Label 'Validation Check completed without findings.';
        SetupMissingForPersistenceErr: Label 'The scan result could not be saved because BCSentinel setup is missing.';
        SyncUnexpectedFailureLbl: Label 'The local scan completed, but backend synchronization failed unexpectedly. Your local findings were preserved.';
        ValidationCheckRunningLbl: Label 'Validation Check is running';
        ValidationCheckStartedLbl: Label 'Validation Check started';
}
