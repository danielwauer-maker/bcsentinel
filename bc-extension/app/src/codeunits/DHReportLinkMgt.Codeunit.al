codeunit 53303 "DH Report Link Mgt."
{
    procedure OpenArchivedFullV6(ScanId: Code[50])
    var
        Setup: Record "DH Setup";
        Client: HttpClient;
        Content: HttpContent;
        ContentHeaders: HttpHeaders;
        Headers: HttpHeaders;
        Response: HttpResponseMessage;
        ResponseText: Text;
        ResponseJson: JsonObject;
        UrlToken: JsonToken;
        SecretMgt: Codeunit "DH Secret Mgt.";
        ApiClient: Codeunit "DH API Client";
        ApiToken: Text;
        Url: Text;
    begin
        if ScanId = '' then
            Error('Please select a completed scan with a backend scan ID.');

        LoadSetup(Setup);
        if Setup."Tenant ID" = '' then
            Error('BCSentinel tenant registration is required.');
        ApiToken := SecretMgt.GetApiToken(Setup);
        if ApiToken = '' then
            Error('BCSentinel tenant token is missing.');

        Content.WriteFrom('{}');
        Content.GetHeaders(ContentHeaders);
        ContentHeaders.Clear();
        ContentHeaders.Add('Content-Type', 'application/json');

        Headers := Client.DefaultRequestHeaders();
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', ApiToken);
        Url := BuildUrl(Setup."API Base URL", '/reports/executive/' + Format(ScanId) + '/v6-link');
        if not Client.Post(Url, Content, Response) then
            Error('BCSentinel report history is temporarily unavailable.');

        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error('BCSentinel report access failed (HTTP %1). %2',
                Response.HttpStatusCode(), ApiClient.GetSafeBackendErrorText(ResponseText));
        if not ResponseJson.ReadFrom(ResponseText) then
            Error('Invalid BCSentinel report link response.');
        if not ResponseJson.Get('url', UrlToken) then
            Error('The BCSentinel report link is missing.');
        Url := UrlToken.AsValue().AsText();
        if Url = '' then
            Error('The BCSentinel report link is empty.');
        Hyperlink(Url);
    end;

    procedure ReviewScopeAndOpenFullV6(ScanId: Code[50])
    var
        Setup: Record "DH Setup";
        SecretMgt: Codeunit "DH Secret Mgt.";
        ApiClient: Codeunit "DH API Client";
        ScopeReview: Page "DH Assessment Scope Review";
        Client: HttpClient;
        Headers: HttpHeaders;
        Response: HttpResponseMessage;
        Payload: JsonObject;
        RequestJson: JsonObject;
        Token: JsonToken;
        RequestText: Text;
        ResponseText: Text;
        ApiToken: Text;
        ApiUrl: Text;
        Content: HttpContent;
        ContentHeaders: HttpHeaders;
    begin
        if ScanId = '' then
            Error('Select an original completed Free scan.');
        LoadSetup(Setup);
        ApiToken := SecretMgt.GetApiToken(Setup);
        if (Setup."Tenant ID" = '') or (ApiToken = '') then
            Error('BCSentinel registration and token are required.');

        Headers := Client.DefaultRequestHeaders();
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', ApiToken);

        ApiUrl := BuildUrl(Setup."API Base URL", '/scans/' + Format(ScanId) + '/assessment-scope');
        if not Client.Get(ApiUrl, Response) then
            Error('Could not load the BCSentinel assessment scope.');
        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error('Assessment scope unavailable (HTTP %1). %2',
                Response.HttpStatusCode(), ApiClient.GetSafeBackendErrorText(ResponseText));
        if not Payload.ReadFrom(ResponseText) then
            Error('Invalid assessment scope response.');

        if Payload.Get('state', Token) and (Token.AsValue().AsText() = 'confirmed') then begin
            // Already confirmed: never rewrite the baseline.
            OpenArchivedFullV6(ScanId);
            exit;
        end;
        ScopeReview.LoadScope(ScanId, Payload);
        if ScopeReview.RunModal() <> Action::OK then
            exit;

        RequestJson := ScopeReview.GetConfirmationPayload();
        RequestJson.WriteTo(RequestText);
        Content.WriteFrom(RequestText);
        Content.GetHeaders(ContentHeaders);
        ContentHeaders.Clear();
        ContentHeaders.Add('Content-Type', 'application/json');
        ApiUrl := BuildUrl(Setup."API Base URL", '/scans/' + Format(ScanId) + '/assessment-scope/confirm');
        Clear(Response);
        if not Client.Post(ApiUrl, Content, Response) then
            Error('Could not confirm the BCSentinel assessment scope.');
        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error('Assessment confirmation failed (HTTP %1). %2',
                Response.HttpStatusCode(), ApiClient.GetSafeBackendErrorText(ResponseText));
        if not Payload.ReadFrom(ResponseText) then
            Error('Invalid assessment confirmation response.');
        if not Payload.Get('state', Token) then
            Error('Assessment confirmation state missing.');
        if Token.AsValue().AsText() <> 'confirmed' then
            Error('The BCSentinel assessment scope was not confirmed.');

        OpenArchivedFullV6(ScanId);
    end;

    procedure OpenReportVariantV2(ScanId: Code[50]; Variant: Text)
    var
        Setup: Record "DH Setup";
        SecretMgt: Codeunit "DH Secret Mgt.";
        ApiClient: Codeunit "DH API Client";
        Client: HttpClient;
        Headers: HttpHeaders;
        Content: HttpContent;
        ContentHeaders: HttpHeaders;
        Response: HttpResponseMessage;
        ResponseJson: JsonObject;
        UrlToken: JsonToken;
        ApiToken: Text;
        ResponseText: Text;
        Url: Text;
    begin
        if ScanId = '' then
            Error('Select a completed BCSentinel scan.');
        if (Variant <> 'validation') and (Variant <> 'monitoring') then
            Error('Unsupported BCSentinel report type.');

        LoadSetup(Setup);
        ApiToken := SecretMgt.GetApiToken(Setup);
        if (Setup."Tenant ID" = '') or (ApiToken = '') then
            Error('BCSentinel tenant registration and token are required.');
        Headers := Client.DefaultRequestHeaders();
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', ApiToken);

        Content.WriteFrom('{}');
        Content.GetHeaders(ContentHeaders);
        ContentHeaders.Clear();
        ContentHeaders.Add('Content-Type', 'application/json');
        Url := BuildUrl(Setup."API Base URL", '/reports/live/' + Variant + '/' + Format(ScanId) + '/link');
        if not Client.Post(Url, Content, Response) then
            Error('BCSentinel report link service is temporarily unavailable.');
        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error('BCSentinel report unavailable (HTTP %1). %2',
                Response.HttpStatusCode(), ApiClient.GetSafeBackendErrorText(ResponseText));
        if not ResponseJson.ReadFrom(ResponseText) then
            Error('Invalid BCSentinel report link response.');
        if not ResponseJson.Get('url', UrlToken) then
            Error('BCSentinel report link missing.');
        Url := UrlToken.AsValue().AsText();
        if Url = '' then
            Error('BCSentinel report link empty.');
        Hyperlink(Url);
    end;

    local procedure LoadSetup(var Setup: Record "DH Setup")
    begin
        if not Setup.Get('SETUP') then begin
            Setup.Init();
            Setup."Primary Key" := 'SETUP';
            Setup.Insert(true);
        end;
        Setup.ApplyDefaults();
    end;

    local procedure BuildUrl(BaseUrl: Text; Path: Text): Text
    var
        NormalizedBaseUrl: Text;
    begin
        NormalizedBaseUrl := BaseUrl;
        while (StrLen(NormalizedBaseUrl) > 0) and (CopyStr(NormalizedBaseUrl, StrLen(NormalizedBaseUrl), 1) = '/') do
            NormalizedBaseUrl := CopyStr(NormalizedBaseUrl, 1, StrLen(NormalizedBaseUrl) - 1);

        if NormalizedBaseUrl = '' then
            Error('Please configure the BCSentinel API Base URL first.');

        exit(NormalizedBaseUrl + Path);
    end;
}
