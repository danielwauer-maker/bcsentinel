page 53123 "DHM Analytics"
{
    PageType = Card;
    ApplicationArea = All;
    UsageCategory = None;
    Caption = 'DHM Analytics';

    layout
    {
        area(Content)
        {
            group(General)
            {
                Caption = 'Analytics';

                field(DescriptionTxt; DescriptionTxt)
                {
                    ApplicationArea = All;
                    Caption = 'Description';
                    ToolTip = 'Specifies Description.';
                    Editable = false;
                    MultiLine = true;
                }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(OpenDashboard)
            {
                ApplicationArea = All;
                Caption = 'Open Analytics Dashboard';
                Image = View;
                ToolTip = 'Opens the external Data Health Management Analytics dashboard.';

                trigger OnAction()
                var
                    Setup: Record "DH Setup";
                    ApiClient: Codeunit "DH API Client";
                    Token: Text;
                begin
                    LoadSetupOrError(Setup);

                    Token := ApiClient.GetAnalyticsDashboardToken(Setup);

                    if Token = '' then
                        Error('No valid token was found in the token service response.');

                    Hyperlink(GetDashboardUrl(Setup, Token));
                end;
            }
        }
    }

    var
        DescriptionTxt: Text[250];

    trigger OnOpenPage()
    var
        Setup: Record "DH Setup";
        BaseUrl: Text;
    begin
        DescriptionTxt := 'Opens the Data Health Management Analytics dashboard in a new browser tab.';

        if Setup.Get('SETUP') then begin
            BaseUrl := RemoveTrailingSlash(Setup."API Base URL");
            if BaseUrl <> '' then
                DescriptionTxt := StrSubstNo(
                    'Opens the Data Health Management Analytics dashboard in a new browser tab. Backend: %1',
                    CopyStr(BaseUrl, 1, 180));
        end;
    end;

    local procedure LoadSetupOrError(var Setup: Record "DH Setup")
    begin
        if not Setup.Get('SETUP') then
            Error('DH Setup was not found.');

        if Setup."API Base URL" = '' then
            Error('Please enter the API Base URL in DH Setup first.');

        if Setup."Tenant ID" = '' then
            Error('Please register the tenant in DH Setup first.');

        if GetApiToken(Setup) = '' then
            Error('Please register the tenant in DH Setup first so that an API token is stored.');
    end;

    local procedure RequestDashboardToken(var Setup: Record "DH Setup"): Text
    var
        Client: HttpClient;
        Request: HttpRequestMessage;
        Headers: HttpHeaders;
        Response: HttpResponseMessage;
        ResponseText: Text;
        ApiClient: Codeunit "DH API Client";
    begin
        Request.Method := 'GET';
        Request.SetRequestUri(GetTokenUrl(Setup));
        Request.GetHeaders(Headers);
        Headers.Clear();
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', GetApiToken(Setup));

        if not Client.Send(Request, Response) then
            Error('The token service could not be reached.');

        Response.Content().ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error(
                'The token service returned an error. Status: %1. %2',
                Response.HttpStatusCode(),
                ApiClient.GetSafeBackendErrorText(ResponseText));

        exit(ResponseText);
    end;


    local procedure GetTokenUrl(var Setup: Record "DH Setup"): Text
    var
        BaseUrl: Text;
        CompanyValue: Text;
        EnvironmentValue: Text;
        TenantValue: Text;
        ScanModeValue: Text;
    begin
        BaseUrl := BuildUrl(Setup."API Base URL", '/analytics/get-token');
        CompanyValue := EncodeUrlValue(CompanyName());
        EnvironmentValue := EncodeUrlValue('BC Cloud');
        TenantValue := EncodeUrlValue(Setup."Tenant ID");
        ScanModeValue := EncodeUrlValue(GetScanMode(Setup));

        exit(
            BaseUrl +
            '?company=' + CompanyValue +
            '&environment=' + EnvironmentValue +
            '&tenant_id=' + TenantValue +
            '&scan_mode=' + ScanModeValue +
            '&bc_issue_launch_url=' + EncodeUrlValue(GetIssueDrilldownLaunchUrl()));
    end;


    local procedure GetScanMode(var Setup: Record "DH Setup"): Text
    begin
        if Setup."Premium Enabled" then
            exit('premium_deep');

        exit('free_deep');
    end;

    local procedure GetIssueDrilldownLaunchUrl(): Text
    begin
        exit(GetUrl(ClientType::Web, CompanyName(), ObjectType::Page, Page::"DH Issue Drilldown Launch"));
    end;

    local procedure GetDashboardUrl(var Setup: Record "DH Setup"; Token: Text): Text
    var
        BaseUrl: Text;
    begin
        BaseUrl := BuildUrl(Setup."API Base URL", '/analytics/embed');
        exit(BaseUrl + '?embed_token=' + EncodeUrlValue(Token));
    end;

    local procedure ExtractTokenFromJson(JsonText: Text): Text
    var
        JsonObj: JsonObject;
        JsonToken: JsonToken;
    begin
        if not JsonObj.ReadFrom(JsonText) then
            Error('The token service response is not valid JSON.');

        if not JsonObj.Get('token', JsonToken) then
            Error('The field "token" is missing in the token service response.');

        exit(JsonToken.AsValue().AsText());
    end;

    local procedure BuildUrl(BaseUrl: Text; RelativePath: Text): Text
    begin
        exit(RemoveTrailingSlash(BaseUrl) + RelativePath);
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

    local procedure GetApiToken(var Setup: Record "DH Setup"): Text
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        exit(SecretMgt.GetApiToken(Setup));
    end;
}

