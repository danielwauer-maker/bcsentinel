table 53194 "DH Remediation Action"
{
    Caption = 'BCSentinel Remediation Action';
    DataClassification = CustomerContent;

    fields
    {
        field(1; "Action ID"; Guid) { Caption = 'Action ID'; DataClassification = SystemMetadata; }
        field(2; "Tenant ID"; Text[100]) { Caption = 'Tenant ID'; DataClassification = SystemMetadata; Editable = false; }
        field(3; "Company ID"; Text[100]) { Caption = 'Company ID'; DataClassification = SystemMetadata; Editable = false; }
        field(4; "Finding Key"; Code[100]) { Caption = 'Finding Key'; DataClassification = CustomerContent; }
        field(5; Title; Text[150]) { Caption = 'Title'; DataClassification = CustomerContent; }
        field(6; Description; Text[2048]) { Caption = 'Description'; DataClassification = CustomerContent; }
        field(7; "Recommendation Ref"; Text[100]) { Caption = 'Recommendation Ref.'; DataClassification = CustomerContent; }
        field(8; Status; Enum "DH Remediation Status")
        {
            Caption = 'Status';
            DataClassification = CustomerContent;
            InitValue = Open;
            trigger OnValidate()
            var
                RemediationMgt: Codeunit "DH Remediation Mgt.";
            begin
                if IsNullGuid("Action ID") then
                    exit;
                RemediationMgt.ValidateStatusTransition(xRec.Status, Status);
                case Status of
                    Status::InProgress:
                        if "Started At UTC" = 0DT then
                            "Started At UTC" := CurrentDateTime();
                    Status::Completed:
                        "Completed At UTC" := CurrentDateTime();
                    Status::Cancelled:
                        "Cancelled At UTC" := CurrentDateTime();
                end;
                RemediationMgt.WriteAudit(Rec, 'status', Format(xRec.Status), Format(Status));
            end;
        }
        field(9; Priority; Enum "DH Remediation Priority")
        {
            Caption = 'Priority';
            DataClassification = CustomerContent;
            InitValue = Medium;
            trigger OnValidate()
            var
                RemediationMgt: Codeunit "DH Remediation Mgt.";
            begin
                if not IsNullGuid("Action ID") then
                    RemediationMgt.WriteAudit(Rec, 'priority', Format(xRec.Priority), Format(Priority));
            end;
        }
        field(10; "Owner Principal ID"; Guid)
        {
            Caption = 'Owner Principal ID';
            DataClassification = EndUserPseudonymousIdentifiers;
            trigger OnValidate()
            var
                RemediationMgt: Codeunit "DH Remediation Mgt.";
            begin
                if not IsNullGuid("Action ID") then
                    RemediationMgt.WriteAudit(Rec, 'owner_principal_id', Format(xRec."Owner Principal ID"), Format("Owner Principal ID"));
            end;
        }
        field(11; "Owner Display Name"; Text[100]) { Caption = 'Owner Display Name'; DataClassification = EndUserIdentifiableInformation; }
        field(12; "Due At UTC"; DateTime) { Caption = 'Due At UTC'; DataClassification = CustomerContent; }
        field(13; "Started At UTC"; DateTime) { Caption = 'Started At UTC'; DataClassification = SystemMetadata; Editable = false; }
        field(14; "Completed At UTC"; DateTime) { Caption = 'Completed At UTC'; DataClassification = SystemMetadata; Editable = false; }
        field(15; "Cancelled At UTC"; DateTime) { Caption = 'Cancelled At UTC'; DataClassification = SystemMetadata; Editable = false; }
        field(16; "Blocked Reason"; Text[250]) { Caption = 'Blocked Reason'; DataClassification = CustomerContent; }
        field(17; "Completion Note"; Text[250]) { Caption = 'Completion Note'; DataClassification = CustomerContent; }
        field(18; "Validation Result Ref"; Text[100]) { Caption = 'Validation Result Ref.'; DataClassification = CustomerContent; }
        field(19; Source; Enum "DH Remediation Source") { Caption = 'Source'; DataClassification = CustomerContent; InitValue = Manual; }
        field(20; "Created At UTC"; DateTime) { Caption = 'Created At UTC'; DataClassification = SystemMetadata; Editable = false; }
        field(21; "Updated At UTC"; DateTime) { Caption = 'Updated At UTC'; DataClassification = SystemMetadata; Editable = false; }
    }

    keys
    {
        key(PK; "Action ID") { Clustered = true; }
        key(Finding; "Finding Key", Status, Priority) { }
        key(Owner; "Owner Principal ID", Status, "Due At UTC") { }
    }

    trigger OnInsert()
    var
        Setup: Record "DH Setup";
        RemediationMgt: Codeunit "DH Remediation Mgt.";
    begin
        if IsNullGuid("Action ID") then
            "Action ID" := CreateGuid();
        if Setup.Get() then
            "Tenant ID" := Setup."Tenant ID";
        "Company ID" := CopyStr(CompanyName(), 1, MaxStrLen("Company ID"));
        "Created At UTC" := CurrentDateTime();
        "Updated At UTC" := "Created At UTC";
        TestField("Tenant ID");
        TestField("Company ID");
        TestField("Finding Key");
        TestField(Title);
        RemediationMgt.WriteAudit(Rec, 'created', '', Format(Status));
    end;

    trigger OnModify()
    begin
        "Updated At UTC" := CurrentDateTime();
    end;

    trigger OnDelete()
    begin
        Error('Remediation actions are retained for auditability. Cancel the action instead of deleting it.');
    end;

    trigger OnRename()
    begin
        Error('The Action ID is immutable.');
    end;
}
