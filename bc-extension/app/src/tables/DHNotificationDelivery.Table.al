table 53174 "DH Notification Delivery"
{
    Caption = 'BCSentinel Notification Delivery';
    DataClassification = CustomerContent;

    fields
    {
        field(1; "Delivery ID"; Guid) { Caption = 'Delivery ID'; DataClassification = SystemMetadata; }
        field(2; "Event ID"; Guid) { Caption = 'Event ID'; DataClassification = SystemMetadata; Editable = false; }
        field(3; "Rule ID"; Guid) { Caption = 'Rule ID'; DataClassification = SystemMetadata; Editable = false; }
        field(4; "Recipient ID"; Guid) { Caption = 'Recipient ID'; DataClassification = SystemMetadata; Editable = false; }
        field(5; Channel; Code[20]) { Caption = 'Channel'; DataClassification = SystemMetadata; Editable = false; }
        field(6; Status; Code[20]) { Caption = 'Status'; DataClassification = SystemMetadata; Editable = false; }
        field(7; "Attempt No."; Integer) { Caption = 'Attempt No.'; DataClassification = SystemMetadata; Editable = false; }
        field(8; "Created At UTC"; DateTime) { Caption = 'Created At UTC'; DataClassification = SystemMetadata; Editable = false; }
        field(9; "Updated At UTC"; DateTime) { Caption = 'Updated At UTC'; DataClassification = SystemMetadata; Editable = false; }
        field(10; "Sent At UTC"; DateTime) { Caption = 'Sent At UTC'; DataClassification = SystemMetadata; Editable = false; }
        field(11; "Provider Message ID"; Text[100]) { Caption = 'Provider Message ID'; DataClassification = SystemMetadata; Editable = false; }
        field(12; "Error Code"; Code[50]) { Caption = 'Error Code'; DataClassification = SystemMetadata; Editable = false; }
        field(13; "Error Message Safe"; Text[250]) { Caption = 'Safe Error Message'; DataClassification = SystemMetadata; Editable = false; }
        field(14; "Next Retry At UTC"; DateTime) { Caption = 'Next Retry At UTC'; DataClassification = SystemMetadata; Editable = false; }
        field(15; "Suppression Reason"; Text[150]) { Caption = 'Suppression Reason'; DataClassification = SystemMetadata; Editable = false; }
    }

    keys
    {
        key(PK; "Delivery ID") { Clustered = true; }
        key(DuplicateControl; "Event ID", "Rule ID", "Recipient ID") { }
        key(StatusQueue; Status, "Next Retry At UTC", "Created At UTC") { }
    }

    trigger OnInsert()
    begin
        if IsNullGuid("Delivery ID") then
            "Delivery ID" := CreateGuid();
        if Channel = '' then
            Channel := 'email';
        if Status = '' then
            Status := 'queued';
        if "Attempt No." = 0 then
            "Attempt No." := 1;
        "Created At UTC" := CurrentDateTime();
        "Updated At UTC" := "Created At UTC";
        TestField("Event ID");
        TestField("Rule ID");
        TestField("Recipient ID");
    end;

    trigger OnDelete()
    begin
        Error('Notification delivery evidence is retained and cannot be deleted.');
    end;

    trigger OnRename()
    begin
        Error('Notification delivery IDs are immutable.');
    end;
}
