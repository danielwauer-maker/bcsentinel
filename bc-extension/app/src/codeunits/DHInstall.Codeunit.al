codeunit 53193 "DH Install"
{
    Subtype = Install;

    trigger OnInstallAppPerCompany()
    var
        Setup: Record "DH Setup";
    begin
        if not Setup.Get('SETUP') then begin
            Setup.Init();
            Setup."Primary Key" := 'SETUP';
            Setup.Insert(true);
        end else begin
            Setup.ApplyDefaults();
            Setup.Modify(true);
        end;

        Session.LogMessage(
            'BCS-P0E-001',
            'BCSentinel company setup initialized.',
            Verbosity::Normal,
            DataClassification::SystemMetadata,
            TelemetryScope::ExtensionPublisher,
            'Event', 'extension_installed');
    end;
}
