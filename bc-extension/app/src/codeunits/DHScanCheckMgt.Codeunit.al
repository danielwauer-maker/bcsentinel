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
        AddCheck('CUSTOMERS_DUPLICATE_EMAIL', 'CUSTOMER', 'Customers Duplicate Email', 'Review duplicates and define a primary customer.', 'high', 10);
        AddCheck('VENDORS_DUPLICATE_EMAIL', 'VENDOR', 'Vendors Duplicate Email', 'Review duplicates and clean up affected vendors.', 'high', 20);
        AddCheck('CUSTOMERS_DUPLICATE_VAT', 'CUSTOMER', 'Customers Duplicate VAT Registration No.', 'Review VAT registration numbers and master data for duplicates.', 'high', 30);
        AddCheck('VENDORS_DUPLICATE_VAT', 'VENDOR', 'Vendors Duplicate VAT Registration No.', 'Review VAT registration numbers and vendor master data for duplicates.', 'high', 40);
        AddCheck('CUSTOMERS_DUPLICATE_NAME_POST_CITY', 'CUSTOMER', 'Customers Duplicate Name/Post Code/City', 'Review and merge potential customer duplicates.', 'high', 50);
        AddCheck('VENDORS_DUPLICATE_NAME_POST_CITY', 'VENDOR', 'Vendors Duplicate Name/Post Code/City', 'Review and merge potential vendor duplicates.', 'high', 60);
        AddCheck('CUSTOMERS_MISSING_NAME', 'CUSTOMER', 'Customers Missing Name', 'Maintain names for affected customers.', 'high', 70);
        AddCheck('CUSTOMERS_MISSING_SEARCH_NAME', 'CUSTOMER', 'Customers Missing Search Name', 'Maintain search names to improve search and duplicate checks.', 'low', 80);
        AddCheck('CUSTOMERS_MISSING_ADDRESS', 'CUSTOMER', 'Customers Missing Address', 'Complete address data for the affected customers.', 'high', 90);
        AddCheck('CUSTOMERS_MISSING_CITY', 'CUSTOMER', 'Customers Missing City', 'Maintain cities for affected customers.', 'medium', 100);
        AddCheck('CUSTOMERS_MISSING_POST_CODE', 'CUSTOMER', 'Customers Missing Post Code', 'Maintain post codes so reporting and plausibility checks work reliably.', 'medium', 110);
        AddCheck('CUSTOMERS_MISSING_COUNTRY', 'CUSTOMER', 'Customers Missing Country/Region Code', 'Add country/region codes for the affected customers.', 'medium', 120);
        AddCheck('CUSTOMERS_MISSING_EMAIL', 'CUSTOMER', 'Customers Missing Email', 'Maintain email addresses to improve communication and automation.', 'medium', 130);
        AddCheck('CUSTOMERS_MISSING_PHONE', 'CUSTOMER', 'Customers Missing Phone No.', 'Add phone numbers so contact remains possible.', 'low', 140);
        AddCheck('CUSTOMERS_MISSING_PAYMENT_TERMS', 'CUSTOMER', 'Customers Missing Payment Terms', 'Add payment terms to stabilize ledger entries and processes.', 'high', 150);
        AddCheck('CUSTOMERS_MISSING_PAYMENT_METHOD', 'CUSTOMER', 'Customers Missing Payment Method', 'Maintain payment methods where used in the tenant.', 'medium', 160);
        AddCheck('CUSTOMERS_MISSING_POSTING_GROUP', 'CUSTOMER', 'Customers Missing Customer Posting Group', 'Add customer posting groups for the affected customers.', 'high', 170);
        AddCheck('CUSTOMERS_MISSING_GEN_BUS_POSTING', 'CUSTOMER', 'Customers Missing General Business Posting Group', 'Complete general business posting groups.', 'high', 180);
        AddCheck('CUSTOMERS_MISSING_VAT_BUS_POSTING', 'CUSTOMER', 'Customers Missing VAT Business Posting Group', 'Add VAT business posting groups.', 'high', 190);
        AddCheck('CUSTOMERS_MISSING_CREDIT_LIMIT', 'CUSTOMER', 'Customers Missing Credit Limit', 'Review credit limits and maintain them where required.', 'low', 200);
        AddCheck('BLOCKED_CUSTOMERS_WITH_OPEN_SALES_DOCS', 'CUSTOMER', 'Blocked Customers With Open Sales Documents', 'Clean up blocked customers and open sales documents.', 'high', 210);
        AddCheck('BLOCKED_CUSTOMERS_WITH_OPEN_LEDGER', 'CUSTOMER', 'Blocked Customers With Open Ledger Entries', 'Review open entries for blocked customers and clear legacy items.', 'high', 220);
        AddCheck('VENDORS_MISSING_NAME', 'VENDOR', 'Vendors Missing Name', 'Maintain names for affected vendors.', 'high', 230);
        AddCheck('VENDORS_MISSING_SEARCH_NAME', 'VENDOR', 'Vendors Missing Search Name', 'Maintain search names to improve search and duplicate checks.', 'low', 240);
        AddCheck('VENDORS_MISSING_ADDRESS', 'VENDOR', 'Vendors Missing Address', 'Complete address data for the affected vendors.', 'high', 250);
        AddCheck('VENDORS_MISSING_CITY', 'VENDOR', 'Vendors Missing City', 'Maintain cities for affected vendors.', 'medium', 260);
        AddCheck('VENDORS_MISSING_POST_CODE', 'VENDOR', 'Vendors Missing Post Code', 'Maintain post codes so reporting and plausibility checks work reliably.', 'medium', 270);
        AddCheck('VENDORS_MISSING_COUNTRY', 'VENDOR', 'Vendors Missing Country/Region Code', 'Add country/region codes for the affected vendors.', 'medium', 280);
        AddCheck('VENDORS_MISSING_EMAIL', 'VENDOR', 'Vendors Missing Email', 'Maintain email addresses to improve communication and automation.', 'medium', 290);
        AddCheck('VENDORS_MISSING_PHONE', 'VENDOR', 'Vendors Missing Phone No.', 'Add phone numbers so contact remains possible.', 'low', 300);
        AddCheck('VENDORS_MISSING_PAYMENT_TERMS', 'VENDOR', 'Vendors Missing Payment Terms', 'Add payment terms to stabilize ledger entries and processes.', 'high', 310);
        AddCheck('VENDORS_MISSING_PAYMENT_METHOD', 'VENDOR', 'Vendors Missing Payment Method', 'Maintain payment methods where used in the tenant.', 'medium', 320);
        AddCheck('VENDORS_MISSING_POSTING_GROUP', 'VENDOR', 'Vendors Missing Vendor Posting Group', 'Add vendor posting groups for the affected vendors.', 'high', 330);
        AddCheck('VENDORS_MISSING_GEN_BUS_POSTING', 'VENDOR', 'Vendors Missing General Business Posting Group', 'Complete general business posting groups.', 'high', 340);
        AddCheck('VENDORS_MISSING_VAT_BUS_POSTING', 'VENDOR', 'Vendors Missing VAT Business Posting Group', 'Add VAT business posting groups.', 'high', 350);
        AddCheck('VENDORS_MISSING_BANK_ACCOUNT', 'VENDOR', 'Vendors Missing Bank Account', 'Maintain bank accounts for affected vendors.', 'medium', 360);
        AddCheck('BLOCKED_VENDORS_WITH_OPEN_PURCHASE_DOCS', 'VENDOR', 'Blocked Vendors With Open Purchase Documents', 'Clean up blocked vendors and open purchase documents.', 'high', 370);
        AddCheck('BLOCKED_VENDORS_WITH_OPEN_LEDGER', 'VENDOR', 'Blocked Vendors With Open Ledger Entries', 'Review open entries for blocked vendors and clear legacy items.', 'high', 380);
        AddCheck('ITEMS_MISSING_DESCRIPTION', 'ITEM', 'Items Missing Description', 'Maintain descriptions for affected items.', 'high', 390);
        AddCheck('ITEMS_MISSING_BASE_UOM', 'ITEM', 'Items Missing Base Unit of Measure', 'Add base units of measure for the affected items.', 'high', 400);
        AddCheck('ITEMS_MISSING_CATEGORY', 'ITEM', 'Items Missing Item Category', 'Maintain item categories so reporting and control work reliably.', 'medium', 410);
        AddCheck('ITEMS_MISSING_GEN_PROD_POSTING', 'ITEM', 'Items Missing Gen. Prod. Posting Group', 'Complete product posting groups.', 'high', 420);
        AddCheck('ITEMS_MISSING_INVENTORY_POSTING', 'ITEM', 'Items Missing Inventory Posting Group', 'Complete inventory posting groups.', 'high', 430);
        AddCheck('ITEMS_WITHOUT_VENDOR_NO', 'ITEM', 'Items Missing Default Vendor', 'Add the default vendor for affected items where required.', 'medium', 440);
        AddCheck('ITEMS_WITHOUT_UNIT_COST', 'ITEM', 'Items Missing Unit Cost', 'Review and maintain unit costs for affected items.', 'high', 450);
        AddCheck('ITEMS_WITHOUT_UNIT_PRICE', 'ITEM', 'Items Missing Unit Price', 'Review and maintain sales prices for active items.', 'medium', 460);
        AddCheck('ITEMS_NEGATIVE_INVENTORY', 'ITEM', 'Items With Negative Inventory', 'Review negative inventory and correct posting logic.', 'high', 470);
        AddCheck('BLOCKED_ITEMS_WITH_INVENTORY', 'ITEM', 'Blocked Items With Inventory', 'Align blocked status with existing inventory.', 'medium', 480);
        AddCheck('SALES_ORDERS_MISSING_SHIPMENT_DATE', 'SALES', 'Open Sales Orders Missing Shipment Date', 'Maintain shipment dates in open sales orders.', 'medium', 490);
        AddCheck('SALES_ORDERS_OLD_OPEN', 'SALES', 'Very Old Open Sales Orders', 'Review old orders for relevance, status, and closure.', 'medium', 500);
        AddCheck('SALES_LINES_MISSING_NO', 'SALES', 'Sales Lines Missing Item/G/L Account Reference', 'Correct line references or clean up invalid document lines.', 'high', 510);
        AddCheck('SALES_LINES_ZERO_QUANTITY', 'SALES', 'Sales Lines With Zero Quantity', 'Clean up zero-quantity lines in open sales documents.', 'medium', 520);
        AddCheck('SALES_LINES_ZERO_PRICE', 'SALES', 'Sales Lines With Zero Prices', 'Review pricing and open sales lines with zero price.', 'high', 530);
        AddCheck('SALES_LINES_MISSING_DIMENSIONS', 'SALES', 'Sales Lines Missing Dimensions', 'Add dimensions in open sales documents.', 'high', 540);
        AddCheck('SALES_DOCS_WITH_BLOCKED_CUSTOMERS', 'SALES', 'Sales Documents With Blocked Customers', 'Review customer blocked status and affected documents.', 'high', 550);
        AddCheck('SALES_LINES_WITH_BLOCKED_ITEMS', 'SALES', 'Sales Lines With Blocked Items', 'Review item blocked status and affected sales lines.', 'high', 560);
        AddCheck('PURCHASE_ORDERS_MISSING_EXPECTED_DATE', 'PURCHASE', 'Open Purchase Orders Missing Expected Receipt Date', 'Maintain expected receipt dates in open purchase orders.', 'medium', 570);
        AddCheck('PURCHASE_ORDERS_OLD_OPEN', 'PURCHASE', 'Very Old Open Purchase Orders', 'Review old orders for relevance, status, and closure.', 'medium', 580);
        AddCheck('PURCHASE_LINES_MISSING_NO', 'PURCHASE', 'Purchase Lines Missing Item/G/L Account Reference', 'Correct line references or clean up invalid document lines.', 'high', 590);
        AddCheck('PURCHASE_LINES_ZERO_QUANTITY', 'PURCHASE', 'Purchase Lines With Zero Quantity', 'Clean up zero-quantity lines in open purchase documents.', 'medium', 600);
        AddCheck('PURCHASE_LINES_ZERO_COST', 'PURCHASE', 'Purchase Lines With Zero Costs', 'Review pricing and open purchase lines with zero cost.', 'high', 610);
        AddCheck('PURCHASE_LINES_MISSING_DIMENSIONS', 'PURCHASE', 'Purchase Lines Missing Dimensions', 'Add dimensions in open purchase documents.', 'high', 620);
        AddCheck('PURCHASE_DOCS_WITH_BLOCKED_VENDORS', 'PURCHASE', 'Purchase Documents With Blocked Vendors', 'Review vendor blocked status and affected documents.', 'high', 630);
        AddCheck('PURCHASE_LINES_WITH_BLOCKED_ITEMS', 'PURCHASE', 'Purchase Lines With Blocked Items', 'Review item blocked status and affected purchase lines.', 'high', 640);
        AddCheck('CUSTOMER_LEDGER_OVERDUE_30', 'LEDGER', 'Open Customer Ledger Entries Overdue > 30 Days', 'Review overdue customer entries and improve receivables management.', 'high', 650);
        AddCheck('VENDOR_LEDGER_OVERDUE_30', 'LEDGER', 'Open Vendor Ledger Entries Overdue > 30 Days', 'Review overdue vendor entries and payment processes.', 'medium', 660);
        AddCheck('GL_ENTRIES_MISSING_DIM1', 'SYSTEM', 'G/L Entries Missing Dimension 1', 'Maintain dimension 1 in the relevant posting processes.', 'medium', 670);
        AddCheck('GL_ENTRIES_MISSING_DIM2', 'SYSTEM', 'G/L Entries Missing Dimension 2', 'Maintain dimension 2 in the relevant posting processes.', 'medium', 680);
        AddCheck('GL_ENTRIES_MISSING_BOTH_DIMS', 'SYSTEM', 'G/L Entries Missing Both Dimensions', 'Complete dimension posting logic consistently.', 'high', 690);
        AddCheck('GL_ACCOUNTS_BLOCKED_BUT_USED', 'SYSTEM', 'Blocked G/L Accounts With Entries', 'Review blocked status and account usage.', 'high', 700);
        AddCheck('GL_ACCOUNTS_NO_DIRECT_POSTING_BUT_USED', 'SYSTEM', 'G/L Accounts Without Direct Posting With Entries', 'Align direct posting rules and account master data.', 'medium', 710);
        AddCheck('SYSTEM_CUSTOMERS_MISSING_GEN_BUS_POSTING', 'SYSTEM', 'Customers Missing General Business Posting Group', 'Maintain general business posting groups for customers.', 'high', 720);
        AddCheck('SYSTEM_CUSTOMERS_MISSING_VAT_BUS_POSTING', 'SYSTEM', 'Customers Missing VAT Business Posting Group', 'Add VAT business posting groups for customers.', 'high', 730);
        AddCheck('SYSTEM_VENDORS_MISSING_GEN_BUS_POSTING', 'SYSTEM', 'Vendors Missing General Business Posting Group', 'Maintain general business posting groups for vendors.', 'high', 740);
        AddCheck('SYSTEM_VENDORS_MISSING_VAT_BUS_POSTING', 'SYSTEM', 'Vendors Missing VAT Business Posting Group', 'Add VAT business posting groups for vendors.', 'high', 750);
        AddCheck('SYSTEM_ITEMS_MISSING_GEN_PROD_POSTING', 'SYSTEM', 'Items Missing Product Posting Group', 'Maintain product posting groups for items.', 'high', 760);
        AddCheck('SYSTEM_ITEMS_MISSING_INVENTORY_POSTING', 'SYSTEM', 'Items Missing Inventory Posting Group', 'Maintain inventory posting groups for items.', 'high', 770);
        AddCheck('CUSTOMER_LEDGER_MISSING_DUE_DATE', 'SYSTEM', 'Open Customer Ledger Entries Missing Due Date', 'Review due dates in customer ledger entries and payment terms.', 'medium', 780);
        AddCheck('VENDOR_LEDGER_MISSING_DUE_DATE', 'SYSTEM', 'Open Vendor Ledger Entries Missing Due Date', 'Review due dates in vendor ledger entries and payment terms.', 'medium', 790);
        AddCheck('CUSTOMERS_MISSING_VAT_REG_NO', 'FINANCE', 'Customers Missing VAT Registration No.', 'Add VAT registration numbers for affected customers.', 'medium', 800);
        AddCheck('CUSTOMERS_MISSING_SALESPERSON', 'FINANCE', 'Customers Missing Salesperson Code', 'Assign responsible salespeople.', 'low', 810);
        AddCheck('CUSTOMERS_MISSING_PRICE_GROUP', 'FINANCE', 'Customers Missing Customer Price Group', 'Maintain price groups to ensure clean pricing.', 'medium', 820);
        AddCheck('CUSTOMERS_MISSING_DISC_GROUP', 'FINANCE', 'Customers Missing Customer Discount Group', 'Maintain discount groups to avoid margin leakage.', 'medium', 830);
        AddCheck('CUSTOMERS_MISSING_REMINDER_TERMS', 'FINANCE', 'Customers Missing Reminder Terms', 'Maintain reminder terms for receivables management.', 'medium', 840);
        AddCheck('CUSTOMERS_MISSING_FIN_CHARGE_TERMS', 'FINANCE', 'Customers Missing Finance Charge Terms', 'Review and maintain finance charge terms.', 'low', 850);
        AddCheck('CUSTOMERS_MISSING_CONTACT', 'FINANCE', 'Customers Missing Contact', 'Add contacts in customer master data.', 'low', 860);
        AddCheck('CUSTOMERS_MISSING_HOME_PAGE', 'FINANCE', 'Customers Missing Website', 'Maintain websites only where required.', 'low', 870);
        AddCheck('VENDORS_MISSING_VAT_REG_NO', 'FINANCE', 'Vendors Missing VAT Registration No.', 'Add VAT registration numbers for vendors.', 'medium', 880);
        AddCheck('VENDORS_MISSING_PURCHASER', 'FINANCE', 'Vendors Missing Purchaser Code', 'Assign responsible purchasers.', 'low', 890);
        AddCheck('VENDORS_MISSING_CONTACT', 'FINANCE', 'Vendors Missing Contact', 'Add contacts in vendor master data.', 'low', 900);
        AddCheck('VENDORS_MISSING_HOME_PAGE', 'FINANCE', 'Vendors Missing Website', 'Maintain websites only where required.', 'low', 910);
        AddCheck('CUSTOMER_LEDGER_OVERDUE_60', 'FINANCE', 'Open Customer Ledger Entries Overdue > 60 Days', 'Actively follow up overdue receivables.', 'high', 920);
        AddCheck('CUSTOMER_LEDGER_OVERDUE_90', 'FINANCE', 'Open Customer Ledger Entries Overdue > 90 Days', 'Prioritize critical outstanding receivables.', 'high', 930);
        AddCheck('VENDOR_LEDGER_OVERDUE_60', 'FINANCE', 'Open Vendor Ledger Entries Overdue > 60 Days', 'Review due vendor payments and process bottlenecks.', 'medium', 940);
        AddCheck('VENDOR_LEDGER_OVERDUE_90', 'FINANCE', 'Open Vendor Ledger Entries Overdue > 90 Days', 'Review critical vendor entries and escalation risks.', 'medium', 950);
        AddCheck('SALES_HEADERS_MISSING_PAYMENT_TERMS', 'SALES', 'Sales Orders Missing Payment Terms', 'Add payment terms in open sales orders.', 'medium', 960);
        AddCheck('SALES_HEADERS_MISSING_PAYMENT_METHOD', 'SALES', 'Sales Orders Missing Payment Method', 'Add payment methods in open sales orders.', 'medium', 970);
        AddCheck('SALES_HEADERS_MISSING_REQUESTED_DELIVERY_DATE', 'SALES', 'Sales Orders Missing Requested Delivery Date', 'Maintain requested delivery dates in open orders.', 'medium', 980);
        AddCheck('SALES_HEADERS_MISSING_SHIPMENT_METHOD', 'SALES', 'Sales Orders Missing Shipment Method', 'Add shipment methods in open orders.', 'low', 990);
        AddCheck('SALES_HEADERS_MISSING_EXTERNAL_DOC_NO', 'SALES', 'Sales Orders Missing External Document No.', 'Add external document references where required.', 'low', 1000);
        AddCheck('SALES_HEADERS_PAST_REQUESTED_DELIVERY_DATE', 'SALES', 'Sales Orders With Overdue Requested Delivery Date', 'Clean up overdue orders by schedule and follow up actively.', 'high', 1010);
        AddCheck('SALES_LINES_DISCOUNT_OVER_25', 'SALES', 'Sales Lines With Discount > 25%', 'Review discounts and price approvals.', 'medium', 1020);
        AddCheck('SALES_LINES_DISCOUNT_OVER_50', 'SALES', 'Sales Lines With Discount > 50%', 'Prioritize review of critical discounts.', 'high', 1030);
        AddCheck('SALES_LINES_PRICE_BELOW_UNIT_COST', 'SALES', 'Sales Lines Below Unit Cost', 'Review pricing and margin on affected sales lines.', 'high', 1040);
        AddCheck('SALES_LINES_SHIPPED_NOT_INVOICED', 'SALES', 'Shipped Sales Lines Not Invoiced', 'Invoice shipments promptly to avoid leaving revenue behind.', 'high', 1050);
        AddCheck('SALES_LINES_OUTSTANDING_PAST_SHIPMENT_DATE', 'SALES', 'Open Sales Lines With Overdue Shipment Date', 'Clean up open quantities and shipment dates.', 'medium', 1060);
        AddCheck('SALES_LINES_MISSING_DESCRIPTION', 'SALES', 'Sales Lines Missing Description', 'Add descriptions in sales lines.', 'low', 1070);
        AddCheck('SALES_LINES_MISSING_LOCATION', 'SALES', 'Sales Lines Missing Location', 'Add locations in sales lines.', 'medium', 1080);
        AddCheck('PURCHASE_HEADERS_MISSING_PAYMENT_TERMS', 'PURCHASE', 'Purchase Orders Missing Payment Terms', 'Add payment terms in open purchase orders.', 'medium', 1090);
        AddCheck('PURCHASE_HEADERS_MISSING_PAYMENT_METHOD', 'PURCHASE', 'Purchase Orders Missing Payment Method', 'Add payment methods in open purchase orders.', 'medium', 1100);
        AddCheck('PURCHASE_HEADERS_MISSING_PURCHASER', 'PURCHASE', 'Purchase Orders Missing Purchaser Code', 'Assign responsible purchasers.', 'low', 1110);
        AddCheck('PURCHASE_HEADERS_MISSING_VENDOR_INVOICE_NO', 'PURCHASE', 'Purchase Orders Missing Vendor Invoice No.', 'Add external document references where required.', 'low', 1120);
        AddCheck('PURCHASE_HEADERS_PAST_EXPECTED_RECEIPT_DATE', 'PURCHASE', 'Purchase Orders With Overdue Receipt', 'Clean up overdue purchase orders by schedule and escalate.', 'high', 1130);
        AddCheck('PURCHASE_LINES_DISCOUNT_OVER_25', 'PURCHASE', 'Purchase Lines With Discount > 25%', 'Review discounts and price agreements.', 'low', 1140);
        AddCheck('PURCHASE_LINES_DISCOUNT_OVER_50', 'PURCHASE', 'Purchase Lines With Discount > 50%', 'Validate unusual discounts.', 'medium', 1150);
        AddCheck('PURCHASE_LINES_RECEIVED_NOT_INVOICED', 'PURCHASE', 'Received Purchase Lines Not Invoiced', 'Invoice receipts promptly.', 'medium', 1160);
        AddCheck('PURCHASE_LINES_OUTSTANDING_PAST_RECEIPT_DATE', 'PURCHASE', 'Open Purchase Lines With Overdue Receipt', 'Clean up open orders and delivery dates.', 'medium', 1170);
        AddCheck('PURCHASE_LINES_MISSING_DESCRIPTION', 'PURCHASE', 'Purchase Lines Missing Description', 'Add descriptions in purchase lines.', 'low', 1180);
        AddCheck('PURCHASE_LINES_MISSING_LOCATION', 'PURCHASE', 'Purchase Lines Missing Location', 'Add locations in purchase lines.', 'medium', 1190);
        AddCheck('PURCHASE_LINES_COST_BELOW_LAST_DIRECT_COST', 'PURCHASE', 'Purchase Lines Below Last Direct Cost', 'Review purchase price deviations.', 'low', 1200);
        AddCheck('ITEMS_PRICE_BELOW_UNIT_COST', 'INVENTORY', 'Items With Sales Price Below Unit Cost', 'Review pricing and costing.', 'high', 1210);
        AddCheck('ITEMS_PRICE_BELOW_STANDARD_COST', 'INVENTORY', 'Items With Sales Price Below Standard Cost', 'Align standard costs and sales prices.', 'high', 1220);
        AddCheck('ITEMS_STANDARD_COST_ZERO', 'INVENTORY', 'Items Missing Standard Cost', 'Maintain standard costs.', 'medium', 1230);
        AddCheck('ITEMS_LAST_DIRECT_COST_ZERO', 'INVENTORY', 'Items Missing Last Direct Cost', 'Review last direct costs.', 'medium', 1240);
        AddCheck('ITEMS_MISSING_LEAD_TIME', 'INVENTORY', 'Items Missing Lead Time', 'Maintain lead times for planning.', 'medium', 1250);
        AddCheck('ITEMS_SAFETY_STOCK_ZERO', 'INVENTORY', 'Items Missing Safety Stock', 'Maintain safety stock where relevant.', 'low', 1260);
        AddCheck('ITEMS_REORDER_POINT_ZERO', 'INVENTORY', 'Items Missing Reorder Point', 'Maintain reorder points where relevant.', 'low', 1270);
        AddCheck('ITEMS_MAX_INVENTORY_ZERO', 'INVENTORY', 'Items Missing Maximum Inventory', 'Maintain maximum inventory where relevant.', 'low', 1280);
        AddCheck('ITEMS_MIN_ORDER_QTY_ZERO', 'INVENTORY', 'Items Missing Minimum Order Quantity', 'Maintain minimum order quantities where relevant.', 'low', 1290);
        AddCheck('ITEMS_ORDER_MULTIPLE_ZERO', 'INVENTORY', 'Items Missing Order Multiple', 'Maintain order multiples where relevant.', 'low', 1300);
        AddCheck('ITEMS_MISSING_SHELF_NO', 'INVENTORY', 'Items Missing Shelf No.', 'Add shelf numbers where used.', 'low', 1310);
        AddCheck('ITEMS_MISSING_TARIFF_NO', 'INVENTORY', 'Items Missing Tariff No.', 'Maintain tariff numbers where export-relevant.', 'low', 1320);
        AddCheck('ITEMS_GROSS_WEIGHT_ZERO', 'INVENTORY', 'Items Missing Gross Weight', 'Maintain weight data.', 'low', 1330);
        AddCheck('ITEMS_NET_WEIGHT_ZERO', 'INVENTORY', 'Items Missing Net Weight', 'Maintain weight data.', 'low', 1340);
        AddCheck('ITEMS_UNIT_VOLUME_ZERO', 'INVENTORY', 'Items Missing Volume', 'Maintain volume data.', 'low', 1350);
        AddCheck('DEAD_STOCK_90', 'INVENTORY', 'Inventory Items Without Movement > 90 Days', 'Review slow-moving items.', 'medium', 1360);
        AddCheck('DEAD_STOCK_180', 'INVENTORY', 'Inventory Items Without Movement > 180 Days', 'Review tied-up capital and sell-off options.', 'medium', 1370);
        AddCheck('DEAD_STOCK_365', 'INVENTORY', 'Inventory Items Without Movement > 365 Days', 'Langfristig totes Kapital priorisiert abbauen.', 'high', 1380);
        AddCheck('INVENTORY_WITHOUT_UNIT_COST', 'INVENTORY', 'Inventory Items Missing Unit Cost', 'Correct valuation and costing for inventory items.', 'high', 1390);
        AddCheck('CONTACTS_MISSING_NAME', 'CRM', 'Contacts Missing Name', 'Add names in contact master data.', 'medium', 1400);
        AddCheck('CONTACTS_MISSING_EMAIL', 'CRM', 'Contacts Missing Email', 'Maintain email addresses in contact master data.', 'medium', 1410);
        AddCheck('CONTACTS_MISSING_PHONE', 'CRM', 'Contacts Missing Phone No.', 'Maintain phone numbers where relevant.', 'low', 1420);
        AddCheck('CONTACTS_MISSING_MOBILE_PHONE', 'CRM', 'Contacts Missing Mobile Phone No.', 'Maintain mobile phone numbers where relevant.', 'low', 1430);
        AddCheck('CONTACTS_PERSONS_MISSING_COMPANY', 'CRM', 'Person Contacts Missing Company Assignment', 'Personenkontakte einer Firma zuordnen.', 'medium', 1440);
        AddCheck('CONTACTS_MISSING_ADDRESS', 'CRM', 'Contacts Missing Address', 'Maintain address data in contacts.', 'low', 1450);
        AddCheck('CONTACTS_MISSING_CITY', 'CRM', 'Contacts Missing City', 'Maintain cities in contacts.', 'low', 1460);
        AddCheck('CONTACTS_MISSING_POST_CODE', 'CRM', 'Contacts Missing Post Code', 'Maintain post codes in contacts.', 'low', 1470);
        AddCheck('CONTACTS_MISSING_COUNTRY', 'CRM', 'Contacts Missing Country', 'Maintain country information in contacts.', 'low', 1480);
        AddCheck('MFG_BOM_MISSING_DESCRIPTION', 'MANUFACTURING', 'Production BOMs Missing Description', 'Add descriptions in the affected production BOMs.', 'medium', 1490);
        AddCheck('MFG_BOM_NOT_CERTIFIED', 'MANUFACTURING', 'Uncertified Production BOMs', 'Review and certify BOMs.', 'high', 1500);
        AddCheck('MFG_BOM_LINES_MISSING_NO', 'MANUFACTURING', 'BOM Lines Missing Item/Resource No.', 'Add numbers in the affected BOM lines.', 'high', 1510);
        AddCheck('MFG_BOM_LINES_ZERO_QTY', 'MANUFACTURING', 'BOM Lines With Quantity 0', 'Review quantities in the affected BOM lines.', 'high', 1520);
        AddCheck('MFG_ROUTING_MISSING_DESCRIPTION', 'MANUFACTURING', 'Routings Missing Description', 'Add descriptions in the affected routings.', 'low', 1530);
        AddCheck('MFG_ROUTING_NOT_CERTIFIED', 'MANUFACTURING', 'Uncertified Routings', 'Review and certify routings.', 'high', 1540);
        AddCheck('MFG_ROUTING_LINES_MISSING_NO', 'MANUFACTURING', 'Routing Lines Missing Work Center/Machine Center', 'Maintain work centers or machine centers in routings.', 'high', 1550);
        AddCheck('MFG_ROUTING_LINES_ZERO_SETUP', 'MANUFACTURING', 'Routing Lines Missing Setup Time', 'Review setup times in affected routing steps.', 'medium', 1560);
        AddCheck('MFG_ROUTING_LINES_ZERO_RUN', 'MANUFACTURING', 'Routing Lines Missing Run Time', 'Review run times in affected routing steps.', 'high', 1570);
        AddCheck('MFG_WORK_CENTERS_BLOCKED', 'MANUFACTURING', 'Blocked Work Centers', 'Review blocked work centers.', 'medium', 1580);
        AddCheck('MFG_WORK_CENTERS_MISSING_NAME', 'MANUFACTURING', 'Work Centers Missing Name', 'Add names for affected work centers.', 'low', 1590);
        AddCheck('MFG_WORK_CENTERS_ZERO_COST', 'MANUFACTURING', 'Work Centers Missing Unit Cost', 'Maintain unit costs for work centers.', 'medium', 1600);
        AddCheck('MFG_MACHINE_CENTERS_BLOCKED', 'MANUFACTURING', 'Blocked Machine Centers', 'Review blocked machine centers.', 'medium', 1610);
        AddCheck('MFG_MACHINE_CENTERS_MISSING_NAME', 'MANUFACTURING', 'Machine Centers Missing Name', 'Add names for affected machine centers.', 'low', 1620);
        AddCheck('MFG_MACHINE_CENTERS_ZERO_COST', 'MANUFACTURING', 'Machine Centers Missing Unit Cost', 'Maintain unit costs for machine centers.', 'medium', 1630);
        AddCheck('MFG_ITEMS_MISSING_PROD_BOM_NO', 'MANUFACTURING', 'Items With Routing But Missing Production BOM', 'Add BOMs for the affected items.', 'high', 1640);
        AddCheck('MFG_ITEMS_MISSING_ROUTING_NO', 'MANUFACTURING', 'Items With Production BOM But Missing Routing', 'Add routings for the affected items.', 'high', 1650);
        AddCheck('SERVICE_ITEMS_MISSING_DESCRIPTION', 'SERVICE', 'Service Items Missing Description', 'Add descriptions for the affected service items.', 'medium', 1660);
        AddCheck('SERVICE_ITEMS_MISSING_CUSTOMER', 'SERVICE', 'Service Items Missing Customer', 'Add customer references for the affected service items.', 'high', 1670);
        AddCheck('SERVICE_ITEMS_MISSING_ITEM_NO', 'SERVICE', 'Service Items Missing Item No.', 'Add item numbers for the affected service items.', 'high', 1680);
        AddCheck('SERVICE_ITEMS_MISSING_SERIAL_NO', 'SERVICE', 'Service Items Missing Serial No.', 'Add serial numbers for the affected service items.', 'medium', 1690);
        AddCheck('SERVICE_ORDERS_MISSING_CUSTOMER', 'SERVICE', 'Service Documents Missing Customer', 'Add customers in the affected service documents.', 'high', 1700);
        AddCheck('SERVICE_ORDERS_MISSING_BILL_TO', 'SERVICE', 'Service Documents Missing Bill-to Customer', 'Maintain bill-to customers in the affected service documents.', 'high', 1710);
        AddCheck('SERVICE_ORDERS_MISSING_DESCRIPTION', 'SERVICE', 'Service Documents Missing Description', 'Add descriptions in the affected service documents.', 'medium', 1720);
        AddCheck('SERVICE_ORDERS_MISSING_ASSIGNED_USER', 'SERVICE', 'Service Documents Missing Assigned User', 'Maintain assigned users in service documents.', 'medium', 1730);
        AddCheck('SERVICE_LINES_MISSING_NO', 'SERVICE', 'Service Lines Missing No.', 'Add numbers in the affected service lines.', 'high', 1740);
        AddCheck('SERVICE_LINES_MISSING_DESCRIPTION', 'SERVICE', 'Service Lines Missing Description', 'Add descriptions in the affected service lines.', 'medium', 1750);
        AddCheck('SERVICE_LINES_ZERO_QTY', 'SERVICE', 'Service Lines With Quantity 0', 'Review quantities in the affected service lines.', 'medium', 1760);
        AddCheck('SERVICE_LINES_ZERO_UNIT_PRICE', 'SERVICE', 'Service Lines With Price 0', 'Review sales prices in the affected service lines.', 'high', 1770);
        AddCheck('JOBS_MISSING_DESCRIPTION', 'JOB', 'Jobs Missing Description', 'Add descriptions for the affected jobs.', 'medium', 1780);
        AddCheck('JOBS_MISSING_BILL_TO_CUSTOMER', 'JOB', 'Jobs Missing Bill-to Customer', 'Maintain bill-to customers in the affected jobs.', 'high', 1790);
        AddCheck('JOBS_MISSING_RESPONSIBLE', 'JOB', 'Jobs Missing Person Responsible', 'Maintain the person responsible in the affected jobs.', 'medium', 1800);
        AddCheck('JOBS_MISSING_POSTING_GROUP', 'JOB', 'Jobs Missing Job Posting Group', 'Add job posting groups for the affected jobs.', 'high', 1810);
        AddCheck('JOB_TASKS_MISSING_DESCRIPTION', 'JOB', 'Job Tasks Missing Description', 'Add descriptions in the affected job tasks.', 'medium', 1820);
        AddCheck('JOB_PLANNING_LINES_MISSING_NO', 'JOB', 'Job Planning Lines Missing No.', 'Add numbers in the affected job planning lines.', 'high', 1830);
        AddCheck('JOB_PLANNING_LINES_MISSING_DESCRIPTION', 'JOB', 'Job Planning Lines Missing Description', 'Add descriptions in the affected job planning lines.', 'medium', 1840);
        AddCheck('JOB_PLANNING_LINES_ZERO_QTY', 'JOB', 'Job Planning Lines With Quantity 0', 'Review quantities in the affected job planning lines.', 'medium', 1850);
        AddCheck('JOB_PLANNING_LINES_ZERO_UNIT_COST', 'JOB', 'Job Planning Lines Missing Unit Cost', 'Add unit costs in the affected job planning lines.', 'high', 1860);
        AddCheck('JOB_PLANNING_LINES_ZERO_UNIT_PRICE', 'JOB', 'Job Planning Lines Missing Price', 'Add prices in the affected job planning lines.', 'high', 1870);
        AddCheck('EMPLOYEES_MISSING_FIRST_NAME', 'HR', 'Employees Missing First Name', 'Add first names for the affected employees.', 'low', 1880);
        AddCheck('EMPLOYEES_MISSING_LAST_NAME', 'HR', 'Employees Missing Last Name', 'Add last names for the affected employees.', 'medium', 1890);
        AddCheck('EMPLOYEES_MISSING_SEARCH_NAME', 'HR', 'Employees Missing Search Name', 'Add search names for the affected employees.', 'low', 1900);
        AddCheck('EMPLOYEES_MISSING_EMAIL', 'HR', 'Employees Missing Email', 'Add email addresses for the affected employees.', 'medium', 1910);
        AddCheck('EMPLOYEES_MISSING_PHONE', 'HR', 'Employees Missing Phone No.', 'Add phone numbers for the affected employees.', 'low', 1920);
        AddCheck('EMPLOYEES_MISSING_COUNTRY', 'HR', 'Employees Missing Country/Region Code', 'Add country/region codes for the affected employees.', 'low', 1930);
        AddCheck('EMPLOYEES_MISSING_RESOURCE_NO', 'HR', 'Employees Missing Resource No.', 'Maintain resource numbers for the affected employees.', 'medium', 1940);
        AddCheck('EMPLOYEES_MISSING_JOB_TITLE', 'HR', 'Employees Missing Job Title', 'Add job titles for the affected employees.', 'low', 1950);
        AddCheck('RESOURCES_MISSING_NAME', 'HR', 'Resources Missing Name', 'Add names for the affected resources.', 'medium', 1960);
        AddCheck('RESOURCES_ZERO_UNIT_COST', 'HR', 'Resources Missing Unit Cost', 'Maintain unit costs for the affected resources.', 'medium', 1970);
        AddCheck('RESOURCES_ZERO_UNIT_PRICE', 'HR', 'Resources Missing Price', 'Maintain prices for the affected resources.', 'medium', 1980);
        AddCheck('RESOURCES_MISSING_BASE_UOM', 'HR', 'Resources Missing Base Unit of Measure', 'Add base units of measure for the affected resources.', 'low', 1990);
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

        EnsureDefaultChecks();
        if not ScanCheck.Get(CheckCode) then begin
            AddCheck(CheckCode, 'CUSTOM', Format(CheckCode), '', '', 999000);
            exit(true);
        end;

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

    local procedure AddCheck(CheckCode: Code[50]; ModuleName: Text[100]; CheckName: Text[150]; Description: Text[250]; RiskLevel: Code[20]; SortOrder: Integer)
    var
        ScanCheck: Record "DH Scan Check Selection";
    begin
        if ScanCheck.Get(CheckCode) then begin
            ScanCheck."Module" := ModuleName;
            ScanCheck.Name := CheckName;
            ScanCheck.Description := Description;
            ScanCheck."Default Enabled" := true;
            ScanCheck."Risk Level" := RiskLevel;
            ScanCheck."Sort Order" := SortOrder;
            ScanCheck.Modify(true);
            exit;
        end;

        ScanCheck.Init();
        ScanCheck."Check Code" := CheckCode;
        ScanCheck."Module" := ModuleName;
        ScanCheck.Name := CheckName;
        ScanCheck.Description := Description;
        ScanCheck.Enabled := true;
        ScanCheck."Default Enabled" := true;
        ScanCheck."Risk Level" := RiskLevel;
        ScanCheck."Sort Order" := SortOrder;
        ScanCheck.Insert(true);
    end;
}
