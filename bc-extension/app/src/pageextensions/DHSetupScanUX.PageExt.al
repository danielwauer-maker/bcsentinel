pageextension 53201 "DH Setup Scan UX" extends "DH Setup"
{
    actions
    {
        modify(StartScan)
        {
            Caption = 'Run Data Health Scan';
            ToolTip = 'Runs the full BCSentinel Data Health Scan. New Free Entry tenants can run one initial scan; further scans require Validation credit or active Monitoring.';
        }
        modify(ViewScanHistory)
        {
            Caption = 'Data Health Scan History';
            ToolTip = 'Opens the BCSentinel scan history. Free Entry shows aggregate results; detailed findings require active product access.';
        }
    }
}
