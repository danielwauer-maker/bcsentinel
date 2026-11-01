codeunit 53202 "DH Report Access Client"
{
    procedure GetPreferredReportVariant(ScanId: Code[50]): Text
    var
        Setup: Record "DH Setup";
        Client: HttpClient;
        RequestHeaders: HttpHeaders;
        Response: HttpResponseMessage;
        ResponseText: Text;
        JsonResponse: JsonObject;
        JsonTokenValue: JsonToken;
        ApiToken: Text;
        Url: Text;
        ApiClient: Codeunit "DH API Client";
        SecretMgt: Codeunit "DH Secret Mgt.";
        Variant: Text;
    begin
        if ScanId = '' then
            Error('No completed BCSentinel scan is selected.');

        if not Setup.Get('SETUP') then
            Error('BCSentinel setup was not found.');
        Setup.ApplyDefaults();

        if Setup."Tenant ID" = '' then
            Error('BCSentinel tenant registration is required before opening a report.');

        ApiToken := SecretMgt.GetApiToken(Setup);
        if ApiToken = '' then
            Error('The BCSentinel API token is missing. Please register the tenant again.');

        RequestHeaders := Client.DefaultRequestHeaders();
        RequestHeaders.Add('X-Tenant-Id', Setup."Tenant ID");
        RequestHeaders.Add('X-Api-Token', ApiToken);

        Url := BuildUrl(Setup."API Base URL", '/reports/' + Format(ScanId) + '/preferred-variant');
        if not Client.Get(Url, Response) then
            Error('The BCSentinel report access request could not be sent. Please verify the network connection.');

        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error('BCSentinel report access failed. Status %1. %2', Response.HttpStatusCode(), ApiClient.GetSafeBackendErrorText(ResponseText));

        if not JsonResponse.ReadFrom(ResponseText) then
            Error('BCSentinel returned an invalid report-access response.');

        if not JsonResponse.Get('report_variant', JsonTokenValue) then
            Error('BCSentinel did not return a preferred report variant.');

        Variant := LowerCase(JsonTokenValue.AsValue().AsText());
        if not (Variant in ['free-health', 'quick-assessment', 'assessment', 'validation']) then
            Error('BCSentinel returned an unsupported report variant.');

        exit(Variant);
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
