codeunit 53407 "BCP Self Tests"
{
    Subtype = Test;
    Access = Internal;

    [Test]
    procedure ProfilesRespectBusinessCountThresholds()
    var
        TempGenerationRun: Record "BCP Run" temporary;
        Policy: Codeunit "BCP Policy";
    begin
        TempGenerationRun.Profile := TempGenerationRun.Profile::DEV;
        Policy.SetProfile(TempGenerationRun);
        AssertEqual(20000, TempGenerationRun.TargetCount());
        TempGenerationRun.Profile := TempGenerationRun.Profile::LARGE;
        Policy.SetProfile(TempGenerationRun);
        AssertEqual(500000, TempGenerationRun.TargetCount());
        TempGenerationRun.Profile := TempGenerationRun.Profile::XL;
        Policy.SetProfile(TempGenerationRun);
        AssertEqual(2000000, TempGenerationRun.TargetCount());
        TempGenerationRun.Profile := TempGenerationRun.Profile::STRESS;
        Policy.SetProfile(TempGenerationRun);
        AssertEqual(5000000, TempGenerationRun.TargetCount());
    end;

    [Test]
    procedure EveryFullBlockHasExactRateAcrossSeeds()
    var
        Policy: Codeunit "BCP Policy";
        Seeds: List of [Integer];
        Rates: List of [Integer];
        Seed: Integer;
        Rate: Integer;
        Sequence: Integer;
        Count: Integer;
    begin
        Seeds.AddRange(0, 5001, 1000000);
        Rates.AddRange(1, 5, 10, 20);
        foreach Seed in Seeds do
            foreach Rate in Rates do begin
                Count := 0;
                for Sequence := 1 to 10000 do
                    if Policy.HasScenario(Sequence, Seed, Rate) then
                        Count += 1;
                AssertEqual(Rate * 100, Count);
            end;
    end;

    [Test]
    procedure NamespaceSeparatesRunsAndEntitiesWithoutTruncation()
    var
        Policy: Codeunit "BCP Policy";
    begin
        AssertEqual(17, StrLen(Policy.RecordNumber(999999, 'I', 5000000)));
        if Policy.RecordNumber(1, 'I', 1) = Policy.RecordNumber(2, 'I', 1) then
            Error(CollisionErr);
        if Policy.RecordNumber(1, 'I', 1) = Policy.RecordNumber(1, 'V', 1) then
            Error(CollisionErr);
        asserterror Policy.RecordNumber(1000000, 'I', 1);
    end;

    [Test]
    procedure InvalidConfigurationIsRejected()
    var
        TempGenerationRun: Record "BCP Run" temporary;
        Policy: Codeunit "BCP Policy";
    begin
        TempGenerationRun.Seed := 5001;
        TempGenerationRun."Error Rate" := 10;
        TempGenerationRun."Schema Version" := 1;
        TempGenerationRun."Batch Size" := Policy.DefaultBatchSize();
        Policy.SetProfile(TempGenerationRun);
        Policy.ValidateRun(TempGenerationRun);
        TempGenerationRun."Error Rate" := 2;
        asserterror Policy.ValidateRun(TempGenerationRun);
        TempGenerationRun."Error Rate" := 10;
        TempGenerationRun."Batch Size" := 0;
        asserterror Policy.ValidateRun(TempGenerationRun);
        TempGenerationRun."Batch Size" := 5001;
        asserterror Policy.ValidateRun(TempGenerationRun);
    end;

    local procedure AssertEqual(Expected: Integer; Actual: Integer)
    begin
        if Expected <> Actual then
            Error(CountErr, Expected, Actual);
    end;

    var
        CollisionErr: Label 'QA test: namespace collision.', Locked = true;
        CountErr: Label 'QA test: expected %1, got %2.', Locked = true;
}
