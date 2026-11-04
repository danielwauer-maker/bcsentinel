pageextension 53164 "DH Setup Pilot Actions" extends "DH Setup"
{
    actions
    {
        modify(RegisterTenant)
        {
            Visible = false;
        }

        addafter(RegisterTenant)
        {
            action(RegisterTenantCurrent)
            {
                Caption = 'Register Tenant';
                ToolTip = 'Registers this Business Central tenant with BCSentinel using the current Extension version and pilot invite code.';
                ApplicationArea = All;
                Image = Web;
                Promoted = true;
                PromotedCategory = Process;
                Visible = ShowRegisterTenantAction;

                trigger OnAction()
                var
                    RegistrationClient: Codeunit "DH Tenant Registration Client";
                    ApiClient: Codeunit "DH API Client";
                    SecretMgt: Codeunit "DH Secret Mgt.";
                begin
                    if Rec.Registered and SecretMgt.HasApiToken(Rec) then begin
                        Message('BCSentinel tenant is already registered.');
                        exit;
                    end;

                    Message('BCSentinel tenant registration started.');
                    RegistrationClient.RegisterTenant(Rec);
                    ApiClient.RefreshLicenseStatus(Rec);
                    UpdatePilotActionVisibility();
                    CurrPage.Update(false);
                    Message('BCSentinel tenant registration completed.');
                end;
            }
        }

        addafter(RegisterTenantCurrent)
        {
            action(RunFreeScan)
            {
                Caption = 'Run Free Scan';
                ToolTip = 'Starts the one initial BCSentinel Free Entry Data Health Scan. This consumes the available free scan credit.';
                ApplicationArea = All;
                Image = Start;
                Promoted = true;
                PromotedCategory = Process;
                Visible = ShowFreeScanAction;

                trigger OnAction()
                var
                    Setup: Record "DH Setup";
                    DeepScanMgt: Codeunit "DH Deep Scan Mgt.";
                    ConfirmStartScanQst: Label 'Start your one-time Free Data Health Scan now? This will consume the free scan credit and may affect performance during live operations.';
                begin
                    if not Rec.Registered or (Rec."Tenant ID" = '') then
                        Error('Please register the tenant first.');
                    if not Confirm(ConfirmStartScanQst, false) then
                        exit;

                    Setup := Rec;
                    DeepScanMgt.QueueDeepScan(Setup);
                    Rec.Get('SETUP');
                    UpdatePilotActionVisibility();
                    CurrPage.Update(false);
                end;
            }
        }

        modify(StartScan)
        {
            Visible = false;
        }

        addafter(StartScan)
        {
            action(RunDataHealthScan)
            {
                Caption = 'Run Data Health Scan';
                ToolTip = 'Runs the BCSentinel Data Health Scan using the current product access for this tenant.';
                ApplicationArea = All;
                Image = Start;
                Promoted = true;
                PromotedCategory = Process;
                Visible = ShowOtherScanAction;

                trigger OnAction()
                var
                    Setup: Record "DH Setup";
                    DeepScanMgt: Codeunit "DH Deep Scan Mgt.";
                    ConfirmStartScanQst: Label 'Do you want to start the Data Health Scan now? Performance may be affected during live operations. We recommend running the scan outside business hours.';
                begin
                    if not Rec.Registered or (Rec."Tenant ID" = '') then
                        Error('Please register the tenant first.');

                    Setup := Rec;
                    if not Confirm(ConfirmStartScanQst, false) then
                        exit;

                    DeepScanMgt.QueueDeepScan(Setup);
                    CurrPage.Update(false);
                end;
            }
        }
    }

    var
        ShowRegisterTenantAction: Boolean;
        ShowFreeScanAction: Boolean;
        ShowOtherScanAction: Boolean;

    trigger OnOpenPage()
    begin
        UpdatePilotActionVisibility();
    end;

    trigger OnAfterGetCurrRecord()
    begin
        UpdatePilotActionVisibility();
    end;

    local procedure UpdatePilotActionVisibility()
    begin
        ShowRegisterTenantAction := not Rec.Registered and (Rec."Tenant ID" = '');
        ShowFreeScanAction := Rec.Registered and (Rec."Tenant ID" <> '') and
            (Rec."Scan Credits Available" > 0) and not Rec."Monitoring Active" and
            (LowerCase(Rec."Product Access Model") in ['none', 'free', '']);
        ShowOtherScanAction := Rec.Registered and (Rec."Tenant ID" <> '') and
            Rec."Can Run Deep Scan" and not ShowFreeScanAction;
    end;
}
