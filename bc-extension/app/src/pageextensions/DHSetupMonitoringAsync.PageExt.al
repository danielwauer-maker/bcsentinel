pageextension 53199 "DH Setup Monitoring Async" extends "DH Setup"
{
    actions
    {
        modify(StartMonitoringScan)
        {
            Visible = false;
        }

        addafter(StartMonitoringScan)
        {
            action(StartMonitoringScanAsync)
            {
                Caption = 'Start Monitoring Scan';
                ToolTip = 'Starts the Monitoring scan in a background session so the Business Central client remains responsive.';
                Image = Start;
                ApplicationArea = All;
                Enabled = Rec."Monitoring Active" and (Rec."Tenant ID" <> '');
                Visible = Rec."Monitoring Active";
                Promoted = true;
                PromotedCategory = Process;

                trigger OnAction()
                var
                    Setup: Record "DH Setup";
                    DeepScanRun: Record "DH Deep Scan Run";
                    DeepScanMgt: Codeunit "DH Deep Scan Mgt.";
                    EntryNo: Integer;
                    MonitoringScanStartedMsg: Label 'The Monitoring scan was started in the background. You can follow its progress in the scan history.';
                begin
                    Setup := Rec;
                    EntryNo := DeepScanMgt.QueueDeepScanInNewSession(Setup);
                    if EntryNo = 0 then
                        exit;

                    if Rec.Get('SETUP') then
                        CurrPage.Update(false);

                    Message(MonitoringScanStartedMsg);

                    if DeepScanRun.Get(EntryNo) then
                        Page.Run(Page::"DH Deep Scan Monitor", DeepScanRun);
                end;
            }
        }
    }
}
