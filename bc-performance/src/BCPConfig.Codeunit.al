codeunit 53401 "BCP Config"
{
    procedure Snapshot(TableId: Integer; Number: Code[20]): Text[2048]
    var
        Source: RecordRef;
        SourceField: FieldRef;
        Config: JsonObject;
        FieldIds: List of [Integer];
        FieldId: Integer;
        Output: Text;
    begin
        Source.Open(TableId);
        SourceField := Source.Field(1);
        SourceField.SetRange(Number);
        Source.FindFirst();
        GetFields(TableId, FieldIds);
        foreach FieldId in FieldIds do begin
            SourceField := Source.Field(FieldId);
            SourceField.TestField();
            Config.Add(Format(FieldId, 0, 9), Format(SourceField.Value));
        end;
        Config.WriteTo(Output);
        Source.Close();
        exit(CopyStr(Output, 1, 2048));
    end;

    procedure Apply(var Target: RecordRef; ConfigText: Text)
    var
        TargetField: FieldRef;
        Config: JsonObject;
        Token: JsonToken;
        FieldIds: List of [Integer];
        FieldId: Integer;
    begin
        Config.ReadFrom(ConfigText);
        GetFields(Target.Number, FieldIds);
        foreach FieldId in FieldIds do begin
            Config.Get(Format(FieldId, 0, 9), Token);
            // Item UOM is created explicitly and tracked before base UOM validation.
            if not ((Target.Number = Database::Item) and (FieldId = 8)) then begin
                TargetField := Target.Field(FieldId);
                TargetField.Validate(Token.AsValue().AsText());
            end;
        end;
    end;

    procedure BaseUOM(ConfigText: Text): Code[10]
    var
        Config: JsonObject;
        Token: JsonToken;
    begin
        Config.ReadFrom(ConfigText);
        Config.Get('8', Token);
        exit(CopyStr(Token.AsValue().AsText(), 1, 10));
    end;

    procedure ValidateItemConfig(ConfigText: Text)
    var
        ItemCategory: Record "Item Category";
        AttributeMapping: Record "Item Attribute Value Mapping";
        Config: JsonObject;
        Token: JsonToken;
        CategoryCode: Code[20];
        Visited: List of [Code[20]];
    begin
        Config.ReadFrom(ConfigText);
        Config.Get('5702', Token);
        CategoryCode := CopyStr(Token.AsValue().AsText(), 1, MaxStrLen(CategoryCode));
        AttributeMapping.SetRange("Table ID", Database::"Item Category");
        repeat
            if Visited.Contains(CategoryCode) then
                Error(CategoryErr);
            Visited.Add(CategoryCode);
            ItemCategory.Get(CategoryCode);
            AttributeMapping.SetRange("No.", CategoryCode);
            if not AttributeMapping.IsEmpty() then
                Error(CategoryErr);
            CategoryCode := ItemCategory."Parent Category";
        until CategoryCode = '';
    end;

    local procedure GetFields(TableId: Integer; var FieldIds: List of [Integer])
    begin
        case TableId of
            Database::Customer, Database::Vendor:
                FieldIds.AddRange(21, 27, 35, 47, 88, 110);
            Database::Item:
                FieldIds.AddRange(8, 11, 91, 99, 5702);
        end;
    end;

    var
        CategoryErr: Label 'QA generation requires an item category without own or inherited attributes and without a circular parent hierarchy.';
}
