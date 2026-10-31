codeunit 53139 "DH Tenant Registration Client"
{
    Permissions = tabledata "DH Setup" = RM;

    procedure RegisterTenant(var Setup: Record "DH Setup")
    var
        Client: HttpClient;
        Content: HttpContent;
        ContentHeaders: HttpHeaders;
        Response: HttpResponseMessage;
        RequestText: Text;
        ResponseText: Text;
        JsonRequest: JsonObject;
        JsonResponse: JsonObject;
        Token: JsonToken;
        TenantId: Text;
        ApiToken: Text;
        SecretMgt: Codeunit "DH Secret Mgt.";
        ApiClient: Codeunit "DH API Client";
    begin
        EnsureSetupLoaded(Setup);

        if Setup."API Base URL" = '' then
            Error('Please configure the API Base URL first.');

        if not Setup."Data Processing Consent" then
            Error('Please enable Data Processing Consent before registering the tenant.');

        JsonRequest.Add('environment_name', 'BC Cloud');
        JsonRequest.Add('app_version', '1.0.2.27');
        JsonRequest.Add('preferred_language', GetPreferredLanguage());
        JsonRequest.Add('invite_code', Setup."Registration Invite Code");
        JsonRequest.WriteTo(RequestText);

        Content.WriteFrom(RequestText);
        Content.GetHeaders(ContentHeaders);
        ContentHeaders.Clear();
        ContentHeaders.Add('Content-Type', 'application/json');

        if not Client.Post(BuildUrl(Setup."API Base URL", '/tenant/register'), Content, Response) then
            Error('The backend request could not be sent. Please verify the network connection.');

        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error('Tenant registration failed. Status %1. %2', Response.HttpStatusCode(), ApiClient.GetSafeBackendErrorText(ResponseText));

        if not JsonResponse.ReadFrom(ResponseText) then
            Error('The backend returned an invalid JSON response. Contact BCSentinel support if this continues.');

        if JsonResponse.Get('tenant_id', Token) then
            TenantId := GetJsonTokenText(Token);
        if JsonResponse.Get('api_token', Token) then
            ApiToken := GetJsonTokenText(Token);

        if TenantId = '' then
            Error('The backend response does not contain a tenant_id.');
        if ApiToken = '' then
            Error('The backend response does not contain an api_token.');

        Setup.Validate("Tenant ID", CopyStr(TenantId, 1, MaxStrLen(Setup."Tenant ID")));
        SecretMgt.StoreApiToken(Setup, ApiToken);
        Setup.Registered := true;
        Setup."Registration Date" := CurrentDateTime();
        Setup.Modify(true);
    end;

    local procedure EnsureSetupLoaded(var Setup: Record "DH Setup")
    begin
        if not Setup.Get('SETUP') then begin
            Setup.Init();
            Setup."Primary Key" := 'SETUP';
            Setup.Insert(true);
        end;

        Setup.ApplyDefaults();
        Setup.Modify(true);
    end;

    local procedure GetPreferredLanguage(): Text
    var
        LanguageId: Integer;
    begin
        LanguageId := GlobalLanguage();
        case LanguageId of
            1031, 2055, 3079, 4103, 5127:
                exit('de');
            else
                exit('en');
        end;
    end;

    local procedure GetJsonTokenText(Token: JsonToken): Text
    var
        JsonValueText: Text;
    begin
        JsonValueText := LowerCase(Format(Token));
        if (JsonValueText = 'null') or (JsonValueText = '') then
            exit('');
        exit(Token.AsValue().AsText());
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
}
