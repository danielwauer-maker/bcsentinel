codeunit 53201 "DH Manual Monitoring Background"
{
    TableNo = "DH Setup";

    trigger OnRun()
    var
        DeepScanMgt: Codeunit "DH Deep Scan Mgt.";
    begin
        if not Rec.Get('SETUP') then
            exit;

        DeepScanMgt.QueueDeepScanInBackground(Rec);
    end;
}
