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
                    SessionId: Integer;
                    StartConfirmQst: Label 'Do you want to start a Monitoring scan in the background?';
                    MonitoringScanStartedMsg: Label 'The Monitoring scan was started in the background. You can follow its progress in the scan history.';
                    BackgroundSessionStartErr: Label 'The Monitoring scan could not be started in a background session. Please try again.';
                begin
                    if not Confirm(StartConfirmQst, false) then
                        exit;

                    Setup := Rec;
                    if not Session.StartSession(SessionId, Codeunit::"DH Manual Monitoring Background", CompanyName(), Setup) then
                        Error(BackgroundSessionStartErr);

                    Message(MonitoringScanStartedMsg);
                end;
            }
        }
    }
}
