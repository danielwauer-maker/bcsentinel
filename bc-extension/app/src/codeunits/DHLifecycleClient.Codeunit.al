codeunit 53140 "DH Lifecycle Client"
{
    procedure SyncProfile(var Setup: Record "DH Setup")
    var
        Client: HttpClient;
        Content: HttpContent;
        ContentHeaders: HttpHeaders;
        RequestHeaders: HttpHeaders;
        Response: HttpResponseMessage;
        RequestJson: JsonObject;
        RequestText: Text;
        ResponseText: Text;
        SecretMgt: Codeunit "DH Secret Mgt.";
        LanguageCode: Text;
    begin
        if Setup."Tenant ID" = '' then
            Error('Please register the tenant first.');
        if not SecretMgt.HasApiToken(Setup) then
            Error('The API token is missing. Please register the tenant again.');
        if Setup."Report Notification Email" = '' then
            Error('Please enter the Report & Notification Email first.');

        LanguageCode := LowerCase(Setup."Preferred Report Language");
        if LanguageCode = '' then
            LanguageCode := GetSessionLanguage();
        if not (LanguageCode in ['de', 'en']) then
            LanguageCode := 'en';

        RequestJson.Add('primary_notification_email', Setup."Report Notification Email");
        RequestJson.Add('preferred_language', LanguageCode);
        RequestJson.WriteTo(RequestText);

        Content.WriteFrom(RequestText);
        Content.GetHeaders(ContentHeaders);
        ContentHeaders.Clear();
        ContentHeaders.Add('Content-Type', 'application/json');

        RequestHeaders := Client.DefaultRequestHeaders();
        RequestHeaders.Add('X-Tenant-Id', Setup."Tenant ID");
        RequestHeaders.Add('X-Api-Token', SecretMgt.GetApiToken(Setup));
        RequestHeaders.Add('X-Preferred-Language', LanguageCode);

        if not Client.Put(BuildUrl(Setup."API Base URL", '/tenant/lifecycle-profile'), Content, Response) then
            Error('The BCSentinel notification profile request could not be sent.');

        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error('BCSentinel notification profile synchronization failed. Status %1.', Response.HttpStatusCode());
    end;

    local procedure GetSessionLanguage(): Text
    begin
        case GlobalLanguage() of
            1031, 2055, 3079, 4103, 5127:
                exit('de');
            else
                exit('en');
        end;
    end;

    local procedure BuildUrl(BaseUrl: Text; RelativePath: Text): Text
    begin
        while (StrLen(BaseUrl) > 0) and (CopyStr(BaseUrl, StrLen(BaseUrl), 1) = '/') do
            BaseUrl := CopyStr(BaseUrl, 1, StrLen(BaseUrl) - 1);
        exit(BaseUrl + RelativePath);
    end;
}
