codeunit 53350 "DH Findings Integrity Mgt."
{
    Permissions = tabledata "DH Deep Scan Run" = R,
                  tabledata "DH Deep Scan Finding" = R;

    procedure AssertExpectedFindingsPersisted(var DeepScanRun: Record "DH Deep Scan Run"; ExpectedFindingCount: Integer)
    var
        ActualFindingCount: Integer;
    begin
        ActualFindingCount := GetPersistedFindingCount(DeepScanRun."Entry No.");
        if ActualFindingCount = ExpectedFindingCount then
            exit;

        Session.LogMessage(
            'BCS-FINDINGS-001',
            StrSubstNo('Scan %1 cannot complete: expected %2 persisted finding rows, found %3.', DeepScanRun."Run ID", ExpectedFindingCount, ActualFindingCount),
            Verbosity::Warning,
            DataClassification::SystemMetadata,
            TelemetryScope::ExtensionPublisher,
            'Event', 'findings_persistence_mismatch');
        Error(FindingsPersistenceErr, DeepScanRun."Run ID", ExpectedFindingCount, ActualFindingCount);
    end;

    procedure GetPersistedFindingCount(DeepScanEntryNo: Integer): Integer
    var
        Finding: Record "DH Deep Scan Finding";
    begin
        Finding.SetRange("Deep Scan Entry No.", DeepScanEntryNo);
        exit(Finding.Count());
    end;

    procedure GetMissingDetailsMessage(DeepScanEntryNo: Integer): Text
    var
        DeepScanRun: Record "DH Deep Scan Run";
        ActualFindingCount: Integer;
    begin
        if (DeepScanEntryNo = 0) or not DeepScanRun.Get(DeepScanEntryNo) then
            exit('');
        if DeepScanRun.Status <> DeepScanRun.Status::Completed then
            exit('');

        ActualFindingCount := GetPersistedFindingCount(DeepScanEntryNo);
        if ActualFindingCount = DeepScanRun."Issues Count" then
            exit('');

        exit(StrSubstNo(MissingDetailsLbl, DeepScanRun."Run ID", DeepScanRun."Issues Count", ActualFindingCount));
    end;

    procedure LogFindingDeletion(var DeepScanRun: Record "DH Deep Scan Run"; Source: Text)
    var
        FindingCount: Integer;
    begin
        FindingCount := GetPersistedFindingCount(DeepScanRun."Entry No.");
        Session.LogMessage(
            'BCS-FINDINGS-002',
            StrSubstNo('Deleting %1 persisted finding rows for scan %2. Source: %3.', FindingCount, DeepScanRun."Run ID", Source),
            Verbosity::Normal,
            DataClassification::SystemMetadata,
            TelemetryScope::ExtensionPublisher,
            'Event', 'findings_deleted');
    end;

    var
        FindingsPersistenceErr: Label 'Scan %1 was not completed because the persisted finding count (%3) does not equal the detected finding count (%2).';
        MissingDetailsLbl: Label 'Historical finding details are unavailable for scan %1. The completed scan recorded %2 findings, but %3 local finding rows are available. No findings have been recreated.';
}
