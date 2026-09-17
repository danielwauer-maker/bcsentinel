codeunit 53460 "BCS Finding Identity Tests"
{
    Subtype = Test;

    [Test]
    procedure TwoGroupsReceiveTheirOwnImpactOnReorderedRetry()
    var
        TempFinding: Record "DH Deep Scan Finding" temporary;
        FirstId: Guid;
        SecondId: Guid;
    begin
        AddFinding(TempFinding, 1, 10, 'CHECK_A', 10);
        FirstId := TempFinding.SystemId;
        AddFinding(TempFinding, 2, 10, 'CHECK_A', 20);
        SecondId := TempFinding.SystemId;
        AssertTrue(not IsNullGuid(FirstId));
        AssertTrue(not IsNullGuid(SecondId));
        AssertTrue(FirstId <> SecondId);
        TempFinding.ApplyBackendImpact(10, 'CHECK_A', SecondId, 'high', 250);
        TempFinding.ApplyBackendImpact(10, 'CHECK_A', FirstId, 'medium', 100);
        TempFinding.ApplyBackendImpact(10, 'CHECK_A', SecondId, 'high', 250);
        TempFinding.GetBySystemId(FirstId);
        AssertTrue(TempFinding."Estimated Impact (EUR)" = 100);
        AssertTrue(TempFinding.Severity = 'medium');
        TempFinding.GetBySystemId(SecondId);
        AssertTrue(TempFinding."Estimated Impact (EUR)" = 250);
        AssertTrue(TempFinding.Severity = 'high');
        TempFinding.Reset();
        AssertTrue(TempFinding.Count() = 2);
        TempFinding.CalcSums("Estimated Impact (EUR)");
        AssertTrue(TempFinding."Estimated Impact (EUR)" = 350);
    end;

    [Test]
    procedure ForeignRunAndCheckCannotReceiveImpact()
    var
        TempFinding: Record "DH Deep Scan Finding" temporary;
        FindingId: Guid;
    begin
        AddFinding(TempFinding, 1, 10, 'CHECK_A', 2);
        FindingId := TempFinding.SystemId;
        asserterror TempFinding.ApplyBackendImpact(11, 'CHECK_A', FindingId, 'high', 99);
        asserterror TempFinding.ApplyBackendImpact(10, 'CHECK_B', FindingId, 'high', 99);
        asserterror TempFinding.ApplyBackendImpact(10, 'CHECK_A', CreateGuid(), 'high', 99);
        TempFinding.GetBySystemId(FindingId);
        AssertTrue(TempFinding."Estimated Impact (EUR)" = 0);
    end;

    [Test]
    procedure GroupMarkersPersistAndStayScoped()
    var
        TempFinding: Record "DH Deep Scan Finding" temporary;
        RunId: Guid;
        FirstKey: Text[64];
    begin
        RunId := CreateGuid();
        FirstKey := TempFinding.BuildGroupKey(RunId, 'CHECK_A', 'first');
        AssertTrue(FirstKey = TempFinding.BuildGroupKey(RunId, 'CHECK_A', 'FIRST'));
        AssertTrue(FirstKey <> TempFinding.BuildGroupKey(RunId, 'CHECK_A', 'second'));
        AssertTrue(FirstKey <> TempFinding.BuildGroupKey(RunId, 'CHECK_B', 'first'));
        AssertTrue(FirstKey <> TempFinding.BuildGroupKey(CreateGuid(), 'CHECK_A', 'first'));
        AddFinding(TempFinding, 1, 10, 'CHECK_A', 2);
        TempFinding."Group Key" := FirstKey;
        TempFinding.Modify();
        TempFinding.SetRange("Deep Scan Entry No.", 10);
        TempFinding.SetRange("Issue Code", 'CHECK_A');
        TempFinding.SetRange("Group Key", FirstKey);
        AssertTrue(TempFinding.Count() = 1);
        TempFinding.FindFirst();
        AssertTrue(TempFinding."Group Key" = FirstKey);
    end;

    local procedure AddFinding(var TempFinding: Record "DH Deep Scan Finding" temporary; EntryNo: Integer; RunEntryNo: Integer; IssueCode: Code[50]; Count: Integer)
    begin
        TempFinding.Reset();
        TempFinding.Init();
        TempFinding."Entry No." := EntryNo;
        TempFinding."Deep Scan Entry No." := RunEntryNo;
        TempFinding."Issue Code" := IssueCode;
        TempFinding."Affected Count" := Count;
        // Temporary records need explicit creation identities for this fixture.
        TempFinding.SystemId := CreateGuid();
        TempFinding.Insert(false, true);
    end;

    local procedure AssertTrue(Condition: Boolean)
    begin
        if not Condition then
            Error(AssertionErr);
    end;

    var
        AssertionErr: Label 'Finding identity assertion failed.';
}
