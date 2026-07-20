codeunit 53194 "DH Upgrade"
{
    Subtype = Upgrade;

    trigger OnUpgradePerCompany()
    var
        Setup: Record "DH Setup";
    begin
        if not Setup.Get('SETUP') then begin
            Setup.Init();
            Setup."Primary Key" := 'SETUP';
            Setup.Insert(true);
        end;

        // Pre-P0D positive flags have no trustworthy receipt time or context.
        // Never backfill freshness from local values during an upgrade.
        Setup.InvalidateAccessSnapshot();
        Setup.ApplyDefaults();
        Setup.Modify(true);

        Session.LogMessage(
            'BCS-P0E-002',
            'BCSentinel company data upgraded and cached access invalidated.',
            Verbosity::Normal,
            DataClassification::SystemMetadata,
            TelemetryScope::ExtensionPublisher,
            'Event', 'extension_upgraded');
    end;
}
