codeunit 53407 "BCP Self Tests"
{
    Subtype = Test;
    Access = Internal;

    [Test]
    procedure TemporaryRequestHasPersistedValidDefaults()
    var
        TempRequest: Record "BCP Run" temporary;
        Policy: Codeunit "BCP Policy";
    begin
        TempRequest."Run ID" := 99;
        TempRequest.Customers := 999;
        Policy.InitializeTemporaryRequest(TempRequest);
        AssertEqual(1, TempRequest.Count());
        Clear(TempRequest.Seed);
        TempRequest.FindFirst(); // Read back the actual temporary row, not the buffer.
        AssertEqual(TempRequest.Profile::DEV.AsInteger(), TempRequest.Profile.AsInteger());
        AssertEqual(5001, TempRequest.Seed);
        AssertEqual(10, TempRequest."Error Rate");
        AssertEqual(1000, TempRequest."Batch Size");
        AssertEqual(1, TempRequest."Schema Version");
        AssertEqual(0, TempRequest.BusinessCount());
        AssertTargets(TempRequest, 6000, 2000, 12000);
        Policy.ValidateRun(TempRequest);
    end;

    [Test]
    procedure ProfileSwitchesPersistTargetsWithoutResettingOptions()
    var
        TempRequest: Record "BCP Run" temporary;
        Policy: Codeunit "BCP Policy";
    begin
        Policy.InitializeTemporaryRequest(TempRequest);
        TempRequest.Seed := 42;
        TempRequest."Error Rate" := 5;
        TempRequest."Batch Size" := 2;
        TempRequest.Profile := TempRequest.Profile::LARGE;
        Policy.SetProfile(TempRequest);
        TempRequest.Modify();
        TempRequest.FindFirst();
        AssertTargets(TempRequest, 150000, 50000, 300000);
        AssertEqual(42, TempRequest.Seed);
        AssertEqual(5, TempRequest."Error Rate");
        AssertEqual(2, TempRequest."Batch Size");
        AssertEqual(1, TempRequest."Schema Version");
        Policy.ValidateRun(TempRequest);
        TempRequest.Profile := TempRequest.Profile::DEV;
        Policy.SetProfile(TempRequest);
        AssertTargets(TempRequest, 6000, 2000, 12000);
    end;

    [Test]
    procedure CustomRetainsEnteredTargetsAndPresetOverridesThem()
    var
        TempRequest: Record "BCP Run" temporary;
        Policy: Codeunit "BCP Policy";
    begin
        Policy.InitializeTemporaryRequest(TempRequest);
        TempRequest.Profile := TempRequest.Profile::Custom;
        TempRequest."Customer Target" := 3;
        TempRequest."Vendor Target" := 2;
        TempRequest."Item Target" := 5;
        Policy.SetProfile(TempRequest);
        TempRequest.Modify();
        TempRequest.FindFirst();
        AssertTargets(TempRequest, 3, 2, 5);
        Policy.ValidateRun(TempRequest);
        TempRequest.Profile := TempRequest.Profile::LARGE;
        Policy.SetProfile(TempRequest);
        AssertTargets(TempRequest, 150000, 50000, 300000);
        TempRequest.Profile := TempRequest.Profile::Custom;
        Policy.SetProfile(TempRequest);
        AssertTargets(TempRequest, 150000, 50000, 300000);
    end;

    [Test]
    procedure InitializerRefusesPersistentOrExistingRequests()
    var
        PersistentRequest: Record "BCP Run";
        TempRequest: Record "BCP Run" temporary;
        Policy: Codeunit "BCP Policy";
    begin
        asserterror Policy.InitializeTemporaryRequest(PersistentRequest);
        Policy.InitializeTemporaryRequest(TempRequest);
        TempRequest.Seed := 42;
        TempRequest.Modify();
        asserterror Policy.InitializeTemporaryRequest(TempRequest);
        TempRequest.FindFirst();
        AssertEqual(42, TempRequest.Seed);
        AssertEqual(1, TempRequest.Count());
    end;

    [Test]
    procedure ProfilesRespectBusinessCountThresholds()
    var
        TempGenerationRun: Record "BCP Run" temporary;
        Policy: Codeunit "BCP Policy";
    begin
        TempGenerationRun.Profile := TempGenerationRun.Profile::DEV;
        Policy.SetProfile(TempGenerationRun);
        AssertEqual(20000, TempGenerationRun.TargetCount());
        AssertTargets(TempGenerationRun, 6000, 2000, 12000);
        TempGenerationRun.Profile := TempGenerationRun.Profile::LARGE;
        Policy.SetProfile(TempGenerationRun);
        AssertEqual(500000, TempGenerationRun.TargetCount());
        AssertTargets(TempGenerationRun, 150000, 50000, 300000);
        TempGenerationRun.Profile := TempGenerationRun.Profile::XL;
        Policy.SetProfile(TempGenerationRun);
        AssertEqual(2000000, TempGenerationRun.TargetCount());
        AssertTargets(TempGenerationRun, 600000, 200000, 1200000);
        TempGenerationRun.Profile := TempGenerationRun.Profile::STRESS;
        Policy.SetProfile(TempGenerationRun);
        AssertEqual(5000000, TempGenerationRun.TargetCount());
        AssertTargets(TempGenerationRun, 1500000, 500000, 3000000);
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
        TempGenerationRun."Batch Size" := 1000;
        TempGenerationRun.Seed := -1;
        asserterror Policy.ValidateRun(TempGenerationRun);
        TempGenerationRun.Seed := 1000001;
        asserterror Policy.ValidateRun(TempGenerationRun);
        TempGenerationRun.Seed := 5001;
        TempGenerationRun."Schema Version" := 0;
        asserterror Policy.ValidateRun(TempGenerationRun);
        TempGenerationRun."Schema Version" := 1;
        TempGenerationRun."Item Target" := 0;
        asserterror Policy.ValidateRun(TempGenerationRun);
    end;

    local procedure AssertTargets(Request: Record "BCP Run"; Customers: Integer; Vendors: Integer; Items: Integer)
    begin
        AssertEqual(Customers, Request."Customer Target");
        AssertEqual(Vendors, Request."Vendor Target");
        AssertEqual(Items, Request."Item Target");
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
