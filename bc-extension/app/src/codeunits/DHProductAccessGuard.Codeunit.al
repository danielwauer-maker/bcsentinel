codeunit 53138 "DH Product Access Guard"
{
    procedure RequireIssueDetails()
    var
        Setup: Record "DH Setup";
        ApiClient: Codeunit "DH API Client";
    begin
        if not Setup.Get('SETUP') then
            Error('BCSentinel setup was not found.');

        if Setup."Tenant ID" = '' then
            Error('Please register the tenant first.');

        ApiClient.RefreshLicenseStatus(Setup);
        if not Setup."Can View Issue Details" then
            Error('Detailed findings require an active Assessment, Validation Check, or Monitoring access.');
    end;
}
