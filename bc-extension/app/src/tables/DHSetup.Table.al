table 53100 "DH Setup"
{
    Caption = 'DH Setup';
    DataClassification = SystemMetadata;

    fields
    {
        field(1; "Primary Key"; Code[10])
        {
            Caption = 'Primary Key';
            DataClassification = SystemMetadata;
        }

        field(2; "Tenant ID"; Text[100])
        {
            Caption = 'Tenant ID';
            DataClassification = SystemMetadata;
        }

        field(3; "API Base URL"; Text[250])
        {
            Caption = 'API Base URL';
            DataClassification = SystemMetadata;

            trigger OnValidate()
            begin
                "API Base URL" := NormalizeApiBaseUrl("API Base URL");
            end;
        }

        field(4; "API Token"; Text[250])
        {
            Caption = 'Legacy API Token';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'API tokens are stored in company-scoped isolated storage.';
            ObsoleteTag = '1.0.3.0';
        }

        field(5; "Last Score"; Integer)
        {
            Caption = 'Last Score';
            DataClassification = SystemMetadata;
        }

        field(6; "Last Scan Date"; DateTime)
        {
            Caption = 'Last Scan Date';
            DataClassification = SystemMetadata;
        }

        field(7; "Premium Enabled"; Boolean)
        {
            Caption = 'Product Access Active';
            DataClassification = SystemMetadata;
        }

        field(8; Registered; Boolean)
        {
            Caption = 'Registered';
            DataClassification = SystemMetadata;
        }

        field(9; "Registration Date"; DateTime)
        {
            Caption = 'Registration Date';
            DataClassification = SystemMetadata;
        }

        field(10; "Current Plan"; Enum "DH License Plan")
        {
            Caption = 'Compatibility Plan';
            DataClassification = SystemMetadata;
        }

        field(11; "License Status"; Enum "DH License Status")
        {
            Caption = 'Compatibility Status';
            DataClassification = SystemMetadata;
        }

        field(12; "Last License Check"; DateTime)
        {
            Caption = 'Last Product Access Check';
            DataClassification = SystemMetadata;
        }

        field(13; "Data Processing Consent"; Boolean)
        {
            Caption = 'Data Processing Consent';
            DataClassification = CustomerContent;
        }
        field(27; "Registration Invite Code"; Text[100])
        {
            Caption = 'Registration Invite Code';
            DataClassification = SystemMetadata;
        }

        field(14; "Last Run ID Date"; Date)
        {
            Caption = 'Last Run ID Date';
            DataClassification = SystemMetadata;
        }

        field(15; "Last Run ID Counter"; Integer)
        {
            Caption = 'Last Run ID Counter';
            DataClassification = SystemMetadata;
        }

        field(16; "Scan System Module"; Boolean)
        {
            Caption = 'Scan System';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(17; "Scan Finance Module"; Boolean)
        {
            Caption = 'Scan Finance';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(18; "Scan Sales Module"; Boolean)
        {
            Caption = 'Scan Sales';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(19; "Scan Purchasing Module"; Boolean)
        {
            Caption = 'Scan Purchasing';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(20; "Scan Inventory Module"; Boolean)
        {
            Caption = 'Scan Inventory';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(21; "Scan CRM Module"; Boolean)
        {
            Caption = 'Scan CRM';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(22; "Scan Manufacturing Module"; Boolean)
        {
            Caption = 'Scan Manufacturing';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(23; "Scan Service Module"; Boolean)
        {
            Caption = 'Scan Service';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(24; "Scan Jobs Module"; Boolean)
        {
            Caption = 'Scan Jobs';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(25; "Scan HR Module"; Boolean)
        {
            Caption = 'Scan HR';
            DataClassification = SystemMetadata;
            InitValue = true;
        }
        field(26; "Issue Drilldown Code"; Code[50])
        {
            Caption = 'Issue Drilldown Code';
            DataClassification = SystemMetadata;
        }
        field(28; "Scan Credits Available"; Integer)
        {
            Caption = 'Scan Credits Available';
            DataClassification = SystemMetadata;
        }
        field(29; "Monitoring Active"; Boolean)
        {
            Caption = 'Monitoring Active';
            DataClassification = SystemMetadata;
        }
        field(30; "Dashboard Access Until"; Text[50])
        {
            Caption = 'Dashboard Access Until';
            DataClassification = SystemMetadata;
        }
        field(31; "Issue Access Until"; Text[50])
        {
            Caption = 'Issue Access Until';
            DataClassification = SystemMetadata;
        }
        field(32; "Can Run Deep Scan"; Boolean)
        {
            Caption = 'Can Run Deep Scan';
            DataClassification = SystemMetadata;
        }
        field(33; "Can View Dashboard"; Boolean)
        {
            Caption = 'Can View Dashboard';
            DataClassification = SystemMetadata;
        }
        field(34; "Can View Issue Details"; Boolean)
        {
            Caption = 'Can View Issue Details';
            DataClassification = SystemMetadata;
        }
        field(35; "Product Access Model"; Text[30])
        {
            Caption = 'Product Access';
            DataClassification = SystemMetadata;
        }
        // Legacy schema preserved from verified 1.0.2.23–1.0.2.25 release packages.
        // These fields must remain for non-destructive upgrades from installed tenants.
        field(36; "Contact Email"; Text[100])
        {
            Caption = 'Contact Email';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(37; "Can Run Data Health Score"; Boolean)
        {
            Caption = 'Can Run Data Health Score';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(38; "Data Health Score Completed"; Boolean)
        {
            Caption = 'Data Health Score Completed';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(39; "Scheduled Scans Enabled"; Boolean)
        {
            Caption = 'Scheduled Scans Enabled';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(40; "Schedule Frequency"; Enum "DH Scan Schedule Frequency")
        {
            Caption = 'Schedule Frequency';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(41; "Schedule Time"; Time)
        {
            Caption = 'Schedule Time';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(42; "Schedule Monday"; Boolean)
        {
            Caption = 'Schedule Monday';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(43; "Schedule Tuesday"; Boolean)
        {
            Caption = 'Schedule Tuesday';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(44; "Schedule Wednesday"; Boolean)
        {
            Caption = 'Schedule Wednesday';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(45; "Schedule Thursday"; Boolean)
        {
            Caption = 'Schedule Thursday';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(46; "Schedule Friday"; Boolean)
        {
            Caption = 'Schedule Friday';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(47; "Schedule Saturday"; Boolean)
        {
            Caption = 'Schedule Saturday';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(48; "Schedule Sunday"; Boolean)
        {
            Caption = 'Schedule Sunday';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(49; "Monthly Schedule Day"; Integer)
        {
            Caption = 'Monthly Schedule Day';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(50; "Next Scheduled Scan"; DateTime)
        {
            Caption = 'Next Scheduled Scan';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(51; "Last Scheduled Scan"; DateTime)
        {
            Caption = 'Last Scheduled Scan';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(52; "Last Scheduled Scan Result"; Enum "DH Scheduled Scan Result")
        {
            Caption = 'Last Scheduled Scan Result';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(53; "Last Scheduled Scan Duration"; Duration)
        {
            Caption = 'Last Scheduled Scan Duration';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(54; "Scheduled Scan Failure Count"; Integer)
        {
            Caption = 'Scheduled Scan Failure Count';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(55; "Last Scheduled Scan Error"; Text[250])
        {
            Caption = 'Last Scheduled Scan Error';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(56; "Scheduled Scan Task ID"; Guid)
        {
            Caption = 'Scheduled Scan Task ID';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(57; "Assessment Credits Available"; Integer)
        {
            Caption = 'Assessment Credits Available';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(58; "Validation Credits Available"; Integer)
        {
            Caption = 'Validation Credits Available';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(59; "Access Snapshot Received At"; DateTime)
        {
            Caption = 'Access Snapshot Received At';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(60; "Access Server Time UTC"; DateTime)
        {
            Caption = 'Access Server Time UTC';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(61; "Access Snapshot Expires At"; DateTime)
        {
            Caption = 'Access Snapshot Expires At';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(62; "Access Snapshot Version"; Text[30])
        {
            Caption = 'Access Snapshot Version';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(63; "Access Snapshot Tenant ID"; Text[100])
        {
            Caption = 'Access Snapshot Tenant ID';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(64; "Access Snapshot Environment"; Text[100])
        {
            Caption = 'Access Snapshot Environment';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(65; "Access Snapshot Env. Type"; Text[20])
        {
            Caption = 'Access Snapshot Env. Type';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(66; "Access Snapshot Company ID"; Text[50])
        {
            Caption = 'Access Snapshot Company ID';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(67; "Access Snapshot API URL"; Text[250])
        {
            Caption = 'Access Snapshot API URL';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(68; "Can View Reports"; Boolean)
        {
            Caption = 'Can View Reports';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(69; "Can Use Monitoring"; Boolean)
        {
            Caption = 'Can Use Monitoring';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(70; "Subscription Active"; Boolean)
        {
            Caption = 'Subscription Active';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(71; "Report Access Until"; Text[50])
        {
            Caption = 'Report Access Until';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(72; "Access Correlation ID"; Text[50])
        {
            Caption = 'Access Correlation ID';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(73; "Free Assessment Used"; Boolean)
        {
            Caption = 'Free Assessment Used';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(74; "Premium Until"; Text[50])
        {
            Caption = 'Premium Until';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }
        field(75; "Monitoring Until"; Text[50])
        {
            Caption = 'Monitoring Until';
            DataClassification = SystemMetadata;
            ObsoleteState = Pending;
            ObsoleteReason = 'Retained exclusively for backwards-compatible upgrades from previous BCSentinel versions.';
            ObsoleteTag = '1.0.2.31';
        }

    }

    keys
    {
        key(PK; "Primary Key")
        {
            Clustered = true;
        }
    }

    trigger OnInsert()
    begin
        if "Primary Key" = '' then
            "Primary Key" := 'SETUP';

        ApplyDefaults();
    end;

    trigger OnModify()
    begin
        ApplyDefaults();
    end;

    procedure ApplyDefaults()
    begin
        if "API Base URL" = '' then
            "API Base URL" := GetDefaultApiBaseUrl()
        else
            "API Base URL" := NormalizeApiBaseUrl("API Base URL");

        EnsureModuleDefaults();
    end;

    procedure GetDefaultApiBaseUrl(): Text[250]
    begin
        exit('https://api.bcsentinel.com');
    end;

    procedure GetFixedApiBaseUrl(): Text[250]
    begin
        // Backward-compatible alias used by existing codeunits.
        exit(GetDefaultApiBaseUrl());
    end;

    procedure NormalizeApiBaseUrl(Value: Text): Text[250]
    var
        NormalizedValue: Text;
    begin
        NormalizedValue := DelChr(Value, '<>', ' ');

        if NormalizedValue = '' then
            exit(GetDefaultApiBaseUrl());

        NormalizedValue := RemoveTrailingSlash(NormalizedValue);

        if StrPos(LowerCase(NormalizedValue), 'http://') <> 1 then
            if StrPos(LowerCase(NormalizedValue), 'https://') <> 1 then
                Error('API Base URL must start with http:// or https://');

        if StrLen(NormalizedValue) > MaxStrLen("API Base URL") then
            Error('API Base URL is too long.');

        exit(CopyStr(NormalizedValue, 1, MaxStrLen("API Base URL")));
    end;

    local procedure RemoveTrailingSlash(Value: Text): Text
    begin
        while (StrLen(Value) > 0) and (CopyStr(Value, StrLen(Value), 1) = '/') do
            Value := CopyStr(Value, 1, StrLen(Value) - 1);

        exit(Value);
    end;

    procedure IsPremiumLicenseActive(): Boolean
    begin
        exit(Registered and ("Tenant ID" <> '') and ("Current Plan" = "Current Plan"::Premium) and (("License Status" = "License Status"::Active) or ("License Status" = "License Status"::Trial)));
    end;

    procedure ClearCachedProductAccess()
    begin
        // The backend is authoritative; cached entitlements cannot be reused after a local identity reset.
        "Current Plan" := "Current Plan"::Free;
        "License Status" := "License Status"::Expired;
        "Last License Check" := 0DT;
        "Premium Enabled" := false;
        "Scan Credits Available" := 0;
        "Monitoring Active" := false;
        "Dashboard Access Until" := '';
        "Issue Access Until" := '';
        "Can Run Deep Scan" := false;
        "Can View Dashboard" := false;
        "Can View Issue Details" := false;
        "Product Access Model" := 'none';
    end;

    procedure GetProductAccessDisplayText(): Text[30]
    begin
        // Backend 'none' means no paid entitlement, not that registered Free Entry is unavailable.
        // Keep the underlying access model unchanged for authorization and license checks.
        if not Registered or ("Tenant ID" = '') then
            exit('none');

        if ("Product Access Model" = '') or (LowerCase("Product Access Model") = 'none') then
            exit('Free');

        exit("Product Access Model");
    end;

    procedure GetFeatureAccessText(): Text[100]
    begin
        if not Registered or ("Tenant ID" = '') then
            exit('Register the tenant to activate product access.');

        if "Monitoring Active" then
            exit('Monitoring active');

        if "Scan Credits Available" > 0 then
            exit(StrSubstNo('%1 scan credit(s) available', "Scan Credits Available"));

        if "Premium Enabled" then
            exit('Paid scan access active');

        exit('No scan credit available. Check scan history or request access.');
    end;

    procedure GetUpgradeHintText(): Text[250]
    begin
        if "Monitoring Active" then
            exit('Monitoring is active. Deep scans and dashboard details are available.');

        if "Scan Credits Available" > 0 then
            exit('A scan credit is available. Run Deep Scan to consume it and open the 7-day report window.');

        if "Premium Enabled" then
            exit('Paid recommendations and scan actions are available for this tenant.');

        exit('Buy an Assessment, Validation Check, or Monitoring product to unlock recommendations, drilldowns, and scan actions.');
    end;

    procedure EnsureModuleDefaults()
    begin
        if not HasAnyModuleEnabled() then begin
            "Scan System Module" := true;
            "Scan Finance Module" := true;
            "Scan Sales Module" := true;
            "Scan Purchasing Module" := true;
            "Scan Inventory Module" := true;
            "Scan CRM Module" := true;
            "Scan Manufacturing Module" := true;
            "Scan Service Module" := true;
            "Scan Jobs Module" := true;
            "Scan HR Module" := true;
        end;
    end;

    procedure HasAnyModuleEnabled(): Boolean
    begin
        exit(
          "Scan System Module" or
          "Scan Finance Module" or
          "Scan Sales Module" or
          "Scan Purchasing Module" or
          "Scan Inventory Module" or
          "Scan CRM Module" or
          "Scan Manufacturing Module" or
          "Scan Service Module" or
          "Scan Jobs Module" or
          "Scan HR Module");
    end;

    procedure GetEnabledDeepScanModuleCount(): Integer
    var
        EnabledCount: Integer;
    begin
        if "Scan System Module" then
            EnabledCount += 1;
        if "Scan Finance Module" then
            EnabledCount += 1;
        if "Scan Sales Module" then
            EnabledCount += 1;
        if "Scan Purchasing Module" then
            EnabledCount += 1;
        if "Scan Inventory Module" then
            EnabledCount += 1;
        if "Scan CRM Module" then
            EnabledCount += 1;
        if "Scan Manufacturing Module" then
            EnabledCount += 1;
        if "Scan Service Module" then
            EnabledCount += 1;
        if "Scan Jobs Module" then
            EnabledCount += 1;
        if "Scan HR Module" then
            EnabledCount += 1;

        exit(EnabledCount);
    end;

}
