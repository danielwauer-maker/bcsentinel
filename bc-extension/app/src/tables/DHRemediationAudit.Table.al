table 53195 "DH Remediation Audit"
{
    Caption = 'BCSentinel Remediation Audit';
    DataClassification = CustomerContent;

    fields
    {
        field(1; "Entry No."; Integer) { AutoIncrement = true; Caption = 'Entry No.'; DataClassification = SystemMetadata; }
        field(2; "Action ID"; Guid) { Caption = 'Action ID'; DataClassification = SystemMetadata; }
        field(3; "Changed At UTC"; DateTime) { Caption = 'Changed At UTC'; DataClassification = SystemMetadata; }
        field(4; "Changed By Principal ID"; Guid) { Caption = 'Changed By Principal ID'; DataClassification = EndUserPseudonymousIdentifiers; }
        field(5; "Tenant ID"; Text[100]) { Caption = 'Tenant ID'; DataClassification = SystemMetadata; }
        field(6; "Company ID"; Text[100]) { Caption = 'Company ID'; DataClassification = SystemMetadata; }
        field(7; "Changed Field or Status"; Text[50]) { Caption = 'Changed Field or Status'; DataClassification = SystemMetadata; }
        field(8; "Previous Value"; Text[250]) { Caption = 'Previous Value'; DataClassification = CustomerContent; }
        field(9; "New Value"; Text[250]) { Caption = 'New Value'; DataClassification = CustomerContent; }
    }

    keys
    {
        key(PK; "Entry No.") { Clustered = true; }
        key(ActionTimeline; "Action ID", "Changed At UTC") { }
    }

    trigger OnModify()
    begin
        Error('Remediation audit entries are immutable.');
    end;

    trigger OnDelete()
    begin
        Error('Remediation audit entries are immutable.');
    end;
}
