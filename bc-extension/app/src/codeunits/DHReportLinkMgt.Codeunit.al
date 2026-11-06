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
