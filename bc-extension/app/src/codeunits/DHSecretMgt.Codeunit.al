codeunit 53136 "DH Secret Mgt."
{
    procedure StoreApiToken(var Setup: Record "DH Setup"; ApiToken: Text)
    begin
        if ApiToken = '' then
            exit;

        IsolatedStorage.Set(GetApiTokenKey(), ApiToken, DataScope::Company);
    end;

    procedure GetApiToken(var Setup: Record "DH Setup"): Text
    var
        ApiToken: Text;
    begin
        if IsolatedStorage.Get(GetApiTokenKey(), DataScope::Company, ApiToken) then
            exit(ApiToken);

        exit('');
    end;

    procedure DeleteApiToken(var Setup: Record "DH Setup")
    begin
        if IsolatedStorage.Contains(GetApiTokenKey(), DataScope::Company) then
            IsolatedStorage.Delete(GetApiTokenKey(), DataScope::Company);
    end;

    procedure HasApiToken(var Setup: Record "DH Setup"): Boolean
    begin
        exit(GetApiToken(Setup) <> '');
    end;

    local procedure GetApiTokenKey(): Text
    begin
        exit('BCSentinel.ApiToken');
    end;
}
