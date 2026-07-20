# Business-Central-Objekte

Quelle: Deklarationen unter `bc-extension/app/src/`. Tests: keine AL-Test-App gefunden; Python-Vertragstests prüfen einzelne Quellverträge.

## Tables/Enum im Tabellenfile

| ID | Typ/Name | Verantwortung / Datei |
|---:|---|---|
| 53100 | Table `DH Setup` | Registrierung, Access Snapshot, Module, Scheduler; `tables/DHSetup.Table.al` |
| 53104 | Table `DH Scan Trend` | letzter/vorheriger Score; `tables/DHScanTrend.al` |
| 53120 | Table `DH Scan Header` | lokale Historie/KPIs; `tables/DHScanHeader.Table.al` |
| 53121 | Table `DH Scan Issue` | Quick-Scan-Issues; `tables/DHScanIssue.Table.al` |
| 53128 | Table `DH Deep Scan Run` | Runstatus, Resultate, Start-/Leasefelder; `tables/DHDeepScanRun.Table.al` |
| 53129 | Table `DH Deep Scan Finding` | Findings; `tables/DHDeepScanFinding.Table.al` |
| 53133 | Table `DH Dashboard Issue` | Dashboardpuffer; `tables/DHDashboardIssue.Table.al` |
| 53146 | Enum `DH Duplicate Source Type` | Duplikatquelle; `tables/DHDuplicateBuffer.Table.al` |
| 53149 | Table `DH Duplicate Buffer` | temporäre Duplikate; gleiches File |
| 53150 | Table `DH Issue Exception` | Ausnahmen; `tables/DHIssueException.Table.al` |
| 53151 | Table `DH Issue Action Log` | Aktionen; `tables/DHIssueActionLog.Table.al` |
| 53194 | Table `DH Scan Check Selection` | Checks/Module/Risiko/Last Run; `tables/DHScanCheckSelection.Table.al` |

## Codeunits

53100 API Client; 53123 QuickScan Mgt.; 53124 Deep Scan Mgt.; 53128 Deep Scan Runner; 53129 Deep Scan Failure; 53134 Dashboard Mgt.; 53135 Scan Dispatcher; 53136 Secret Mgt.; 53142 Issue Drilldown Mgt.; 53143 Issue Drilldown Dispatcher; 53145 Run ID Mgt.; 53147 Duplicate Worklist Mgt.; 53150 Data Profiling Mgt.; 53152 Exception Mgt.; 53153 Cost Mgt.; 53160 Monitor Refresh Task; 53170 Scan Scheduler Mgt.; 53171 Scheduled Scan Runner; 53172 Scheduled Scan Failure; 53180 Guided Experience; 53193 Install; 53194 Upgrade; 53195 Access Guard; 53196 Scan Check Mgt.; 53197 Currency Mgt.; 53198 API URL Policy; 53199 Tenant Identity Mgt.

Jede Deklaration liegt in der namensgleichen Datei unter `codeunits/`. Abhängigkeiten: Standard-BC-Tabellen für Customer/Vendor/Item/Ledger/Sales/Purchase, `HttpClient`, TaskScheduler, Isolated Storage/Secretverwaltung und die oben genannten BCSentinel-Tabellen.

## Pages

53100 Setup; 53121 Issues Part; 53122 Score Part; 53123 DHM Analytics; 53124 Dashboard List; 53125 Score Trend Chart; 53126 Scan Issues; 53127 Key Metrics Part; 53130 Deep Scan Runs; 53131 Deep Scan Findings; 53132 Deep Scan Part; 53135 Dashboard Issues; 53136 Item Negative Inventory; 53137 Item Missing Cost; 53138 Blocked Items Inventory; 53139 Sales Line Worklist; 53142 Dashboard KPI Part; 53144 Purchase Line Worklist; 53145 Duplicate Worklist; 53148 Item Missing Price; 53153 Issue Exceptions; 53154 Exception FactBox; 53155 Action Log FactBox; 53156 Customer Issue List; 53157 Vendor Issue List; 53158 Deep Scan Monitor; 53159 Issue Drilldown Launch; 53160 Deep Scan Findings List; 53161 Dashboard Issues List; 53172 Scan Modules; 53195 Scan Checks.

Die Dateien liegen unter `pages/`. Benutzerabläufe: Setup/Registrierung, Scanstart/-monitor, Historie/Findings, Dashboard/Analytics, Checkauswahl, Ausnahme/Aktion und Stammdaten-Drilldown.

## Page Extensions

53158 Customer Card, 53159 Vendor Card, 53160 Item Card, 53161 Customer List, 53162 Vendor List, 53163 Item List; Dateien unter `pageextensions/`; sie ergänzen BCSentinel-Aktionen/FactBoxes.

## Queries, Enums, Permission Sets, Control Add-in

- Queries 53140 Customer Duplicate Email und 53141 Vendor Duplicate Email.
- Enums 53101 License Plan, 53102 License Status, 53170 Schedule Frequency, 53171 Scheduled Result; Enum Extension 53180 Assisted Setup Group.
- Permission Sets 53190 Viewer, 53191 Scan, 53192 Setup, 53193 Admin, 53194 Scheduler; konkrete Objektberechtigungen in `permissionsets/BCSentinelPermissionSets.al`.
- Control Add-in 53110 `DH Analytics Frame` mit lokalem JS/CSS in `controladdin/AnalyticsFrameAddIn.al`.

## Nicht gefunden

Reports, API Pages, Interfaces, Table Extensions, Permission Set Extensions und AL-Testcodeunits wurden im Quellbaum nicht deklariert. Executive Reporting liegt im Backend, nicht als AL Report.
