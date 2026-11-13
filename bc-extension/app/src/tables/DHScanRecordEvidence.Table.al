table 53198 "DH Scan Record Evidence"
{
    Caption = 'Scan Record Identity Evidence';
    DataClassification = SystemMetadata;

    fields
    {
        field(1; "Run Entry No."; Integer)
        {
            Caption = 'Run Entry No.';
        }
        field(2; "Check Code"; Code[50])
        {
            Caption = 'Check Code';
        }
        field(3; "Source Table ID"; Integer)
        {
            Caption = 'Source Table ID';
        }
        field(4; "Source Record SystemId"; Guid)
        {
            Caption = 'Source Record SystemId';
            DataClassification = CustomerContent;
        }
    }

    keys
    {
        key(PK; "Run Entry No.", "Check Code", "Source Table ID", "Source Record SystemId")
        {
            Clustered = true;
        }
    }

    procedure RecordObserved(RunEntryNo: Integer; CheckCode: Code[50]; TableId: Integer; RecordSystemId: Guid)
    var
        EmptyGuid: Guid;
    begin
        if (RunEntryNo <= 0) or (CheckCode = '') or (TableId <= 0) or (RecordSystemId = EmptyGuid) then
            Error(RecordIdentityInvalidErr);

        if Get(RunEntryNo, CheckCode, TableId, RecordSystemId) then
            exit;

        Init();
        "Run Entry No." := RunEntryNo;
        "Check Code" := CheckCode;
        "Source Table ID" := TableId;
        "Source Record SystemId" := RecordSystemId;
        Insert(true);
    end;

    var
        RecordIdentityInvalidErr: Label 'The source record identity must include a run, check, table and a non-empty SystemId.';
}
