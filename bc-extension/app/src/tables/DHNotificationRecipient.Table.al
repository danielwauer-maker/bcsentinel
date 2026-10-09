table 53172 "DH Notification Recipient"
{
    Caption = 'BCSentinel Notification Recipient';
    DataClassification = CustomerContent;

    fields
    {
        field(1; "Recipient ID"; Guid) { Caption = 'Recipient ID'; DataClassification = SystemMetadata; }
        field(2; "Tenant ID"; Text[100]) { Caption = 'Tenant ID'; DataClassification = SystemMetadata; Editable = false; }
        field(3; "Company ID"; Text[100]) { Caption = 'Company ID'; DataClassification = SystemMetadata; Editable = false; }
        field(4; "Display Name"; Text[100]) { Caption = 'Display Name'; DataClassification = EndUserIdentifiableInformation; }
        field(5; "Email Address"; Text[250]) { Caption = 'Email Address'; DataClassification = EndUserIdentifiableInformation; ExtendedDatatype = EMail; }
        field(6; Enabled; Boolean) { Caption = 'Enabled'; DataClassification = CustomerContent; InitValue = true; }
        field(7; "Principal ID"; Guid) { Caption = 'Principal ID'; DataClassification = EndUserPseudonymousIdentifiers; }
        field(8; "Language Code"; Code[10]) { Caption = 'Language Code'; DataClassification = CustomerContent; }
        field(9; "Recipient Role"; Code[30]) { Caption = 'Recipient Role'; DataClassification = CustomerContent; }
        field(10; "Created At UTC"; DateTime) { Caption = 'Created At UTC'; DataClassification = SystemMetadata; Editable = false; }
        field(11; "Updated At UTC"; DateTime) { Caption = 'Updated At UTC'; DataClassification = SystemMetadata; Editable = false; }
        field(12; "Updated By"; Guid) { Caption = 'Updated By'; DataClassification = EndUserPseudonymousIdentifiers; Editable = false; }
    }

    keys
    {
        key(PK; "Recipient ID") { Clustered = true; }
        key(EmailScope; "Tenant ID", "Company ID", "Email Address") { }
    }

    trigger OnInsert()
    var
        Setup: Record "DH Setup";
        NotificationMgt: Codeunit "DH Notification Mgt.";
    begin
        if IsNullGuid("Recipient ID") then
            "Recipient ID" := CreateGuid();
        if Setup.Get() then
            "Tenant ID" := Setup."Tenant ID";
        "Company ID" := CopyStr(CompanyName(), 1, MaxStrLen("Company ID"));
        if "Language Code" = '' then
            "Language Code" := 'en';
        "Created At UTC" := CurrentDateTime();
        "Updated At UTC" := "Created At UTC";
        "Updated By" := UserSecurityId();
        TestField("Tenant ID");
        TestField("Company ID");
        TestField("Display Name");
        TestField("Email Address");
        NotificationMgt.WriteConfigAudit('recipient', Format("Recipient ID"), 'created', '', "Email Address");
    end;

    trigger OnModify()
    var
        NotificationMgt: Codeunit "DH Notification Mgt.";
    begin
        "Updated At UTC" := CurrentDateTime();
        "Updated By" := UserSecurityId();
        NotificationMgt.WriteConfigAudit('recipient', Format("Recipient ID"), 'updated', xRec."Email Address", "Email Address");
    end;

    trigger OnDelete()
    var
        NotificationMgt: Codeunit "DH Notification Mgt.";
    begin
        NotificationMgt.WriteConfigAudit('recipient', Format("Recipient ID"), 'deleted', "Email Address", '');
    end;
}
