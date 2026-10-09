table 53176 "DH Notification Setup"
{
    Caption = 'BCSentinel Notification Setup';
    DataClassification = CustomerContent;

    fields
    {
        field(1; "Primary Key"; Code[10]) { Caption = 'Primary Key'; DataClassification = SystemMetadata; }
        field(2; "Tenant ID"; Text[100]) { Caption = 'Tenant ID'; DataClassification = SystemMetadata; Editable = false; }
        field(3; "Company ID"; Text[100]) { Caption = 'Company ID'; DataClassification = SystemMetadata; Editable = false; }
        field(4; Enabled; Boolean) { Caption = 'Notifications Enabled'; DataClassification = CustomerContent; InitValue = true; }
        field(5; "Preferred Language"; Code[10]) { Caption = 'Preferred Language'; DataClassification = CustomerContent; InitValue = 'en'; }
        field(6; "Delivery Evidence Retention Days"; Integer) { Caption = 'Delivery Evidence Retention Days'; DataClassification = SystemMetadata; InitValue = 365; MinValue = 30; }
        field(7; "Last Processing At UTC"; DateTime) { Caption = 'Last Processing At UTC'; DataClassification = SystemMetadata; Editable = false; }
        field(8; "Updated At UTC"; DateTime) { Caption = 'Updated At UTC'; DataClassification = SystemMetadata; Editable = false; }
        field(9; "Updated By"; Guid) { Caption = 'Updated By'; DataClassification = EndUserPseudonymousIdentifiers; Editable = false; }
    }

    keys { key(PK; "Primary Key") { Clustered = true; } }

    trigger OnInsert()
    var
        CoreSetup: Record "DH Setup";
        NotificationMgt: Codeunit "DH Notification Mgt.";
    begin
        "Primary Key" := '';
        if CoreSetup.Get() then
            "Tenant ID" := CoreSetup."Tenant ID";
        "Company ID" := CopyStr(CompanyName(), 1, MaxStrLen("Company ID"));
        if "Preferred Language" = '' then
            "Preferred Language" := 'en';
        if "Delivery Evidence Retention Days" = 0 then
            "Delivery Evidence Retention Days" := 365;
        "Updated At UTC" := CurrentDateTime();
        "Updated By" := UserSecurityId();
        TestField("Tenant ID");
        NotificationMgt.WriteConfigAudit('setup', 'tenant', 'created', '', Format(Enabled));
    end;

    trigger OnModify()
    var
        NotificationMgt: Codeunit "DH Notification Mgt.";
    begin
        "Updated At UTC" := CurrentDateTime();
        "Updated By" := UserSecurityId();
        NotificationMgt.WriteConfigAudit('setup', 'tenant', 'updated', Format(xRec.Enabled), Format(Enabled));
    end;
}
