codeunit 53159 "DH Exception Snapshot Sync"
{
    [EventSubscriber(ObjectType::Table, Database::"DH Deep Scan Run", 'OnAfterModifyEvent', '', false, false)]
    local procedure OnAfterDeepScanRunModify(var Rec: Record "DH Deep Scan Run"; var xRec: Record "DH Deep Scan Run"; RunTrigger: Boolean)
    var
        Setup: Record "DH Setup";
    begin
        if Rec.IsTemporary then
            exit;
        if Rec.Status <> Rec.Status::Completed then
            exit;
        if Rec."Run ID" = '' then
            exit;
        if not Setup.Get('SETUP') then
            exit;
        if (Setup."Tenant ID" = '') or (Setup."API Base URL" = '') then
            exit;

        if not TrySendSnapshot(Setup, Rec."Run ID") then;
    end;

    [TryFunction]
    local procedure TrySendSnapshot(var Setup: Record "DH Setup"; ScanId: Code[50])
    var
        SecretMgt: Codeunit "DH Secret Mgt.";
        IssueException: Record "DH Issue Exception";
        Client: HttpClient;
        Content: HttpContent;
        ContentHeaders: HttpHeaders;
        RequestHeaders: HttpHeaders;
        Response: HttpResponseMessage;
        Payload: JsonObject;
        Exceptions: JsonArray;
        Item: JsonObject;
        RequestText: Text;
        ResponseText: Text;
        ApiToken: Text;
        Url: Text;
    begin
        ApiToken := SecretMgt.GetApiToken(Setup);
        if ApiToken = '' then
            Error('BCSentinel API token is not available.');

        Payload.Add('company_id', CopyStr(CompanyName(), 1, 100));

        IssueException.SetRange(Active, true);
        if IssueException.FindSet() then
            repeat
                Clear(Item);
                Item.Add('source_exception_entry_no', IssueException."Entry No.");
                Item.Add('table_id', IssueException."Table ID");
                if not IsNullGuid(IssueException."Record SystemId") then
                    Item.Add('record_system_id', Format(IssueException."Record SystemId"));
                if IssueException."Record No." <> '' then
                    Item.Add('record_no', Format(IssueException."Record No."));
                if IssueException."Record Caption" <> '' then
                    Item.Add('record_caption', IssueException."Record Caption");
                Item.Add('issue_code', Format(IssueException."Issue Code"));
                Item.Add('reason', IssueException.Reason);
                if IssueException."Created By User" <> '' then
                    Item.Add('exception_created_by', Format(IssueException."Created By User"));
                if IssueException."Created At" <> 0DT then
                    Item.Add('exception_created_at_utc', IssueException."Created At");
                Exceptions.Add(Item);
            until IssueException.Next() = 0;

        Payload.Add('exceptions', Exceptions);
        Payload.WriteTo(RequestText);

        Content.WriteFrom(RequestText);
        Content.GetHeaders(ContentHeaders);
        ContentHeaders.Clear();
        ContentHeaders.Add('Content-Type', 'application/json');

        RequestHeaders := Client.DefaultRequestHeaders();
        RequestHeaders.Add('X-Tenant-Id', Setup."Tenant ID");
        RequestHeaders.Add('X-Api-Token', ApiToken);

        Url := BuildUrl(Setup."API Base URL", '/scans/' + Format(ScanId) + '/exception-snapshot');
        if not Client.Post(Url, Content, Response) then
            Error('The exception snapshot request could not be sent.');

        Response.Content.ReadAs(ResponseText);
        if Response.HttpStatusCode() = 409 then
            exit;
        if not Response.IsSuccessStatusCode() then
            Error('Exception snapshot upload failed. Status %1.', Response.HttpStatusCode());
    end;

    local procedure BuildUrl(BaseUrl: Text; RelativePath: Text): Text
    begin
        while (StrLen(BaseUrl) > 0) and (CopyStr(BaseUrl, StrLen(BaseUrl), 1) = '/') do
            BaseUrl := CopyStr(BaseUrl, 1, StrLen(BaseUrl) - 1);
        if CopyStr(RelativePath, 1, 1) <> '/' then
            RelativePath := '/' + RelativePath;
        exit(BaseUrl + RelativePath);
    end;
}
