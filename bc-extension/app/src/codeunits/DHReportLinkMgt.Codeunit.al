codeunit 53200 "DH Report Link Mgt."
{
    procedure OpenBestAvailableReport(ScanId: Code[50]; ReportType: Text)
    var
        AccessClient: Codeunit "DH Report Access Client";
        ReportVariant: Text;
    begin
        ReportVariant := AccessClient.GetPreferredReportVariant(ScanId);
        OpenReport(ScanId, ReportVariant, ReportType);
    end;

    procedure OpenReport(ScanId: Code[50]; ReportVariant: Text; ReportType: Text)
    var
        Setup: Record "DH Setup";
        ReportUrl: Text;
    begin
        LoadSetup(Setup);
        ReportUrl := GetReportShareUrl(Setup, ScanId, ReportVariant, ReportType);
        Hyperlink(ReportUrl);
    end;

    procedure GetReportShareUrl(var Setup: Record "DH Setup"; ScanId: Code[50]; ReportVariant: Text; ReportType: Text): Text
    var
        Client: HttpClient;
        Content: HttpContent;
        ContentHeaders: HttpHeaders;
        RequestHeaders: HttpHeaders;
        Response: HttpResponseMessage;
        JsonRequest: JsonObject;
        JsonResponse: JsonObject;
        JsonTokenValue: JsonToken;
        RequestText: Text;
        ResponseText: Text;
        ApiToken: Text;
        Url: Text;
        ApiClient: Codeunit "DH API Client";
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        ValidateReportVariant(ReportVariant);
        ValidateReportType(ReportType);

        if ScanId = '' then
            Error('No completed BCSentinel scan is selected.');

        if Setup."Tenant ID" = '' then
            Error('BCSentinel tenant registration is required before opening a report.');

        ApiToken := SecretMgt.GetApiToken(Setup);
        if ApiToken = '' then
            Error('The BCSentinel API token is missing. Please register the tenant again.');

        JsonRequest.Add('report_type', LowerCase(ReportType));
        JsonRequest.WriteTo(RequestText);
        Content.WriteFrom(RequestText);
        Content.GetHeaders(ContentHeaders);
        ContentHeaders.Clear();
        ContentHeaders.Add('Content-Type', 'application/json');

        RequestHeaders := Client.DefaultRequestHeaders();
        RequestHeaders.Add('X-Tenant-Id', Setup."Tenant ID");
        RequestHeaders.Add('X-Api-Token', ApiToken);

        Url := BuildUrl(Setup."API Base URL", '/reports/' + ReportVariant + '/' + Format(ScanId) + '/share-link');
        if not Client.Post(Url, Content, Response) then
            Error('The BCSentinel report request could not be sent. Please verify the network connection.');

        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error('BCSentinel report access failed. Status %1. %2', Response.HttpStatusCode(), ApiClient.GetSafeBackendErrorText(ResponseText));

        if not JsonResponse.ReadFrom(ResponseText) then
            Error('BCSentinel returned an invalid report-link response.');

        if not JsonResponse.Get('url', JsonTokenValue) then
            Error('BCSentinel did not return a report URL.');

        if JsonTokenValue.AsValue().AsText() = '' then
            Error('BCSentinel returned an empty report URL.');

        exit(JsonTokenValue.AsValue().AsText());
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

    local procedure ValidateReportVariant(ReportVariant: Text)
    begin
        if not (ReportVariant in ['free-health', 'quick-assessment', 'assessment', 'validation']) then
            Error('Unsupported BCSentinel report variant.');
    end;

    local procedure ValidateReportType(ReportType: Text)
    begin
        if not (LowerCase(ReportType) in ['html', 'pdf']) then
            Error('Unsupported BCSentinel report format.');
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
