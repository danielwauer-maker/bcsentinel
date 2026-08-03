pageextension 53200 "DH Setup Monitoring Async" extends "DH Setup"
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
                ToolTip = 'Creates the Monitoring scan immediately and processes it in a background session so the Business Central client remains responsive.';
                Image = Start;
                ApplicationArea = All;
                Enabled = Rec."Monitoring Active" and (Rec."Tenant ID" <> '');
                Visible = Rec."Monitoring Active";
                Promoted = true;
                PromotedCategory = Process;

                trigger OnAction()
                var
                    Setup: Record "DH Setup";
                    DeepScanMgt: Codeunit "DH Deep Scan Mgt.";
                    StartConfirmQst: Label 'Do you want to start a Monitoring scan in the background?';
                    MonitoringScanStartedMsg: Label 'The Monitoring scan was created and started in the background. You can follow its progress in the scan history.';
                begin
                    if not Confirm(StartConfirmQst, false) then
                        exit;

                    Setup := Rec;
                    DeepScanMgt.QueueDeepScanInNewSession(Setup);
                    Message(MonitoringScanStartedMsg);
                end;
            }
        }
    }
}
