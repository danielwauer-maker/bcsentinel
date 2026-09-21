table 53401 "BCP Owned Record"
{
    Caption = 'QA record ownership';
    DataClassification = SystemMetadata;
    fields
    {
        field(1; "Run ID"; Integer) { Caption = 'Run ID'; }
        field(2; "Table ID"; Integer) { Caption = 'Table ID'; }
        field(3; "Record SystemId"; Guid) { Caption = 'Record SystemId'; }
        field(4; "Record ID"; RecordId) { Caption = 'Record ID'; }
        field(5; "Record No."; Code[20]) { Caption = 'Record number'; }
        field(6; "Modified At"; DateTime) { Caption = 'Original modification timestamp'; }
        field(7; Scenario; Code[50]) { Caption = 'Expected check'; }
        field(8; Supporting; Boolean) { Caption = 'Supporting record'; }
    }
    keys
    {
        key(PK; "Run ID", "Table ID", "Record SystemId") { Clustered = true; }
        key(Identity; "Table ID", "Record SystemId") { Unique = true; }
        key(Number; "Run ID", "Record No.") { }
    }
}
