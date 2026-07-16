codeunit 53198 "DH API URL Policy"
{
    procedure NormalizeAndValidateBaseUrl(Value: Text): Text[250]
    var
        EnvironmentInformation: Codeunit "Environment Information";
        NormalizedValue: Text;
        Authority: Text;
        Host: Text;
        SchemeSeparatorPos: Integer;
        PathPos: Integer;
    begin
        NormalizedValue := DelChr(Value, '<>', ' ');
        if NormalizedValue = '' then
            Error(ConfigureApiBaseUrlErr);
        if StrPos(NormalizedValue, ' ') > 0 then
            Error(InvalidApiBaseUrlErr);
        if (StrPos(NormalizedValue, '?') > 0) or (StrPos(NormalizedValue, '#') > 0) then
            Error(BaseUrlQueryFragmentErr);

        SchemeSeparatorPos := StrPos(NormalizedValue, '://');
        if SchemeSeparatorPos = 0 then
            Error(InvalidApiBaseUrlErr);

        Authority := CopyStr(NormalizedValue, SchemeSeparatorPos + 3);
        PathPos := StrPos(Authority, '/');
        if PathPos > 0 then
            Authority := CopyStr(Authority, 1, PathPos - 1);
        if Authority = '' then
            Error(InvalidApiBaseUrlErr);
        if StrPos(Authority, '@') > 0 then
            Error(EmbeddedCredentialsErr);

        Host := GetHostWithoutPort(Authority);
        if Host = '' then
            Error(InvalidApiBaseUrlErr);

        if StrPos(LowerCase(NormalizedValue), 'https://') = 1 then
            exit(CopyStr(RemoveTrailingSlash(NormalizedValue), 1, 250));

        if StrPos(LowerCase(NormalizedValue), 'http://') <> 1 then
            Error(InvalidApiBaseUrlErr);

        if EnvironmentInformation.IsProduction() or not IsLoopbackHost(Host) then
            Error(UnsafeApiConnectionErr);

        exit(CopyStr(RemoveTrailingSlash(NormalizedValue), 1, 250));
    end;

    procedure BuildUrl(BaseUrl: Text; RelativePath: Text): Text
    var
        ValidatedBaseUrl: Text[250];
    begin
        ValidatedBaseUrl := NormalizeAndValidateBaseUrl(BaseUrl);
        if (RelativePath = '') or (CopyStr(RelativePath, 1, 1) <> '/') then
            Error(InvalidRelativePathErr);
        if (StrPos(RelativePath, '://') > 0) or (CopyStr(RelativePath, 1, 2) = '//') or (StrPos(RelativePath, '\') > 0) then
            Error(InvalidRelativePathErr);
        exit(ValidatedBaseUrl + RelativePath);
    end;

    local procedure GetHostWithoutPort(Authority: Text): Text
    var
        ClosingBracketPos: Integer;
        ColonPos: Integer;
    begin
        if CopyStr(Authority, 1, 1) = '[' then begin
            ClosingBracketPos := StrPos(Authority, ']');
            if ClosingBracketPos = 0 then
                exit('');
            exit(LowerCase(CopyStr(Authority, 2, ClosingBracketPos - 2)));
        end;

        ColonPos := StrPos(Authority, ':');
        if ColonPos > 0 then
            exit(LowerCase(CopyStr(Authority, 1, ColonPos - 1)));
        exit(LowerCase(Authority));
    end;

    local procedure IsLoopbackHost(Host: Text): Boolean
    begin
        exit((Host = 'localhost') or (Host = '127.0.0.1') or (Host = '::1'));
    end;

    local procedure RemoveTrailingSlash(Value: Text): Text
    begin
        while (StrLen(Value) > 0) and (CopyStr(Value, StrLen(Value), 1) = '/') do
            Value := CopyStr(Value, 1, StrLen(Value) - 1);
        exit(Value);
    end;

    var
        ConfigureApiBaseUrlErr: Label 'Please configure the API Base URL first.';
        InvalidApiBaseUrlErr: Label 'The API Base URL is invalid. Enter an absolute HTTPS URL.';
        BaseUrlQueryFragmentErr: Label 'The API Base URL must not contain a query string or fragment.';
        EmbeddedCredentialsErr: Label 'The API Base URL must not contain embedded credentials.';
        UnsafeApiConnectionErr: Label 'Unsafe API connection blocked. HTTPS is required for production environments.';
        InvalidRelativePathErr: Label 'The API request path is invalid.';
}
