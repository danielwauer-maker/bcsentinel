permissionset 53190 "BCSENTINEL VIEWER"
{
    Assignable = true;
    Caption = 'BCSentinel Viewer';

    Permissions =
        tabledata "DH Setup" = R,
        tabledata "DH Scan Header" = R,
        tabledata "DH Scan Issue" = R,
        tabledata "DH Scan Trend" = R,
        tabledata "DH Deep Scan Run" = R,
        tabledata "DH Deep Scan Finding" = R,
        tabledata "DH Dashboard Issue" = R,
        tabledata "DH Issue Exception" = R,
        tabledata "DH Issue Action Log" = R,
        tabledata "DH Duplicate Buffer" = R,
        page "DH Dashboard List" = X,
        page "DH Scan Issues" = X,
        page "DH Score Part" = X,
        page "DH Score Trend Chart" = X,
        page "DH Key Metrics Part" = X,
        page "DH Issues Part" = X,
        page "DH Dashboard KPI Part" = X,
        page "DH Deep Scan Runs" = X,
        page "DH Deep Scan Findings" = X,
        page "DH Deep Scan Findings List" = X,
        page "DH Deep Scan Part" = X,
        page "DH Dashboard Issues" = X,
        page "DH Dashboard Issues List" = X,
        page "DHM Analytics" = X,
        codeunit "DH Dashboard Mgt." = X,
        codeunit "DH Issue Drilldown Mgt." = X;
}

permissionset 53191 "BCSENTINEL SCAN"
{
    Assignable = true;
    Caption = 'BCSentinel Scan';

    Permissions =
        tabledata "DH Setup" = R,
        tabledata "DH Scan Header" = RIMD,
        tabledata "DH Scan Issue" = RIMD,
        tabledata "DH Scan Trend" = RIMD,
        tabledata "DH Deep Scan Run" = RIMD,
        tabledata "DH Deep Scan Finding" = RIMD,
        tabledata "DH Dashboard Issue" = RIMD,
        tabledata "DH Issue Exception" = R,
        tabledata "DH Issue Action Log" = RIMD,
        tabledata "DH Duplicate Buffer" = RIMD,
        page "DH Dashboard List" = X,
        page "DH Deep Scan Runs" = X,
        page "DH Deep Scan Monitor" = X,
        page "DH Deep Scan Findings" = X,
        page "DH Duplicate Worklist" = X,
        page "DH Customer Issue List" = X,
        page "DH Vendor Issue List" = X,
        page "DH Item Neg. Inventory" = X,
        page "DH Item Missing Cost List" = X,
        page "DH Item Missing Price List" = X,
        page "DH Blocked Items Inv" = X,
        page "DH Purch. Line Worklist" = X,
        page "DH Sales Line Issue Worklist" = X,
        page "DH Issue Drilldown Launch" = X,
        codeunit "DH API Client" = X,
        codeunit "DH QuickScan Mgt." = X,
        codeunit "DH Scan Dispatcher" = X,
        codeunit "DH Deep Scan Mgt." = X,
        codeunit "DH Deep Scan Runner" = X,
        codeunit "DH Deep Scan Failure" = X,
        codeunit "DH Monitor Refresh Task" = X,
        codeunit "DH Run ID Mgt." = X,
        codeunit "DH Data Profiling Mgt." = X,
        codeunit "DH Exception Mgt." = X,
        codeunit "DH Duplicate Worklist Mgt." = X,
        codeunit "DH Issue Drilldown Mgt." = X,
        codeunit "DH Issue Drilldown Dispatcher" = X,
        codeunit "DH Secret Mgt." = X,
        query "DH Customer Duplicate Email" = X,
        query "DH Vendor Duplicate Email" = X;
}

permissionset 53192 "BCSENTINEL SETUP"
{
    Assignable = true;
    Caption = 'BCSentinel Setup';

    Permissions =
        tabledata "DH Setup" = RIMD,
        page "DH Setup" = X,
        codeunit "DH API Client" = X,
        codeunit "DH Guided Experience" = X,
        codeunit "DH Secret Mgt." = X,
        codeunit "DH Run ID Mgt." = X;
}

permissionset 53193 "BCSENTINEL ADMIN"
{
    Assignable = true;
    Caption = 'BCSentinel Admin';

    Permissions =
        tabledata "DH Setup" = RIMD,
        tabledata "DH Scan Header" = RIMD,
        tabledata "DH Scan Issue" = RIMD,
        tabledata "DH Scan Trend" = RIMD,
        tabledata "DH Deep Scan Run" = RIMD,
        tabledata "DH Deep Scan Finding" = RIMD,
        tabledata "DH Dashboard Issue" = RIMD,
        tabledata "DH Issue Exception" = RIMD,
        tabledata "DH Issue Action Log" = RIMD,
        tabledata "DH Duplicate Buffer" = RIMD,
        page "DH Setup" = X,
        page "DH Dashboard List" = X,
        page "DH Scan Issues" = X,
        page "DH Score Part" = X,
        page "DH Score Trend Chart" = X,
        page "DH Key Metrics Part" = X,
        page "DH Issues Part" = X,
        page "DH Dashboard KPI Part" = X,
        page "DH Deep Scan Runs" = X,
        page "DH Deep Scan Monitor" = X,
        page "DH Deep Scan Findings" = X,
        page "DH Deep Scan Findings List" = X,
        page "DH Deep Scan Part" = X,
        page "DH Dashboard Issues" = X,
        page "DH Dashboard Issues List" = X,
        page "DH Duplicate Worklist" = X,
        page "DH Customer Issue List" = X,
        page "DH Vendor Issue List" = X,
        page "DH Item Neg. Inventory" = X,
        page "DH Item Missing Cost List" = X,
        page "DH Item Missing Price List" = X,
        page "DH Blocked Items Inv" = X,
        page "DH Purch. Line Worklist" = X,
        page "DH Sales Line Issue Worklist" = X,
        page "DH Issue Drilldown Launch" = X,
        page "DH Issue Exceptions" = X,
        page "DH Action Log FB" = X,
        page "DH Excp. FactBox" = X,
        page "DHM Analytics" = X,
        codeunit "DH API Client" = X,
        codeunit "DH QuickScan Mgt." = X,
        codeunit "DH Scan Dispatcher" = X,
        codeunit "DH Deep Scan Mgt." = X,
        codeunit "DH Deep Scan Runner" = X,
        codeunit "DH Deep Scan Failure" = X,
        codeunit "DH Monitor Refresh Task" = X,
        codeunit "DH Run ID Mgt." = X,
        codeunit "DH Data Profiling Mgt." = X,
        codeunit "DH Dashboard Mgt." = X,
        codeunit "DH Guided Experience" = X,
        codeunit "DH Exception Mgt." = X,
        codeunit "DH Duplicate Worklist Mgt." = X,
        codeunit "DH Issue Drilldown Mgt." = X,
        codeunit "DH Issue Drilldown Dispatcher" = X,
        codeunit "DH Secret Mgt." = X,
        query "DH Customer Duplicate Email" = X,
        query "DH Vendor Duplicate Email" = X;
}
