codeunit 53404 "BCP References"
{
    Access = Internal;

    procedure AssertPhaseUnreferenced(Owned: Record "BCP Owned Record")
    var
        Metadata: Record Field;
        Other: RecordRef;
        OtherField: FieldRef;
    begin
        // Fail closed on missing read permission. Include conditional/polymorphic number
        // fields as well as declared relations; do not silently skip inaccessible tables.
        Metadata.SetRange(Class, Metadata.Class::Normal);
        Metadata.SetRange(Enabled, true);
        Metadata.SetFilter(ObsoleteState, '<>%1', Metadata.ObsoleteState::Removed);
        Metadata.SetFilter(TableNo, '<%1', 2000000000);
        Metadata.SetFilter(Type, '%1|%2', Metadata.Type::Code, Metadata.Type::Text);
        if Metadata.FindSet() then
            repeat
                if IsReferenceCandidate(Metadata, Owned."Table ID") then begin
                    Other.Open(Metadata.TableNo);
                    OtherField := Other.Field(Metadata."No.");
                    OtherField.SetFilter(CopyStr(Owned."Record No.", 1, 10) + '*');
                    if not Other.IsEmpty() then
                        Error(ReferenceErr, Owned."Record No.", Other.Caption, OtherField.Caption);
                    Other.Close();
                end;
            until Metadata.Next() = 0;
    end;

    local procedure IsReferenceCandidate(Metadata: Record Field; TargetTable: Integer): Boolean
    var
        TableMetadata: Record "Table Metadata";
    begin
        TableMetadata.Get(Metadata.TableNo);
        if (TableMetadata.TableType <> TableMetadata.TableType::Normal) or
           (TableMetadata.ObsoleteState = TableMetadata.ObsoleteState::Removed) then
            exit(false); // not an active local business table
        if Metadata.TableNo in [Database::"BCP Run", Database::"BCP Owned Record"] then
            exit(false);
        // UOM ownership is checked individually by cleanup before the standard item cascade.
        if (TargetTable = Database::Item) and (Metadata.TableNo = Database::"Item Unit of Measure") then
            exit(false);
        if (Metadata.TableNo = TargetTable) and (Metadata."No." in [1, 33]) then
            exit(false); // primary number and self invoice-discount number
        exit((Metadata.RelationTableNo = TargetTable) or
            (Metadata.FieldName in ['No.', 'Source No.', 'Record No.', 'Reference Type No.', 'Document No.']));
    end;

    procedure CheckRecordIds(Owned: Record "BCP Owned Record")
    var
        RecordLink: Record "Record Link";
        ApprovalEntry: Record "Approval Entry";
        EntityText: Record "Entity Text";
        UnitGroup: Record "Unit Group";
    begin
        RecordLink.SetRange("Record ID", Owned."Record ID");
        if not RecordLink.IsEmpty() then
            Error(RelatedErr);
        ApprovalEntry.SetRange("Record ID to Approve", Owned."Record ID");
        if not ApprovalEntry.IsEmpty() then
            Error(RelatedErr);
        if Owned."Table ID" = Database::Item then begin
            EntityText.SetRange(Company, CompanyName());
            EntityText.SetRange("Source Table Id", Database::Item);
            EntityText.SetRange("Source System Id", Owned."Record SystemId");
            if not EntityText.IsEmpty() then
                Error(ReferenceErr, Owned."Record No.", EntityText.TableCaption(), EntityText.FieldCaption("Source System Id"));
            if UnitGroup.Get(UnitGroup."Source Type"::Item, Owned."Record SystemId") then
                Error(ReferenceErr, Owned."Record No.", UnitGroup.TableCaption(), UnitGroup.FieldCaption("Source Id"));
        end;
    end;

    var
        ReferenceErr: Label 'Cleanup refused: %1 is referenced by %2.%3.', Comment = '%1 = generated number, %2 = table, %3 = field';
        RelatedErr: Label 'Cleanup refused because record links or approvals exist.';
}
