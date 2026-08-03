codeunit 53201 "DH Manual Monitoring BG"
{
    TableNo = "DH Setup";

    trigger OnRun()
    var
        Setup: Record "DH Setup";
        DeepScanMgt: Codeunit "DH Deep Scan Mgt.";
        SetupMissingErr: Label 'BCSentinel setup could not be loaded in the Monitoring background session.';
    begin
        if not Setup.Get('SETUP') then
            Error(SetupMissingErr);

        DeepScanMgt.QueueDeepScanInBackground(Setup);
    end;
}
