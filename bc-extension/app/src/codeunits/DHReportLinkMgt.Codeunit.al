codeunit 53303 "DH Report Link Mgt."
{
    procedure OpenArchivedFullV6(ScanId: Code[50])
    var
        Setup: Record "DH Setup";
        SecretMgt: Codeunit "DH Secret Mgt.";
        Client: HttpClient;
        Content: HttpContent;
        ContentHeaders: HttpHeaders;
        Headers: HttpHeaders;
        Response: HttpResponseMessage;
        ResponseText: Text;
        ResponseJson: JsonObject;
        UrlToken: JsonToken;
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
                Response.HttpStatusCode(), GetReportErrorText(ResponseText));
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

        ApiUrl := BuildUrl(Setup."API Base URL", '/scans/' + Format(ScanId) + '/report-preflight');
        if not Client.Get(ApiUrl, Response) then
            Error('Could not load the BCSentinel assessment scope.');
        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error('Assessment scope unavailable (HTTP %1). %2',
                Response.HttpStatusCode(), GetReportErrorText(ResponseText));
        if not Payload.ReadFrom(ResponseText) then
            Error('Invalid assessment scope response.');
        if Payload.Get('full_report_reason', Token) and Token.IsValue() then
            if not Token.AsValue().IsNull() then
                if Token.AsValue().AsText() <> 'ASSESSMENT_SCOPE_NOT_CONFIRMED' then
                    Error(GetReportReasonText(Token.AsValue().AsText()));

        Clear(Response);
        Clear(Payload);
        ApiUrl := BuildUrl(Setup."API Base URL", '/scans/' + Format(ScanId) + '/assessment-scope');
        if not Client.Get(ApiUrl, Response) then
            Error('Could not load the BCSentinel assessment scope.');
        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error('Assessment scope unavailable (HTTP %1). %2',
                Response.HttpStatusCode(), GetReportErrorText(ResponseText));
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
                Response.HttpStatusCode(), GetReportErrorText(ResponseText));
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
                Response.HttpStatusCode(), GetReportErrorText(ResponseText));
        if not ResponseJson.ReadFrom(ResponseText) then
            Error('Invalid BCSentinel report link response.');
        if not ResponseJson.Get('url', UrlToken) then
            Error('BCSentinel report link missing.');
        Url := UrlToken.AsValue().AsText();
        if Url = '' then
            Error('BCSentinel report link empty.');
        Hyperlink(Url);
    end;

    procedure GetCompletedReportVariant(ScanRun: Record "DH Deep Scan Run"): Text
    begin
        if (ScanRun."Run ID" = '') or
           (ScanRun.Status in [ScanRun.Status::Failed, ScanRun.Status::Canceled]) or
           (LowerCase(ScanRun."Backend Status") = 'rejected') then
            exit('');
        if (ScanRun.Status <> ScanRun.Status::Completed) and
           not (LowerCase(ScanRun."Backend Status") in ['completed', 'completed_with_warnings']) then
            exit('');

        case LowerCase(ScanRun."Scan Mode") of
            'data_health_score', 'free', 'free_deep':
                exit('full');
            'validation', 'validation_scan', 'full_analysis', 'one_time', 'credit':
                exit('validation');
            'monitoring', 'scheduled':
                exit('monitoring');
        end;
        exit('');
    end;

    local procedure GetReportErrorText(ResponseText: Text): Text
    var
        Payload: JsonObject;
        Detail: JsonToken;
    begin
        if Payload.ReadFrom(ResponseText) then
            if Payload.Get('detail', Detail) and Detail.IsValue() then
                if not Detail.AsValue().IsNull() then
                    exit(GetReportReasonText(Detail.AsValue().AsText()));
        exit(GetReportReasonText(''));
    end;

    local procedure GetReportReasonText(Reason: Text): Text
    var
        WrongVariantLbl: Label 'Open the report that matches the selected scan type.';
        BaselineUnverifiedLbl: Label 'Select the original completed Data Health Score scan. Contact BCSentinel support if its history cannot be verified.';
        CompanyUnverifiedLbl: Label 'The company for this scan could not be verified. Contact BCSentinel support.';
        CurrencyUnverifiedLbl: Label 'This scan has no verified EUR local currency. Contact BCSentinel support.';
        ScanIncompleteLbl: Label 'Wait until the scan completes and synchronizes, then try again.';
        ScopeUnconfirmedLbl: Label 'Review and confirm the original scan scope in the scan monitor before opening Full Assessment.';
        FullAccessInactiveLbl: Label 'Check that the required report access is active in BCSentinel Setup.';
        ArchiveUnavailableLbl: Label 'The report could not be built from verified scan evidence. Contact BCSentinel support.';
        ViewerUnavailableLbl: Label 'The report viewer is not available. Contact BCSentinel support.';
        TechnicalErrorLbl: Label 'The report service returned an unexpected response. Contact BCSentinel support if this continues.';
    begin
        case Reason of
            'WRONG_REPORT_VARIANT':
                exit(WrongVariantLbl);
            'FULL_BASELINE_NOT_VERIFIED':
                exit(BaselineUnverifiedLbl);
            'SCAN_COMPANY_NOT_VERIFIED':
                exit(CompanyUnverifiedLbl);
            'SCAN_CURRENCY_NOT_VERIFIED':
                exit(CurrencyUnverifiedLbl);
            'SCAN_NOT_COMPLETED':
                exit(ScanIncompleteLbl);
            'ASSESSMENT_SCOPE_NOT_CONFIRMED', 'Full report evidence unavailable: confirmed scope snapshot missing':
                exit(ScopeUnconfirmedLbl);
            'FULL_ACCESS_INACTIVE':
                exit(FullAccessInactiveLbl);
            'REPORT_ARCHIVE_UNAVAILABLE':
                exit(ArchiveUnavailableLbl);
            'REPORT_VIEWER_UNAVAILABLE', 'REPORT_VARIANT_UNAVAILABLE':
                exit(ViewerUnavailableLbl);
        end;
        exit(TechnicalErrorLbl);
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
