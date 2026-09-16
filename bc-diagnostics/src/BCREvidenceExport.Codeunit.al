codeunit 53450 "BCR Evidence Export"
{
    procedure DownloadEvidence()
    var
        TempBlob: Codeunit "Temp Blob";
        Evidence: JsonObject;
        OutputStream: OutStream;
        InputStream: InStream;
        FileName: Text;
    begin
        Evidence := BuildEvidence();
        TempBlob.CreateOutStream(OutputStream, TextEncoding::UTF8);
        Evidence.WriteTo(OutputStream);
        TempBlob.CreateInStream(InputStream, TextEncoding::UTF8);
        FileName := 'BCSentinel-DEV-Run1-evidence.json';
        DownloadFromStream(InputStream, '', '', '', FileName);
    end;

    procedure BuildEvidence(): JsonObject
    var
        ScanRun: Record "DH Deep Scan Run";
        Finding: Record "DH Deep Scan Finding";
        GenerationRun: Record "BCP Run";
        Customer: Record Customer;
        Vendor: Record Vendor;
        Item: Record Item;
        Evidence: JsonObject;
        Context: JsonObject;
        Snapshot: JsonObject;
        Exports: JsonObject;
        BCExport: JsonObject;
        Rows: JsonArray;
        Row: JsonObject;
        Scenarios: JsonObject;
        Occurrences: BigInteger;
        RowImpact: Decimal;
        RowsRead: Integer;
    begin
        RequireSandbox();
        ScanRun.SetRange("Run ID", TargetRunId());
        if not ScanRun.FindFirst() then
            Error(RunMissingErr);
        if ScanRun.Count() <> 1 then
            Error(RunMissingErr);
        if ScanRun.Status <> ScanRun.Status::Completed then
            Error(RunIncompleteErr);
        GenerationRun.Get(1);
        if (GenerationRun.Seed <> 5001) or (GenerationRun."Error Rate" <> 10) or
           (GenerationRun.Customers <> 6000) or (GenerationRun.Vendors <> 2000) or
           (GenerationRun.Items <> 12000) or (GenerationRun."Expected Scenarios" <> 2000)
        then
            Error(GeneratorMismatchErr);

        Context.Add('company', CompanyName());
        Context.Add('scan_id', ScanRun."Run ID");
        Context.Add('generator_run_id', 1);
        Context.Add('exported_at_utc', CurrentDateTime());
        Context.Add('bcsentinel_version', GetAppVersion('8c7f0f9c-0c1a-4a4e-9c6f-111111111111'));
        Context.Add('generator_version', GetAppVersion('1bf95437-93b6-4329-bc49-40585f1272a0'));
        Evidence.Add('schema_version', 1);
        Evidence.Add('evidence_kind', 'BC_PERSISTED_FINDINGS_AND_CURRENT_READ_ONLY_ATTRIBUTION');
        Evidence.Add('context', Context);

        Finding.SetRange("Deep Scan Entry No.", ScanRun."Entry No.");
        Finding.SetCurrentKey("Entry No.");
        if Finding.FindSet() then
            repeat
                Clear(Row);
                Row.Add('id', Format(Finding."Entry No.", 0, 9));
                Row.Add('scan_id', ScanRun."Run ID");
                Row.Add('code', Finding."Issue Code");
                Row.Add('check_name', Finding.Title);
                Row.Add('category', Finding.Category);
                Row.Add('module', ModuleFromCategory(Finding.Category));
                Row.Add('severity', LowerCase(Finding.Severity));
                Row.Add('affected_count', Finding."Affected Count");
                Row.Add('impact_eur', Finding."Estimated Impact (EUR)");
                Row.Add('aggregation_key_available', false);
                Row.Add('aggregation_note', 'Original duplicate value/group key is not persisted in this table.');
                AddScenarioFieldMetadata(Row, Finding."Issue Code");
                Rows.Add(Row);
                RowsRead += 1;
                Occurrences += Finding."Affected Count";
                RowImpact += Finding."Estimated Impact (EUR)";
            until Finding.Next() = 0;
        BCExport.Add('company', CompanyName());
        BCExport.Add('scan_id', ScanRun."Run ID");
        BCExport.Add('complete', true);
        BCExport.Add('exported_row_count', RowsRead);
        BCExport.Add('row_order', 'BC Entry No. ascending; same default order as sync payload');
        BCExport.Add('rows', Rows);
        Exports.Add('bc', BCExport);
        Evidence.Add('exports', Exports);

        Snapshot.Add('run_entry_no', ScanRun."Entry No.");
        Snapshot.Add('issues_count', ScanRun."Issues Count");
        Snapshot.Add('checks_count', ScanRun."Checks Count");
        Snapshot.Add('affected_records', ScanRun."Affected Records");
        Snapshot.Add('exported_occurrences', Occurrences);
        Snapshot.Add('exported_row_impact_eur', RowImpact);
        Snapshot.Add('score', ScanRun."Deep Score");
        Snapshot.Add('estimated_loss_eur', ScanRun."Estimated Loss (EUR)");
        Snapshot.Add('potential_saving_eur', ScanRun."Potential Saving (EUR)");
        Snapshot.Add('started_at', ScanRun."Started At");
        Snapshot.Add('finished_at', ScanRun."Finished At");
        Snapshot.Add('status', Format(ScanRun.Status, 0, 9));
        Snapshot.Add('synchronization', Format(ScanRun."Backend Sync Status", 0, 9));
        Snapshot.Add('module_scores', RunScores(ScanRun));
        Evidence.Add('run_snapshot', Snapshot);
        Evidence.Add('current_setup_not_scan_time_snapshot', CurrentModules());
        Evidence.Add('generator_namespace_hint', 'BCP000001; finding rows mix generated and non-generated matches.');

        AddScenario(Scenarios, 'CUSTOMERS_MISSING_EMAIL', Database::Customer, Customer.FieldNo("E-Mail"), false);
        AddScenario(Scenarios, 'VENDORS_MISSING_PHONE', Database::Vendor, Vendor.FieldNo("Phone No."), false);
        AddScenario(Scenarios, 'ITEMS_WITHOUT_UNIT_PRICE', Database::Item, Item.FieldNo("Unit Price"), true);
        AddScenario(Scenarios, 'ITEMS_WITHOUT_UNIT_COST', Database::Item, Item.FieldNo("Unit Cost"), true);
        Evidence.Add('scenario_observations', Scenarios);
        Evidence.Add('attribution_caveat', 'Current field/exception state, not an immutable scan-time record snapshot. No master contents or identifiers exported.');
        exit(Evidence);
    end;

    local procedure RequireSandbox()
    var
        EnvironmentInformation: Codeunit "Environment Information";
    begin
        if not EnvironmentInformation.IsSaaS() or not EnvironmentInformation.IsSandbox() or EnvironmentInformation.IsProduction() then
            Error(SandboxErr);
        if CompanyName() <> 'BCS-PERF-DEV' then
            Error(SandboxErr);
    end;

    local procedure TargetRunId(): Code[50]
    begin
        exit('RUN_20260916_000001_43F57A071BFF485BAF20C68FF578B');
    end;

    local procedure AddScenario(var Scenarios: JsonObject; CheckCode: Code[50]; TableId: Integer; FieldId: Integer; ZeroValue: Boolean)
    var
        Owned: Record "BCP Owned Record";
        AnyOwned: Record "BCP Owned Record";
        Target: RecordRef;
        ValueField: FieldRef;
        SystemField: FieldRef;
        Scenario: JsonObject;
        SystemId: Guid;
        ModifiedAt: DateTime;
        GeneratedCount: Integer;
        MatchCount: Integer;
        ExcludedCount: Integer;
        NonOwnedCount: Integer;
        MissingCount: Integer;
        ModifiedCount: Integer;
    begin
        Owned.SetRange("Run ID", 1);
        Owned.SetRange("Table ID", TableId);
        Owned.SetRange(Scenario, CheckCode);
        Owned.SetRange(Supporting, false);
        Target.Open(TableId);
        if Owned.FindSet() then
            repeat
                GeneratedCount += 1;
                if Target.GetBySystemId(Owned."Record SystemId") then begin
                    SystemField := Target.Field(Target.SystemModifiedAtNo());
                    ModifiedAt := SystemField.Value;
                    if ModifiedAt <> Owned."Modified At" then
                        ModifiedCount += 1;
                    if MatchesField(Target, FieldId, ZeroValue) then begin
                        MatchCount += 1;
                        if IsExcluded(TableId, Owned."Record SystemId", CheckCode) then
                            ExcludedCount += 1;
                    end;
                end else
                    MissingCount += 1;
            until Owned.Next() = 0;
        Target.Reset();
        ValueField := Target.Field(FieldId);
        if ZeroValue then
            ValueField.SetRange(0)
        else
            ValueField.SetRange('');
        if Target.FindSet() then
            repeat
                SystemField := Target.Field(Target.SystemIdNo());
                SystemId := SystemField.Value;
                if not AnyOwned.Get(1, TableId, SystemId) then
                    if not IsExcluded(TableId, SystemId, CheckCode) then
                        NonOwnedCount += 1;
            until Target.Next() = 0;
        Target.Close();
        Scenario.Add('generated_count', GeneratedCount);
        Scenario.Add('matching_owned_count', MatchCount);
        Scenario.Add('excluded_matching_owned_count', ExcludedCount);
        Scenario.Add('non_owned_nonexcluded_matches', NonOwnedCount);
        Scenario.Add('missing_owned_records', MissingCount);
        Scenario.Add('modified_since_generation', ModifiedCount);
        Scenarios.Add(CheckCode, Scenario);
    end;

    local procedure MatchesField(var Target: RecordRef; FieldId: Integer; ZeroValue: Boolean): Boolean
    var
        ValueField: FieldRef;
        Amount: Decimal;
        FieldText: Text;
    begin
        ValueField := Target.Field(FieldId);
        if ZeroValue then begin
            Amount := ValueField.Value;
            exit(Amount = 0);
        end;
        FieldText := ValueField.Value;
        exit(FieldText = '');
    end;

    local procedure IsExcluded(TableId: Integer; SystemId: Guid; CheckCode: Code[50]): Boolean
    var
        IssueException: Record "DH Issue Exception";
    begin
        IssueException.SetRange("Table ID", TableId);
        IssueException.SetRange("Record SystemId", SystemId);
        IssueException.SetRange("Issue Code", CheckCode);
        IssueException.SetRange(Active, true);
        exit(not IssueException.IsEmpty());
    end;

    local procedure AddScenarioFieldMetadata(var Row: JsonObject; CheckCode: Code[50])
    var
        TableId: Integer;
        FieldName: Text;
    begin
        case CheckCode of
            'CUSTOMERS_MISSING_EMAIL':
                begin
                    TableId := Database::Customer;
                    FieldName := 'E-Mail';
                end;
            'VENDORS_MISSING_PHONE':
                begin
                    TableId := Database::Vendor;
                    FieldName := 'Phone No.';
                end;
            'ITEMS_WITHOUT_UNIT_PRICE':
                begin
                    TableId := Database::Item;
                    FieldName := 'Unit Price';
                end;
            'ITEMS_WITHOUT_UNIT_COST':
                begin
                    TableId := Database::Item;
                    FieldName := 'Unit Cost';
                end;
        end;
        Row.Add('table_id_if_direct_scenario', TableId);
        Row.Add('field_if_direct_scenario', FieldName);
        Row.Add('field_metadata_note', 'Other checks: derive from pinned source catalog; not stored in finding.');
    end;

    local procedure ModuleFromCategory(Category: Code[30]): Text
    begin
        case Category of
            'FINANCE', 'CUSTOMER', 'VENDOR', 'LEDGER': exit('Finance');
            'ITEM', 'INVENTORY': exit('Inventory');
            'SYSTEM': exit('System');
            'SALES': exit('Sales');
            'PURCHASE': exit('Purchasing');
            'CRM': exit('CRM');
            'MANUFACTURING': exit('Manufacturing');
            'SERVICE': exit('Service');
            'JOB': exit('Jobs');
            'HR': exit('HR');
        end;
        exit('Unknown');
    end;

    local procedure RunScores(ScanRun: Record "DH Deep Scan Run"): JsonObject
    var
        Scores: JsonObject;
    begin
        Scores.Add('System', ScanRun."System Score");
        Scores.Add('Finance', ScanRun."Finance Score");
        Scores.Add('Sales', ScanRun."Sales Score");
        Scores.Add('Purchasing', ScanRun."Purchasing Score");
        Scores.Add('Inventory', ScanRun."Inventory Score");
        Scores.Add('CRM', ScanRun."CRM Score");
        Scores.Add('Manufacturing', ScanRun."Manufacturing Score");
        Scores.Add('Service', ScanRun."Service Score");
        Scores.Add('Jobs', ScanRun."Jobs Score");
        Scores.Add('HR', ScanRun."HR Score");
        exit(Scores);
    end;

    local procedure CurrentModules(): JsonObject
    var
        Setup: Record "DH Setup";
        Modules: JsonObject;
    begin
        if not Setup.Get('SETUP') then
            exit(Modules);
        Modules.Add('System', Setup."Scan System Module");
        Modules.Add('Finance', Setup."Scan Finance Module");
        Modules.Add('Sales', Setup."Scan Sales Module");
        Modules.Add('Purchasing', Setup."Scan Purchasing Module");
        Modules.Add('Inventory', Setup."Scan Inventory Module");
        Modules.Add('CRM', Setup."Scan CRM Module");
        Modules.Add('Manufacturing', Setup."Scan Manufacturing Module");
        Modules.Add('Service', Setup."Scan Service Module");
        Modules.Add('Jobs', Setup."Scan Jobs Module");
        Modules.Add('HR', Setup."Scan HR Module");
        exit(Modules);
    end;

    local procedure GetAppVersion(AppIdText: Text): Text
    var
        Info: ModuleInfo;
        AppId: Guid;
    begin
        Evaluate(AppId, AppIdText);
        NavApp.GetModuleInfo(AppId, Info);
        exit(Format(Info.AppVersion()));
    end;

    var
        SandboxErr: Label 'This read-only export is restricted to the BCS-PERF-DEV SaaS sandbox company.';
        RunMissingErr: Label 'The preserved DEV scan was not found uniquely. No data was changed.';
        RunIncompleteErr: Label 'The preserved scan must be completed. No data was changed.';
        GeneratorMismatchErr: Label 'Generator Run 1 does not match the expected DEV counters. No data was changed.';
}
