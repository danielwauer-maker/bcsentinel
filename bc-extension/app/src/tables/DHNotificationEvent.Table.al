table 53170 "DH Notification Event"
{
    Caption = 'BCSentinel Notification Event';
    DataClassification = CustomerContent;

    fields
    {
        field(1; "Event ID"; Guid) { Caption = 'Event ID'; DataClassification = SystemMetadata; }
        field(2; "Tenant ID"; Text[100]) { Caption = 'Tenant ID'; DataClassification = SystemMetadata; Editable = false; }
        field(3; "Company ID"; Text[100]) { Caption = 'Company ID'; DataClassification = SystemMetadata; Editable = false; }
        field(4; "Event Type"; Code[50]) { Caption = 'Event Type'; DataClassification = SystemMetadata; Editable = false; }
        field(5; "Occurred At UTC"; DateTime) { Caption = 'Occurred At UTC'; DataClassification = SystemMetadata; Editable = false; }
        field(6; "Correlation Key"; Text[150]) { Caption = 'Correlation Key'; DataClassification = SystemMetadata; Editable = false; }
        field(7; "Source Ref"; Text[150]) { Caption = 'Source Ref.'; DataClassification = SystemMetadata; Editable = false; }
        field(8; Severity; Code[20]) { Caption = 'Severity'; DataClassification = CustomerContent; Editable = false; }
        field(9; "Finding Key"; Code[100]) { Caption = 'Finding Key'; DataClassification = CustomerContent; Editable = false; }
        field(10; "Action ID"; Guid) { Caption = 'Action ID'; DataClassification = CustomerContent; Editable = false; }
        field(11; "Scan ID"; Code[50]) { Caption = 'Scan ID'; DataClassification = CustomerContent; Editable = false; }
        field(12; "Validation Ref"; Text[100]) { Caption = 'Validation Ref.'; DataClassification = CustomerContent; Editable = false; }
        field(13; Summary; Text[250]) { Caption = 'Summary'; DataClassification = CustomerContent; Editable = false; }
        field(14; "Metadata Version"; Code[20]) { Caption = 'Metadata Version'; DataClassification = SystemMetadata; Editable = false; }
    }

    keys
    {
        key(PK; "Event ID") { Clustered = true; }
        key(Idempotency; "Tenant ID", "Company ID", "Event Type", "Correlation Key") { }
        key(Occurred; "Occurred At UTC", "Event Type") { }
    }

    trigger OnInsert()
    begin
        if IsNullGuid("Event ID") then
            "Event ID" := CreateGuid();
        if "Occurred At UTC" = 0DT then
            "Occurred At UTC" := CurrentDateTime();
        if "Metadata Version" = '' then
            "Metadata Version" := 'v1';
        TestField("Tenant ID");
        TestField("Company ID");
        TestField("Event Type");
        TestField("Correlation Key");
        TestField("Source Ref");
    end;

    trigger OnModify()
    begin
        Error('Notification events are immutable.');
    end;

    trigger OnDelete()
    begin
        Error('Notification events are retained as delivery evidence.');
    end;

    trigger OnRename()
    begin
        Error('Notification event IDs are immutable.');
    end;
}
