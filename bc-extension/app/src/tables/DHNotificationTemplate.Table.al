table 53173 "DH Notification Template"
{
    Caption = 'BCSentinel Notification Template';
    DataClassification = CustomerContent;

    fields
    {
        field(1; "Template Key"; Code[50]) { Caption = 'Template Key'; DataClassification = SystemMetadata; }
        field(2; "Event Type"; Code[50]) { Caption = 'Event Type'; DataClassification = SystemMetadata; }
        field(3; "Language Code"; Code[10]) { Caption = 'Language Code'; DataClassification = SystemMetadata; }
        field(4; "Subject Template"; Text[250]) { Caption = 'Subject Template'; DataClassification = CustomerContent; }
        field(5; "Body Template"; Text[2048]) { Caption = 'Body Template'; DataClassification = CustomerContent; }
        field(6; "Template Version"; Code[20]) { Caption = 'Template Version'; DataClassification = SystemMetadata; }
        field(7; Enabled; Boolean) { Caption = 'Enabled'; DataClassification = CustomerContent; InitValue = true; }
        field(8; "Updated At UTC"; DateTime) { Caption = 'Updated At UTC'; DataClassification = SystemMetadata; Editable = false; }
        field(9; "Updated By"; Guid) { Caption = 'Updated By'; DataClassification = EndUserPseudonymousIdentifiers; Editable = false; }
    }

    keys
    {
        key(PK; "Template Key", "Language Code") { Clustered = true; }
        key(EventLanguage; "Event Type", "Language Code", Enabled) { }
    }

    trigger OnInsert()
    var
        NotificationMgt: Codeunit "DH Notification Mgt.";
    begin
        if "Language Code" = '' then
            "Language Code" := 'en';
        if "Template Version" = '' then
            "Template Version" := '1.0';
        "Updated At UTC" := CurrentDateTime();
        "Updated By" := UserSecurityId();
        TestField("Template Key");
        TestField("Event Type");
        TestField("Subject Template");
        TestField("Body Template");
        NotificationMgt.WriteConfigAudit('template', "Template Key" + ':' + "Language Code", 'created', '', "Event Type");
    end;

    trigger OnModify()
    var
        NotificationMgt: Codeunit "DH Notification Mgt.";
    begin
        "Updated At UTC" := CurrentDateTime();
        "Updated By" := UserSecurityId();
        NotificationMgt.WriteConfigAudit('template', "Template Key" + ':' + "Language Code", 'updated', '', "Event Type");
    end;

    trigger OnDelete()
    var
        NotificationMgt: Codeunit "DH Notification Mgt.";
    begin
        NotificationMgt.WriteConfigAudit('template', "Template Key" + ':' + "Language Code", 'deleted', "Event Type", '');
    end;
}
