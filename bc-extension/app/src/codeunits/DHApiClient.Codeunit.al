codeunit 53100 "DH API Client"
{
    procedure TestConnection(var Setup: Record "DH Setup")
    var
        Client: HttpClient;
        Response: HttpResponseMessage;
        ResponseText: Text;
        JsonResponse: JsonObject;
        Token: JsonToken;
        StatusText: Text;
    begin
        EnsureSetupLoaded(Setup);

        if not Client.Get(BuildUrl(Setup."API Base URL", '/health'), Response) then
            Error('The backend request could not be sent. Please verify the network connection.');

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error('Backend connection test failed. Status %1 - %2', Response.HttpStatusCode(), ResponseText);

        if JsonResponse.ReadFrom(ResponseText) then
            if JsonResponse.Get('status', Token) then
                if not IsJsonNull(Token) then
                    StatusText := Token.AsValue().AsText();

        if StatusText = '' then
            StatusText := 'ok';

        Message('BCSentinel backend reachable. Status: %1', StatusText);
    end;

    procedure EnsureTenantRegistered(var Setup: Record "DH Setup")
    begin
        EnsureSetupLoaded(Setup);

        if not Setup."Data Processing Consent" then
            Error('Please enable Data Processing Consent first.');

        // Nur wenn wirklich noch nichts existiert
        if (Setup."Tenant ID" = '') or (GetApiToken(Setup) = '') then
            RegisterTenant(Setup);
    end;

    procedure RegisterTenant(var Setup: Record "DH Setup")
    var
        Client: HttpClient;
        Content: HttpContent;
        Headers: HttpHeaders;
        Response: HttpResponseMessage;
        RequestText: Text;
        ResponseText: Text;
        JsonRequest: JsonObject;
        JsonResponse: JsonObject;
        Token: JsonToken;
        TenantId: Text;
        ApiToken: Text;
    begin
        EnsureSetupLoaded(Setup);

        JsonRequest.Add('environment_name', 'BC Cloud');
        JsonRequest.Add('app_version', '0.4.0');
        JsonRequest.Add('invite_code', Setup."Registration Invite Code");
        JsonRequest.WriteTo(RequestText);

        Content.WriteFrom(RequestText);
        Content.GetHeaders(Headers);
        Headers.Clear();
        Headers.Add('Content-Type', 'application/json');

        if not Client.Post(BuildUrl(Setup."API Base URL", '/tenant/register'), Content, Response) then
            Error('The backend request could not be sent. Please verify the network connection.');

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error('Tenant registration failed. Status %1 - %2', Response.HttpStatusCode(), ResponseText);

        if not JsonResponse.ReadFrom(ResponseText) then
            Error('The backend returned an invalid JSON response: %1', ResponseText);

        if JsonResponse.Get('tenant_id', Token) then
            if not IsJsonNull(Token) then
                TenantId := Token.AsValue().AsText();

        if JsonResponse.Get('api_token', Token) then
            if not IsJsonNull(Token) then
                ApiToken := Token.AsValue().AsText();

        if TenantId = '' then
            Error('The backend response does not contain a tenant_id.');

        if ApiToken = '' then
            Error('The backend response does not contain an api_token.');

        Setup.Validate("Tenant ID", CopyStr(TenantId, 1, MaxStrLen(Setup."Tenant ID")));
        StoreApiToken(Setup, ApiToken);
        Setup."Registration Invite Code" := '';
        Setup.Registered := true;
        Setup."Registration Date" := CurrentDateTime();
        Setup.Modify(true);
    end;

    procedure RefreshLicenseStatus(var Setup: Record "DH Setup")
    var
        Client: HttpClient;
        Response: HttpResponseMessage;
        ResponseText: Text;
        Headers: HttpHeaders;
        JsonResponse: JsonObject;
        Token: JsonToken;
        FeaturesToken: JsonToken;
        Features: JsonArray;
    begin
        EnsureTenantAccessConfigured(Setup);

        Headers := Client.DefaultRequestHeaders();
        if Headers.Contains('X-Tenant-Id') then
            Headers.Remove('X-Tenant-Id');
        if Headers.Contains('X-Api-Token') then
            Headers.Remove('X-Api-Token');
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', GetApiToken(Setup));

        if not Client.Get(BuildUrl(Setup."API Base URL", '/license/status'), Response) then
            Error('The backend request could not be sent. Please verify the network connection.');

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error('License status request failed. Status %1 - %2', Response.HttpStatusCode(), ResponseText);

        if not JsonResponse.ReadFrom(ResponseText) then
            Error('The backend returned an invalid JSON response: %1', ResponseText);

        if JsonResponse.Get('plan', Token) then
            if not IsJsonNull(Token) then
                Setup."Current Plan" := MapPlan(Token.AsValue().AsText());

        if JsonResponse.Get('license_status', Token) then
            if not IsJsonNull(Token) then
                Setup."License Status" := MapLicenseStatus(Token.AsValue().AsText());

        Setup."Last License Check" := CurrentDateTime();
        Setup."Premium Enabled" := false;

        if JsonResponse.Get('features', FeaturesToken) then begin
            Features := FeaturesToken.AsArray();
            Setup."Premium Enabled" := HasPremiumActionFeatures(Features);
        end;

        Setup.Modify(true);
    end;

    procedure EnsureReadyForScan(var Setup: Record "DH Setup")
    begin
        EnsureTenantRegistered(Setup);
        RefreshLicenseStatus(Setup);
    end;

    procedure IsPremiumAllowed(Setup: Record "DH Setup"): Boolean
    begin
        exit(
            (Setup."Current Plan" = Setup."Current Plan"::Premium) and
            (Setup."License Status" in [Setup."License Status"::Trial, Setup."License Status"::Active]));
    end;

    procedure ExecuteScan(var Setup: Record "DH Setup"; var ScanId: Code[50]; var DataScore: Integer; var IssuesCount: Integer; var UsedPremiumLicense: Boolean): Text
    var
        ResponseText: Text;
        GeneratedAtUtc: DateTime;
        RunIdMgt: Codeunit "DH Run ID Mgt.";
        QuickRunId: Code[50];
    begin
        EnsureReadyForScan(Setup);

        UsedPremiumLicense := Setup."Premium Enabled";

        QuickRunId := RunIdMgt.GetNextRunId(Setup);

        ResponseText := RunQuickScan(Setup, QuickRunId);

        ParseScanResponse(ResponseText, ScanId, DataScore, IssuesCount, GeneratedAtUtc);
        UpdateSetupFromScanResult(Setup, DataScore, GeneratedAtUtc);

        exit(ResponseText);
    end;

    procedure RunQuickScan(var Setup: Record "DH Setup"): Text
    var
        RunIdMgt: Codeunit "DH Run ID Mgt.";
        QuickRunId: Code[50];
    begin
        QuickRunId := RunIdMgt.GetNextRunId(Setup);
        exit(RunQuickScan(Setup, QuickRunId));
    end;

    procedure RunQuickScan(var Setup: Record "DH Setup"; QuickRunId: Code[50]): Text
    var
        Client: HttpClient;
        Content: HttpContent;
        Headers: HttpHeaders;
        Response: HttpResponseMessage;
        RequestText: Text;
        ResponseText: Text;
        JsonRequest: JsonObject;
        JsonMetrics: JsonObject;
    begin
        EnsureReadyForScan(Setup);

        JsonRequest.Add('tenant_id', Setup."Tenant ID");
        JsonRequest.Add('bc_run_id', Format(QuickRunId));
        AddCustomerMetrics(JsonMetrics);
        AddVendorMetrics(JsonMetrics);
        AddItemMetrics(JsonMetrics);
        JsonRequest.Add('metrics', JsonMetrics);
        JsonRequest.Add('data_profile', BuildDataProfile());
        JsonRequest.WriteTo(RequestText);

        Content.WriteFrom(RequestText);
        Content.GetHeaders(Headers);
        Headers.Clear();
        Headers.Add('Content-Type', 'application/json');

        Headers := Client.DefaultRequestHeaders();
        if Headers.Contains('X-Tenant-Id') then
            Headers.Remove('X-Tenant-Id');
        if Headers.Contains('X-Api-Token') then
            Headers.Remove('X-Api-Token');
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', GetApiToken(Setup));

        if not Client.Post(BuildUrl(Setup."API Base URL", '/scan/quick'), Content, Response) then
            Error('The backend request could not be sent. Please verify the network connection.');

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error('Quick scan failed. Status %1 - %2', Response.HttpStatusCode(), ResponseText);

        exit(ResponseText);
    end;

    procedure GetScanHistory(var Setup: Record "DH Setup"; Limit: Integer): Text
    var
        Client: HttpClient;
        Response: HttpResponseMessage;
        ResponseText: Text;
        Url: Text;
        Headers: HttpHeaders;
    begin
        EnsureReadyForScan(Setup);

        if Limit <= 0 then
            Limit := 10;

        Url := BuildUrl(Setup."API Base URL", '/scan/history/' + Setup."Tenant ID" + '?limit=' + Format(Limit));

        Headers := Client.DefaultRequestHeaders();
        if Headers.Contains('X-Tenant-Id') then
            Headers.Remove('X-Tenant-Id');
        if Headers.Contains('X-Api-Token') then
            Headers.Remove('X-Api-Token');
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', GetApiToken(Setup));

        if not Client.Get(Url, Response) then
            Error('The backend request could not be sent. Please verify the network connection.');

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error('History request failed. Status %1 - %2', Response.HttpStatusCode(), ResponseText);

        exit(ResponseText);
    end;

    procedure GetScanTrend(var Setup: Record "DH Setup"): Text
    var
        Client: HttpClient;
        Response: HttpResponseMessage;
        Url: Text;
        ResponseText: Text;
        Headers: HttpHeaders;
    begin
        EnsureReadyForScan(Setup);

        Url := BuildUrl(Setup."API Base URL", '/scan/trend/' + Setup."Tenant ID");

        Headers := Client.DefaultRequestHeaders();
        if Headers.Contains('X-Tenant-Id') then
            Headers.Remove('X-Tenant-Id');
        if Headers.Contains('X-Api-Token') then
            Headers.Remove('X-Api-Token');
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', GetApiToken(Setup));

        if not Client.Get(Url, Response) then
            Error('The backend request could not be sent. Please verify the network connection.');

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error('Trend request failed. Status %1 - %2', Response.HttpStatusCode(), ResponseText);

        exit(ResponseText);
    end;

    procedure SyncScanToBackend(var Setup: Record "DH Setup"; RequestText: Text)
    begin
        SyncScanToBackendAndGetResponse(Setup, RequestText);
    end;

    procedure SyncScanToBackendAndGetResponse(var Setup: Record "DH Setup"; RequestText: Text): Text
    var
        Client: HttpClient;
        Content: HttpContent;
        Headers: HttpHeaders;
        Response: HttpResponseMessage;
        ResponseText: Text;
    begin
        EnsureReadyForScan(Setup);

        Content.WriteFrom(RequestText);
        Content.GetHeaders(Headers);
        Headers.Clear();
        Headers.Add('Content-Type', 'application/json');

        Headers := Client.DefaultRequestHeaders();
        if Headers.Contains('X-Tenant-Id') then
            Headers.Remove('X-Tenant-Id');
        if Headers.Contains('X-Api-Token') then
            Headers.Remove('X-Api-Token');
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', GetApiToken(Setup));

        if not Client.Post(BuildUrl(Setup."API Base URL", '/scan/sync'), Content, Response) then
            Error('The backend sync request could not be sent. Please verify the network connection.');

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error('Scan sync failed. Status %1 - %2', Response.HttpStatusCode(), ResponseText);

        exit(ResponseText);
    end;

    procedure DeleteScanFromBackend(var Setup: Record "DH Setup"; ScanId: Code[50])
    var
        Client: HttpClient;
        Response: HttpResponseMessage;
        ResponseText: Text;
        Headers: HttpHeaders;
    begin
        EnsureReadyForScan(Setup);

        Headers := Client.DefaultRequestHeaders();
        if Headers.Contains('X-Tenant-Id') then
            Headers.Remove('X-Tenant-Id');
        if Headers.Contains('X-Api-Token') then
            Headers.Remove('X-Api-Token');
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', GetApiToken(Setup));

        if not Client.Delete(
            BuildUrl(Setup."API Base URL", '/scan/' + Setup."Tenant ID" + '/' + Format(ScanId)),
            Response)
        then
            Error('The backend delete request could not be sent. Please verify the network connection.');

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error('Backend scan delete failed. Status %1 - %2', Response.HttpStatusCode(), ResponseText);
    end;

    procedure ReconcileScansWithBackend(var Setup: Record "DH Setup")
    var
        Client: HttpClient;
        Content: HttpContent;
        Headers: HttpHeaders;
        Response: HttpResponseMessage;
        RequestText: Text;
        ResponseText: Text;
        JsonRequest: JsonObject;
        ScanIds: JsonArray;
        ScanHeader: Record "DH Scan Header";
        EffectiveScanId: Code[50];
    begin
        EnsureReadyForScan(Setup);

        JsonRequest.Add('tenant_id', Setup."Tenant ID");

        if ScanHeader.FindSet() then
            repeat
                EffectiveScanId := GetEffectiveScanId(ScanHeader);
                if EffectiveScanId <> '' then
                    ScanIds.Add(Format(EffectiveScanId));
            until ScanHeader.Next() = 0;

        JsonRequest.Add('scan_ids', ScanIds);
        JsonRequest.WriteTo(RequestText);

        Content.WriteFrom(RequestText);
        Content.GetHeaders(Headers);
        Headers.Clear();
        Headers.Add('Content-Type', 'application/json');

        Headers := Client.DefaultRequestHeaders();
        if Headers.Contains('X-Tenant-Id') then
            Headers.Remove('X-Tenant-Id');
        if Headers.Contains('X-Api-Token') then
            Headers.Remove('X-Api-Token');
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', GetApiToken(Setup));

        if not Client.Post(BuildUrl(Setup."API Base URL", '/scan/reconcile'), Content, Response) then
            Error('The backend reconcile request could not be sent. Please verify the network connection.');

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error('Backend reconcile failed. Status %1 - %2', Response.HttpStatusCode(), ResponseText);
    end;

    procedure UpdateScanProgress(var Setup: Record "DH Setup"; var DeepScanRun: Record "DH Deep Scan Run"; StatusValue: Text; CurrentStep: Text; EventMessage: Text)
    var
        Client: HttpClient;
        Content: HttpContent;
        ContentHeaders: HttpHeaders;
        RequestHeaders: HttpHeaders;
        Response: HttpResponseMessage;
        RequestText: Text;
        ResponseText: Text;
        JsonRequest: JsonObject;
    begin
        EnsureTenantAccessConfigured(Setup);

        if DeepScanRun."Run ID" = '' then
            exit;

        JsonRequest.Add('tenant_id', Setup."Tenant ID");
        JsonRequest.Add('run_id', Format(DeepScanRun."Run ID"));
        JsonRequest.Add('scan_mode', 'deep');
        JsonRequest.Add('status', StatusValue);
        JsonRequest.Add('progress_percent', DeepScanRun."Progress %");
        JsonRequest.Add('current_module', DeepScanRun."Current Module");
        JsonRequest.Add('current_step', CurrentStep);
        JsonRequest.Add('event_message', EventMessage);
        JsonRequest.Add('total_modules', DeepScanRun."Total Modules");
        JsonRequest.Add('completed_modules', DeepScanRun."Completed Modules");
        JsonRequest.Add('failed_modules', DeepScanRun."Failed Modules");
        if DeepScanRun."Error Message" <> '' then
            JsonRequest.Add('error_message', DeepScanRun."Error Message");
        if DeepScanRun."Warning Message" <> '' then
            JsonRequest.Add('warning_message', DeepScanRun."Warning Message");
        JsonRequest.WriteTo(RequestText);

        Content.WriteFrom(RequestText);
        Content.GetHeaders(ContentHeaders);
        ContentHeaders.Clear();
        ContentHeaders.Add('Content-Type', 'application/json');

        RequestHeaders := Client.DefaultRequestHeaders();
        if RequestHeaders.Contains('X-Tenant-Id') then
            RequestHeaders.Remove('X-Tenant-Id');
        if RequestHeaders.Contains('X-Api-Token') then
            RequestHeaders.Remove('X-Api-Token');
        RequestHeaders.Add('X-Tenant-Id', Setup."Tenant ID");
        RequestHeaders.Add('X-Api-Token', GetApiToken(Setup));

        if not Client.Post(BuildUrl(Setup."API Base URL", '/scan/status/update'), Content, Response) then
            Error('Scan status update could not be sent. Endpoint: %1. Run ID: %2. Tenant: %3',
                BuildUrl(Setup."API Base URL", '/scan/status/update'),
                Format(DeepScanRun."Run ID"),
                MaskTenantId(Setup."Tenant ID"));

        Response.Content.ReadAs(ResponseText);
        if Response.IsSuccessStatusCode() then
            ParseScanStatusResponse(ResponseText, DeepScanRun)
        else
            Error('Scan status update failed. Endpoint: %1. Status: %2. Run ID: %3. Tenant: %4. Response: %5',
                BuildUrl(Setup."API Base URL", '/scan/status/update'),
                Response.HttpStatusCode(),
                Format(DeepScanRun."Run ID"),
                MaskTenantId(Setup."Tenant ID"),
                CopyStr(ResponseText, 1, 250));
    end;

    procedure GetScanStatus(var Setup: Record "DH Setup"; RunId: Code[50]): Text
    var
        Client: HttpClient;
        Response: HttpResponseMessage;
        ResponseText: Text;
        Headers: HttpHeaders;
    begin
        EnsureTenantAccessConfigured(Setup);

        Headers := Client.DefaultRequestHeaders();
        if Headers.Contains('X-Tenant-Id') then
            Headers.Remove('X-Tenant-Id');
        if Headers.Contains('X-Api-Token') then
            Headers.Remove('X-Api-Token');
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', GetApiToken(Setup));

        if not Client.Get(BuildUrl(Setup."API Base URL", '/scan/status/' + Format(RunId)), Response) then
            Error('The scan status request could not be sent. Endpoint: %1. Run ID: %2. Tenant: %3',
                BuildUrl(Setup."API Base URL", '/scan/status/' + Format(RunId)),
                Format(RunId),
                MaskTenantId(Setup."Tenant ID"));

        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error('Scan status request failed. Endpoint: %1. Status: %2. Run ID: %3. Tenant: %4. Response: %5',
                BuildUrl(Setup."API Base URL", '/scan/status/' + Format(RunId)),
                Response.HttpStatusCode(),
                Format(RunId),
                MaskTenantId(Setup."Tenant ID"),
                CopyStr(ResponseText, 1, 250));

        exit(ResponseText);
    end;

    procedure RefreshScanStatus(var Setup: Record "DH Setup"; var DeepScanRun: Record "DH Deep Scan Run")
    var
        ResponseText: Text;
    begin
        if DeepScanRun."Run ID" = '' then
            exit;

        ResponseText := GetScanStatus(Setup, DeepScanRun."Run ID");
        ParseScanStatusResponse(ResponseText, DeepScanRun);
        DeepScanRun.Modify(true);
    end;

    procedure ParseScanStatusResponse(ResponseText: Text; var DeepScanRun: Record "DH Deep Scan Run")
    var
        JsonResponse: JsonObject;
        Token: JsonToken;
        EventsToken: JsonToken;
        BackendStatus: Text;
    begin
        if ResponseText = '' then
            exit;

        if not JsonResponse.ReadFrom(ResponseText) then
            Error('The scan status response is not valid JSON.');

        DeepScanRun."Warning Message" := '';
        DeepScanRun."Error Message" := '';

        if JsonResponse.Get('status', Token) then begin
            BackendStatus := GetJsonTokenText(Token);
            DeepScanRun."Backend Status" := CopyStr(GetJsonTokenText(Token), 1, MaxStrLen(DeepScanRun."Backend Status"));
            ApplyBackendStatusToLocalRun(BackendStatus, DeepScanRun);
        end;
        if JsonResponse.Get('progress_percent', Token) then
            DeepScanRun."Progress %" := GetJsonTokenInteger(Token, DeepScanRun."Progress %");
        if JsonResponse.Get('current_module', Token) then
            DeepScanRun."Current Module" := CopyStr(GetJsonTokenText(Token), 1, MaxStrLen(DeepScanRun."Current Module"));
        if JsonResponse.Get('current_step', Token) then
            DeepScanRun."Current Step" := CopyStr(GetJsonTokenText(Token), 1, MaxStrLen(DeepScanRun."Current Step"));
        if JsonResponse.Get('heartbeat_at', Token) then
            DeepScanRun."Last Heartbeat" := ParseJsonDateTime(GetJsonTokenText(Token));
        if JsonResponse.Get('estimated_remaining_seconds', Token) then
            DeepScanRun."Estimated Remaining Seconds" := GetJsonTokenInteger(Token, DeepScanRun."Estimated Remaining Seconds");
        if JsonResponse.Get('total_modules', Token) then
            DeepScanRun."Total Modules" := GetJsonTokenInteger(Token, DeepScanRun."Total Modules");
        if JsonResponse.Get('completed_modules', Token) then
            DeepScanRun."Completed Modules" := GetJsonTokenInteger(Token, DeepScanRun."Completed Modules");
        if JsonResponse.Get('failed_modules', Token) then
            DeepScanRun."Failed Modules" := GetJsonTokenInteger(Token, DeepScanRun."Failed Modules");
        if JsonResponse.Get('error_message', Token) then
            DeepScanRun."Error Message" := CopyStr(GetJsonTokenText(Token), 1, MaxStrLen(DeepScanRun."Error Message"));
        if JsonResponse.Get('warning_message', Token) then
            DeepScanRun."Warning Message" := CopyStr(GetJsonTokenText(Token), 1, MaxStrLen(DeepScanRun."Warning Message"));
        if JsonResponse.Get('recent_events', EventsToken) then
            DeepScanRun."Recent Events" := CopyStr(BuildRecentEventsText(EventsToken), 1, MaxStrLen(DeepScanRun."Recent Events"));

        NormalizeParsedScanStatus(DeepScanRun);
    end;

    procedure ParseScanResponse(ResponseText: Text; var ScanId: Code[50]; var DataScore: Integer; var IssuesCount: Integer; var GeneratedAtUtc: DateTime)
    var
        JsonResponse: JsonObject;
        Token: JsonToken;
        GeneratedAtText: Text;
    begin
        Clear(ScanId);
        Clear(DataScore);
        Clear(IssuesCount);
        Clear(GeneratedAtUtc);

        if not JsonResponse.ReadFrom(ResponseText) then
            Error('The backend returned an invalid JSON response: %1', ResponseText);

        if JsonResponse.Get('scan_id', Token) then
            if not IsJsonNull(Token) then
                ScanId := CopyStr(Token.AsValue().AsText(), 1, MaxStrLen(ScanId));

        if JsonResponse.Get('data_score', Token) then
            if not IsJsonNull(Token) then
                DataScore := Token.AsValue().AsInteger();

        if JsonResponse.Get('issues_count', Token) then
            if not IsJsonNull(Token) then
                IssuesCount := Token.AsValue().AsInteger();

        if JsonResponse.Get('generated_at_utc', Token) then
            if not IsJsonNull(Token) then
                GeneratedAtText := Token.AsValue().AsText();

        if GeneratedAtText <> '' then
            Evaluate(GeneratedAtUtc, GeneratedAtText);
    end;

    procedure UpdateSetupFromScanResult(var Setup: Record "DH Setup"; DataScore: Integer; GeneratedAtUtc: DateTime)
    begin
        Setup."Last Score" := DataScore;

        if GeneratedAtUtc <> 0DT then
            Setup."Last Scan Date" := GeneratedAtUtc
        else
            Setup."Last Scan Date" := CurrentDateTime();

        Setup.Modify(true);
    end;

    local procedure EnsureSetupLoaded(var Setup: Record "DH Setup")
    var
        OriginalApiBaseUrl: Text[250];
        NormalizedApiBaseUrl: Text[250];
    begin
        if not Setup.Get('SETUP') then begin
            Setup.Init();
            Setup."Primary Key" := 'SETUP';
            Setup.Insert(true);
        end;

        OriginalApiBaseUrl := Setup."API Base URL";
        NormalizedApiBaseUrl := Setup.NormalizeApiBaseUrl(OriginalApiBaseUrl);
        if OriginalApiBaseUrl <> NormalizedApiBaseUrl then begin
            Setup."API Base URL" := NormalizedApiBaseUrl;
            Setup.Modify(true);
        end;
    end;

    local procedure EnsureTenantAccessConfigured(var Setup: Record "DH Setup")
    begin
        EnsureSetupLoaded(Setup);

        if Setup."Tenant ID" = '' then
            Error('Please register the tenant first.');

        if GetApiToken(Setup) = '' then
            Error('The API token is missing. Please register the tenant again.');
    end;

    local procedure GetApiToken(var Setup: Record "DH Setup"): Text
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        exit(SecretMgt.GetApiToken(Setup));
    end;

    local procedure StoreApiToken(var Setup: Record "DH Setup"; ApiToken: Text)
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        SecretMgt.StoreApiToken(Setup, ApiToken);
    end;

    procedure GetAnalyticsDashboardToken(var Setup: Record "DH Setup"): Text
    var
        Client: HttpClient;
        Response: HttpResponseMessage;
        ResponseText: Text;
        Url: Text;
        Headers: HttpHeaders;
        JsonResponse: JsonObject;
        TokenValue: JsonToken;
    begin
        EnsureTenantAccessConfigured(Setup);

        Url :=
            BuildUrl(Setup."API Base URL", '/analytics/get-token') +
            '?company=' + EncodeUrlValue(CompanyName()) +
            '&environment=' + EncodeUrlValue('BC Cloud') +
            '&tenant_id=' + EncodeUrlValue(Setup."Tenant ID") +
            '&scan_mode=' + EncodeUrlValue(GetAnalyticsScanMode(Setup)) +
            '&bc_issue_launch_url=' + EncodeUrlValue(GetIssueDrilldownLaunchUrl());

        Headers := Client.DefaultRequestHeaders();
        if Headers.Contains('X-Tenant-Id') then
            Headers.Remove('X-Tenant-Id');
        if Headers.Contains('X-Api-Token') then
            Headers.Remove('X-Api-Token');
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', GetApiToken(Setup));

        if not Client.Get(Url, Response) then
            Error('The dashboard token service could not be reached.');

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error(
                'The dashboard token service returned an error. Status: %1. Response: %2',
                Response.HttpStatusCode(),
                ResponseText);

        if not JsonResponse.ReadFrom(ResponseText) then
            Error('The dashboard token service returned invalid JSON: %1', ResponseText);

        if not JsonResponse.Get('token', TokenValue) then
            Error('The field "token" is missing in the dashboard token response.');

        exit(TokenValue.AsValue().AsText());
    end;

    procedure OpenPremiumCheckout(var Setup: Record "DH Setup")
    var
        CheckoutUrl: Text;
    begin
        CheckoutUrl := CreatePremiumCheckoutSession(Setup);
        Hyperlink(CheckoutUrl);
    end;

    procedure CreatePremiumCheckoutSession(var Setup: Record "DH Setup"): Text
    var
        Client: HttpClient;
        Content: HttpContent;
        ContentHeaders: HttpHeaders;
        RequestHeaders: HttpHeaders;
        Response: HttpResponseMessage;
        RequestText: Text;
        ResponseText: Text;
        JsonRequest: JsonObject;
        JsonResponse: JsonObject;
        TokenValue: JsonToken;
        CheckoutUrl: Text;
    begin
        EnsureTenantAccessConfigured(Setup);

        JsonRequest.Add('tenant_id', Setup."Tenant ID");
        JsonRequest.Add('plan_code', 'premium');
        JsonRequest.WriteTo(RequestText);

        Content.WriteFrom(RequestText);
        Content.GetHeaders(ContentHeaders);
        ContentHeaders.Clear();
        ContentHeaders.Add('Content-Type', 'application/json');

        RequestHeaders := Client.DefaultRequestHeaders();
        if RequestHeaders.Contains('X-Tenant-Id') then
            RequestHeaders.Remove('X-Tenant-Id');
        if RequestHeaders.Contains('X-Api-Token') then
            RequestHeaders.Remove('X-Api-Token');
        RequestHeaders.Add('X-Tenant-Id', Setup."Tenant ID");
        RequestHeaders.Add('X-Api-Token', GetApiToken(Setup));

        if not Client.Post(BuildUrl(Setup."API Base URL", '/billing/checkout/session'), Content, Response) then
            Error('The billing checkout request could not be sent. Please verify the network connection.');

        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error('Billing checkout session failed. Status %1 - %2', Response.HttpStatusCode(), ResponseText);

        if not JsonResponse.ReadFrom(ResponseText) then
            Error('The billing checkout response is not valid JSON: %1', ResponseText);

        if JsonResponse.Get('checkout_url', TokenValue) then
            if not IsJsonNull(TokenValue) then
                CheckoutUrl := TokenValue.AsValue().AsText();

        if CheckoutUrl = '' then
            Error('The billing checkout response does not contain checkout_url.');

        exit(CheckoutUrl);
    end;

    local procedure GetAnalyticsScanMode(var Setup: Record "DH Setup"): Text
    begin
        if Setup."Premium Enabled" then
            exit('premium_deep');

        exit('free_deep');
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

    local procedure BuildUrl(BaseUrl: Text; RelativePath: Text): Text
    begin
        exit(RemoveTrailingSlash(BaseUrl) + RelativePath);
    end;

    local procedure MaskTenantId(TenantId: Text): Text
    begin
        if StrLen(TenantId) <= 8 then
            exit('***');

        exit(CopyStr(TenantId, 1, 4) + '...' + CopyStr(TenantId, StrLen(TenantId) - 3, 4));
    end;

    local procedure GetIssueDrilldownLaunchUrl(): Text
    begin
        exit(GetUrl(ClientType::Web, CompanyName(), ObjectType::Page, Page::"DH Issue Drilldown Launch"));
    end;

    local procedure RemoveTrailingSlash(Value: Text): Text
    begin
        while (StrLen(Value) > 0) and (CopyStr(Value, StrLen(Value), 1) = '/') do
            Value := CopyStr(Value, 1, StrLen(Value) - 1);

        exit(Value);
    end;

    local procedure IsJsonNull(Token: JsonToken): Boolean
    var
        JsonValueText: Text;
    begin
        JsonValueText := LowerCase(Format(Token));
        exit((JsonValueText = 'null') or (JsonValueText = ''));
    end;

    local procedure GetJsonTokenText(Token: JsonToken): Text
    begin
        if IsJsonNull(Token) then
            exit('');

        exit(Token.AsValue().AsText());
    end;

    local procedure GetJsonTokenInteger(Token: JsonToken; DefaultValue: Integer): Integer
    var
        ParsedValue: Integer;
    begin
        if IsJsonNull(Token) then
            exit(DefaultValue);

        if not Evaluate(ParsedValue, Token.AsValue().AsText()) then
            exit(DefaultValue);

        exit(ParsedValue);
    end;

    local procedure ApplyBackendStatusToLocalRun(StatusValue: Text; var DeepScanRun: Record "DH Deep Scan Run")
    begin
        if IsLocalTerminalStatus(DeepScanRun) then
            case LowerCase(StatusValue) of
                'queued', 'preparing', 'running', 'finalizing':
                    exit;
            end;

        case LowerCase(StatusValue) of
            'queued', 'preparing':
                DeepScanRun.Status := DeepScanRun.Status::Queued;
            'running', 'finalizing':
                DeepScanRun.Status := DeepScanRun.Status::Running;
            'completed':
                DeepScanRun.Status := DeepScanRun.Status::Completed;
            'failed', 'stalled':
                DeepScanRun.Status := DeepScanRun.Status::Failed;
            'cancelled', 'canceled':
                DeepScanRun.Status := DeepScanRun.Status::Canceled;
        end;
    end;

    local procedure IsLocalTerminalStatus(var DeepScanRun: Record "DH Deep Scan Run"): Boolean
    begin
        exit(DeepScanRun.Status in [DeepScanRun.Status::Completed, DeepScanRun.Status::Failed, DeepScanRun.Status::Canceled]);
    end;

    local procedure NormalizeParsedScanStatus(var DeepScanRun: Record "DH Deep Scan Run")
    begin
        case LowerCase(DeepScanRun."Backend Status") of
            'queued':
                begin
                    DeepScanRun."Progress %" := 0;
                    if DeepScanRun."Current Module" = '' then
                        DeepScanRun."Current Module" := 'Preparing';
                    if DeepScanRun."Current Step" = '' then
                        DeepScanRun."Current Step" := 'Waiting for backend status';
                end;
            'preparing':
                begin
                    if DeepScanRun."Progress %" < 0 then
                        DeepScanRun."Progress %" := 0;
                    if DeepScanRun."Current Module" = '' then
                        DeepScanRun."Current Module" := 'Preparing';
                    if DeepScanRun."Current Step" = '' then
                        DeepScanRun."Current Step" := 'Preparing scan';
                end;
            'completed':
                begin
                    DeepScanRun."Progress %" := 100;
                    DeepScanRun."Current Module" := 'All modules completed';
                    DeepScanRun."Current Step" := 'Scan completed';
                    DeepScanRun."Estimated Remaining Seconds" := 0;
                    if DeepScanRun."Total Modules" > 0 then
                        DeepScanRun."Completed Modules" := DeepScanRun."Total Modules";
                end;
            'failed':
                begin
                    if DeepScanRun."Current Module" = '' then
                        DeepScanRun."Current Module" := 'Failed';
                    if DeepScanRun."Current Step" = '' then
                        DeepScanRun."Current Step" := 'Scan failed';
                end;
            'stalled':
                begin
                    if DeepScanRun."Current Step" = '' then
                        DeepScanRun."Current Step" := 'Waiting for heartbeat';
                end;
        end;

        if DeepScanRun."Progress %" < 0 then
            DeepScanRun."Progress %" := 0;
        if DeepScanRun."Progress %" > 100 then
            DeepScanRun."Progress %" := 100;
    end;

    local procedure ParseJsonDateTime(Value: Text): DateTime
    var
        ParsedDateTime: DateTime;
    begin
        Value := Value.Replace('T', ' ');
        Value := Value.Replace('Z', '');
        if StrLen(Value) > 19 then
            Value := CopyStr(Value, 1, 19);

        if Evaluate(ParsedDateTime, Value) then
            exit(ParsedDateTime);

        exit(0DT);
    end;

    local procedure BuildRecentEventsText(EventsToken: JsonToken): Text
    var
        Events: JsonArray;
        EventToken: JsonToken;
        EventObj: JsonObject;
        MessageToken: JsonToken;
        Result: Text;
        MessageText: Text;
        i: Integer;
    begin
        if IsJsonNull(EventsToken) then
            exit('');

        Events := EventsToken.AsArray();
        for i := 0 to Events.Count() - 1 do begin
            Events.Get(i, EventToken);
            EventObj := EventToken.AsObject();
            if EventObj.Get('message', MessageToken) then begin
                MessageText := GetJsonTokenText(MessageToken);
                if MessageText <> '' then begin
                    if Result <> '' then
                        Result += ' | ';
                    Result += MessageText;
                end;
            end;
        end;

        exit(Result);
    end;

    local procedure MapPlan(Value: Text): Enum "DH License Plan"
    begin
        case LowerCase(Value) of
            'free':
                exit("DH License Plan"::Free);
            'standard':
                exit("DH License Plan"::Standard);
            'premium':
                exit("DH License Plan"::Premium);
            else
                exit("DH License Plan"::Free);
        end;
    end;

    local procedure MapLicenseStatus(Value: Text): Enum "DH License Status"
    begin
        case LowerCase(Value) of
            'trial':
                exit("DH License Status"::Trial);
            'active':
                exit("DH License Status"::Active);
            'expired':
                exit("DH License Status"::Expired);
            'blocked':
                exit("DH License Status"::Blocked);
            else
                exit("DH License Status"::Trial);
        end;
    end;

    local procedure JsonArrayContainsText(Values: JsonArray; SearchText: Text): Boolean
    var
        Token: JsonToken;
        i: Integer;
    begin
        for i := 0 to Values.Count() - 1 do begin
            Values.Get(i, Token);
            if LowerCase(Token.AsValue().AsText()) = LowerCase(SearchText) then
                exit(true);
        end;

        exit(false);
    end;

    local procedure HasPremiumActionFeatures(Values: JsonArray): Boolean
    begin
        exit(
            JsonArrayContainsText(Values, 'recommendations') or
            JsonArrayContainsText(Values, 'record_drilldown') or
            JsonArrayContainsText(Values, 'correction_worklists') or
            JsonArrayContainsText(Values, 'analytics_full'));
    end;

    local procedure GetEffectiveScanId(var ScanHeader: Record "DH Scan Header"): Code[50]
    begin
        if ScanHeader."Backend Scan Id" <> '' then
            exit(ScanHeader."Backend Scan Id");

        exit(ScanHeader.GetDisplayRunId());
    end;

    local procedure BuildDataProfile(): JsonObject
    var
        DataProfilingMgt: Codeunit "DH Data Profiling Mgt.";
    begin
        exit(DataProfilingMgt.BuildDataProfile());
    end;

    local procedure AddCustomerMetrics(var JsonMetrics: JsonObject)
    begin
        JsonMetrics.Add('customers_total', CountCustomers());
        JsonMetrics.Add('customers_missing_postcode', CountCustomersMissingPostCode());
        JsonMetrics.Add('customers_missing_payment_terms', CountCustomersMissingPaymentTerms());
        JsonMetrics.Add('customers_missing_country_code', CountCustomersMissingCountryCode());
        JsonMetrics.Add('customers_missing_vat_reg_no', CountCustomersMissingVATRegNo());
        JsonMetrics.Add('customers_missing_email', CountCustomersMissingEmail());
        JsonMetrics.Add('customers_missing_phone_no', CountCustomersMissingPhoneNo());
        JsonMetrics.Add('customers_missing_customer_posting_group', CountCustomersMissingCustomerPostingGroup());
        JsonMetrics.Add('customers_missing_gen_bus_posting_group', CountCustomersMissingGenBusPostingGroup());
        JsonMetrics.Add('customers_blocked_total', CountBlockedCustomers());
    end;

    local procedure AddVendorMetrics(var JsonMetrics: JsonObject)
    begin
        JsonMetrics.Add('vendors_total', CountVendors());
        JsonMetrics.Add('vendors_missing_payment_terms', CountVendorsMissingPaymentTerms());
        JsonMetrics.Add('vendors_missing_country_code', CountVendorsMissingCountryCode());
        JsonMetrics.Add('vendors_missing_email', CountVendorsMissingEmail());
        JsonMetrics.Add('vendors_missing_phone_no', CountVendorsMissingPhoneNo());
        JsonMetrics.Add('vendors_missing_vendor_posting_group', CountVendorsMissingVendorPostingGroup());
        JsonMetrics.Add('vendors_missing_gen_bus_posting_group', CountVendorsMissingGenBusPostingGroup());
        JsonMetrics.Add('vendors_blocked_total', CountBlockedVendors());
    end;

    local procedure AddItemMetrics(var JsonMetrics: JsonObject)
    begin
        JsonMetrics.Add('items_total', CountItems());
        JsonMetrics.Add('items_missing_category', CountItemsMissingCategory());
        JsonMetrics.Add('items_missing_base_unit', CountItemsMissingBaseUnit());
        JsonMetrics.Add('items_missing_gen_prod_posting_group', CountItemsMissingGenProdPostingGroup());
        JsonMetrics.Add('items_missing_inventory_posting_group', CountItemsMissingInventoryPostingGroup());
        JsonMetrics.Add('items_missing_vat_prod_posting_group', CountItemsMissingVATProdPostingGroup());
        JsonMetrics.Add('items_missing_vendor_no', CountItemsMissingVendorNo());
        JsonMetrics.Add('items_blocked_total', CountBlockedItems());
    end;

    local procedure CountCustomers(): Integer
    var
        Customer: Record Customer;
    begin
        exit(Customer.Count());
    end;

    local procedure CountCustomersMissingPostCode(): Integer
    var
        Customer: Record Customer;
    begin
        Customer.SetRange("Post Code", '');
        exit(Customer.Count());
    end;

    local procedure CountCustomersMissingPaymentTerms(): Integer
    var
        Customer: Record Customer;
    begin
        Customer.SetRange("Payment Terms Code", '');
        exit(Customer.Count());
    end;

    local procedure CountCustomersMissingCountryCode(): Integer
    var
        Customer: Record Customer;
    begin
        Customer.SetRange("Country/Region Code", '');
        exit(Customer.Count());
    end;

    local procedure CountCustomersMissingVATRegNo(): Integer
    var
        Customer: Record Customer;
    begin
        Customer.SetRange("VAT Registration No.", '');
        exit(Customer.Count());
    end;

    local procedure CountCustomersMissingEmail(): Integer
    var
        Customer: Record Customer;
    begin
        Customer.SetRange("E-Mail", '');
        exit(Customer.Count());
    end;

    local procedure CountCustomersMissingPhoneNo(): Integer
    var
        Customer: Record Customer;
    begin
        Customer.SetRange("Phone No.", '');
        exit(Customer.Count());
    end;

    local procedure CountCustomersMissingCustomerPostingGroup(): Integer
    var
        Customer: Record Customer;
    begin
        Customer.SetRange("Customer Posting Group", '');
        exit(Customer.Count());
    end;

    local procedure CountCustomersMissingGenBusPostingGroup(): Integer
    var
        Customer: Record Customer;
    begin
        Customer.SetRange("Gen. Bus. Posting Group", '');
        exit(Customer.Count());
    end;

    local procedure CountBlockedCustomers(): Integer
    var
        Customer: Record Customer;
    begin
        Customer.SetFilter(Blocked, '<>%1', Customer.Blocked::" ");
        exit(Customer.Count());
    end;

    local procedure CountVendors(): Integer
    var
        Vendor: Record Vendor;
    begin
        exit(Vendor.Count());
    end;

    local procedure CountVendorsMissingPaymentTerms(): Integer
    var
        Vendor: Record Vendor;
    begin
        Vendor.SetRange("Payment Terms Code", '');
        exit(Vendor.Count());
    end;

    local procedure CountVendorsMissingCountryCode(): Integer
    var
        Vendor: Record Vendor;
    begin
        Vendor.SetRange("Country/Region Code", '');
        exit(Vendor.Count());
    end;

    local procedure CountVendorsMissingEmail(): Integer
    var
        Vendor: Record Vendor;
    begin
        Vendor.SetRange("E-Mail", '');
        exit(Vendor.Count());
    end;

    local procedure CountVendorsMissingPhoneNo(): Integer
    var
        Vendor: Record Vendor;
    begin
        Vendor.SetRange("Phone No.", '');
        exit(Vendor.Count());
    end;

    local procedure CountVendorsMissingVendorPostingGroup(): Integer
    var
        Vendor: Record Vendor;
    begin
        Vendor.SetRange("Vendor Posting Group", '');
        exit(Vendor.Count());
    end;

    local procedure CountVendorsMissingGenBusPostingGroup(): Integer
    var
        Vendor: Record Vendor;
    begin
        Vendor.SetRange("Gen. Bus. Posting Group", '');
        exit(Vendor.Count());
    end;

    local procedure CountBlockedVendors(): Integer
    var
        Vendor: Record Vendor;
    begin
        Vendor.SetFilter(Blocked, '<>%1', Vendor.Blocked::" ");
        exit(Vendor.Count());
    end;

    local procedure CountItems(): Integer
    var
        Item: Record Item;
    begin
        exit(Item.Count());
    end;

    local procedure CountItemsMissingCategory(): Integer
    var
        Item: Record Item;
    begin
        Item.SetRange("Item Category Code", '');
        exit(Item.Count());
    end;

    local procedure CountItemsMissingBaseUnit(): Integer
    var
        Item: Record Item;
    begin
        Item.SetRange("Base Unit of Measure", '');
        exit(Item.Count());
    end;

    local procedure CountItemsMissingGenProdPostingGroup(): Integer
    var
        Item: Record Item;
    begin
        Item.SetRange("Gen. Prod. Posting Group", '');
        exit(Item.Count());
    end;

    local procedure CountItemsMissingInventoryPostingGroup(): Integer
    var
        Item: Record Item;
    begin
        Item.SetRange("Inventory Posting Group", '');
        exit(Item.Count());
    end;

    local procedure CountItemsMissingVATProdPostingGroup(): Integer
    var
        Item: Record Item;
    begin
        Item.SetRange("VAT Prod. Posting Group", '');
        exit(Item.Count());
    end;

    local procedure CountItemsMissingVendorNo(): Integer
    var
        Item: Record Item;
    begin
        Item.SetRange("Vendor No.", '');
        exit(Item.Count());
    end;

    local procedure CountBlockedItems(): Integer
    var
        Item: Record Item;
    begin
        Item.SetRange(Blocked, true);
        exit(Item.Count());
    end;
}
