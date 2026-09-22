codeunit 53405 "BCP Cleanup Batch"
{
    TableNo = "BCP Run";
    Access = Internal;
    Permissions = tabledata "BCP Run" = RM,
                  tabledata "BCP Owned Record" = RD,
                  tabledata Customer = RD,
                  tabledata Vendor = RD,
                  tabledata Item = RD,
                  tabledata "Item Unit of Measure" = RD;

    trigger OnRun()
    begin
        CleanBatch(Rec);
    end;

    [CommitBehavior(CommitBehavior::Error)]
    local procedure CleanBatch(var GenerationRun: Record "BCP Run")
    var
        Owned: Record "BCP Owned Record";
        Policy: Codeunit "BCP Policy";
        References: Codeunit "BCP References";
        Count: Integer;
    begin
        Policy.RequireSandbox();
        GenerationRun.LockTable();
        GenerationRun.Get(GenerationRun."Run ID");
        GenerationRun.TestField(Status, GenerationRun.Status::Cleaning);
        Owned.SetRange("Run ID", GenerationRun."Run ID");
        Owned.SetRange(Supporting, false);
        // Dependency order: items (including their UOM), customers, then vendors.
        Owned.SetRange("Table ID", Database::Item);
        if Owned.IsEmpty() then begin
            Owned.SetRange("Table ID", Database::Customer);
            if Owned.IsEmpty() then
                Owned.SetRange("Table ID", Database::Vendor);
        end;
        if Owned.FindFirst() then
            References.AssertPhaseUnreferenced(Owned);
        Count := 0;
        while (Count < GenerationRun."Batch Size") and Owned.FindFirst() do begin
            DeleteOwned(Owned, GenerationRun);
            Count += 1;
        end;
        Owned.Reset();
        Owned.SetRange("Run ID", GenerationRun."Run ID");
        if Owned.IsEmpty() then
            GenerationRun.Status := GenerationRun.Status::Cleaned
        else
            if Count = 0 then
                Error(OwnershipErr);
        GenerationRun."Last Batch At" := CurrentDateTime();
        GenerationRun."Error Text" := '';
        GenerationRun.Modify();
    end;

    local procedure DeleteOwned(var Owned: Record "BCP Owned Record"; var GenerationRun: Record "BCP Run")
    var
        Support: Record "BCP Owned Record";
        ItemUOM: Record "Item Unit of Measure";
        References: Codeunit "BCP References";
        Target: RecordRef;
        SupportTarget: RecordRef;
    begin
        VerifyIdentity(Owned, Target);
        References.CheckRecordIds(Owned);
        if Owned."Table ID" = Database::Item then begin
            ItemUOM.LockTable();
            ItemUOM.SetRange("Item No.", Owned."Record No.");
            if ItemUOM.FindSet() then
                repeat
                    // Every row the standard item trigger can cascade must be ours and unchanged.
                    Support.Get(Owned."Run ID", Database::"Item Unit of Measure", ItemUOM.SystemId);
                    VerifyIdentity(Support, SupportTarget);
                    SupportTarget.Close();
                until ItemUOM.Next() = 0;
        end;
        Target.Delete(true);
        Target.Close();
        Support.SetRange("Run ID", Owned."Run ID");
        Support.SetRange("Record No.", Owned."Record No.");
        Support.SetRange(Supporting, true);
        if Support.FindSet(true) then
            repeat
                SupportTarget.Open(Support."Table ID");
                if SupportTarget.GetBySystemId(Support."Record SystemId") then
                    Error(OwnershipErr);
                SupportTarget.Close();
                Support.Delete();
                GenerationRun."Cleanup Count" += 1;
            until Support.Next() = 0;
        Owned.Delete();
        GenerationRun."Cleanup Count" += 1;
    end;

    local procedure VerifyIdentity(Owned: Record "BCP Owned Record"; var Target: RecordRef)
    var
        SystemField: FieldRef;
        ModifiedAt: DateTime;
    begin
        if not (Owned."Table ID" in [Database::Customer, Database::Vendor, Database::Item, Database::"Item Unit of Measure"]) then
            Error(OwnershipErr);
        if CopyStr(Owned."Record No.", 1, 9) <> 'BCP' + Format(Owned."Run ID", 0, '<Integer,6><Filler Character,0>') then
            Error(OwnershipErr);
        Target.Open(Owned."Table ID");
        Target.LockTable();
        if not Target.GetBySystemId(Owned."Record SystemId") then
            Error(OwnershipErr);
        if Target.RecordId <> Owned."Record ID" then
            Error(OwnershipErr);
        SystemField := Target.Field(Target.SystemModifiedAtNo);
        ModifiedAt := SystemField.Value;
        if ModifiedAt <> Owned."Modified At" then
            Error(OwnershipErr);
    end;

    var
        OwnershipErr: Label 'Cleanup refused: a tracked record is missing, changed, renamed, replaced or not owned. Review manually; no forced cleanup is available.';
}
