table 53129 "DH Deep Scan Finding"
{
    Caption = 'DH Deep Scan Finding';
    DataClassification = CustomerContent;

    fields
    {
        field(1; "Entry No."; Integer)
        {
            Caption = 'Entry No.';
        }
        field(2; "Deep Scan Entry No."; Integer)
        {
            Caption = 'Deep Scan Entry No.';
        }
        field(3; Category; Code[30])
        {
            Caption = 'Category';
        }
        field(4; "Issue Code"; Code[50])
        {
            Caption = 'Issue Code';
        }
        field(5; Title; Text[150])
        {
            Caption = 'Title';
        }
        field(6; Severity; Code[20])
        {
            Caption = 'Severity';
        }
        field(7; "Affected Count"; Integer)
        {
            Caption = 'Affected Count';
        }
        field(8; "Recommendation Preview"; Text[250])
        {
            Caption = 'Recommendation Preview';
        }
        field(9; "Premium Only"; Boolean)
        {
            Caption = 'Product Access';
        }
        field(10; "Severity Sort Order"; Integer)
        {
            Caption = 'Severity Sort Order';
        }
        field(11; "Affected Count Sort Value"; Integer)
        {
            Caption = 'Affected Count Sort Value';
        }
        field(12; "Estimated Impact (EUR)"; Decimal)
        {
            Caption = 'Estimated Impact';
            DecimalPlaces = 0 : 2;
        }
        field(13; "Group Key"; Text[64])
        {
            Caption = 'Group Key';
            DataClassification = SystemMetadata;
        }
    }

    keys
    {
        key(PK; "Entry No.")
        {
            Clustered = true;
        }
        key(GroupIdentity; "Deep Scan Entry No.", "Issue Code", "Group Key")
        {
        }
        key(Key2; "Deep Scan Entry No.")
        {
        }
        key(Key3; "Deep Scan Entry No.", Category)
        {
        }
        key(Key4; "Deep Scan Entry No.", "Affected Count")
        {
        }
        key(Key5; "Deep Scan Entry No.", "Severity Sort Order", "Affected Count Sort Value")
        {
        }
    }

    procedure ApplyBackendImpact(RunEntryNo: Integer; IssueCode: Code[50]; FindingId: Guid; SeverityValue: Code[20]; Impact: Decimal)
    begin
        Reset();
        if not GetBySystemId(FindingId) then
            Error(FindingIdentityErr);
        if ("Deep Scan Entry No." <> RunEntryNo) or ("Issue Code" <> IssueCode) then
            Error(FindingIdentityErr);
        if SeverityValue <> '' then begin
            Severity := SeverityValue;
            case LowerCase(SeverityValue) of
                'critical': "Severity Sort Order" := 0;
                'high': "Severity Sort Order" := 1;
                'medium': "Severity Sort Order" := 2;
                'low': "Severity Sort Order" := 3;
                else "Severity Sort Order" := 99;
            end;
        end;
        "Estimated Impact (EUR)" := Impact;
        Modify(true);
    end;

    procedure BuildGroupKey(RunSystemId: Guid; IssueCode: Code[50]; ValueMarker: Text): Text[64]
    var
        Cryptography: Codeunit "Cryptography Management";
        HashAlgorithm: Option MD5,SHA1,SHA256,SHA384,SHA512;
        Parts: JsonArray;
        Canonical: Text;
    begin
        Parts.Add(Format(RunSystemId));
        Parts.Add(Format(IssueCode));
        Parts.Add(UpperCase(ValueMarker));
        Parts.WriteTo(Canonical);
        exit(CopyStr(Cryptography.GenerateHash(Canonical, HashAlgorithm::SHA256), 1, 64));
    end;

    var
        FindingIdentityErr: Label 'The backend finding identity does not belong to this run and check.';
}
