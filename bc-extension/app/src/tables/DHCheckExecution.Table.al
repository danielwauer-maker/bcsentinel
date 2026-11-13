table 53197 "DH Check Execution"
{
    Caption = 'Check Execution Evidence';
    DataClassification = SystemMetadata;

    fields
    {
        field(1; "Run Entry No."; Integer) { Caption = 'Run Entry No.'; TableRelation = "DH Deep Scan Run"."Entry No."; }
        field(2; "Check Code"; Code[50]) { Caption = 'Check Code'; }
        field(3; "Execution Status"; Code[20]) { Caption = 'Execution Status'; }
        field(4; "Finding Count"; Integer) { Caption = 'Finding Count'; }
        field(5; "Observed At"; DateTime) { Caption = 'Observed At'; }
    }
    keys
    {
        key(PK; "Run Entry No.", "Check Code") { Clustered = true; }
    }
}
