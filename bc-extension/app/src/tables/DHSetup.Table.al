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
        field(36; "Contact Email"; Text[100])
        {
            Caption = 'Contact Email';
            DataClassification = CustomerContent;

            trigger OnValidate()
            begin
                "Contact Email" := CopyStr(LowerCase(DelChr("Contact Email", '<>', ' ')), 1, MaxStrLen("Contact Email"));
            end;
        }
        field(37; "Can Run Data Health Score"; Boolean)
        {
            Caption = 'Can Run Data Health Score';
            DataClassification = SystemMetadata;
            InitValue = true;
        }
        field(38; "Data Health Score Completed"; Boolean)
        {
            Caption = 'Data Health Score Completed';
            DataClassification = SystemMetadata;
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
            Caption = 'System';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(17; "Scan Finance Module"; Boolean)
        {
            Caption = 'Finance';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(18; "Scan Sales Module"; Boolean)
        {
            Caption = 'Sales';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(19; "Scan Purchasing Module"; Boolean)
        {
            Caption = 'Purchasing';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(20; "Scan Inventory Module"; Boolean)
        {
            Caption = 'Inventory';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(21; "Scan CRM Module"; Boolean)
        {
            Caption = 'CRM';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(22; "Scan Manufacturing Module"; Boolean)
        {
            Caption = 'Manufacturing';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(23; "Scan Service Module"; Boolean)
        {
            Caption = 'Service';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(24; "Scan Jobs Module"; Boolean)
        {
            Caption = 'Jobs';
            DataClassification = SystemMetadata;
            InitValue = true;
        }

        field(25; "Scan HR Module"; Boolean)
        {
            Caption = 'HR';
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
        field(39; "Scheduled Scans Enabled"; Boolean)
        {
            Caption = 'Scheduled Scans Enabled';
            DataClassification = SystemMetadata;
        }
        field(40; "Schedule Frequency"; Enum "DH Scan Schedule Frequency")
        {
            Caption = 'Schedule Frequency';
            DataClassification = SystemMetadata;
        }
        field(41; "Schedule Time"; Time)
        {
            Caption = 'Schedule Time';
            DataClassification = SystemMetadata;
        }
        field(42; "Schedule Monday"; Boolean)
        {
            Caption = 'Monday';
            DataClassification = SystemMetadata;
        }
        field(43; "Schedule Tuesday"; Boolean)
        {
            Caption = 'Tuesday';
            DataClassification = SystemMetadata;
        }
        field(44; "Schedule Wednesday"; Boolean)
        {
            Caption = 'Wednesday';
            DataClassification = SystemMetadata;
        }
        field(45; "Schedule Thursday"; Boolean)
        {
            Caption = 'Thursday';
            DataClassification = SystemMetadata;
        }
        field(46; "Schedule Friday"; Boolean)
        {
            Caption = 'Friday';
            DataClassification = SystemMetadata;
        }
        field(47; "Schedule Saturday"; Boolean)
        {
            Caption = 'Saturday';
            DataClassification = SystemMetadata;
        }
        field(48; "Schedule Sunday"; Boolean)
        {
            Caption = 'Sunday';
            DataClassification = SystemMetadata;
        }
        field(49; "Monthly Schedule Day"; Integer)
        {
            Caption = 'Monthly Day';
            DataClassification = SystemMetadata;
            MinValue = 1;
            MaxValue = 31;
        }
        field(50; "Next Scheduled Scan"; DateTime)
        {
            Caption = 'Next Scheduled Scan';
            DataClassification = SystemMetadata;
        }
        field(51; "Last Scheduled Scan"; DateTime)
        {
            Caption = 'Last Scheduled Scan';
            DataClassification = SystemMetadata;
        }
        field(52; "Last Scheduled Scan Result"; Enum "DH Scheduled Scan Result")
        {
            Caption = 'Last Scheduled Scan Result';
            DataClassification = SystemMetadata;
        }
        field(53; "Last Scheduled Scan Duration"; Duration)
        {
            Caption = 'Last Scheduled Scan Duration';
            DataClassification = SystemMetadata;
        }
        field(54; "Scheduled Scan Failure Count"; Integer)
        {
            Caption = 'Scheduled Scan Failure Count';
            DataClassification = SystemMetadata;
        }
        field(55; "Last Scheduled Scan Error"; Text[250])
        {
            Caption = 'Last Scheduled Scan Error';
            DataClassification = SystemMetadata;
        }
        field(56; "Scheduled Scan Task ID"; Guid)
        {
            Caption = 'Scheduled Scan Task ID';
            DataClassification = SystemMetadata;
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
        EnsureModuleDefaults();
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

        EnsureSchedulerDefaults();
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
        ApiUrlPolicy: Codeunit "DH API URL Policy";
    begin
        if DelChr(Value, '<>', ' ') = '' then
            exit(GetDefaultApiBaseUrl());
        exit(ApiUrlPolicy.NormalizeAndValidateBaseUrl(Value));
    end;

    local procedure RemoveTrailingSlash(Value: Text): Text
    begin
        while (StrLen(Value) > 0) and (CopyStr(Value, StrLen(Value), 1) = '/') do
            Value := CopyStr(Value, 1, StrLen(Value) - 1);

        exit(Value);
    end;

    procedure IsPremiumLicenseActive(): Boolean
    begin
        exit(("Current Plan" = "Current Plan"::Premium) and (("License Status" = "License Status"::Active) or ("License Status" = "License Status"::Trial)));
    end;

    procedure GetFeatureAccessText(): Text[100]
    begin
        if "Monitoring Active" then
            exit(LocalizeText('Monitoring active', 'Monitoring aktiv'));

        if "Scan Credits Available" > 0 then
            exit(StrSubstNo(LocalizeText('%1 scan credit(s) available', '%1 Scan-Guthaben verfügbar'), "Scan Credits Available"));

        if "Premium Enabled" then
            exit(LocalizeText('Paid scan access active', 'Bezahlter Scan-Zugang aktiv'));

        exit(LocalizeText('Register the tenant and unlock Full Analysis or Monitoring.', 'Registrieren Sie den Tenant und schalten Sie Full Analysis oder Monitoring frei.'));
    end;

    procedure GetProductAccessDisplay(): Text[100]
    var
        AccessModel: Text;
    begin
        if "Monitoring Active" then begin
            AccessModel := LowerCase("Product Access Model");
            if AccessModel.Contains('annual') then
                exit(LocalizeText('Monitoring Annual', 'Monitoring Jahresabo'));
            exit(LocalizeText('Monitoring Monthly', 'Monitoring Monatsabo'));
        end;

        if "Can View Issue Details" or "Premium Enabled" then begin
            if "Scan Credits Available" > 0 then
                exit(LocalizeText('Validation Check', 'Validation Check'));
            exit(LocalizeText('Full Analysis', 'Full Analysis'));
        end;

        exit(LocalizeText('Free Data Health Score', 'Kostenloser Data Health Score'));
    end;

    procedure GetDeepScanAccessDisplay(): Text[100]
    begin
        if "Monitoring Active" then
            exit(LocalizeText('Unlimited', 'Unbegrenzt'));

        if "Can Run Deep Scan" then begin
            if "Scan Credits Available" > 0 then
                exit(StrSubstNo(LocalizeText('%1 scan credit(s) available', '%1 Scan-Guthaben verfügbar'), "Scan Credits Available"));
            exit(LocalizeText('Available', 'Verf?gbar'));
        end;

        exit(LocalizeText('Not available', 'Nicht verfügbar'));
    end;

    procedure GetScheduledScanAccessDisplay(): Text[100]
    begin
        if "Monitoring Active" then
            exit(LocalizeText('Available', 'Verf?gbar'));

        exit(LocalizeText('Scheduled scans require active Monitoring.', 'Geplante Scans erfordern aktives Monitoring.'));
    end;

    procedure GetSubscriptionStatusDisplay(): Text[100]
    begin
        if "Monitoring Active" then
            exit(LocalizeText('Monitoring active', 'Monitoring aktiv'));

        if "Can View Issue Details" or "Premium Enabled" then
            exit(LocalizeText('Paid scan access active', 'Bezahlter Scan-Zugang aktiv'));

        if Registered then
            exit(LocalizeText('Free access active', 'Kostenloser Zugang aktiv'));

        exit(LocalizeText('Not registered', 'Nicht registriert'));
    end;

    procedure GetUpgradeHintText(): Text[250]
    begin
        if "Monitoring Active" then
            exit(LocalizeText('Monitoring is active. Scans and dashboard details are available.', 'Monitoring ist aktiv. Scans und Dashboard-Details sind verfügbar.'));

        if "Scan Credits Available" > 0 then
            exit(LocalizeText('A scan credit is available. Run Deep Scan to consume it and open the 7-day report window.', 'Ein Scan-Guthaben ist verfügbar. Starten Sie einen Deep Scan, um es zu verwenden und das 7-Tage-Reportfenster zu öffnen.'));

        if "Premium Enabled" then
            exit(LocalizeText('Paid recommendations and scan actions are available for this tenant.', 'Bezahlte Empfehlungen und Scan-Aktionen sind für diesen Tenant verfügbar.'));

        exit(LocalizeText('Buy Full Analysis, Validation Check, or Monitoring to unlock recommendations, drilldowns, and scan actions.', 'Kaufen Sie Full Analysis, Validation Check oder Monitoring, um Empfehlungen, Drilldowns und Scan-Aktionen freizuschalten.'));
    end;

    procedure HasValidContactEmail(): Boolean
    var
        AtPos: Integer;
        DomainPart: Text;
    begin
        if "Contact Email" = '' then
            exit(false);

        if StrPos("Contact Email", ' ') > 0 then
            exit(false);

        AtPos := StrPos("Contact Email", '@');
        if AtPos <= 1 then
            exit(false);

        DomainPart := CopyStr("Contact Email", AtPos + 1);
        if StrPos(DomainPart, '.') <= 1 then
            exit(false);

        if CopyStr(DomainPart, StrLen(DomainPart), 1) = '.' then
            exit(false);

        exit(true);
    end;

    procedure EnsureValidContactEmail()
    begin
        if not HasValidContactEmail() then
            Error(LocalizeText('Please enter a valid contact email before registering.', 'Bitte geben Sie vor der Registrierung eine gültige Kontakt-E-Mail-Adresse ein.'));
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

    procedure SetAllScanModules(Enabled: Boolean)
    begin
        "Scan System Module" := Enabled;
        "Scan Finance Module" := Enabled;
        "Scan Sales Module" := Enabled;
        "Scan Purchasing Module" := Enabled;
        "Scan Inventory Module" := Enabled;
        "Scan CRM Module" := Enabled;
        "Scan Manufacturing Module" := Enabled;
        "Scan Service Module" := Enabled;
        "Scan Jobs Module" := Enabled;
        "Scan HR Module" := Enabled;
    end;

    procedure RestoreDefaultScanModules()
    begin
        SetAllScanModules(true);
    end;

    procedure EnsureSchedulerDefaults()
    begin
        if "Schedule Time" = 0T then
            "Schedule Time" := 020000T;

        if "Monthly Schedule Day" = 0 then
            "Monthly Schedule Day" := 1;

        if not ("Schedule Monday" or "Schedule Tuesday" or "Schedule Wednesday" or "Schedule Thursday" or "Schedule Friday" or "Schedule Saturday" or "Schedule Sunday") then begin
            "Schedule Monday" := true;
            "Schedule Tuesday" := true;
            "Schedule Wednesday" := true;
            "Schedule Thursday" := true;
            "Schedule Friday" := true;
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

    local procedure LocalizeText(EnglishText: Text; GermanText: Text): Text
    begin
        if IsGermanLanguage() then
            exit(GermanText);

        exit(EnglishText);
    end;

    local procedure IsGermanLanguage(): Boolean
    begin
        case GlobalLanguage() of
            1031, 2055, 3079, 4103, 5127:
                exit(true);
        end;

        exit(false);
    end;

}
