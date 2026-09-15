codeunit 53400 "BCP Policy"
{
    procedure RequireSandbox()
    var
        EnvironmentInformation: Codeunit "Environment Information";
    begin
        if not EnvironmentInformation.IsSaaS() or not EnvironmentInformation.IsSandbox() or EnvironmentInformation.IsProduction() then
            Error(SandboxErr);
        if CopyStr(CompanyName(), 1, 9) <> 'BCS-PERF-' then
            Error(CompanyErr);
    end;

    procedure SetProfile(var GenerationRun: Record "BCP Run")
    begin
        case GenerationRun.Profile of
            GenerationRun.Profile::DEV: SetTargets(GenerationRun, 6000, 2000, 12000);
            GenerationRun.Profile::LARGE: SetTargets(GenerationRun, 150000, 50000, 300000);
            GenerationRun.Profile::XL: SetTargets(GenerationRun, 600000, 200000, 1200000);
            GenerationRun.Profile::STRESS: SetTargets(GenerationRun, 1500000, 500000, 3000000);
            GenerationRun.Profile::Custom: ;
            else Error(ConfigErr);
        end;
    end;

    procedure ValidateRun(GenerationRun: Record "BCP Run")
    begin
        if not (GenerationRun."Error Rate" in [1, 5, 10, 20]) or (GenerationRun.Seed < 0) or (GenerationRun.Seed > 1000000) then
            Error(ConfigErr);
        if (GenerationRun."Batch Size" < 1) or (GenerationRun."Batch Size" > 5000) then
            Error(ConfigErr);
        if (GenerationRun."Customer Target" < 1) or (GenerationRun."Vendor Target" < 1) or (GenerationRun."Item Target" < 1) then
            Error(ConfigErr);
        if (GenerationRun."Customer Target" > 5000000) or (GenerationRun."Vendor Target" > 5000000) or (GenerationRun."Item Target" > 5000000) then
            Error(ConfigErr);
        if GenerationRun.TargetCount() > 10000000 then
            Error(ConfigErr);
        if GenerationRun."Schema Version" <> 1 then
            Error(ConfigErr);
    end;

    procedure DefaultBatchSize(): Integer
    begin
        exit(1000);
    end;

    procedure HasScenario(Sequence: Integer; Seed: Integer; Rate: Integer): Boolean
    begin
        // A permutation of each block of 100: exact rate per full block, no PRNG state.
        exit(((Sequence mod 100) * 37 + (Seed mod 100)) mod 100 < Rate);
    end;

    procedure RecordNumber(RunId: Integer; Kind: Code[1]; Sequence: Integer): Code[20]
    begin
        if (RunId < 1) or (RunId > 999999) or (Sequence < 1) or (Sequence > 9999999) then
            Error(ConfigErr);
        exit(CopyStr('BCP' + Format(RunId, 0, '<Integer,6><Filler Character,0>') + Kind +
            Format(Sequence, 0, '<Integer,7><Filler Character,0>'), 1, 20));
    end;

    local procedure SetTargets(var GenerationRun: Record "BCP Run"; Customers: Integer; Vendors: Integer; Items: Integer)
    begin
        GenerationRun."Customer Target" := Customers;
        GenerationRun."Vendor Target" := Vendors;
        GenerationRun."Item Target" := Items;
    end;

    var
        SandboxErr: Label 'QA generator requires a Business Central SaaS sandbox. Production and unknown environments are blocked.';
        CompanyErr: Label 'Use a dedicated disposable company whose name starts with BCS-PERF-.';
        ConfigErr: Label 'Invalid QA configuration, profile, schema, or number range. Review the generator guide.';
}
