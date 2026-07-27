pageextension 53199 "DH Setup Product Copy" extends "DH Setup"
{
    actions
    {
        modify(BuyFullAnalysis)
        {
            Caption = 'Start Assessment';
            ToolTip = 'Opens the secure BCSentinel checkout for an Assessment.';
        }
        modify(BuyValidationCheck)
        {
            Caption = 'Start Validation Check';
            ToolTip = 'Opens the secure BCSentinel checkout for a Validation Check follow-up scan.';
        }
        modify(StartMonitoringMonthly)
        {
            Caption = 'Start Monitoring Monthly';
            ToolTip = 'Opens the secure BCSentinel checkout for monthly Monitoring.';
        }
        modify(StartMonitoringAnnual)
        {
            Caption = 'Start Monitoring Annual';
            ToolTip = 'Opens the secure BCSentinel checkout for annual Monitoring.';
        }
    }
}
