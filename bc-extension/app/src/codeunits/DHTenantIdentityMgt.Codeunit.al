codeunit 53199 "DH Tenant Identity Mgt."
{
    procedure GetEntraTenantId(): Text[100]
    begin
        exit(CopyStr(TenantId(), 1, 100));
    end;

    procedure GetEnvironmentName(): Text[100]
    var
        EnvironmentInformation: Codeunit "Environment Information";
    begin
        exit(CopyStr(EnvironmentInformation.GetEnvironmentName(), 1, 100));
    end;

    procedure GetEnvironmentType(): Text[20]
    var
        EnvironmentInformation: Codeunit "Environment Information";
    begin
        if EnvironmentInformation.IsProduction() then
            exit('production');
        if EnvironmentInformation.IsSandbox() then
            exit('sandbox');
        exit('onprem');
    end;

    procedure GetCompanyId(): Text[50]
    var
        CompanyInformation: Record "Company Information";
    begin
        if not CompanyInformation.Get() then
            Error(CompanyInformationMissingErr);
        if IsNullGuid(CompanyInformation.SystemId) then
            Error(CompanyIdentityMissingErr);
        exit(CopyStr(LowerCase(Format(CompanyInformation.SystemId)), 1, 50));
    end;

    procedure GetCompanyName(): Text[100]
    begin
        exit(CopyStr(CompanyName(), 1, 100));
    end;

    procedure GetAppVersion(): Text[30]
    var
        CurrentModule: ModuleInfo;
    begin
        if NavApp.GetCurrentModuleInfo(CurrentModule) then
            exit(CopyStr(Format(CurrentModule.AppVersion()), 1, 30));
        exit('unknown');
    end;

    var
        CompanyInformationMissingErr: Label 'Company Information must exist before BCSentinel registration.';
        CompanyIdentityMissingErr: Label 'The Business Central company identity is missing.';
}
