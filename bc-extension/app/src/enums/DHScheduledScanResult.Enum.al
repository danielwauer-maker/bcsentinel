enum 53171 "DH Scheduled Scan Result"
{
    Extensible = false;
    Caption = 'Scheduled Scan Result';

    value(0; None)
    {
        Caption = 'None';
    }
    value(1; Queued)
    {
        Caption = 'Queued';
    }
    value(2; Completed)
    {
        Caption = 'Completed';
    }
    value(3; Failed)
    {
        Caption = 'Failed';
    }
    value(4; SkippedMonitoringInactive)
    {
        Caption = 'Skipped - Monitoring inactive';
    }
    value(5; SkippedConfiguration)
    {
        Caption = 'Skipped - Configuration incomplete';
    }
    value(6; Disabled)
    {
        Caption = 'Disabled';
    }
}
