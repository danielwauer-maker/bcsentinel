codeunit 53192 "DH Check Catalog Mgt."
{
    SingleInstance = true;

    procedure ResolveTitle(CheckId: Code[80]): Text[250]
    var
        Value: Text;
    begin
        EnsureLoaded();
        if Titles.Get(CheckId, Value) and (Value <> '') then
            exit(CopyStr(Value, 1, 250));
        exit(CopyStr(CheckId, 1, 250));
    end;

    procedure ResolveShortDescription(CheckId: Code[80]): Text[250]
    var
        Value: Text;
    begin
        EnsureLoaded();
        if ShortDescriptions.Get(CheckId, Value) and (Value <> '') then
            exit(CopyStr(Value, 1, 250));
        exit(CopyStr(CheckId, 1, 250));
    end;

    procedure ResolveRecommendation(CheckId: Code[80]): Text[2048]
    var
        Value: Text;
    begin
        EnsureLoaded();
        if Recommendations.Get(CheckId, Value) and (Value <> '') then
            exit(CopyStr(Value, 1, 2048));
        exit(CopyStr(CheckId, 1, 2048));
    end;

    procedure Refresh()
    begin
        Clear(Titles);
        Clear(ShortDescriptions);
        Clear(Recommendations);
        LoadAttempted := false;
        LastLoadAttemptAt := 0DT;
        EnsureLoaded();
    end;

    local procedure EnsureLoaded()
    var
        ApiClient: Codeunit "DH API Client";
        Response: JsonObject;
        ChecksToken: JsonToken;
        CheckToken: JsonToken;
        Checks: JsonArray;
        CheckObject: JsonObject;
        Index: Integer;
        CheckId: Code[80];
    begin
        if LoadAttempted then
            if (CurrentDateTime() - LastLoadAttemptAt) < CatalogRefreshInterval() then
                exit;
        LoadAttempted := true;
        LastLoadAttemptAt := CurrentDateTime();
        if not ApiClient.TryGetCheckCatalog(Response) then
            exit;
        if not Response.Get('checks', ChecksToken) or not ChecksToken.IsArray() then
            exit;
        Clear(Titles);
        Clear(ShortDescriptions);
        Clear(Recommendations);
        Checks := ChecksToken.AsArray();
        for Index := 0 to Checks.Count() - 1 do begin
            Checks.Get(Index, CheckToken);
            if CheckToken.IsObject() then begin
                CheckObject := CheckToken.AsObject();
                CheckId := CopyStr(GetJsonText(CheckObject, 'check_id'), 1, MaxStrLen(CheckId));
                if CheckId <> '' then begin
                    Titles.Set(CheckId, GetJsonText(CheckObject, 'title'));
                    ShortDescriptions.Set(CheckId, GetJsonText(CheckObject, 'short_description'));
                    Recommendations.Set(CheckId, GetJsonText(CheckObject, 'recommendation'));
                end;
            end;
        end;
    end;

    local procedure CatalogRefreshInterval(): Duration
    begin
        exit(300000);
    end;

    local procedure GetJsonText(JsonObject: JsonObject; PropertyName: Text): Text
    var
        Token: JsonToken;
    begin
        if not JsonObject.Get(PropertyName, Token) then
            exit('');
        if not Token.IsValue() then
            exit('');
        if Token.AsValue().IsNull() then
            exit('');
        exit(Token.AsValue().AsText());
    end;

    var
        Titles: Dictionary of [Code[80], Text];
        ShortDescriptions: Dictionary of [Code[80], Text];
        Recommendations: Dictionary of [Code[80], Text];
        LoadAttempted: Boolean;
        LastLoadAttemptAt: DateTime;
}
