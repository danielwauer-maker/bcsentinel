table 53175 "DH Notification Config Audit"
{
    Caption = 'BCSentinel Notification Config Audit';
    DataClassification = CustomerContent;

    fields
    {
        field(1; "Entry No."; Integer) { Caption = 'Entry No.'; AutoIncrement = true; DataClassification = SystemMetadata; }
        field(2; "Object Type"; Code[30]) { Caption = 'Object Type'; DataClassification = SystemMetadata; }
        field(3; "Object Ref"; Text[150]) { Caption = 'Object Ref.'; DataClassification = SystemMetadata; }
        field(4; "Changed Field"; Code[50]) { Caption = 'Changed Field'; DataClassification = SystemMetadata; }
        field(5; "Previous Value"; Text[250]) { Caption = 'Previous Value'; DataClassification = CustomerContent; }
        field(6; "New Value"; Text[250]) { Caption = 'New Value'; DataClassification = CustomerContent; }
        field(7; "Changed At UTC"; DateTime) { Caption = 'Changed At UTC'; DataClassification = SystemMetadata; }
        field(8; "Changed By"; Guid) { Caption = 'Changed By'; DataClassification = EndUserPseudonymousIdentifiers; }
        field(9; "Tenant ID"; Text[100]) { Caption = 'Tenant ID'; DataClassification = SystemMetadata; }
        field(10; "Company ID"; Text[100]) { Caption = 'Company ID'; DataClassification = SystemMetadata; }
    }

    keys
    {
        key(PK; "Entry No.") { Clustered = true; }
        key(ObjectHistory; "Object Type", "Object Ref", "Changed At UTC") { }
    }

    trigger OnModify()
    begin
        Error('Notification configuration audit records are immutable.');
    end;

    trigger OnDelete()
    begin
        Error('Notification configuration audit records are retained.');
    end;
}
