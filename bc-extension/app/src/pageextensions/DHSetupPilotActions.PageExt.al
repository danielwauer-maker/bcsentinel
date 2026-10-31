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
                    CurrPage.Update(false);
                    Message('BCSentinel tenant registration completed.');
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
}
