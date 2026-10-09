table 53171 "DH Notification Rule"
{
    Caption = 'BCSentinel Notification Rule';
    DataClassification = CustomerContent;

    fields
    {
        field(1; "Rule ID"; Guid) { Caption = 'Rule ID'; DataClassification = SystemMetadata; }
        field(2; "Tenant ID"; Text[100]) { Caption = 'Tenant ID'; DataClassification = SystemMetadata; Editable = false; }
        field(3; "Company ID"; Text[100]) { Caption = 'Company ID'; DataClassification = SystemMetadata; Editable = false; }
        field(4; "Event Type"; Code[50]) { Caption = 'Event Type'; DataClassification = SystemMetadata; }
        field(5; Enabled; Boolean) { Caption = 'Enabled'; DataClassification = CustomerContent; InitValue = true; }
        field(6; Channel; Code[20]) { Caption = 'Channel'; DataClassification = SystemMetadata; InitValue = 'email'; }
        field(7; "Template Key"; Code[50]) { Caption = 'Template Key'; DataClassification = SystemMetadata; }
        field(8; "Minimum Severity"; Code[20]) { Caption = 'Minimum Severity'; DataClassification = CustomerContent; }
        field(9; "Module Scope"; Code[50]) { Caption = 'Module Scope'; DataClassification = CustomerContent; }
        field(10; "Business Area"; Code[50]) { Caption = 'Business Area'; DataClassification = CustomerContent; }
        field(11; "Quiet Hours Policy"; Code[50]) { Caption = 'Quiet Hours Policy'; DataClassification = CustomerContent; }
        field(12; "Digest Policy"; Code[50]) { Caption = 'Digest Policy'; DataClassification = CustomerContent; }
        field(13; "Updated At UTC"; DateTime) { Caption = 'Updated At UTC'; DataClassification = SystemMetadata; Editable = false; }
        field(14; "Updated By"; Guid) { Caption = 'Updated By'; DataClassification = EndUserPseudonymousIdentifiers; Editable = false; }
    }

    keys
    {
        key(PK; "Rule ID") { Clustered = true; }
        key(EventScope; "Tenant ID", "Company ID", "Event Type", Enabled) { }
    }

    trigger OnInsert()
    var
        Setup: Record "DH Setup";
        AuditMgt: Codeunit "DH Notification Mgt.";
    begin
        if IsNullGuid("Rule ID") then
            "Rule ID" := CreateGuid();
        if Setup.Get() then
            "Tenant ID" := Setup."Tenant ID";
        "Company ID" := CopyStr(CompanyName(), 1, MaxStrLen("Company ID"));
        Channel := 'email';
        "Updated At UTC" := CurrentDateTime();
        "Updated By" := UserSecurityId();
        TestField("Tenant ID");
        TestField("Company ID");
        TestField("Event Type");
        TestField("Template Key");
        AuditMgt.WriteConfigAudit('rule', Format("Rule ID"), 'created', '', "Event Type");
    end;

    trigger OnModify()
    var
        AuditMgt: Codeunit "DH Notification Mgt.";
    begin
        "Updated At UTC" := CurrentDateTime();
        "Updated By" := UserSecurityId();
        AuditMgt.WriteConfigAudit('rule', Format("Rule ID"), 'updated', '', "Event Type");
    end;

    trigger OnDelete()
    var
        AuditMgt: Codeunit "DH Notification Mgt.";
    begin
        AuditMgt.WriteConfigAudit('rule', Format("Rule ID"), 'deleted', "Event Type", '');
    end;
}
