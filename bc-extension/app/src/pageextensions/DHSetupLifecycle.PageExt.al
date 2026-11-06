pageextension 53202 "DH Setup Lifecycle Ext" extends "DH Setup"
{
    layout
    {
        addafter("Data Processing Consent")
        {
            field("Report Notification Email"; Rec."Report Notification Email")
            {
                ApplicationArea = All;
                ToolTip = 'Email address used for transactional BCSentinel scan, report, assessment and validation notifications.';
                ShowMandatory = true;
            }
            field("Preferred Report Language"; Rec."Preferred Report Language")
            {
                ApplicationArea = All;
                ToolTip = 'Preferred language for BCSentinel reports and transactional notifications. Use DE or EN.';
            }
        }
    }

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

        addafter(RefreshLicenseStatus)
        {
            action(SyncLifecycleProfile)
            {
                Caption = 'Sync Notification Profile';
                ApplicationArea = All;
                Image = SendTo;
                ToolTip = 'Synchronize the report and notification email and preferred language with BCSentinel.';

                trigger OnAction()
                var
                    LifecycleClient: Codeunit "DH Lifecycle Client";
                begin
                    LifecycleClient.SyncProfile(Rec);
                    Message('BCSentinel notification profile synchronized.');
                end;
            }
        }
    }
}
