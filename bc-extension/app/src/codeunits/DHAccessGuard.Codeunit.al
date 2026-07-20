codeunit 53195 "DH Access Guard"
{
    Permissions = tabledata "DH Setup" = RM;

    procedure EnsureIssuesAccess()
    begin
        EnsureCapability('issues_access', true);
    end;

    procedure EnsureDashboardAccess()
    begin
        EnsureCapability('dashboard_access', true);
    end;

    procedure EnsureReportAccess()
    begin
        EnsureCapability('report_access', true);
    end;

    procedure EnsureMonitoringAccess()
    begin
        EnsureCapability('monitoring_access', true);
    end;

    procedure RefreshAccessSnapshot()
    var
        Setup: Record "DH Setup";
    begin
        GetSetup(Setup);
        if not TryRefreshAccessSnapshot(Setup) then
            Error(AccessNotVerifiedErr);
    end;

    procedure InvalidateAccessSnapshot()
    var
        Setup: Record "DH Setup";
    begin
        GetSetup(Setup);
        Setup.InvalidateAccessSnapshot();
        Setup.Modify(true);
    end;

    procedure HasFreshCapability(Capability: Text): Boolean
    var
        Setup: Record "DH Setup";
    begin
        if not Setup.Get('SETUP') then
            exit(false);
        if not IsSnapshotFreshAndBound(Setup) then
            exit(false);
        exit(IsCapabilityGranted(Setup, Capability));
    end;

    local procedure EnsureCapability(Capability: Text; ForceRefresh: Boolean)
    var
        Setup: Record "DH Setup";
    begin
        GetSetup(Setup);
        if ForceRefresh or not IsSnapshotFreshAndBound(Setup) then
            if not TryRefreshAccessSnapshot(Setup) then
                Error(AccessNotVerifiedErr);

        if not IsSnapshotFreshAndBound(Setup) then
            Error(AccessNotVerifiedErr);
        if not IsCapabilityGranted(Setup, Capability) then
            case Capability of
                'issues_access':
                    Error(IssuesAccessExpiredErr);
                'dashboard_access':
                    Error(DashboardAccessExpiredErr);
                'report_access':
                    Error(ReportAccessExpiredErr);
                else
                    Error(AccessExpiredErr);
            end;
    end;

    [TryFunction]
    local procedure TryRefreshAccessSnapshot(var Setup: Record "DH Setup")
    var
        ApiClient: Codeunit "DH API Client";
    begin
        ApiClient.RefreshLicenseStatus(Setup);
    end;

    local procedure IsSnapshotFreshAndBound(var Setup: Record "DH Setup"): Boolean
    var
        IdentityMgt: Codeunit "DH Tenant Identity Mgt.";
        MaximumLocalAge: DateTime;
    begin
        if (Setup."Access Snapshot Version" = '') or
           (Setup."Access Snapshot Received At" = 0DT) or
           (Setup."Access Server Time UTC" = 0DT) or
           (Setup."Access Snapshot Expires At" = 0DT)
        then
            exit(false);
        if Setup."Access Snapshot Expires At" <= Setup."Access Server Time UTC" then
            exit(false);
        if (Setup."Access Snapshot Expires At" - Setup."Access Server Time UTC") > 60000 then
            exit(false);

        MaximumLocalAge := Setup."Access Snapshot Received At" + 60000;
        if (CurrentDateTime() < Setup."Access Snapshot Received At") or (CurrentDateTime() > MaximumLocalAge) then
            exit(false);
        if LowerCase(Setup."Access Snapshot Tenant ID") <> LowerCase(Setup."Tenant ID") then
            exit(false);
        if LowerCase(Setup."Access Snapshot API URL") <> LowerCase(Setup."API Base URL") then
            exit(false);
        if LowerCase(Setup."Access Snapshot Environment") <> LowerCase(IdentityMgt.GetEnvironmentName()) then
            exit(false);
        if LowerCase(Setup."Access Snapshot Env. Type") <> LowerCase(IdentityMgt.GetEnvironmentType()) then
            exit(false);
        if LowerCase(DelChr(Setup."Access Snapshot Company ID", '=', '{}')) <>
           LowerCase(DelChr(IdentityMgt.GetCompanyId(), '=', '{}'))
        then
            exit(false);
        exit(true);
    end;

    local procedure IsCapabilityGranted(var Setup: Record "DH Setup"; Capability: Text): Boolean
    begin
        case Capability of
            'product_access':
                exit(Setup."Premium Enabled");
            'dashboard_access':
                exit(Setup."Can View Dashboard");
            'issues_access':
                exit(Setup."Can View Issue Details");
            'report_access':
                exit(Setup."Can View Reports");
            'monitoring_access':
                exit(Setup."Can Use Monitoring");
            'subscription_active':
                exit(Setup."Subscription Active");
            'scan_start_access':
                exit(Setup."Can Run Deep Scan" or Setup."Can Run Data Health Score");
        end;
        exit(false);
    end;

    local procedure GetSetup(var Setup: Record "DH Setup")
    begin
        if not Setup.Get('SETUP') then
            Error(SetupMissingErr);
    end;

    var
        AccessNotVerifiedErr: Label 'Current product access could not be verified. Protected details remain blocked. Check the connection and refresh product access.';
        AccessExpiredErr: Label 'Product access has expired or is not active. Refresh product access or open license management.';
        IssuesAccessExpiredErr: Label 'Access to detailed findings has expired or could not be verified. Refresh product access or open license management.';
        DashboardAccessExpiredErr: Label 'Dashboard access has expired or could not be verified. Refresh product access or open license management.';
        ReportAccessExpiredErr: Label 'Report access has expired or could not be verified. Refresh product access or open license management.';
        SetupMissingErr: Label 'BCSentinel setup is missing. Complete setup before opening protected details.';
}
