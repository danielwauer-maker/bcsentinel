codeunit 53464 "BCS Finding QA Invite Mgt."
{
    // QA-only least-privilege writer; every write independently revalidates the SaaS sandbox/company guard.
    Permissions = tabledata "DH Setup" = RM;

    procedure SetRegistrationInvite(InviteCode: Text[100])
    var
        Setup: Record "DH Setup";
    begin
        RequireQASandbox();
        if InviteCode = '' then
            Error(InviteRequiredErr);
        if not Setup.Get('SETUP') then
            Error(SetupRequiredErr);

        Setup."Registration Invite Code" := InviteCode;
        Setup.Modify(true);
    end;

    procedure ClearRegistrationInvite()
    var
        Setup: Record "DH Setup";
    begin
        RequireQASandbox();
        if not Setup.Get('SETUP') then
            Error(SetupRequiredErr);

        Clear(Setup."Registration Invite Code");
        Setup.Modify(true);
    end;

    local procedure RequireQASandbox()
    var
        EnvironmentInformation: Codeunit "Environment Information";
    begin
        if not EnvironmentInformation.IsSaaSInfrastructure() then
            Error(QAOnlyErr);
        if not EnvironmentInformation.IsSandbox() then
            Error(QAOnlyErr);
        if CompanyName() <> 'BCS-FINDING-QA' then
            Error(QAOnlyErr);
    end;

    var
        QAOnlyErr: Label 'This QA helper requires the BCS-FINDING-QA company in a SaaS sandbox.';
        InviteRequiredErr: Label 'Enter a registration invite code.';
        SetupRequiredErr: Label 'BCSentinel Setup was not found.';
}
