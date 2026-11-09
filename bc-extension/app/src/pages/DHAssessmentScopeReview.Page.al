page 53340 "DH Assessment Scope Review"
{
    PageType = StandardDialog;
    ApplicationArea = All;
    Caption = 'Review Full Assessment Scope';

    layout
    {
        area(Content)
        {
            group(Instructions)
            {
                Caption = 'Assessment baseline';
                field(ScanIdDisplay; ScanIdDisplay)
                {
                    ApplicationArea = All;
                    Caption = 'Original Free Scan';
                    Editable = false;
                }
                field(ScoreDisplay; ScoreDisplay)
                {
                    ApplicationArea = All;
                    Caption = 'Preliminary Score';
                    Editable = false;
                }
                field(ConsentText; ConsentText)
                {
                    ApplicationArea = All;
                    Caption = 'Confirmation';
                    Editable = false;
                    MultiLine = true;
                }
            }
            group(Modules)
            {
                Caption = 'Included Business Central areas';
                field(IncludeSystem; IncludeSystem)
                {
                    Caption = 'System (required)';
                    ApplicationArea = All;
                    Editable = false;
                }
                field(IncludeFinance; IncludeFinance) { Caption = 'Finance'; ApplicationArea = All; }
                field(IncludeSales; IncludeSales) { Caption = 'Sales'; ApplicationArea = All; }
                field(IncludePurchasing; IncludePurchasing) { Caption = 'Purchasing'; ApplicationArea = All; }
                field(IncludeInventory; IncludeInventory) { Caption = 'Inventory'; ApplicationArea = All; }
                field(IncludeCrm; IncludeCrm) { Caption = 'CRM'; ApplicationArea = All; }
                field(IncludeManufacturing; IncludeManufacturing) { Caption = 'Manufacturing'; ApplicationArea = All; }
                field(IncludeService; IncludeService) { Caption = 'Service'; ApplicationArea = All; }
                field(IncludeJobs; IncludeJobs) { Caption = 'Jobs'; ApplicationArea = All; }
                field(IncludeHr; IncludeHr) { Caption = 'HR'; ApplicationArea = All; }
            }
        }
    }

    procedure LoadScope(ScanId: Code[50]; ScopeJson: JsonObject)
    var
        ModulesToken: JsonToken;
        ModuleToken: JsonToken;
        ModuleJson: JsonObject;
        ValueToken: JsonToken;
        ModulesArray: JsonArray;
        ModuleCode: Text;
        Included: Boolean;
        LoadedCount: Integer;
    begin
        ScanIdDisplay := Format(ScanId);
        IncludeSystem := true;
        ConsentText := 'Review the detected areas. Confirming creates an immutable Full Assessment baseline for this scan. Third-party and custom modules are not included.';
        if ScopeJson.Get('score', ValueToken) then
            ScoreDisplay := Format(ValueToken.AsValue().AsInteger()) + ' / 100';
        if not ScopeJson.Get('modules', ModulesToken) then
            Error('BCSentinel cannot show the assessment modules. Full Access may be inactive.');
        ModulesArray := ModulesToken.AsArray();
        if ModulesArray.Count() < 1 then
            Error('BCSentinel did not provide any supported assessment modules.');
        foreach ModuleToken in ModulesArray do begin
            ModuleJson := ModuleToken.AsObject();
            if ModuleJson.Get('module_code', ValueToken) then begin
                ModuleCode := ValueToken.AsValue().AsText();
                if not ModuleJson.Get('included_in_score', ValueToken) then
                    Error('Missing module inclusion decision for %1.', ModuleCode);
                Included := ValueToken.AsValue().AsBoolean();
                case ModuleCode of
                    'system': begin
                        if not Included then
                            Error('System is required for a Full baseline.');
                        IncludeSystem := true;
                    end;
                    'finance': IncludeFinance := Included;
                    'sales': IncludeSales := Included;
                    'purchasing': IncludePurchasing := Included;
                    'inventory': IncludeInventory := Included;
                    'crm': IncludeCrm := Included;
                    'manufacturing': IncludeManufacturing := Included;
                    'service': IncludeService := Included;
                    'jobs': IncludeJobs := Included;
                    'hr': IncludeHr := Included;
                    else
                        Error('Unexpected unsupported scope module: %1.', ModuleCode);
                end;
                LoadedCount += 1;
            end;
        end;
        if LoadedCount <> 10 then
            Error('The assessment scope is incomplete (%1 of 10 expected modules).', LoadedCount);
    end;

    procedure GetConfirmationPayload(): JsonObject
    var
        Root: JsonObject;
        Decisions: JsonObject;
    begin
        Decisions.Add('system', 'include');
        AddDecision(Decisions, 'finance', IncludeFinance);
        AddDecision(Decisions, 'sales', IncludeSales);
        AddDecision(Decisions, 'purchasing', IncludePurchasing);
        AddDecision(Decisions, 'inventory', IncludeInventory);
        AddDecision(Decisions, 'crm', IncludeCrm);
        AddDecision(Decisions, 'manufacturing', IncludeManufacturing);
        AddDecision(Decisions, 'service', IncludeService);
        AddDecision(Decisions, 'jobs', IncludeJobs);
        AddDecision(Decisions, 'hr', IncludeHr);
        Root.Add('decisions', Decisions);
        exit(Root);
    end;

    local procedure AddDecision(var Decisions: JsonObject; ModuleCode: Text; Included: Boolean)
    begin
        if Included then
            Decisions.Add(ModuleCode, 'include')
        else
            Decisions.Add(ModuleCode, 'exclude');
    end;

    var
        ScanIdDisplay: Text[50];
        ScoreDisplay: Text[40];
        ConsentText: Text[250];
        IncludeSystem: Boolean;
        IncludeFinance: Boolean;
        IncludeSales: Boolean;
        IncludePurchasing: Boolean;
        IncludeInventory: Boolean;
        IncludeCrm: Boolean;
        IncludeManufacturing: Boolean;
        IncludeService: Boolean;
        IncludeJobs: Boolean;
        IncludeHr: Boolean;
}
