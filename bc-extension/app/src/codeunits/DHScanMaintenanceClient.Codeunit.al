codeunit 53137 "DH Scan Maintenance Client"
{
    Permissions = tabledata "DH Setup" = R,
                  tabledata "DH Scan Header" = R;

    procedure DeleteScanFromBackend(var Setup: Record "DH Setup"; ScanId: Code[50])
    var
        Client: HttpClient;
        Response: HttpResponseMessage;
        ResponseText: Text;
        Headers: HttpHeaders;
        ApiClient: Codeunit "DH API Client";
    begin
        EnsureTenantAccessConfigured(Setup);

        if ScanId = '' then
            Error('The scan id is required.');

        AddTenantHeaders(Client, Setup);

        if not Client.Delete(
            BuildUrl(Setup."API Base URL", '/scan/' + Setup."Tenant ID" + '/' + Format(ScanId)),
            Response)
        then
            Error('The backend delete request could not be sent. Please verify the network connection.');

        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error('Backend scan delete failed. Status %1. %2', Response.HttpStatusCode(), ApiClient.GetSafeBackendErrorText(ResponseText));
    end;

    procedure ReconcileScansWithBackend(var Setup: Record "DH Setup")
    var
        Client: HttpClient;
        Content: HttpContent;
        ContentHeaders: HttpHeaders;
        Response: HttpResponseMessage;
        RequestText: Text;
        ResponseText: Text;
        JsonRequest: JsonObject;
        ScanIds: JsonArray;
        ScanHeader: Record "DH Scan Header";
        EffectiveScanId: Code[50];
        ApiClient: Codeunit "DH API Client";
    begin
        EnsureTenantAccessConfigured(Setup);

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
        Content.GetHeaders(ContentHeaders);
        ContentHeaders.Clear();
        ContentHeaders.Add('Content-Type', 'application/json');

        AddTenantHeaders(Client, Setup);

        if not Client.Post(BuildUrl(Setup."API Base URL", '/scan/reconcile'), Content, Response) then
            Error('The backend reconcile request could not be sent. Please verify the network connection.');

        Response.Content.ReadAs(ResponseText);
        if not Response.IsSuccessStatusCode() then
            Error('Backend reconcile failed. Status %1. %2', Response.HttpStatusCode(), ApiClient.GetSafeBackendErrorText(ResponseText));
    end;

    local procedure EnsureTenantAccessConfigured(var Setup: Record "DH Setup")
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        if not Setup.Get('SETUP') then
            Error('BCSentinel setup was not found.');

        if Setup."Tenant ID" = '' then
            Error('Please register the tenant first.');

        if SecretMgt.GetApiToken(Setup) = '' then
            Error('The API token is missing. Please register the tenant again.');
    end;

    local procedure AddTenantHeaders(var Client: HttpClient; var Setup: Record "DH Setup")
    var
        Headers: HttpHeaders;
        SecretMgt: Codeunit "DH Secret Mgt.";
    begin
        Headers := Client.DefaultRequestHeaders();
        if Headers.Contains('X-Tenant-Id') then
            Headers.Remove('X-Tenant-Id');
        if Headers.Contains('X-Api-Token') then
            Headers.Remove('X-Api-Token');

        Headers.Add('X-Tenant-Id', Setup."Tenant ID");
        Headers.Add('X-Api-Token', SecretMgt.GetApiToken(Setup));
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

    local procedure GetEffectiveScanId(var ScanHeader: Record "DH Scan Header"): Code[50]
    begin
        if ScanHeader."Backend Scan Id" <> '' then
            exit(ScanHeader."Backend Scan Id");

        exit(ScanHeader.GetDisplayRunId());
    end;
}
