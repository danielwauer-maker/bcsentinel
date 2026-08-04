codeunit 53196 "DH Scan Check Mgt."
{
    var
        MonitoringRequiredErr: Label 'Selecting individual checks is only available with active Monitoring.';
        NoChecksEnabledErr: Label 'At least one scan check must be enabled before starting a Monitoring scan.';

    procedure EnsureMonitoringAccess(RefreshLicense: Boolean)
    var
        Setup: Record "DH Setup";
        ApiClient: Codeunit "DH API Client";
    begin
        if not Setup.Get('SETUP') then
            Error(MonitoringRequiredErr);

        if RefreshLicense and (Setup."Tenant ID" <> '') then begin
            ApiClient.RefreshLicenseStatus(Setup);
            Setup.Get('SETUP');
        end;

        if not Setup."Monitoring Active" then
            Error(MonitoringRequiredErr);
    end;

    procedure EnsureDefaultChecks()
    begin
        AddCheck('CUSTOMERS_DUPLICATE_EMAIL', 'CUSTOMER', 'high', 10);
        AddCheck('VENDORS_DUPLICATE_EMAIL', 'VENDOR', 'high', 20);
        AddCheck('CUSTOMERS_DUPLICATE_VAT', 'CUSTOMER', 'high', 30);
        AddCheck('VENDORS_DUPLICATE_VAT', 'VENDOR', 'high', 40);
        AddCheck('CUSTOMERS_DUPLICATE_NAME_POST_CITY', 'CUSTOMER', 'high', 50);
        AddCheck('VENDORS_DUPLICATE_NAME_POST_CITY', 'VENDOR', 'high', 60);
        AddCheck('CUSTOMERS_MISSING_NAME', 'CUSTOMER', 'high', 70);
        AddCheck('CUSTOMERS_MISSING_SEARCH_NAME', 'CUSTOMER', 'low', 80);
        AddCheck('CUSTOMERS_MISSING_ADDRESS', 'CUSTOMER', 'high', 90);
        AddCheck('CUSTOMERS_MISSING_CITY', 'CUSTOMER', 'medium', 100);
        AddCheck('CUSTOMERS_MISSING_POST_CODE', 'CUSTOMER', 'medium', 110);
        AddCheck('CUSTOMERS_MISSING_COUNTRY', 'CUSTOMER', 'medium', 120);
        AddCheck('CUSTOMERS_MISSING_EMAIL', 'CUSTOMER', 'medium', 130);
        AddCheck('CUSTOMERS_MISSING_PHONE', 'CUSTOMER', 'low', 140);
        AddCheck('CUSTOMERS_MISSING_PAYMENT_TERMS', 'CUSTOMER', 'high', 150);
        AddCheck('CUSTOMERS_MISSING_PAYMENT_METHOD', 'CUSTOMER', 'medium', 160);
        AddCheck('CUSTOMERS_MISSING_POSTING_GROUP', 'CUSTOMER', 'high', 170);
        AddCheck('CUSTOMERS_MISSING_GEN_BUS_POSTING', 'CUSTOMER', 'high', 180);
        AddCheck('CUSTOMERS_MISSING_VAT_BUS_POSTING', 'CUSTOMER', 'high', 190);
        AddCheck('CUSTOMERS_MISSING_CREDIT_LIMIT', 'CUSTOMER', 'low', 200);
        AddCheck('BLOCKED_CUSTOMERS_WITH_OPEN_SALES_DOCS', 'CUSTOMER', 'high', 210);
        AddCheck('BLOCKED_CUSTOMERS_WITH_OPEN_LEDGER', 'CUSTOMER', 'high', 220);
        AddCheck('VENDORS_MISSING_NAME', 'VENDOR', 'high', 230);
        AddCheck('VENDORS_MISSING_SEARCH_NAME', 'VENDOR', 'low', 240);
        AddCheck('VENDORS_MISSING_ADDRESS', 'VENDOR', 'high', 250);
        AddCheck('VENDORS_MISSING_CITY', 'VENDOR', 'medium', 260);
        AddCheck('VENDORS_MISSING_POST_CODE', 'VENDOR', 'medium', 270);
        AddCheck('VENDORS_MISSING_COUNTRY', 'VENDOR', 'medium', 280);
        AddCheck('VENDORS_MISSING_EMAIL', 'VENDOR', 'medium', 290);
        AddCheck('VENDORS_MISSING_PHONE', 'VENDOR', 'low', 300);
        AddCheck('VENDORS_MISSING_PAYMENT_TERMS', 'VENDOR', 'high', 310);
        AddCheck('VENDORS_MISSING_PAYMENT_METHOD', 'VENDOR', 'medium', 320);
        AddCheck('VENDORS_MISSING_POSTING_GROUP', 'VENDOR', 'high', 330);
        AddCheck('VENDORS_MISSING_GEN_BUS_POSTING', 'VENDOR', 'high', 340);
        AddCheck('VENDORS_MISSING_VAT_BUS_POSTING', 'VENDOR', 'high', 350);
        AddCheck('VENDORS_MISSING_BANK_ACCOUNT', 'VENDOR', 'medium', 360);
        AddCheck('BLOCKED_VENDORS_WITH_OPEN_PURCHASE_DOCS', 'VENDOR', 'high', 370);
        AddCheck('BLOCKED_VENDORS_WITH_OPEN_LEDGER', 'VENDOR', 'high', 380);
        AddCheck('ITEMS_MISSING_DESCRIPTION', 'ITEM', 'high', 390);
        AddCheck('ITEMS_MISSING_BASE_UOM', 'ITEM', 'high', 400);
        AddCheck('ITEMS_MISSING_CATEGORY', 'ITEM', 'medium', 410);
        AddCheck('ITEMS_MISSING_GEN_PROD_POSTING', 'ITEM', 'high', 420);
        AddCheck('ITEMS_MISSING_INVENTORY_POSTING', 'ITEM', 'high', 430);
        AddCheck('ITEMS_WITHOUT_VENDOR_NO', 'ITEM', 'medium', 440);
        AddCheck('ITEMS_WITHOUT_UNIT_COST', 'ITEM', 'high', 450);
        AddCheck('ITEMS_WITHOUT_UNIT_PRICE', 'ITEM', 'medium', 460);
        AddCheck('ITEMS_NEGATIVE_INVENTORY', 'ITEM', 'high', 470);
        AddCheck('BLOCKED_ITEMS_WITH_INVENTORY', 'ITEM', 'medium', 480);
        AddCheck('SALES_ORDERS_MISSING_SHIPMENT_DATE', 'SALES', 'medium', 490);
        AddCheck('SALES_ORDERS_OLD_OPEN', 'SALES', 'medium', 500);
        AddCheck('SALES_LINES_MISSING_NO', 'SALES', 'high', 510);
        AddCheck('SALES_LINES_ZERO_QUANTITY', 'SALES', 'medium', 520);
        AddCheck('SALES_LINES_ZERO_PRICE', 'SALES', 'high', 530);
        AddCheck('SALES_LINES_MISSING_DIMENSIONS', 'SALES', 'high', 540);
        AddCheck('SALES_DOCS_WITH_BLOCKED_CUSTOMERS', 'SALES', 'high', 550);
        AddCheck('SALES_LINES_WITH_BLOCKED_ITEMS', 'SALES', 'high', 560);
        AddCheck('PURCHASE_ORDERS_MISSING_EXPECTED_DATE', 'PURCHASE', 'medium', 570);
        AddCheck('PURCHASE_ORDERS_OLD_OPEN', 'PURCHASE', 'medium', 580);
        AddCheck('PURCHASE_LINES_MISSING_NO', 'PURCHASE', 'high', 590);
        AddCheck('PURCHASE_LINES_ZERO_QUANTITY', 'PURCHASE', 'medium', 600);
        AddCheck('PURCHASE_LINES_ZERO_COST', 'PURCHASE', 'high', 610);
        AddCheck('PURCHASE_LINES_MISSING_DIMENSIONS', 'PURCHASE', 'high', 620);
        AddCheck('PURCHASE_DOCS_WITH_BLOCKED_VENDORS', 'PURCHASE', 'high', 630);
        AddCheck('PURCHASE_LINES_WITH_BLOCKED_ITEMS', 'PURCHASE', 'high', 640);
        AddCheck('CUSTOMER_LEDGER_OVERDUE_30', 'LEDGER', 'high', 650);
        AddCheck('VENDOR_LEDGER_OVERDUE_30', 'LEDGER', 'medium', 660);
        AddCheck('GL_ENTRIES_MISSING_DIM1', 'SYSTEM', 'medium', 670);
        AddCheck('GL_ENTRIES_MISSING_DIM2', 'SYSTEM', 'medium', 680);
        AddCheck('GL_ENTRIES_MISSING_BOTH_DIMS', 'SYSTEM', 'high', 690);
        AddCheck('GL_ACCOUNTS_BLOCKED_BUT_USED', 'SYSTEM', 'high', 700);
        AddCheck('GL_ACCOUNTS_NO_DIRECT_POSTING_BUT_USED', 'SYSTEM', 'medium', 710);
        AddCheck('SYSTEM_CUSTOMERS_MISSING_GEN_BUS_POSTING', 'SYSTEM', 'high', 720);
        AddCheck('SYSTEM_CUSTOMERS_MISSING_VAT_BUS_POSTING', 'SYSTEM', 'high', 730);
        AddCheck('SYSTEM_VENDORS_MISSING_GEN_BUS_POSTING', 'SYSTEM', 'high', 740);
        AddCheck('SYSTEM_VENDORS_MISSING_VAT_BUS_POSTING', 'SYSTEM', 'high', 750);
        AddCheck('SYSTEM_ITEMS_MISSING_GEN_PROD_POSTING', 'SYSTEM', 'high', 760);
        AddCheck('SYSTEM_ITEMS_MISSING_INVENTORY_POSTING', 'SYSTEM', 'high', 770);
        AddCheck('CUSTOMER_LEDGER_MISSING_DUE_DATE', 'SYSTEM', 'medium', 780);
        AddCheck('VENDOR_LEDGER_MISSING_DUE_DATE', 'SYSTEM', 'medium', 790);
        AddCheck('CUSTOMERS_MISSING_VAT_REG_NO', 'FINANCE', 'medium', 800);
        AddCheck('CUSTOMERS_MISSING_SALESPERSON', 'FINANCE', 'low', 810);
        AddCheck('CUSTOMERS_MISSING_PRICE_GROUP', 'FINANCE', 'medium', 820);
        AddCheck('CUSTOMERS_MISSING_DISC_GROUP', 'FINANCE', 'medium', 830);
        AddCheck('CUSTOMERS_MISSING_REMINDER_TERMS', 'FINANCE', 'medium', 840);
        AddCheck('CUSTOMERS_MISSING_FIN_CHARGE_TERMS', 'FINANCE', 'low', 850);
        AddCheck('CUSTOMERS_MISSING_CONTACT', 'FINANCE', 'low', 860);
        AddCheck('CUSTOMERS_MISSING_HOME_PAGE', 'FINANCE', 'low', 870);
        AddCheck('VENDORS_MISSING_VAT_REG_NO', 'FINANCE', 'medium', 880);
        AddCheck('VENDORS_MISSING_PURCHASER', 'FINANCE', 'low', 890);
        AddCheck('VENDORS_MISSING_CONTACT', 'FINANCE', 'low', 900);
        AddCheck('VENDORS_MISSING_HOME_PAGE', 'FINANCE', 'low', 910);
        AddCheck('CUSTOMER_LEDGER_OVERDUE_60', 'FINANCE', 'high', 920);
        AddCheck('CUSTOMER_LEDGER_OVERDUE_90', 'FINANCE', 'high', 930);
        AddCheck('VENDOR_LEDGER_OVERDUE_60', 'FINANCE', 'medium', 940);
        AddCheck('VENDOR_LEDGER_OVERDUE_90', 'FINANCE', 'medium', 950);
        AddCheck('SALES_HEADERS_MISSING_PAYMENT_TERMS', 'SALES', 'medium', 960);
        AddCheck('SALES_HEADERS_MISSING_PAYMENT_METHOD', 'SALES', 'medium', 970);
        AddCheck('SALES_HEADERS_MISSING_REQUESTED_DELIVERY_DATE', 'SALES', 'medium', 980);
        AddCheck('SALES_HEADERS_MISSING_SHIPMENT_METHOD', 'SALES', 'low', 990);
        AddCheck('SALES_HEADERS_MISSING_EXTERNAL_DOC_NO', 'SALES', 'low', 1000);
        AddCheck('SALES_HEADERS_PAST_REQUESTED_DELIVERY_DATE', 'SALES', 'high', 1010);
        AddCheck('SALES_LINES_DISCOUNT_OVER_25', 'SALES', 'medium', 1020);
        AddCheck('SALES_LINES_DISCOUNT_OVER_50', 'SALES', 'high', 1030);
        AddCheck('SALES_LINES_PRICE_BELOW_UNIT_COST', 'SALES', 'high', 1040);
        AddCheck('SALES_LINES_SHIPPED_NOT_INVOICED', 'SALES', 'high', 1050);
        AddCheck('SALES_LINES_OUTSTANDING_PAST_SHIPMENT_DATE', 'SALES', 'medium', 1060);
        AddCheck('SALES_LINES_MISSING_DESCRIPTION', 'SALES', 'low', 1070);
        AddCheck('SALES_LINES_MISSING_LOCATION', 'SALES', 'medium', 1080);
        AddCheck('PURCHASE_HEADERS_MISSING_PAYMENT_TERMS', 'PURCHASE', 'medium', 1090);
        AddCheck('PURCHASE_HEADERS_MISSING_PAYMENT_METHOD', 'PURCHASE', 'medium', 1100);
        AddCheck('PURCHASE_HEADERS_MISSING_PURCHASER', 'PURCHASE', 'low', 1110);
        AddCheck('PURCHASE_HEADERS_MISSING_VENDOR_INVOICE_NO', 'PURCHASE', 'low', 1120);
        AddCheck('PURCHASE_HEADERS_PAST_EXPECTED_RECEIPT_DATE', 'PURCHASE', 'high', 1130);
        AddCheck('PURCHASE_LINES_DISCOUNT_OVER_25', 'PURCHASE', 'low', 1140);
        AddCheck('PURCHASE_LINES_DISCOUNT_OVER_50', 'PURCHASE', 'medium', 1150);
        AddCheck('PURCHASE_LINES_RECEIVED_NOT_INVOICED', 'PURCHASE', 'medium', 1160);
        AddCheck('PURCHASE_LINES_OUTSTANDING_PAST_RECEIPT_DATE', 'PURCHASE', 'medium', 1170);
        AddCheck('PURCHASE_LINES_MISSING_DESCRIPTION', 'PURCHASE', 'low', 1180);
        AddCheck('PURCHASE_LINES_MISSING_LOCATION', 'PURCHASE', 'medium', 1190);
        AddCheck('PURCHASE_LINES_COST_BELOW_LAST_DIRECT_COST', 'PURCHASE', 'low', 1200);
        AddCheck('ITEMS_PRICE_BELOW_UNIT_COST', 'INVENTORY', 'high', 1210);
        AddCheck('ITEMS_PRICE_BELOW_STANDARD_COST', 'INVENTORY', 'high', 1220);
        AddCheck('ITEMS_STANDARD_COST_ZERO', 'INVENTORY', 'medium', 1230);
        AddCheck('ITEMS_LAST_DIRECT_COST_ZERO', 'INVENTORY', 'medium', 1240);
        AddCheck('ITEMS_MISSING_LEAD_TIME', 'INVENTORY', 'medium', 1250);
        AddCheck('ITEMS_SAFETY_STOCK_ZERO', 'INVENTORY', 'low', 1260);
        AddCheck('ITEMS_REORDER_POINT_ZERO', 'INVENTORY', 'low', 1270);
        AddCheck('ITEMS_MAX_INVENTORY_ZERO', 'INVENTORY', 'low', 1280);
        AddCheck('ITEMS_MIN_ORDER_QTY_ZERO', 'INVENTORY', 'low', 1290);
        AddCheck('ITEMS_ORDER_MULTIPLE_ZERO', 'INVENTORY', 'low', 1300);
        AddCheck('ITEMS_MISSING_SHELF_NO', 'INVENTORY', 'low', 1310);
        AddCheck('ITEMS_MISSING_TARIFF_NO', 'INVENTORY', 'low', 1320);
        AddCheck('ITEMS_GROSS_WEIGHT_ZERO', 'INVENTORY', 'low', 1330);
        AddCheck('ITEMS_NET_WEIGHT_ZERO', 'INVENTORY', 'low', 1340);
        AddCheck('ITEMS_UNIT_VOLUME_ZERO', 'INVENTORY', 'low', 1350);
        AddCheck('DEAD_STOCK_90', 'INVENTORY', 'medium', 1360);
        AddCheck('DEAD_STOCK_180', 'INVENTORY', 'medium', 1370);
        AddCheck('DEAD_STOCK_365', 'INVENTORY', 'high', 1380);
        AddCheck('INVENTORY_WITHOUT_UNIT_COST', 'INVENTORY', 'high', 1390);
        AddCheck('CONTACTS_MISSING_NAME', 'CRM', 'medium', 1400);
        AddCheck('CONTACTS_MISSING_EMAIL', 'CRM', 'medium', 1410);
        AddCheck('CONTACTS_MISSING_PHONE', 'CRM', 'low', 1420);
        AddCheck('CONTACTS_MISSING_MOBILE_PHONE', 'CRM', 'low', 1430);
        AddCheck('CONTACTS_PERSONS_MISSING_COMPANY', 'CRM', 'medium', 1440);
        AddCheck('CONTACTS_MISSING_ADDRESS', 'CRM', 'low', 1450);
        AddCheck('CONTACTS_MISSING_CITY', 'CRM', 'low', 1460);
        AddCheck('CONTACTS_MISSING_POST_CODE', 'CRM', 'low', 1470);
        AddCheck('CONTACTS_MISSING_COUNTRY', 'CRM', 'low', 1480);
        AddCheck('MFG_BOM_MISSING_DESCRIPTION', 'MANUFACTURING', 'medium', 1490);
        AddCheck('MFG_BOM_NOT_CERTIFIED', 'MANUFACTURING', 'high', 1500);
        AddCheck('MFG_BOM_LINES_MISSING_NO', 'MANUFACTURING', 'high', 1510);
        AddCheck('MFG_BOM_LINES_ZERO_QTY', 'MANUFACTURING', 'high', 1520);
        AddCheck('MFG_ROUTING_MISSING_DESCRIPTION', 'MANUFACTURING', 'low', 1530);
        AddCheck('MFG_ROUTING_NOT_CERTIFIED', 'MANUFACTURING', 'high', 1540);
        AddCheck('MFG_ROUTING_LINES_MISSING_NO', 'MANUFACTURING', 'high', 1550);
        AddCheck('MFG_ROUTING_LINES_ZERO_SETUP', 'MANUFACTURING', 'medium', 1560);
        AddCheck('MFG_ROUTING_LINES_ZERO_RUN', 'MANUFACTURING', 'high', 1570);
        AddCheck('MFG_WORK_CENTERS_BLOCKED', 'MANUFACTURING', 'medium', 1580);
        AddCheck('MFG_WORK_CENTERS_MISSING_NAME', 'MANUFACTURING', 'low', 1590);
        AddCheck('MFG_WORK_CENTERS_ZERO_COST', 'MANUFACTURING', 'medium', 1600);
        AddCheck('MFG_MACHINE_CENTERS_BLOCKED', 'MANUFACTURING', 'medium', 1610);
        AddCheck('MFG_MACHINE_CENTERS_MISSING_NAME', 'MANUFACTURING', 'low', 1620);
        AddCheck('MFG_MACHINE_CENTERS_ZERO_COST', 'MANUFACTURING', 'medium', 1630);
        AddCheck('MFG_ITEMS_MISSING_PROD_BOM_NO', 'MANUFACTURING', 'high', 1640);
        AddCheck('MFG_ITEMS_MISSING_ROUTING_NO', 'MANUFACTURING', 'high', 1650);
        AddCheck('SERVICE_ITEMS_MISSING_DESCRIPTION', 'SERVICE', 'medium', 1660);
        AddCheck('SERVICE_ITEMS_MISSING_CUSTOMER', 'SERVICE', 'high', 1670);
        AddCheck('SERVICE_ITEMS_MISSING_ITEM_NO', 'SERVICE', 'high', 1680);
        AddCheck('SERVICE_ITEMS_MISSING_SERIAL_NO', 'SERVICE', 'medium', 1690);
        AddCheck('SERVICE_ORDERS_MISSING_CUSTOMER', 'SERVICE', 'high', 1700);
        AddCheck('SERVICE_ORDERS_MISSING_BILL_TO', 'SERVICE', 'high', 1710);
        AddCheck('SERVICE_ORDERS_MISSING_DESCRIPTION', 'SERVICE', 'medium', 1720);
        AddCheck('SERVICE_ORDERS_MISSING_ASSIGNED_USER', 'SERVICE', 'medium', 1730);
        AddCheck('SERVICE_LINES_MISSING_NO', 'SERVICE', 'high', 1740);
        AddCheck('SERVICE_LINES_MISSING_DESCRIPTION', 'SERVICE', 'medium', 1750);
        AddCheck('SERVICE_LINES_ZERO_QTY', 'SERVICE', 'medium', 1760);
        AddCheck('SERVICE_LINES_ZERO_UNIT_PRICE', 'SERVICE', 'high', 1770);
        AddCheck('JOBS_MISSING_DESCRIPTION', 'JOB', 'medium', 1780);
        AddCheck('JOBS_MISSING_BILL_TO_CUSTOMER', 'JOB', 'high', 1790);
        AddCheck('JOBS_MISSING_RESPONSIBLE', 'JOB', 'medium', 1800);
        AddCheck('JOBS_MISSING_POSTING_GROUP', 'JOB', 'high', 1810);
        AddCheck('JOB_TASKS_MISSING_DESCRIPTION', 'JOB', 'medium', 1820);
        AddCheck('JOB_PLANNING_LINES_MISSING_NO', 'JOB', 'high', 1830);
        AddCheck('JOB_PLANNING_LINES_MISSING_DESCRIPTION', 'JOB', 'medium', 1840);
        AddCheck('JOB_PLANNING_LINES_ZERO_QTY', 'JOB', 'medium', 1850);
        AddCheck('JOB_PLANNING_LINES_ZERO_UNIT_COST', 'JOB', 'high', 1860);
        AddCheck('JOB_PLANNING_LINES_ZERO_UNIT_PRICE', 'JOB', 'high', 1870);
        AddCheck('EMPLOYEES_MISSING_FIRST_NAME', 'HR', 'low', 1880);
        AddCheck('EMPLOYEES_MISSING_LAST_NAME', 'HR', 'medium', 1890);
        AddCheck('EMPLOYEES_MISSING_SEARCH_NAME', 'HR', 'low', 1900);
        AddCheck('EMPLOYEES_MISSING_EMAIL', 'HR', 'medium', 1910);
        AddCheck('EMPLOYEES_MISSING_PHONE', 'HR', 'low', 1920);
        AddCheck('EMPLOYEES_MISSING_COUNTRY', 'HR', 'low', 1930);
        AddCheck('EMPLOYEES_MISSING_RESOURCE_NO', 'HR', 'medium', 1940);
        AddCheck('EMPLOYEES_MISSING_JOB_TITLE', 'HR', 'low', 1950);
        AddCheck('RESOURCES_MISSING_NAME', 'HR', 'medium', 1960);
        AddCheck('RESOURCES_ZERO_UNIT_COST', 'HR', 'medium', 1970);
        AddCheck('RESOURCES_ZERO_UNIT_PRICE', 'HR', 'medium', 1980);
        AddCheck('RESOURCES_MISSING_BASE_UOM', 'HR', 'low', 1990);
    end;

    procedure EnableAll()
    var
        ScanCheck: Record "DH Scan Check Selection";
    begin
        EnsureDefaultChecks();
        if ScanCheck.FindSet(true) then
            repeat
                ScanCheck.Enabled := true;
                ScanCheck.Modify(true);
            until ScanCheck.Next() = 0;
    end;

    procedure DisableAll()
    var
        ScanCheck: Record "DH Scan Check Selection";
    begin
        EnsureDefaultChecks();
        if ScanCheck.FindSet(true) then
            repeat
                ScanCheck.Enabled := false;
                ScanCheck.Modify(true);
            until ScanCheck.Next() = 0;
    end;

    procedure RestoreDefaults()
    var
        ScanCheck: Record "DH Scan Check Selection";
    begin
        EnsureDefaultChecks();
        if ScanCheck.FindSet(true) then
            repeat
                ScanCheck.Enabled := ScanCheck."Default Enabled";
                ScanCheck.Modify(true);
            until ScanCheck.Next() = 0;
    end;

    procedure HasEnabledChecks(): Boolean
    var
        ScanCheck: Record "DH Scan Check Selection";
    begin
        EnsureDefaultChecks();
        ScanCheck.SetRange(Enabled, true);
        exit(not ScanCheck.IsEmpty());
    end;

    procedure GetExpectedChecksCount(var Setup: Record "DH Setup"): Integer
    var
        ScanCheck: Record "DH Scan Check Selection";
        Count: Integer;
    begin
        EnsureDefaultChecks();
        if ScanCheck.FindSet() then
            repeat
                if IsModuleIncluded(Setup, ScanCheck."Module") then
                    if (not Setup."Monitoring Active") or ScanCheck.Enabled then
                        Count += 1;
            until ScanCheck.Next() = 0;

        exit(Count);
    end;

    procedure GetTotalModuleChecksCount(var Setup: Record "DH Setup"): Integer
    var
        ScanCheck: Record "DH Scan Check Selection";
        Count: Integer;
    begin
        EnsureDefaultChecks();
        if ScanCheck.FindSet() then
            repeat
                if IsModuleIncluded(Setup, ScanCheck."Module") then
                    Count += 1;
            until ScanCheck.Next() = 0;

        exit(Count);
    end;

    procedure BuildCheckSelectionEventText(var Setup: Record "DH Setup"): Text[250]
    var
        ActiveChecks: Integer;
        SkippedChecks: Integer;
        TotalChecks: Integer;
        ActiveChecksLoadedTxt: Label 'Active checks loaded: %1';
        ActiveAndSkippedChecksLoadedTxt: Label 'Active checks loaded: %1 | Skipped checks: %2';
    begin
        TotalChecks := GetTotalModuleChecksCount(Setup);
        ActiveChecks := GetExpectedChecksCount(Setup);
        SkippedChecks := TotalChecks - ActiveChecks;
        if SkippedChecks < 0 then
            SkippedChecks := 0;

        if Setup."Monitoring Active" then
            exit(CopyStr(StrSubstNo(ActiveAndSkippedChecksLoadedTxt, ActiveChecks, SkippedChecks), 1, 250));

        exit(CopyStr(StrSubstNo(ActiveChecksLoadedTxt, ActiveChecks), 1, 250));
    end;

    procedure RequireEnabledChecksForMonitoring()
    var
        Setup: Record "DH Setup";
    begin
        if not Setup.Get('SETUP') then
            exit;

        if not Setup."Monitoring Active" then
            exit;

        if not HasEnabledChecks() then
            Error(NoChecksEnabledErr);
    end;

    procedure IsCheckEnabled(CheckCode: Code[50]): Boolean
    var
        Setup: Record "DH Setup";
        ScanCheck: Record "DH Scan Check Selection";
    begin
        if not Setup.Get('SETUP') then
            exit(true);

        if not Setup."Monitoring Active" then
            exit(true);

        if not ScanCheck.Get(CheckCode) then
            exit(true);

        exit(ScanCheck.Enabled);
    end;

    procedure UpdateLastRun(CheckCode: Code[50]; FindingCount: Integer)
    var
        Setup: Record "DH Setup";
        ScanCheck: Record "DH Scan Check Selection";
    begin
        if not Setup.Get('SETUP') then
            exit;
        if not Setup."Monitoring Active" then
            exit;
        if not ScanCheck.Get(CheckCode) then
            exit;

        ScanCheck."Last Run At" := CurrentDateTime();
        ScanCheck."Last Finding Count" := FindingCount;
        ScanCheck.Modify(true);
    end;

    procedure GetLocalizedModule(ModuleName: Text[100]): Text[100]
    begin
        case UpperCase(ModuleName) of
            'CUSTOMER':
                exit(CustomerModuleLbl);
            'VENDOR':
                exit(VendorModuleLbl);
            'LEDGER':
                exit(LedgerModuleLbl);
            'FINANCE':
                exit(FinanceModuleLbl);
            'SALES':
                exit(SalesModuleLbl);
            'PURCHASE':
                exit(PurchaseModuleLbl);
            'ITEM', 'INVENTORY':
                exit(InventoryModuleLbl);
            'CRM':
                exit(CrmModuleLbl);
            'SYSTEM':
                exit(SystemModuleLbl);
            'MANUFACTURING':
                exit(ManufacturingModuleLbl);
            'SERVICE':
                exit(ServiceModuleLbl);
            'JOB':
                exit(JobsModuleLbl);
            'HR':
                exit(HrModuleLbl);
            else
                exit(ModuleName);
        end;
    end;

    procedure GetLocalizedRiskLevel(RiskLevel: Code[20]): Text[30]
    begin
        case LowerCase(Format(RiskLevel)) of
            'critical':
                exit(CriticalRiskLbl);
            'high':
                exit(HighRiskLbl);
            'medium':
                exit(MediumRiskLbl);
            'low':
                exit(LowRiskLbl);
            else
                exit(Format(RiskLevel));
        end;
    end;

    procedure GetLocalizedCheckName(CheckCode: Code[50]; DefaultName: Text[150]): Text[150]
    var
        CheckCatalogMgt: Codeunit "DH Check Catalog Mgt.";
    begin
        exit(CopyStr(CheckCatalogMgt.ResolveTitle(CheckCode), 1, 150));
    end;

    procedure GetLocalizedCheckDescription(CheckCode: Code[50]; DefaultDescription: Text[250]): Text[250]
    var
        CheckCatalogMgt: Codeunit "DH Check Catalog Mgt.";
    begin
        exit(CopyStr(CheckCatalogMgt.ResolveRecommendation(CheckCode), 1, 250));
    end;

    local procedure IsModuleIncluded(var Setup: Record "DH Setup"; ModuleName: Text[100]): Boolean
    begin
        case UpperCase(ModuleName) of
            'SYSTEM':
                exit(Setup."Scan System Module");
            'CUSTOMER', 'VENDOR', 'LEDGER', 'FINANCE':
                exit(Setup."Scan Finance Module");
            'SALES':
                exit(Setup."Scan Sales Module");
            'PURCHASE':
                exit(Setup."Scan Purchasing Module");
            'ITEM', 'INVENTORY':
                exit(Setup."Scan Inventory Module");
            'CRM':
                exit(Setup."Scan CRM Module");
            'MANUFACTURING':
                exit(Setup."Scan Manufacturing Module");
            'SERVICE':
                exit(Setup."Scan Service Module");
            'JOB':
                exit(Setup."Scan Jobs Module");
            'HR':
                exit(Setup."Scan HR Module");
            else
                exit(true);
        end;
    end;

    local procedure AddCheck(CheckCode: Code[50]; ModuleName: Text[100]; RiskLevel: Code[20]; SortOrder: Integer)
    var
        ScanCheck: Record "DH Scan Check Selection";
        ExpectedName: Text[150];
        ExpectedDescription: Text[250];
    begin
        ExpectedName := CopyStr(CheckCode, 1, MaxStrLen(ScanCheck.Name));
        ExpectedDescription := CopyStr(CheckCode, 1, MaxStrLen(ScanCheck.Description));

        if ScanCheck.Get(CheckCode) then begin
            if (ScanCheck."Module" = ModuleName) and
               (ScanCheck.Name = ExpectedName) and
               (ScanCheck.Description = ExpectedDescription) and
               ScanCheck."Default Enabled" and
               (ScanCheck."Risk Level" = RiskLevel) and
               (ScanCheck."Sort Order" = SortOrder)
            then
                exit;

            ScanCheck."Module" := ModuleName;
            ScanCheck.Name := ExpectedName;
            ScanCheck.Description := ExpectedDescription;
            ScanCheck."Default Enabled" := true;
            ScanCheck."Risk Level" := RiskLevel;
            ScanCheck."Sort Order" := SortOrder;
            ScanCheck.Modify(true);
            exit;
        end;

        ScanCheck.Init();
        ScanCheck."Check Code" := CheckCode;
        ScanCheck."Module" := ModuleName;
        ScanCheck.Name := ExpectedName;
        ScanCheck.Description := ExpectedDescription;
        ScanCheck.Enabled := true;
        ScanCheck."Default Enabled" := true;
        ScanCheck."Risk Level" := RiskLevel;
        ScanCheck."Sort Order" := SortOrder;
        ScanCheck.Insert(true);
    end;

    var
        CustomerModuleLbl: Label 'Customers';
        VendorModuleLbl: Label 'Vendors';
        LedgerModuleLbl: Label 'Ledger Entries';
        FinanceModuleLbl: Label 'Finance';
        SalesModuleLbl: Label 'Sales';
        PurchaseModuleLbl: Label 'Purchasing';
        InventoryModuleLbl: Label 'Inventory';
        CrmModuleLbl: Label 'CRM';
        SystemModuleLbl: Label 'System';
        ManufacturingModuleLbl: Label 'Manufacturing';
        ServiceModuleLbl: Label 'Service';
        JobsModuleLbl: Label 'Projects';
        HrModuleLbl: Label 'Human Resources';
        CriticalRiskLbl: Label 'Critical';
        HighRiskLbl: Label 'High';
        MediumRiskLbl: Label 'Medium';
        LowRiskLbl: Label 'Low';
        CustomersDuplicateEmailLbl: Label 'Customers with duplicate email addresses';
        VendorsDuplicateEmailLbl: Label 'Vendors with duplicate email addresses';
        CustomersDuplicateVatLbl: Label 'Customers with duplicate VAT registration numbers';
        VendorsDuplicateVatLbl: Label 'Vendors with duplicate VAT registration numbers';
        CustomersDuplicateNamePostCityLbl: Label 'Customers with the same name, post code and city';
        VendorsDuplicateNamePostCityLbl: Label 'Vendors with the same name, post code and city';
        ReviewAndCorrectLbl: Label 'Review and correct: %1.', Comment = '%1 = localized finding title';
}
