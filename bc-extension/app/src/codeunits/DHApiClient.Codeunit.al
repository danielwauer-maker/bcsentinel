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
            Error(BackendRequestNotSentLbl);

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error(BackendConnectionTestFailedLbl, Response.HttpStatusCode(), GetSafeBackendErrorText(ResponseText));

        if JsonResponse.ReadFrom(ResponseText) then
            if JsonResponse.Get('status', Token) then
                if not IsJsonNull(Token) then
                    StatusText := Token.AsValue().AsText();

        if StatusText = '' then
            StatusText := 'ok';

        Message(BackendReachableMsg, StatusText);
    end;

    procedure GetSafeBackendErrorText(ResponseText: Text): Text
    var
        JsonResponse: JsonObject;
        Token: JsonToken;
        Detail: Text;
    begin
        if ResponseText = '' then
            exit('No response body was returned. Contact BCSentinel support if this continues.');

        if JsonResponse.ReadFrom(ResponseText) then
            if JsonResponse.Get('detail', Token) then
                if not IsJsonNull(Token) then begin
                    Detail := Token.AsValue().AsText();
                    if IsSafeBackendDetail(Detail) then
                        exit(Detail);
                end;

        exit('Backend returned a technical error. Contact BCSentinel support if this continues.');
    end;

    local procedure IsSafeBackendDetail(Detail: Text): Boolean
    begin
        if Detail = '' then
            exit(false);

        if StrPos(Detail, 'checkout is not configured') > 0 then
            exit(true);
        if StrPos(Detail, 'Stripe is not configured') > 0 then
            exit(true);
        if StrPos(Detail, 'BILLING_SUCCESS_URL') > 0 then
            exit(true);
        if StrPos(Detail, 'BILLING_CANCEL_URL') > 0 then
            exit(true);
        if StrPos(LowerCase(Detail), 'tenant not found') > 0 then
            exit(true);
        if StrPos(LowerCase(Detail), 'invalid invite') > 0 then
            exit(true);
        if StrPos(LowerCase(Detail), 'invite code') > 0 then
            exit(true);
        if StrPos(LowerCase(Detail), 'not authorized') > 0 then
            exit(true);
        if StrPos(LowerCase(Detail), 'forbidden') > 0 then
            exit(true);

        exit(false);
    end;

    local procedure IsTenantNotFoundResponse(ResponseText: Text): Boolean
    var
        JsonResponse: JsonObject;
        Token: JsonToken;
        Detail: Text;
        ResponseTextLower: Text;
    begin
        if JsonResponse.ReadFrom(ResponseText) then
            if JsonResponse.Get('detail', Token) then
                if not IsJsonNull(Token) then begin
                    Detail := LowerCase(Token.AsValue().AsText());
                    if StrPos(Detail, 'tenant not found') > 0 then
                        exit(true);
                end;

        ResponseTextLower := LowerCase(ResponseText);
        exit(StrPos(ResponseTextLower, 'tenant not found') > 0);
    end;

    local procedure GetBackendErrorMessage(OperationName: Text; StatusCode: Integer; ResponseText: Text): Text
    var
        SafeDetail: Text;
    begin
        SafeDetail := GetSafeBackendErrorText(ResponseText);

        case StatusCode of
            401:
                exit(StrSubstNo('%1 failed. Status 401. The backend did not accept the credentials or invite code. Please check the invite code and register again.', OperationName));
            403:
                exit(StrSubstNo('%1 failed. Status 403. The invite code or tenant access was rejected by BCSentinel. Please check the invite code or contact BCSentinel support.', OperationName));
            404:
                exit(StrSubstNo('%1 failed. Status 404. Tenant not found in backend. Please reset registration and register again.', OperationName));
            422:
                exit(StrSubstNo('%1 failed. Status 422. The submitted registration data was not accepted. Check the invite code and API Base URL. %2', OperationName, SafeDetail));
            500:
                exit(StrSubstNo('%1 failed. Status 500. BCSentinel returned a server error. Try again later or contact BCSentinel support if this continues.', OperationName));
            else
                exit(StrSubstNo('%1 failed. Status %2. %3', OperationName, StatusCode, SafeDetail));
        end;
    end;

    local procedure GetRegistrationErrorMessage(StatusCode: Integer; ResponseText: Text): Text
    var
        JsonResponse: JsonObject;
        Token: JsonToken;
        ErrorCode: Text;
    begin
        if JsonResponse.ReadFrom(ResponseText) then
            if JsonResponse.Get('code', Token) then
                if not IsJsonNull(Token) and Token.IsValue() then
                    ErrorCode := UpperCase(Token.AsValue().AsText());

        case ErrorCode of
            'REGISTRATION_IDENTITY_CONFLICT':
                exit(RegistrationIdentityConflictLbl);
            'TENANT_MEMBERSHIP_NOT_ALLOWED', 'TENANT_ACCESS_FORBIDDEN':
                exit(RegistrationPermissionDeniedLbl);
            'TENANT_NOT_FOUND':
                exit(RegistrationTenantNotFoundLbl);
            'INVALID_REGISTRATION_PAYLOAD':
                exit(RegistrationInvalidDataLbl);
            'DASHBOARD_USER_DISABLED':
                exit(RegistrationDashboardUserDisabledLbl);
            'TENANT_MEMBERSHIP_DISABLED':
                exit(RegistrationMembershipDisabledLbl);
            'REGISTRATION_TEMPORARILY_UNAVAILABLE':
                exit(RegistrationTemporarilyUnavailableLbl);
            'REGISTRATION_UNEXPECTED_ERROR':
                exit(RegistrationUnexpectedErrorLbl);
        end;

        case StatusCode of
            400, 422:
                exit(RegistrationInvalidDataLbl);
            401, 403:
                exit(RegistrationPermissionDeniedLbl);
            404:
                exit(RegistrationTenantNotFoundLbl);
            409:
                exit(RegistrationIdentityConflictLbl);
            500 .. 599:
                exit(RegistrationUnexpectedErrorLbl);
            else
                exit(RegistrationUnexpectedErrorLbl);
        end;
    end;

    procedure EnsureTenantRegistered(var Setup: Record "DH Setup")
    var
        RegistrationMessage: Text;
    begin
        EnsureSetupLoaded(Setup);

        if not Setup."Data Processing Consent" then
            Error(EnableDataProcessingConsentLbl);

        // Nur wenn wirklich noch nichts existiert
        if (Setup."Tenant ID" = '') or (GetApiToken(Setup) = '') then
            RegistrationMessage := RegisterTenant(Setup);
    end;

    procedure RegisterTenant(var Setup: Record "DH Setup"): Text
    var
        Client: HttpClient;
        Content: HttpContent;
        Headers: HttpHeaders;
        RequestHeaders: HttpHeaders;
        Response: HttpResponseMessage;
        RequestText: Text;
        ResponseText: Text;
        JsonRequest: JsonObject;
        JsonResponse: JsonObject;
        Token: JsonToken;
        TenantId: Text;
        ApiToken: Text;
        DashboardInviteEmail: Text;
        DashboardInviteError: Text;
        DashboardInviteSent: Boolean;
        ExistingDashboardUser: Boolean;
        MembershipCreated: Boolean;
        IdentityMgt: Codeunit "DH Tenant Identity Mgt.";
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        EnsureSetupLoaded(Setup);

        if Setup."API Base URL" = '' then
            Error(ConfigureApiBaseUrlLbl);

        if not Setup."Data Processing Consent" then
            Error(EnableDataProcessingConsentBeforeRegisterLbl);

        Setup.EnsureValidContactEmail();

        Client.Timeout(30000);

        JsonRequest.Add('entra_tenant_id', IdentityMgt.GetEntraTenantId());
        JsonRequest.Add('environment_name', IdentityMgt.GetEnvironmentName());
        JsonRequest.Add('environment_type', IdentityMgt.GetEnvironmentType());
        JsonRequest.Add('company_id', IdentityMgt.GetCompanyId());
        JsonRequest.Add('company_name', IdentityMgt.GetCompanyName());
        JsonRequest.Add('app_version', IdentityMgt.GetAppVersion());
        JsonRequest.Add('preferred_language', GetPreferredLanguage());
        JsonRequest.Add('contact_email', Setup."Contact Email");
        JsonRequest.Add('invite_code', Setup."Registration Invite Code");
        if Setup."Tenant ID" <> '' then
            JsonRequest.Add('existing_tenant_id', Setup."Tenant ID");
        JsonRequest.WriteTo(RequestText);

        Content.WriteFrom(RequestText);
        Content.GetHeaders(Headers);
        Headers.Clear();
        Headers.Add('Content-Type', 'application/json');

        if (Setup."Tenant ID" <> '') and SecretMgt.HasApiToken(Setup) then begin
            RequestHeaders := Client.DefaultRequestHeaders();
            RequestHeaders.Add('X-Tenant-Id', Setup."Tenant ID");
            RequestHeaders.Add('X-Api-Token', SecretMgt.GetApiToken(Setup));
        end;

        if not Client.Post(BuildUrl(Setup."API Base URL", '/tenant/register'), Content, Response) then
            Error(RegistrationNetworkErrorLbl);

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error(GetRegistrationErrorMessage(Response.HttpStatusCode(), ResponseText));

        if not JsonResponse.ReadFrom(ResponseText) then
            Error(BackendInvalidJsonLbl);

        if JsonResponse.Get('tenant_id', Token) then
            if not IsJsonNull(Token) then
                TenantId := Token.AsValue().AsText();

        if JsonResponse.Get('api_token', Token) then
            if not IsJsonNull(Token) then
                ApiToken := Token.AsValue().AsText();

        if JsonResponse.Get('dashboard_invite_sent', Token) then
            if not IsJsonNull(Token) then
                DashboardInviteSent := Token.AsValue().AsBoolean();

        if JsonResponse.Get('dashboard_invite_email', Token) then
            if not IsJsonNull(Token) then
                DashboardInviteEmail := Token.AsValue().AsText();

        if JsonResponse.Get('dashboard_invite_error', Token) then
            if not IsJsonNull(Token) then
                DashboardInviteError := Token.AsValue().AsText();

        if JsonResponse.Get('existing_dashboard_user', Token) then
            if not IsJsonNull(Token) then
                ExistingDashboardUser := Token.AsValue().AsBoolean();

        if JsonResponse.Get('membership_created', Token) then
            if not IsJsonNull(Token) then
                MembershipCreated := Token.AsValue().AsBoolean();

        if TenantId = '' then
            Error(BackendMissingTenantIdLbl);

        if ApiToken = '' then
            Error(BackendMissingApiTokenLbl);

        Setup.Validate("Tenant ID", CopyStr(TenantId, 1, MaxStrLen(Setup."Tenant ID")));
        StoreApiToken(Setup, ApiToken);
        Setup.Registered := true;
        Setup."Registration Date" := CurrentDateTime();
        Setup.Modify(true);

        if DashboardInviteEmail = '' then
            DashboardInviteEmail := Setup."Contact Email";

        if ExistingDashboardUser and MembershipCreated then
            exit(StrSubstNo(RegistrationExistingUserAddedLbl, IdentityMgt.GetEnvironmentName()));

        if ExistingDashboardUser then
            exit(RegistrationExistingMembershipLbl);

        if DashboardInviteSent then
            exit(StrSubstNo(RegistrationCompletedInviteSentLbl, DashboardInviteEmail));

        if DashboardInviteError <> '' then
            exit(StrSubstNo(RegistrationCompletedInviteFailedLbl, DashboardInviteError));

        exit(RegistrationCompletedInviteUnknownLbl);
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
        ProductAccessToken: JsonToken;
        ProductAccess: JsonObject;
        CapabilitiesToken: JsonToken;
        Capabilities: JsonObject;
        TenantContextToken: JsonToken;
        TenantContext: JsonObject;
        IdentityMgt: Codeunit "DH Tenant Identity Mgt.";
        ProductAccessGranted: Boolean;
        DashboardAccessGranted: Boolean;
        IssuesAccessGranted: Boolean;
        ReportAccessGranted: Boolean;
        PermanentFreeAccess: Boolean;
        MonitoringAccessGranted: Boolean;
        SubscriptionGranted: Boolean;
        ScanStartGranted: Boolean;
        ServerTimeUtc: DateTime;
        SnapshotExpiresAt: DateTime;
    begin
        EnsureTenantAccessConfigured(Setup);

        // Invalidate and persist old positive authorization before any network operation.
        Setup.InvalidateAccessSnapshot();
        Setup.Modify(true);
        Commit();

        Headers := Client.DefaultRequestHeaders();
        if Headers.Contains('X-Tenant-Id') then
            Headers.Remove('X-Tenant-Id');
        if Headers.Contains('X-Api-Token') then
            Headers.Remove('X-Api-Token');
        if Headers.Contains('X-Preferred-Language') then
            Headers.Remove('X-Preferred-Language');
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', GetApiToken(Setup));
        Headers.Add('X-Preferred-Language', GetPreferredLanguage());

        if not Client.Get(BuildUrl(Setup."API Base URL", '/license/status'), Response) then
            Error(BackendRequestNotSentLbl);

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then begin
            if (Response.HttpStatusCode() = 404) and IsTenantNotFoundResponse(ResponseText) then
                Error(TenantNotFoundLbl);

            Error(GetBackendErrorMessage('License status request', Response.HttpStatusCode(), ResponseText));
        end;

        if not JsonResponse.ReadFrom(ResponseText) then
            Error(BackendInvalidJsonLbl);

        if not JsonResponse.Get('snapshot_version', Token) then
            Error(IncompleteAccessSnapshotLbl);
        Setup."Access Snapshot Version" := CopyStr(GetJsonTokenText(Token), 1, MaxStrLen(Setup."Access Snapshot Version"));
        if Setup."Access Snapshot Version" = '' then
            Error(IncompleteAccessSnapshotLbl);

        if not JsonResponse.Get('current_time_utc', Token) then
            Error(IncompleteAccessSnapshotLbl);
        ServerTimeUtc := ParseJsonDateTime(GetJsonTokenText(Token));
        if ServerTimeUtc = 0DT then
            Error(InvalidServerTimeLbl);

        if not JsonResponse.Get('snapshot_expires_at_utc', Token) then
            Error(IncompleteAccessSnapshotLbl);
        SnapshotExpiresAt := ParseJsonDateTime(GetJsonTokenText(Token));
        if (SnapshotExpiresAt = 0DT) or (SnapshotExpiresAt <= ServerTimeUtc) then
            Error(InvalidAccessSnapshotExpiryLbl);

        if not JsonResponse.Get('tenant_context', TenantContextToken) then
            Error(MissingTenantContextLbl);
        TenantContext := TenantContextToken.AsObject();
        if not TenantContext.Get('tenant_id', Token) then
            Error(IncompleteTenantContextLbl);
        Setup."Access Snapshot Tenant ID" := CopyStr(GetJsonTokenText(Token), 1, MaxStrLen(Setup."Access Snapshot Tenant ID"));
        if LowerCase(Setup."Access Snapshot Tenant ID") <> LowerCase(Setup."Tenant ID") then
            Error(AccessSnapshotTenantMismatchLbl);
        if not TenantContext.Get('environment_name', Token) then
            Error(IncompleteEnvironmentContextLbl);
        Setup."Access Snapshot Environment" := CopyStr(GetJsonTokenText(Token), 1, MaxStrLen(Setup."Access Snapshot Environment"));
        if LowerCase(Setup."Access Snapshot Environment") <> LowerCase(IdentityMgt.GetEnvironmentName()) then
            Error(AccessSnapshotEnvironmentMismatchLbl);
        if not TenantContext.Get('environment_type', Token) then
            Error(IncompleteEnvironmentContextLbl);
        Setup."Access Snapshot Env. Type" := CopyStr(GetJsonTokenText(Token), 1, MaxStrLen(Setup."Access Snapshot Env. Type"));
        if LowerCase(Setup."Access Snapshot Env. Type") <> LowerCase(IdentityMgt.GetEnvironmentType()) then
            Error(AccessSnapshotEnvironmentTypeMismatchLbl);
        if not TenantContext.Get('company_id', Token) then
            Error(IncompleteCompanyContextLbl);
        Setup."Access Snapshot Company ID" := CopyStr(GetJsonTokenText(Token), 1, MaxStrLen(Setup."Access Snapshot Company ID"));
        if LowerCase(DelChr(Setup."Access Snapshot Company ID", '=', '{}')) <> LowerCase(DelChr(IdentityMgt.GetCompanyId(), '=', '{}')) then
            Error(AccessSnapshotCompanyMismatchLbl);

        if not JsonResponse.Get('capabilities', CapabilitiesToken) then
            Error(MissingCapabilitiesLbl);
        Capabilities := CapabilitiesToken.AsObject();
        if not TryGetCapabilityGranted(Capabilities, 'product_access', ProductAccessGranted) or
           not TryGetCapabilityGranted(Capabilities, 'dashboard_access', DashboardAccessGranted) or
           not TryGetCapabilityGranted(Capabilities, 'issues_access', IssuesAccessGranted) or
           not TryGetCapabilityGranted(Capabilities, 'report_access', ReportAccessGranted) or
           not TryGetCapabilityGranted(Capabilities, 'monitoring_access', MonitoringAccessGranted) or
           not TryGetCapabilityGranted(Capabilities, 'subscription_active', SubscriptionGranted) or
           not TryGetCapabilityGranted(Capabilities, 'scan_start_access', ScanStartGranted)
        then
            Error(IncompleteCapabilitiesLbl);

        if JsonResponse.Get('plan', Token) then
            if not IsJsonNull(Token) then
                Setup."Current Plan" := MapPlan(Token.AsValue().AsText());

        if JsonResponse.Get('license_status', Token) then
            if not IsJsonNull(Token) then
                Setup."License Status" := MapLicenseStatus(Token.AsValue().AsText());

        Setup."Last License Check" := CurrentDateTime();
        Setup."Premium Enabled" := false;
        Setup."Scan Credits Available" := 0;
        /*Setup."Assessment Credits Available" := 0;*/
        Setup."Validation Credits Available" := 0;
        Setup."Monitoring Active" := false;
        Setup."Dashboard Access Until" := '';
        Setup."Issue Access Until" := '';
        Setup."Report Access Until" := '';
        Setup."Can Run Deep Scan" := false;
        Setup."Can View Dashboard" := false;
        Setup."Can View Issue Details" := false;
        Setup."Product Access Model" := '';
        Setup."Can Run Data Health Score" := true;
        Setup."Data Health Score Completed" := false;
        Setup."Free Assessment Used" := false;
        Setup."Premium Until" := '';
        Setup."Monitoring Until" := '';

        if JsonResponse.Get('features', FeaturesToken) then begin
            Features := FeaturesToken.AsArray();
            Setup."Premium Enabled" := HasPremiumActionFeatures(Features);
        end;

        Setup."Premium Enabled" := ProductAccessGranted;
        Setup."Can View Dashboard" := DashboardAccessGranted;
        Setup."Can View Issue Details" := IssuesAccessGranted;
        Setup."Can View Reports" := ReportAccessGranted;
        Setup."Can Use Monitoring" := MonitoringAccessGranted;
        Setup."Subscription Active" := SubscriptionGranted;
        Setup."Can Run Deep Scan" := ScanStartGranted;

        if JsonResponse.Get('validation_credits', Token) then
            Setup."Validation Credits Available" := GetJsonTokenInteger(Token, 0)
        else if JsonResponse.Get('validation_scan_credits_available', Token) then
            Setup."Validation Credits Available" := GetJsonTokenInteger(Token, 0);
        Setup."Scan Credits Available" := Setup."Validation Credits Available";

        if JsonResponse.Get('free_assessment_used', Token) then begin
            Setup."Free Assessment Used" := GetJsonTokenBoolean(Token, false);
            Setup."Data Health Score Completed" := Setup."Free Assessment Used";
            Setup."Can Run Data Health Score" := not Setup."Free Assessment Used";
        end;
        if JsonResponse.Get('premium_until', Token) then
            Setup."Premium Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Premium Until"));
        if JsonResponse.Get('monitoring_until', Token) then
            Setup."Monitoring Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Monitoring Until"));

        if JsonResponse.Get('monitoring_active', Token) then
            Setup."Monitoring Active" := GetJsonTokenBoolean(Token, false);

        if JsonResponse.Get('dashboard_access_until_bc', Token) then
            Setup."Dashboard Access Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Dashboard Access Until"));

        if (Setup."Dashboard Access Until" = '') and JsonResponse.Get('dashboard_access_until', Token) then
            Setup."Dashboard Access Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Dashboard Access Until"));

        if JsonResponse.Get('issue_access_until_bc', Token) then
            Setup."Issue Access Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Issue Access Until"));

        if (Setup."Issue Access Until" = '') and JsonResponse.Get('issue_access_until', Token) then
            Setup."Issue Access Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Issue Access Until"));

        if JsonResponse.Get('can_run_deep_scan', Token) then
            Setup."Can Run Deep Scan" := GetJsonTokenBoolean(Token, false);

        if JsonResponse.Get('can_view_dashboard', Token) then
            Setup."Can View Dashboard" := GetJsonTokenBoolean(Token, false);

        if JsonResponse.Get('can_view_issue_details', Token) then
            Setup."Can View Issue Details" := GetJsonTokenBoolean(Token, false);

        if JsonResponse.Get('can_run_data_health_score', Token) then
            Setup."Can Run Data Health Score" := GetJsonTokenBoolean(Token, true);

        if JsonResponse.Get('has_completed_data_health_score', Token) then
            Setup."Data Health Score Completed" := GetJsonTokenBoolean(Token, false);

        if JsonResponse.Get('product_access', ProductAccessToken) then begin
            ProductAccess := ProductAccessToken.AsObject();
            if ProductAccess.Get('access_model', Token) then
                Setup."Product Access Model" := CopyStr(GetJsonTokenText(Token), 1, MaxStrLen(Setup."Product Access Model"));
            if ProductAccess.Get('free_access_permanent', Token) then
                PermanentFreeAccess := GetJsonTokenBoolean(Token, false);
            if (Setup."Dashboard Access Until" = '') and ProductAccess.Get('dashboard_access_until_bc', Token) then
                Setup."Dashboard Access Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Dashboard Access Until"));
            if (Setup."Dashboard Access Until" = '') and ProductAccess.Get('dashboard_access_until', Token) then
                Setup."Dashboard Access Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Dashboard Access Until"));
            if (Setup."Dashboard Access Until" = '') and ProductAccess.Get('premium_access_until_bc', Token) then
                Setup."Dashboard Access Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Dashboard Access Until"));
            if (Setup."Dashboard Access Until" = '') and ProductAccess.Get('premium_access_until', Token) then
                Setup."Dashboard Access Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Dashboard Access Until"));
            if (Setup."Dashboard Access Until" = '') and ProductAccess.Get('subscription_end_bc', Token) then
                Setup."Dashboard Access Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Dashboard Access Until"));
            if (Setup."Dashboard Access Until" = '') and ProductAccess.Get('subscription_end', Token) then
                Setup."Dashboard Access Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Dashboard Access Until"));
            if (Setup."Issue Access Until" = '') and ProductAccess.Get('issue_access_until_bc', Token) then
                Setup."Issue Access Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Issue Access Until"));
            if (Setup."Issue Access Until" = '') and ProductAccess.Get('issue_access_until', Token) then
                Setup."Issue Access Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Issue Access Until"));
            if (Setup."Issue Access Until" = '') and ProductAccess.Get('premium_access_until_bc', Token) then
                Setup."Issue Access Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Issue Access Until"));
            if (Setup."Issue Access Until" = '') and ProductAccess.Get('premium_access_until', Token) then
                Setup."Issue Access Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Issue Access Until"));
            if (Setup."Issue Access Until" = '') and ProductAccess.Get('subscription_end_bc', Token) then
                Setup."Issue Access Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Issue Access Until"));
            if (Setup."Issue Access Until" = '') and ProductAccess.Get('subscription_end', Token) then
                Setup."Issue Access Until" := CopyStr(FormatJsonDateTimeText(GetJsonTokenText(Token)), 1, MaxStrLen(Setup."Issue Access Until"));
        end;

        if Setup."Product Access Model" = '' then
            if Setup."Monitoring Active" then
                Setup."Product Access Model" := 'monitoring'
            else
                if Setup."Scan Credits Available" > 0 then
                    Setup."Product Access Model" := 'one_time'
                else
                    Setup."Product Access Model" := 'none';

        Setup."Access Snapshot Received At" := CurrentDateTime();
        Setup."Access Server Time UTC" := ServerTimeUtc;
        Setup."Access Snapshot Expires At" := SnapshotExpiresAt;
        Setup."Access Snapshot API URL" := CopyStr(Setup."API Base URL", 1, MaxStrLen(Setup."Access Snapshot API URL"));
        if JsonResponse.Get('correlation_id', Token) then
            Setup."Access Correlation ID" := CopyStr(GetJsonTokenText(Token), 1, MaxStrLen(Setup."Access Correlation ID"));
        Setup."Report Access Until" := CopyStr(FormatJsonDateTimeText(GetCapabilityUntil(Capabilities, 'report_access')), 1, MaxStrLen(Setup."Report Access Until"));
        if PermanentFreeAccess then begin
            Setup."Dashboard Access Until" := '';
            Setup."Issue Access Until" := '';
            Setup."Report Access Until" := '';
        end;

        Setup.Modify(true);
    end;

    local procedure TryGetCapabilityGranted(var Capabilities: JsonObject; CapabilityName: Text; var Granted: Boolean): Boolean
    var
        CapabilityToken: JsonToken;
        Capability: JsonObject;
        GrantedToken: JsonToken;
    begin
        Granted := false;
        if not Capabilities.Get(CapabilityName, CapabilityToken) then
            exit(false);
        Capability := CapabilityToken.AsObject();
        if not Capability.Get('granted', GrantedToken) then
            exit(false);
        Granted := GetJsonTokenBoolean(GrantedToken, false);
        exit(true);
    end;

    local procedure GetCapabilityUntil(var Capabilities: JsonObject; CapabilityName: Text): Text
    var
        CapabilityToken: JsonToken;
        Capability: JsonObject;
        UntilToken: JsonToken;
    begin
        if not Capabilities.Get(CapabilityName, CapabilityToken) then
            exit('');
        Capability := CapabilityToken.AsObject();
        if not Capability.Get('valid_until_utc', UntilToken) then
            exit('');
        exit(GetJsonTokenText(UntilToken));
    end;

    procedure EnsureReadyForScan(var Setup: Record "DH Setup")
    begin
        EnsureTenantRegistered(Setup);
        RefreshLicenseStatus(Setup);
        if not Setup."Can Run Deep Scan" then
            if not IsPremiumAllowed(Setup) then
                Error(ValidationOrMonitoringRequiredLbl);
    end;

    procedure IsPremiumAllowed(Setup: Record "DH Setup"): Boolean
    begin
        exit(
            (Setup."Current Plan" = Setup."Current Plan"::Premium) and
            (Setup."License Status" in [Setup."License Status"::Trial, Setup."License Status"::Active]));
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
            Error(BackendRequestNotSentLbl);

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error(HistoryRequestFailedLbl, Response.HttpStatusCode(), GetSafeBackendErrorText(ResponseText));

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
            Error(BackendRequestNotSentLbl);

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error(TrendRequestFailedLbl, Response.HttpStatusCode(), GetSafeBackendErrorText(ResponseText));

        exit(ResponseText);
    end;

    procedure SyncScanToBackend(var Setup: Record "DH Setup"; RequestText: Text)
    begin
        SyncScanToBackendAndGetResponse(Setup, RequestText);
    end;

    procedure SyncScanToBackendAndGetResponse(var Setup: Record "DH Setup"; RequestText: Text): Text
    var
        ResponseText: Text;
        FailureMessage: Text;
        LeaseRejected: Boolean;
    begin
        if not TrySyncScanToBackendAndGetResponse(Setup, RequestText, ResponseText, FailureMessage, LeaseRejected) then
            Error(FailureMessage);
        exit(ResponseText);
    end;

    procedure TrySyncScanToBackendAndGetResponse(var Setup: Record "DH Setup"; RequestText: Text; var ResponseText: Text; var FailureMessage: Text; var LeaseRejected: Boolean): Boolean
    var
        Client: HttpClient;
        Content: HttpContent;
        Headers: HttpHeaders;
        Response: HttpResponseMessage;
    begin
        Clear(ResponseText);
        Clear(FailureMessage);
        LeaseRejected := false;
        EnsureTenantAccessConfigured(Setup);

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

        if not Client.Post(BuildUrl(Setup."API Base URL", '/scan/sync'), Content, Response) then begin
            FailureMessage := ScanSyncNetworkErrorLbl;
            exit(false);
        end;

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then begin
            FailureMessage := GetExecutionLeaseConflictMessage(ResponseText, LeaseRejected);
            if FailureMessage = '' then
                FailureMessage := StrSubstNo(ScanSyncFailedLbl, Response.HttpStatusCode(), GetSafeBackendErrorText(ResponseText));
            exit(false);
        end;

        exit(true);
    end;

    local procedure IsDataHealthScoreSyncPayload(RequestText: Text): Boolean
    var
        Payload: JsonObject;
        Token: JsonToken;
    begin
        if not Payload.ReadFrom(RequestText) then
            exit(false);

        if not Payload.Get('scan_type', Token) then
            exit(false);

        if IsJsonNull(Token) then
            exit(false);

        exit(LowerCase(Token.AsValue().AsText()) = 'data_health_score');
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
            Error(BackendDeleteRequestNotSentLbl);

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error(BackendScanDeleteFailedLbl, Response.HttpStatusCode(), GetSafeBackendErrorText(ResponseText));
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
            Error(BackendReconcileRequestNotSentLbl);

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error(BackendReconcileFailedLbl, Response.HttpStatusCode(), GetSafeBackendErrorText(ResponseText));
    end;

    procedure ClearBackendScanHistoryForReset(var Setup: Record "DH Setup")
    var
        Client: HttpClient;
        Content: HttpContent;
        Headers: HttpHeaders;
        Response: HttpResponseMessage;
        RequestText: Text;
        ResponseText: Text;
        JsonRequest: JsonObject;
        ScanIds: JsonArray;
    begin
        EnsureSetupLoaded(Setup);

        if Setup."Tenant ID" = '' then
            exit;

        if GetApiToken(Setup) = '' then
            exit;

        JsonRequest.Add('tenant_id', Setup."Tenant ID");
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
            Error(BackendHistoryCleanupRequestNotSentLbl);

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error(BackendHistoryCleanupFailedLbl, Response.HttpStatusCode(), GetSafeBackendErrorText(ResponseText));
    end;

    procedure StartDeepScan(var Setup: Record "DH Setup"; var DeepScanRun: Record "DH Deep Scan Run"; TotalModules: Integer)
    var
        FailureMessage: Text;
        TerminalFailure: Boolean;
    begin
        if not TryStartDeepScan(Setup, DeepScanRun, TotalModules, FailureMessage, TerminalFailure) then
            Error(FailureMessage);
    end;

    procedure StartDataHealthScore(var Setup: Record "DH Setup"; var DeepScanRun: Record "DH Deep Scan Run"; TotalModules: Integer)
    var
        FailureMessage: Text;
        TerminalFailure: Boolean;
    begin
        if not TryStartDeepScan(Setup, DeepScanRun, TotalModules, FailureMessage, TerminalFailure) then
            Error(FailureMessage);
    end;

    procedure TryStartDeepScan(var Setup: Record "DH Setup"; var DeepScanRun: Record "DH Deep Scan Run"; TotalModules: Integer; var FailureMessage: Text; var TerminalFailure: Boolean): Boolean
    begin
        exit(TryStartBackendScan(Setup, DeepScanRun, TotalModules, FailureMessage, TerminalFailure));
    end;

    local procedure TryStartBackendScan(var Setup: Record "DH Setup"; var DeepScanRun: Record "DH Deep Scan Run"; TotalModules: Integer; var FailureMessage: Text; var TerminalFailure: Boolean): Boolean
    var
        Client: HttpClient;
        Content: HttpContent;
        ContentHeaders: HttpHeaders;
        RequestHeaders: HttpHeaders;
        Response: HttpResponseMessage;
        RequestText: Text;
        ResponseText: Text;
        JsonRequest: JsonObject;
        IdentityMgt: Codeunit "DH Tenant Identity Mgt.";
    begin
        Clear(FailureMessage);
        TerminalFailure := false;
        EnsureTenantAccessConfigured(Setup);

        if DeepScanRun."Run ID" = '' then begin
            FailureMessage := ScanStartInvalidRequestLbl;
            TerminalFailure := true;
            exit(false);
        end;
        if IsNullGuid(DeepScanRun."Client Request ID") then begin
            FailureMessage := ScanStartInvalidRequestLbl;
            TerminalFailure := true;
            exit(false);
        end;

        JsonRequest.Add('tenant_id', Setup."Tenant ID");
        JsonRequest.Add('preferred_language', GetPreferredLanguage());
        JsonRequest.Add('run_id', Format(DeepScanRun."Run ID"));
        JsonRequest.Add('client_request_id', Format(DeepScanRun."Client Request ID"));
        JsonRequest.Add('scan_mode', DeepScanRun."Scan Mode");
        JsonRequest.Add('total_modules', TotalModules);
        JsonRequest.Add('company_name', CompanyName());
        JsonRequest.Add('environment_name', IdentityMgt.GetEnvironmentName());
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

        if not Client.Post(BuildUrl(Setup."API Base URL", '/scan/start'), Content, Response) then begin
            FailureMessage := ScanStartNetworkErrorLbl;
            exit(false);
        end;

        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then begin
            FailureMessage := GetScanStartErrorMessage(Response.HttpStatusCode(), ResponseText, TerminalFailure);
            exit(false);
        end;

        if not TryParseScanStartLifecycle(ResponseText, DeepScanRun) then begin
            FailureMessage := ScanStartInvalidResponseLbl;
            exit(false);
        end;
        DeepScanRun.Modify(true);
        exit(true);
    end;

    local procedure GetScanStartErrorMessage(StatusCode: Integer; ResponseText: Text; var TerminalFailure: Boolean): Text
    var
        JsonResponse: JsonObject;
        Token: JsonToken;
        ErrorCode: Text;
    begin
        TerminalFailure := (StatusCode >= 400) and (StatusCode < 500);
        if JsonResponse.ReadFrom(ResponseText) then
            if JsonResponse.Get('code', Token) then
                if not IsJsonNull(Token) and Token.IsValue() then
                    ErrorCode := UpperCase(Token.AsValue().AsText());

        case ErrorCode of
            'SCAN_ID_TENANT_CONFLICT', 'SCAN_ID_REQUEST_CONFLICT', 'SCAN_ID_CONFLICT':
                exit(ScanIdConflictLbl);
            'SCAN_REQUEST_PAYLOAD_CONFLICT':
                exit(ScanRequestConflictLbl);
            'FREE_SCAN_ALREADY_USED':
                exit(FreeScanAlreadyUsedLbl);
        end;

        case StatusCode of
            400, 422:
                exit(ScanStartInvalidRequestLbl);
            401, 403:
                exit(ScanStartPermissionDeniedLbl);
            409:
                exit(ScanStartConflictLbl);
            500 .. 599:
                begin
                    TerminalFailure := false;
                    exit(ScanStartTemporaryErrorLbl);
                end;
            else begin
                TerminalFailure := false;
                exit(ScanStartTemporaryErrorLbl);
            end;
        end;
    end;

    local procedure GetExecutionLeaseConflictMessage(ResponseText: Text; var LeaseRejected: Boolean): Text
    var
        JsonResponse: JsonObject;
        Token: JsonToken;
        ErrorCode: Text;
    begin
        LeaseRejected := false;
        if not JsonResponse.ReadFrom(ResponseText) then
            exit('');
        if not JsonResponse.Get('code', Token) then
            exit('');
        if IsJsonNull(Token) or not Token.IsValue() then
            exit('');

        ErrorCode := LowerCase(Token.AsValue().AsText());
        case ErrorCode of
            'scan_execution_token_stale',
            'scan_execution_lease_expired',
            'scan_worker_mismatch',
            'scan_execution_not_owned':
                begin
                    LeaseRejected := true;
                    exit(ScanLeaseRejectedLbl);
                end;
        end;
        exit('');
    end;

    [TryFunction]
    local procedure TryParseScanStartLifecycle(ResponseText: Text; var DeepScanRun: Record "DH Deep Scan Run")
    var
        JsonResponse: JsonObject;
        Token: JsonToken;
        ExecutionToken: Guid;
        WorkerId: Guid;
    begin
        if not JsonResponse.ReadFrom(ResponseText) then
            Error(ScanStartResponseInvalidJsonLbl);
        if not JsonResponse.Get('execution_token', Token) then
            Error(ScanStartExecutionTokenMissingLbl);
        if not Evaluate(ExecutionToken, GetJsonTokenText(Token)) then
            Error(ScanStartExecutionTokenInvalidLbl);
        if JsonResponse.Get('worker_id', Token) then begin
            if not Evaluate(WorkerId, GetJsonTokenText(Token)) then
                Error(ScanStartWorkerIdentityInvalidLbl);
            if WorkerId <> DeepScanRun."Client Request ID" then
                Error(ScanStartWorkerMismatchLbl);
        end;

        DeepScanRun."Execution Token" := ExecutionToken;
        DeepScanRun."Correlation ID" := '';
        if JsonResponse.Get('correlation_id', Token) then
            DeepScanRun."Correlation ID" := CopyStr(GetJsonTokenText(Token), 1, MaxStrLen(DeepScanRun."Correlation ID"));
    end;

    procedure UpdateScanProgress(var Setup: Record "DH Setup"; var DeepScanRun: Record "DH Deep Scan Run"; StatusValue: Text; CurrentStep: Text; EventMessage: Text)
    var
        FailureMessage: Text;
        LeaseRejected: Boolean;
    begin
        if not TryUpdateScanProgress(Setup, DeepScanRun, StatusValue, CurrentStep, EventMessage, FailureMessage, LeaseRejected) then
            Error(FailureMessage);
    end;

    procedure TryUpdateScanProgress(var Setup: Record "DH Setup"; var DeepScanRun: Record "DH Deep Scan Run"; StatusValue: Text; CurrentStep: Text; EventMessage: Text; var FailureMessage: Text; var LeaseRejected: Boolean): Boolean
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
        Clear(FailureMessage);
        LeaseRejected := false;
        EnsureTenantAccessConfigured(Setup);

        if DeepScanRun."Run ID" = '' then
            exit(true);

        JsonRequest.Add('tenant_id', Setup."Tenant ID");
        JsonRequest.Add('preferred_language', GetPreferredLanguage());
        JsonRequest.Add('run_id', Format(DeepScanRun."Run ID"));
        JsonRequest.Add('scan_mode', GetDeepScanRunMode(DeepScanRun));
        JsonRequest.Add('status', StatusValue);
        JsonRequest.Add('progress_percent', DeepScanRun."Progress %");
        JsonRequest.Add('current_module', DeepScanRun."Current Module");
        JsonRequest.Add('current_step', CurrentStep);
        JsonRequest.Add('event_message', EventMessage);
        JsonRequest.Add('total_modules', DeepScanRun."Total Modules");
        JsonRequest.Add('completed_modules', DeepScanRun."Completed Modules");
        JsonRequest.Add('failed_modules', DeepScanRun."Failed Modules");
        if not IsNullGuid(DeepScanRun."Execution Token") then
            JsonRequest.Add('execution_token', Format(DeepScanRun."Execution Token"));
        JsonRequest.Add('worker_id', Format(DeepScanRun."Client Request ID"));
        if DeepScanRun."Correlation ID" <> '' then
            JsonRequest.Add('correlation_id', DeepScanRun."Correlation ID");
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

        if not Client.Post(BuildUrl(Setup."API Base URL", '/scan/status/update'), Content, Response) then begin
            FailureMessage := ScanStatusNetworkErrorLbl;
            exit(false);
        end;

        Response.Content.ReadAs(ResponseText);
        if Response.IsSuccessStatusCode() then
            ParseScanStatusResponse(ResponseText, DeepScanRun)
        else begin
            FailureMessage := GetExecutionLeaseConflictMessage(ResponseText, LeaseRejected);
            if FailureMessage = '' then
                FailureMessage := StrSubstNo(ScanStatusFailedLbl, Response.HttpStatusCode(), Format(DeepScanRun."Run ID"), GetSafeBackendErrorText(ResponseText));
            exit(false);
        end;
        exit(true);
    end;

    local procedure GetDeepScanRunMode(var DeepScanRun: Record "DH Deep Scan Run"): Text
    begin
        if LowerCase(DeepScanRun."Scan Mode") = 'data_health_score' then
            exit('data_health_score');

        if LowerCase(DeepScanRun."Scan Mode") = 'monitoring' then
            exit('monitoring');

        exit('deep');
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
            Error(ScanStatusRequestNotSentLbl, Format(RunId));

        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error(ScanStatusRequestFailedLbl,
                Response.HttpStatusCode(),
                Format(RunId),
                GetSafeBackendErrorText(ResponseText));

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
        ExecutionToken: Guid;
    begin
        if ResponseText = '' then
            exit;

        if not JsonResponse.ReadFrom(ResponseText) then
            Error(ScanStatusResponseInvalidJsonLbl);

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
        if JsonResponse.Get('started_at', Token) then
            if DeepScanRun."Started At" = 0DT then
                DeepScanRun."Started At" := ParseJsonDateTime(GetJsonTokenText(Token));
        if JsonResponse.Get('completed_at', Token) then
            DeepScanRun."Finished At" := ParseJsonDateTime(GetJsonTokenText(Token));
        if JsonResponse.Get('estimated_remaining_seconds', Token) then
            DeepScanRun."Estimated Remaining Seconds" := GetJsonTokenInteger(Token, DeepScanRun."Estimated Remaining Seconds");
        if JsonResponse.Get('total_modules', Token) then
            DeepScanRun."Total Modules" := GetJsonTokenInteger(Token, DeepScanRun."Total Modules");
        if JsonResponse.Get('completed_modules', Token) then
            DeepScanRun."Completed Modules" := GetJsonTokenInteger(Token, DeepScanRun."Completed Modules");
        if JsonResponse.Get('failed_modules', Token) then
            DeepScanRun."Failed Modules" := GetJsonTokenInteger(Token, DeepScanRun."Failed Modules");
        if JsonResponse.Get('execution_attempt', Token) then
            DeepScanRun."Execution Attempt" := GetJsonTokenInteger(Token, DeepScanRun."Execution Attempt");
        if JsonResponse.Get('lease_expires_at', Token) then
            DeepScanRun."Lease Expires At" := ParseJsonDateTime(GetJsonTokenText(Token));
        if JsonResponse.Get('execution_token', Token) then
            if Evaluate(ExecutionToken, GetJsonTokenText(Token)) then
                DeepScanRun."Execution Token" := ExecutionToken;
        if JsonResponse.Get('correlation_id', Token) then
            DeepScanRun."Correlation ID" := CopyStr(GetJsonTokenText(Token), 1, MaxStrLen(DeepScanRun."Correlation ID"));
        if JsonResponse.Get('recovery_required', Token) then
            if GetJsonTokenBoolean(Token, false) then
                DeepScanRun."Start Request Status" := DeepScanRun."Start Request Status"::RetryRequired;
        if JsonResponse.Get('error_message', Token) then
            DeepScanRun."Error Message" := CopyStr(GetJsonTokenText(Token), 1, MaxStrLen(DeepScanRun."Error Message"));
        if JsonResponse.Get('warning_message', Token) then
            DeepScanRun."Warning Message" := CopyStr(GetJsonTokenText(Token), 1, MaxStrLen(DeepScanRun."Warning Message"));
        if JsonResponse.Get('recent_events', EventsToken) then
            DeepScanRun."Recent Events" := CopyStr(BuildRecentEventsText(EventsToken), 1, MaxStrLen(DeepScanRun."Recent Events"));

        NormalizeParsedScanStatus(DeepScanRun);
    end;

    procedure ApplyScanSyncLifecycleResponse(ResponseText: Text; var DeepScanRun: Record "DH Deep Scan Run")
    var
        JsonResponse: JsonObject;
        LifecycleToken: JsonToken;
        LifecycleText: Text;
    begin
        if not JsonResponse.ReadFrom(ResponseText) then
            exit;
        if not JsonResponse.Get('scan_status', LifecycleToken) then
            exit;
        if not LifecycleToken.IsObject() then
            exit;

        LifecycleToken.AsObject().WriteTo(LifecycleText);
        ParseScanStatusResponse(LifecycleText, DeepScanRun);
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
            Error(BackendInvalidJsonLbl);

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
            Error(RegisterTenantFirstLbl);

        if GetApiToken(Setup) = '' then
            Error(ApiTokenMissingLbl);
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
        IdentityMgt: Codeunit "DH Tenant Identity Mgt.";
    begin
        EnsureTenantAccessConfigured(Setup);

        Url :=
            BuildUrl(Setup."API Base URL", '/analytics/get-token') +
            '?company=' + EncodeUrlValue(CompanyName()) +
            '&environment=' + EncodeUrlValue(IdentityMgt.GetEnvironmentName()) +
            '&environment_type=' + EncodeUrlValue(IdentityMgt.GetEnvironmentType()) +
            '&entra_tenant_id=' + EncodeUrlValue(IdentityMgt.GetEntraTenantId()) +
            '&company_id=' + EncodeUrlValue(IdentityMgt.GetCompanyId()) +
            '&tenant_id=' + EncodeUrlValue(Setup."Tenant ID") +
            '&preferred_language=' + EncodeUrlValue(GetPreferredLanguage()) +
            '&scan_mode=' + EncodeUrlValue(GetAnalyticsScanMode(Setup)) +
            '&bc_issue_launch_url=' + EncodeUrlValue(GetIssueDrilldownLaunchUrl());

        Headers := Client.DefaultRequestHeaders();
        if Headers.Contains('X-Tenant-Id') then
            Headers.Remove('X-Tenant-Id');
        if Headers.Contains('X-Api-Token') then
            Headers.Remove('X-Api-Token');
        if Headers.Contains('X-Preferred-Language') then
            Headers.Remove('X-Preferred-Language');
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', GetApiToken(Setup));
        Headers.Add('X-Preferred-Language', GetPreferredLanguage());

        if not Client.Get(Url, Response) then
            Error(DashboardTokenServiceNotReachableLbl);

        Response.Content.ReadAs(ResponseText);

        if not Response.IsSuccessStatusCode() then
            Error(
                DashboardTokenServiceErrorLbl,
                Response.HttpStatusCode(),
                GetSafeBackendErrorText(ResponseText));

        if not JsonResponse.ReadFrom(ResponseText) then
            Error(DashboardTokenResponseInvalidJsonLbl);

        if not JsonResponse.Get('token', TokenValue) then
            Error(DashboardTokenMissingLbl);

        exit(TokenValue.AsValue().AsText());
    end;

    procedure OpenPremiumCheckout(var Setup: Record "DH Setup")
    begin
        OpenProductCheckout(Setup, 'monitoring_monthly');
    end;

    procedure OpenProductCheckout(var Setup: Record "DH Setup"; ProductCode: Text)
    var
        CheckoutUrl: Text;
    begin
        CheckoutUrl := CreateProductCheckoutSession(Setup, ProductCode);
        Hyperlink(CheckoutUrl);
    end;

    procedure CreatePremiumCheckoutSession(var Setup: Record "DH Setup"): Text
    begin
        exit(CreateProductCheckoutSession(Setup, 'monitoring_monthly'));
    end;

    procedure CreateProductCheckoutSession(var Setup: Record "DH Setup"; ProductCode: Text): Text
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
        JsonRequest.Add('preferred_language', GetPreferredLanguage());
        JsonRequest.Add('product_code', ProductCode);
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
            Error(BillingCheckoutRequestNotSentLbl);

        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error(BillingCheckoutFailedLbl, Response.HttpStatusCode(), GetSafeBackendErrorText(ResponseText));

        if not JsonResponse.ReadFrom(ResponseText) then
            Error(BillingCheckoutResponseInvalidJsonLbl);

        if JsonResponse.Get('checkout_url', TokenValue) then
            if not IsJsonNull(TokenValue) then
                CheckoutUrl := TokenValue.AsValue().AsText();

        if CheckoutUrl = '' then
            Error(BillingCheckoutUrlMissingLbl);

        exit(CheckoutUrl);
    end;

    local procedure GetAnalyticsScanMode(var Setup: Record "DH Setup"): Text
    begin
        if Setup."Premium Enabled" then
            exit('premium_deep');

        exit('free_deep');
    end;

    procedure TryGetCheckCatalog(var CatalogResponse: JsonObject): Boolean
    var
        Setup: Record "DH Setup";
        Client: HttpClient;
        Headers: HttpHeaders;
        Response: HttpResponseMessage;
        ResponseText: Text;
        Url: Text;
    begin
        Clear(CatalogResponse);
        if not Setup.Get('SETUP') then
            exit(false);
        if (Setup."API Base URL" = '') or (Setup."Tenant ID" = '') or (GetApiToken(Setup) = '') then
            exit(false);

        Client.Timeout(30000);
        Headers := Client.DefaultRequestHeaders();
        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', GetApiToken(Setup));
        Url := BuildUrl(Setup."API Base URL", '/catalog/checks?language=' + EncodeUrlValue(GetPreferredLanguage()));
        if not Client.Get(Url, Response) then
            exit(false);
        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            exit(false);
        exit(CatalogResponse.ReadFrom(ResponseText));
    end;

    local procedure GetPreferredLanguage(): Text
    var
        LanguageId: Integer;
    begin
        LanguageId := GlobalLanguage();

        case LanguageId of
            1031, // German - Germany
            2055, // German - Switzerland
            3079, // German - Austria
            4103, // German - Luxembourg
            5127: // German - Liechtenstein
                exit('de');
            else
                exit('en');
        end;
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
    var
        ApiUrlPolicy: Codeunit "DH API URL Policy";
    begin
        exit(ApiUrlPolicy.BuildUrl(BaseUrl, RelativePath));
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

    local procedure GetJsonTokenBoolean(Token: JsonToken; DefaultValue: Boolean): Boolean
    var
        ParsedValue: Boolean;
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
            'completed', 'completed_with_warnings':
                DeepScanRun.Status := DeepScanRun.Status::Completed;
            'failed', 'stalled', 'expired':
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
            'completed', 'completed_with_warnings':
                begin
                    DeepScanRun."Progress %" := 100;
                    DeepScanRun."Current Module" := 'All modules completed';
                    DeepScanRun."Current Step" := 'Scan completed';
                    DeepScanRun."Estimated Remaining Seconds" := 0;
                    if DeepScanRun."Total Modules" > 0 then
                        DeepScanRun."Completed Modules" := DeepScanRun."Total Modules";
                end;
            'failed', 'expired':
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
        if Evaluate(ParsedDateTime, Value, 9) then
            exit(ParsedDateTime);

        Value := Value.Replace('T', ' ');
        Value := Value.Replace('Z', '');
        if StrLen(Value) > 19 then
            Value := CopyStr(Value, 1, 19);

        if Evaluate(ParsedDateTime, Value) then
            exit(ParsedDateTime);

        exit(0DT);
    end;

    local procedure FormatJsonDateTimeText(Value: Text): Text
    begin
        if StrLen(Value) < 19 then
            exit(Value);

        if (CopyStr(Value, 5, 1) <> '-') or (CopyStr(Value, 8, 1) <> '-') then
            exit(Value);

        exit(CopyStr(Value, 9, 2) + '.' + CopyStr(Value, 6, 2) + '.' + CopyStr(Value, 1, 4) + ' ' + CopyStr(Value, 12, 8));
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


    var
        EnableDataProcessingConsentLbl: Label 'Please enable Data Processing Consent first.';
        ConfigureApiBaseUrlLbl: Label 'Please configure the API Base URL first.';
        EnableDataProcessingConsentBeforeRegisterLbl: Label 'Please enable Data Processing Consent before registering the tenant.';
        BackendRequestNotSentLbl: Label 'The backend request could not be sent. Please verify the network connection.';
        BackendInvalidJsonLbl: Label 'The backend returned an invalid JSON response. Contact BCSentinel support if this continues.';
        BackendMissingTenantIdLbl: Label 'The backend response does not contain a tenant_id.';
        BackendMissingApiTokenLbl: Label 'The backend response does not contain an api_token.';
        AccessSnapshotCompanyMismatchLbl: Label 'The access snapshot belongs to a different company. Detailed access remains blocked.';
        AccessSnapshotEnvironmentMismatchLbl: Label 'The access snapshot belongs to a different environment. Detailed access remains blocked.';
        AccessSnapshotEnvironmentTypeMismatchLbl: Label 'The access snapshot belongs to a different environment type. Detailed access remains blocked.';
        AccessSnapshotTenantMismatchLbl: Label 'The access snapshot belongs to a different tenant. Detailed access remains blocked.';
        ApiTokenMissingLbl: Label 'The API token is missing. Register the tenant again.';
        BackendConnectionTestFailedLbl: Label 'Backend connection test failed. Status: %1. %2', Comment = '%1 = HTTP status, %2 = safe backend error';
        BackendDeleteRequestNotSentLbl: Label 'The backend delete request could not be sent. Check the network connection.';
        BackendHistoryCleanupFailedLbl: Label 'Backend scan history cleanup failed. Status: %1. %2', Comment = '%1 = HTTP status, %2 = safe backend error';
        BackendHistoryCleanupRequestNotSentLbl: Label 'The backend scan history cleanup request could not be sent. Check the network connection.';
        BackendReachableMsg: Label 'BCSentinel connection successfully tested. Status: %1', Comment = '%1 = backend status';
        BackendReconcileFailedLbl: Label 'Backend reconciliation failed. Status: %1. %2', Comment = '%1 = HTTP status, %2 = safe backend error';
        BackendReconcileRequestNotSentLbl: Label 'The backend reconciliation request could not be sent. Check the network connection.';
        BackendScanDeleteFailedLbl: Label 'Deleting the backend scan failed. Status: %1. %2', Comment = '%1 = HTTP status, %2 = safe backend error';
        BillingCheckoutFailedLbl: Label 'Opening the secure checkout failed. Status: %1. %2', Comment = '%1 = HTTP status, %2 = safe backend error';
        BillingCheckoutRequestNotSentLbl: Label 'The secure checkout request could not be sent. Check the network connection.';
        BillingCheckoutResponseInvalidJsonLbl: Label 'The secure checkout returned an invalid response. Contact BCSentinel support if this continues.';
        BillingCheckoutUrlMissingLbl: Label 'The secure checkout response does not contain a checkout URL.';
        DashboardTokenMissingLbl: Label 'The field "token" is missing in the dashboard token response.';
        DashboardTokenResponseInvalidJsonLbl: Label 'The dashboard token service returned an invalid response. Contact BCSentinel support if this continues.';
        DashboardTokenServiceErrorLbl: Label 'The dashboard token service returned an error. Status: %1. %2', Comment = '%1 = HTTP status, %2 = safe backend error';
        DashboardTokenServiceNotReachableLbl: Label 'The dashboard token service could not be reached.';
        HistoryRequestFailedLbl: Label 'Retrieving scan history failed. Status: %1. %2', Comment = '%1 = HTTP status, %2 = safe backend error';
        IncompleteAccessSnapshotLbl: Label 'The backend returned an incomplete access snapshot. Detailed access remains blocked.';
        IncompleteCapabilitiesLbl: Label 'The backend returned an incomplete capability set. Detailed access remains blocked.';
        IncompleteCompanyContextLbl: Label 'The backend returned an incomplete company context. Detailed access remains blocked.';
        IncompleteEnvironmentContextLbl: Label 'The backend returned an incomplete environment context. Detailed access remains blocked.';
        IncompleteTenantContextLbl: Label 'The backend returned an incomplete tenant context. Detailed access remains blocked.';
        InvalidAccessSnapshotExpiryLbl: Label 'The backend returned an invalid access snapshot expiry. Detailed access remains blocked.';
        InvalidServerTimeLbl: Label 'The backend returned an invalid server time. Detailed access remains blocked.';
        MissingCapabilitiesLbl: Label 'The backend returned no capability decisions. Detailed access remains blocked.';
        MissingTenantContextLbl: Label 'The backend returned no tenant context. Detailed access remains blocked.';
        RegisterTenantFirstLbl: Label 'Register the tenant first.';
        ScanStartExecutionTokenInvalidLbl: Label 'The scan start response contains an invalid execution token. Retry the same scan request.';
        ScanStartExecutionTokenMissingLbl: Label 'The scan start response has no execution token. Retry the same scan request.';
        ScanStartResponseInvalidJsonLbl: Label 'The scan start response is invalid. Retry the same scan request.';
        ScanStartWorkerIdentityInvalidLbl: Label 'The scan start response contains an invalid worker identity. Retry the same scan request.';
        ScanStartWorkerMismatchLbl: Label 'The scan start response belongs to another worker. Retry the same scan request.';
        ScanStatusRequestFailedLbl: Label 'Retrieving the scan status failed. Status: %1. Run ID: %2. %3', Comment = '%1 = HTTP status, %2 = run ID, %3 = safe backend error';
        ScanStatusRequestNotSentLbl: Label 'The scan status request could not be sent. Run ID: %1.', Comment = '%1 = run ID';
        ScanStatusResponseInvalidJsonLbl: Label 'The scan status response is invalid.';
        TenantNotFoundLbl: Label 'The tenant was not found in BCSentinel. Reset the cached registration and register again.';
        TrendRequestFailedLbl: Label 'Retrieving the score trend failed. Status: %1. %2', Comment = '%1 = HTTP status, %2 = safe backend error';
        RegistrationNetworkErrorLbl: Label 'BCSentinel could not complete the registration because the service was not reachable. Check the API address and try again.';
        RegistrationInvalidDataLbl: Label 'The registration could not be completed because required information is missing or invalid.';
        RegistrationPermissionDeniedLbl: Label 'The registration was rejected because this environment is not authorized.';
        RegistrationIdentityConflictLbl: Label 'The registration conflicts with an existing Business Central identity. Verify the environment and company or contact BCSentinel support.';
        RegistrationTenantNotFoundLbl: Label 'The registered BCSentinel tenant could not be found. Reset the cached registration and register again.';
        RegistrationDashboardUserDisabledLbl: Label 'The BCSentinel dashboard account for this email address is disabled. Contact BCSentinel support.';
        RegistrationMembershipDisabledLbl: Label 'Access to this Business Central environment is disabled for the dashboard account. Contact BCSentinel support.';
        RegistrationTemporarilyUnavailableLbl: Label 'BCSentinel registration is temporarily unavailable. Try again later.';
        RegistrationUnexpectedErrorLbl: Label 'The registration could not be completed because of an internal error. Try again later or contact BCSentinel support.';
        RegistrationExistingUserAddedLbl: Label 'This email address is already linked to a BCSentinel account. The environment "%1" was added successfully. After signing in, you can switch between your available BCSentinel dashboards.', Comment = '%1 = Business Central environment name';
        RegistrationExistingMembershipLbl: Label 'This Business Central environment is already linked to the existing BCSentinel dashboard account.';
        ScanStartNetworkErrorLbl: Label 'BCSentinel could not send the scan start request. Check the API connection and retry the same scan.';
        ScanStartInvalidRequestLbl: Label 'The scan could not be started because the request identity or required scan data is invalid. Start a new scan.';
        ScanStartInvalidResponseLbl: Label 'BCSentinel accepted the connection but returned an incomplete scan start response. Retry the same scan.';
        ScanStartPermissionDeniedLbl: Label 'The scan start was rejected because this environment is not authorized. Refresh product access and try again.';
        ScanIdConflictLbl: Label 'This scan ID is already assigned to another scan. The local run was stopped safely. Start the scan again to create a new unique run.';
        ScanRequestConflictLbl: Label 'This scan request was already used with different start data. The local run was stopped safely. Start a new scan.';
        FreeScanAlreadyUsedLbl: Label 'The one-time free Data Health Score has already been started for this environment.';
        ScanStartConflictLbl: Label 'The scan start conflicts with an existing request. The local run was stopped safely. Start a new scan.';
        ScanStartTemporaryErrorLbl: Label 'BCSentinel could not confirm the scan start because of a temporary backend error. Retry the same scan request.';
        ScanLeaseRejectedLbl: Label 'Backend synchronization stopped because the scan execution ownership expired or changed. Your local scan result is preserved. Start a new scan or contact BCSentinel support.';
        ScanStatusNetworkErrorLbl: Label 'The scan status could not be sent to BCSentinel. The local scan continues and synchronization will be retried.';
        ScanStatusFailedLbl: Label 'Scan status update failed. Status: %1. Run ID: %2. %3', Comment = '%1 = HTTP status, %2 = run ID, %3 = safe backend error';
        ScanSyncNetworkErrorLbl: Label 'The local scan completed, but its result could not be sent to BCSentinel. Check the connection and retry synchronization.';
        ScanSyncFailedLbl: Label 'The local scan completed, but backend synchronization failed. Status: %1. %2', Comment = '%1 = HTTP status, %2 = safe backend error';
        RegistrationCompletedInviteSentLbl: Label 'BCSentinel tenant registration completed. Dashboard access was sent to %1.', Comment = '%1 = runtime value';
        RegistrationCompletedInviteFailedLbl: Label 'BCSentinel tenant registration completed, but the dashboard invitation email could not be sent. Please resend the invitation in the admin dashboard. Details: %1', Comment = '%1 = runtime value';
        RegistrationCompletedInviteUnknownLbl: Label 'BCSentinel tenant registration completed, but the dashboard invitation email could not be confirmed. Please check the admin dashboard.';

    var
        ValidationOrMonitoringRequiredLbl: Label 'A new scan requires a Validation Check or active Monitoring.';
}
