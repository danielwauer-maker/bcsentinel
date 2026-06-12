page 53100 "DH Setup"
{
    PageType = Card;
    SourceTable = "DH Setup";
    Caption = 'BCSentinel Setup';
    ApplicationArea = All;
    UsageCategory = Administration;

    layout
    {
        area(Content)
        {
            group(Overview)
            {
                Caption = 'Overview';

                field(ProductAccessModel; Rec."Product Access Model")
                {
                    ApplicationArea = All;
                    Caption = 'Product Access';
                    ToolTip = 'Specifies Product Access.';
                    Editable = false;
                }

                field("Scan Credits Available"; Rec."Scan Credits Available")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Scan Credits Available.';
                    Editable = false;
                }

                field("Monitoring Active"; Rec."Monitoring Active")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Monitoring Active.';
                    Editable = false;
                }

                field("Dashboard Access Until"; Rec."Dashboard Access Until")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Dashboard Access Until.';
                    Editable = false;
                }

                field("Issue Access Until"; Rec."Issue Access Until")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Issue Access Until.';
                    Editable = false;
                }

                field("Can Run Deep Scan"; Rec."Can Run Deep Scan")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Can Run Deep Scan.';
                    Editable = false;
                }

                field("Last License Check"; Rec."Last License Check")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Last License Check.';
                    Editable = false;
                }

                field(FeatureAccess; Rec.GetFeatureAccessText())
                {
                    ApplicationArea = All;
                    Caption = 'Feature access';
                    Editable = false;
                    ToolTip = 'Shows whether paid scan access is available.';
                }
            }

            group(General)
            {
                Caption = 'General';

                field("API Base URL"; Rec."API Base URL")
                {
                    ApplicationArea = All;
                    Editable = true;
                    ToolTip = 'Base URL of the BCSentinel API. Default is production.';
                }

                field("Tenant ID"; Rec."Tenant ID")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Tenant ID.';
                    Editable = false;
                    Visible = false;
                }

                field(ApiTokenConfigured; HasStoredApiToken())
                {
                    ApplicationArea = All;
                    Caption = 'API Token Configured';
                    Editable = false;
                    ToolTip = 'Shows whether the API token is stored securely for this company. The token itself is not displayed.';
                }

                field("Registration Invite Code"; Rec."Registration Invite Code")
                {
                    ApplicationArea = All;
                    ExtendedDatatype = Masked;
                    ToolTip = 'Specifies the BCSentinel pilot invite code. Current backend registration requires this code; AppSource self-service signup is a follow-up backend task.';
                }

                field(Registered; Rec.Registered)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Registered.';
                    Editable = false;
                }

                field("Registration Date"; Rec."Registration Date")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies Registration Date.';
                    Editable = false;
                }

                field("Data Processing Consent"; Rec."Data Processing Consent")
                {
                    ApplicationArea = All;
                    ToolTip = 'Confirms that BCSentinel may send tenant and company identifiers, metadata, configuration data, scan results, findings, and aggregated quality metrics to BCSentinel for data health analysis, dashboards, executive reports, and license or credit checks. API tokens are stored securely and are not included in reports or share URLs. Review the privacy policy and terms before enabling consent.';
                }

                field(DataProcessingNotice; DataProcessingNoticeTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Data Processing Notice';
                    Editable = false;
                    MultiLine = true;
                    ToolTip = 'Explains which data BCSentinel sends to the backend and why consent is required.';
                }

                field(InviteNotice; InviteNoticeTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Onboarding Notice';
                    Editable = false;
                    MultiLine = true;
                    ToolTip = 'Explains the current pilot invite requirement for tenant registration.';
                }
            }

            group("Enabled Scan Modules")
            {
                Caption = 'Enabled Scan Modules';

                field("Scan System Module"; Rec."Scan System Module")
                {
                    ApplicationArea = All;
                    ToolTip = 'Include system and setup checks in the deep scan.';
                }

                field("Scan Finance Module"; Rec."Scan Finance Module")
                {
                    ApplicationArea = All;
                    ToolTip = 'Include finance-related checks in the deep scan.';
                }

                field("Scan Sales Module"; Rec."Scan Sales Module")
                {
                    ApplicationArea = All;
                    ToolTip = 'Include sales-related checks in the deep scan.';
                }

                field("Scan Purchasing Module"; Rec."Scan Purchasing Module")
                {
                    ApplicationArea = All;
                    ToolTip = 'Include purchasing-related checks in the deep scan.';
                }

                field("Scan Inventory Module"; Rec."Scan Inventory Module")
                {
                    ApplicationArea = All;
                    ToolTip = 'Include inventory-related checks in the deep scan.';
                }

                field("Scan CRM Module"; Rec."Scan CRM Module")
                {
                    ApplicationArea = All;
                    ToolTip = 'Include CRM/contact-related checks in the deep scan.';
                }

                field("Scan Manufacturing Module"; Rec."Scan Manufacturing Module")
                {
                    ApplicationArea = All;
                    ToolTip = 'Include manufacturing and production master data checks in the deep scan.';
                }

                field("Scan Service Module"; Rec."Scan Service Module")
                {
                    ApplicationArea = All;
                    ToolTip = 'Include service-related checks in the deep scan.';
                }

                field("Scan Jobs Module"; Rec."Scan Jobs Module")
                {
                    ApplicationArea = All;
                    ToolTip = 'Include jobs and project-related checks in the deep scan.';
                }

                field("Scan HR Module"; Rec."Scan HR Module")
                {
                    ApplicationArea = All;
                    ToolTip = 'Include employee and resource-related checks in the deep scan.';
                }
            }

            group(Scan)
            {
                Caption = 'Last Scan';

                field("Last Scan Date 2"; Rec."Last Scan Date")
                {
                    ApplicationArea = All;
                    Caption = 'Last Scan Date';
                    ToolTip = 'Specifies Last Scan Date.';
                    Editable = false;
                    Visible = false;
                }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(TestConnection)
            {
                Caption = 'Test BCSentinel Connection';
                ToolTip = 'Runs Test BCSentinel Connection.';
                ApplicationArea = All;
                Image = TestFile;

                trigger OnAction()
                var
                    ApiClient: Codeunit "DH API Client";
                begin
                    ApiClient.TestConnection(Rec);
                end;
            }

            action(RegisterTenant)
            {
                Caption = 'Register Tenant';
                ToolTip = 'Registers this Business Central tenant with BCSentinel by using the API Base URL and invite code, if required.';
                ApplicationArea = All;
                Image = Web;
                Enabled = CanRegisterTenant;
                Visible = true;
                Promoted = true;
                PromotedCategory = Process;
                PromotedOnly = false;

                trigger OnAction()
                var
                    ApiClient: Codeunit "DH API Client";
                begin
                    if Rec.Registered then begin
                        if HasStoredApiToken() then begin
                            Message('BCSentinel tenant is already registered.');
                            exit;
                        end;

                        Message('BCSentinel registration data is incomplete. Registration will request a fresh API token.');
                    end;

                    Message('BCSentinel tenant registration started.');
                    ApiClient.RegisterTenant(Rec);
                    ApiClient.RefreshLicenseStatus(Rec);
                    UpdateActionState();
                    CurrPage.Update(false);
                    Message('BCSentinel tenant registration completed.');
                end;
            }

            action(ResetRegistration)
            {
                Caption = 'Reset Registration';
                ToolTip = 'Clears only the local BCSentinel registration state and stored API token so the tenant can be registered again. Backend data is not deleted.';
                ApplicationArea = All;
                Image = ResetStatus;
                Enabled = CanResetRegistration;
                Visible = true;
                Promoted = true;
                PromotedCategory = Process;
                PromotedOnly = false;

                trigger OnAction()
                var
                    ResetRegistrationQst: Label 'Reset the local BCSentinel registration state? This keeps the API Base URL, invite code, and consent. Backend data is not deleted.';
                begin
                    if not Confirm(ResetRegistrationQst, false) then
                        exit;

                    ResetLocalRegistrationState();
                    UpdateActionState();
                    CurrPage.Update(false);
                    Message('Local BCSentinel registration was reset. Please register again.');
                end;
            }

            action(RequestAccess)
            {
                Caption = 'Request Access';
                ToolTip = 'Opens the BCSentinel website to request onboarding access.';
                ApplicationArea = All;
                Image = LinkWeb;

                trigger OnAction()
                begin
                    Hyperlink('https://bcsentinel.com');
                end;
            }

            action(BuyAssessment)
            {
                Caption = 'Buy Assessment';
                ApplicationArea = All;
                Image = Add;
                ToolTip = 'Open the secure BCSentinel checkout for the Assessment one-time scan.';

                trigger OnAction()
                var
                    ApiClient: Codeunit "DH API Client";
                begin
                    ApiClient.OpenProductCheckout(Rec, 'assessment');
                end;
            }

            action(BuyValidationCheck)
            {
                Caption = 'Buy Validation Check';
                ApplicationArea = All;
                Image = Add;
                ToolTip = 'Open the secure BCSentinel checkout for a Validation Check follow-up scan.';

                trigger OnAction()
                var
                    ApiClient: Codeunit "DH API Client";
                begin
                    ApiClient.OpenProductCheckout(Rec, 'validation_check');
                end;
            }

            action(StartMonitoringMonthly)
            {
                Caption = 'Start Monitoring Monthly';
                ApplicationArea = All;
                Image = Add;
                ToolTip = 'Open the secure BCSentinel checkout for monthly monitoring.';

                trigger OnAction()
                var
                    ApiClient: Codeunit "DH API Client";
                begin
                    ApiClient.OpenProductCheckout(Rec, 'monitoring_monthly');
                end;
            }

            action(StartMonitoringAnnual)
            {
                Caption = 'Start Monitoring Annual';
                ApplicationArea = All;
                Image = Add;
                ToolTip = 'Open the secure BCSentinel checkout for annual monitoring.';

                trigger OnAction()
                var
                    ApiClient: Codeunit "DH API Client";
                begin
                    ApiClient.OpenProductCheckout(Rec, 'monitoring_annual');
                end;
            }

            action(RefreshLicenseStatus)
            {
                Caption = 'Refresh Product Access';
                ApplicationArea = All;
                Image = Refresh;
                ToolTip = 'Refresh scan credits, monitoring status, and product access from BCSentinel.';

                trigger OnAction()
                var
                    ApiClient: Codeunit "DH API Client";
                begin
                    if Rec."Tenant ID" = '' then
                        Error('Please register the tenant first.');

                    ApiClient.RefreshLicenseStatus(Rec);
                    CurrPage.Update(false);
                    Message('Product access refreshed.');
                end;
            }

            group(ScanMenu)
            {
                Caption = 'Scan';
                Image = Start;

                action(StartScan)
                {
                    Caption = 'Start Scan';
                    ToolTip = 'Runs Start Scan.';
                    Image = Start;
                    ApplicationArea = All;

                    trigger OnAction()
                    var
                        Setup: Record "DH Setup";
                        ApiClient: Codeunit "DH API Client";
                        DeepScanMgt: Codeunit "DH Deep Scan Mgt.";
                        ConfirmStartScanQst: Label 'Do you want to start the scan now? Performance may be affected during live operations. We recommend running the scan outside business hours.';
                    begin
                        EnsureSetupExists();
                        Setup := Rec;
                        ApiClient.EnsureReadyForScan(Setup);

                        if not Confirm(ConfirmStartScanQst, false) then
                            exit;

                        DeepScanMgt.QueueDeepScan(Setup);
                        CurrPage.Update(false);
                    end;
                }

                action(ViewScanHistory)
                {
                    Caption = 'Scan History';
                    ToolTip = 'Runs Scan History.';
                    Image = List;
                    ApplicationArea = All;

                    trigger OnAction()
                    begin
                        Page.Run(Page::"DH Deep Scan Runs");
                    end;
                }
            }
        }
    }

    var
        CanRegisterTenant: Boolean;
        CanResetRegistration: Boolean;
        DataProcessingNoticeTxt: Text[1024];
        InviteNoticeTxt: Text[512];

    trigger OnOpenPage()
    begin
        EnsureSetupExists();
        UpdateActionState();
        UpdateNoticeTexts();
        //RefreshLicenseSilently();
        CurrPage.Update(false);
    end;

    trigger OnAfterGetCurrRecord()
    begin
        UpdateActionState();
        UpdateNoticeTexts();
    end;

    local procedure EnsureSetupExists()
    begin
        if not Rec.Get('SETUP') then begin
            Rec.Init();
            Rec."Primary Key" := 'SETUP';
            Rec.Insert(true);
        end;

        Rec.ApplyDefaults();
        Rec.Modify(true);
    end;

    local procedure HasStoredApiToken(): Boolean
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        exit(SecretMgt.HasApiToken(Rec));
    end;

    local procedure DeleteStoredApiToken()
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        SecretMgt.DeleteApiToken(Rec);
    end;

    local procedure ResetLocalRegistrationState()
    begin
        Rec."Tenant ID" := '';
        Rec.Registered := false;
        Rec."Registration Date" := 0DT;
        DeleteStoredApiToken();
        Rec.Modify(true);
    end;

    local procedure RefreshLicenseSilently()
    var
        ApiClient: Codeunit "DH API Client";
    begin
        if Rec."Tenant ID" = '' then
            exit;

        ApiClient.RefreshLicenseStatus(Rec);
    end;

    local procedure UpdateActionState()
    begin
        CanRegisterTenant := Rec."Data Processing Consent" and (Rec."API Base URL" <> '');
        CanResetRegistration :=
            Rec.Registered or
            (Rec."Tenant ID" <> '') or
            (Rec."Registration Date" <> 0DT) or
            HasStoredApiToken();
    end;

    local procedure UpdateNoticeTexts()
    begin
        DataProcessingNoticeTxt :=
            'Before registration or scans, BCSentinel requires consent to send tenant and company identifiers, metadata, configuration data, scan results, findings, and aggregated quality metrics to BCSentinel. The data is used for Data Health analysis, dashboards, executive reports, and license or credit checks. API tokens are stored securely and are not included in reports or share URLs. Review the privacy policy and terms before enabling consent.';

        InviteNoticeTxt :=
            'Current pilot registration requires a BCSentinel invite code. AppSource self-service signup must be enabled in the backend before this field can be optional for marketplace customers.';
    end;

    local procedure GetTokenUrl(var Setup: Record "DH Setup"): Text
    begin
        if Setup."API Base URL" = '' then
            Error('Please configure the API Base URL first.');

        if Setup."Tenant ID" = '' then
            Error('Tenant is not registered yet.');

        exit(RemoveTrailingSlash(Setup."API Base URL") + '/analytics/get-token?company=' + EncodeUrlValue(CompanyName()) + '&environment=' + EncodeUrlValue('BC Cloud') + '&tenant_id=' + EncodeUrlValue(Setup."Tenant ID") + '&scan_mode=' + EncodeUrlValue(GetScanMode(Setup)) + '&bc_issue_launch_url=' + EncodeUrlValue(GetIssueDrilldownLaunchUrl()));
    end;

    local procedure GetScanMode(var Setup: Record "DH Setup"): Text
    begin
        if Setup."Premium Enabled" then
            exit('premium_deep');
        exit('free_deep');
    end;

    local procedure GetDashboardUrl(var Setup: Record "DH Setup"; Token: Text): Text
    begin
        exit(RemoveTrailingSlash(Setup."API Base URL") + '/analytics/embed?embed_token=' + EncodeUrlValue(Token));
    end;

    local procedure GetIssueDrilldownLaunchUrl(): Text
    begin
        exit(GetUrl(ClientType::Web, CompanyName(), ObjectType::Page, Page::"DH Issue Drilldown Launch"));
    end;

    local procedure ExtractTokenFromJson(JsonText: Text): Text
    var
        JsonObj: JsonObject;
        JsonToken: JsonToken;
    begin
        if not JsonObj.ReadFrom(JsonText) then
            Error('The token response is not valid JSON.');

        if not JsonObj.Get('token', JsonToken) then
            Error('The token field is missing in the response.');

        exit(JsonToken.AsValue().AsText());
    end;

    local procedure RemoveTrailingSlash(Value: Text): Text
    begin
        while (StrLen(Value) > 0) and (CopyStr(Value, StrLen(Value), 1) = '/') do
            Value := CopyStr(Value, 1, StrLen(Value) - 1);
        exit(Value);
    end;

    local procedure EncodeUrlValue(Value: Text): Text
    begin
        Value := Value.Replace('%', '%25');
        Value := Value.Replace(' ', '%20');
        Value := Value.Replace('&', '%26');
        Value := Value.Replace('?', '%3F');
        Value := Value.Replace('=', '%3D');
        Value := Value.Replace('#', '%23');
        Value := Value.Replace('+', '%2B');
        Value := Value.Replace('/', '%2F');
        exit(Value);
    end;
}

