codeunit 53402 "BCP Batch"
{
    TableNo = "BCP Run";
    Access = Internal;
    Permissions = tabledata "BCP Run" = RM,
                  tabledata "BCP Owned Record" = RI,
                  tabledata Customer = RI,
                  tabledata Vendor = RI,
                  tabledata Item = RIM,
                  tabledata "Item Unit of Measure" = RI;

    trigger OnRun()
    begin
        GenerateBatch(Rec);
    end;

    [CommitBehavior(CommitBehavior::Error)]
    local procedure GenerateBatch(var GenerationRun: Record "BCP Run")
    var
        Remaining: Integer;
    begin
        Policy.RequireSandbox();
        GenerationRun.LockTable();
        GenerationRun.Get(GenerationRun."Run ID");
        Policy.ValidateRun(GenerationRun);
        if not (GenerationRun.Status in [GenerationRun.Status::Pending, GenerationRun.Status::Running, GenerationRun.Status::Failed]) then
            exit;
        if GenerationRun."Started At" = 0DT then
            GenerationRun."Started At" := CurrentDateTime();
        GenerationRun.Status := GenerationRun.Status::Running;
        GenerationRun."Ended At" := 0DT;
        GenerationRun."Error Text" := '';
        Remaining := GenerationRun."Batch Size";
        while (Remaining > 0) and (GenerationRun.BusinessCount() < GenerationRun.TargetCount()) do begin
            if GenerationRun.Vendors < GenerationRun."Vendor Target" then begin
                GenerationRun."Current Phase" := 'VENDOR';
                CreateVendor(GenerationRun);
                GenerationRun.Vendors += 1;
            end else
                if GenerationRun.Customers < GenerationRun."Customer Target" then begin
                    GenerationRun."Current Phase" := 'CUSTOMER';
                    CreateCustomer(GenerationRun);
                    GenerationRun.Customers += 1;
                end else begin
                    GenerationRun."Current Phase" := 'ITEM';
                    CreateItem(GenerationRun);
                    GenerationRun.Items += 1;
                end;
            Remaining -= 1;
        end;
        GenerationRun."Current Batch" += 1;
        GenerationRun."Last Batch At" := CurrentDateTime();
        if GenerationRun.BusinessCount() = GenerationRun.TargetCount() then begin
            GenerationRun.Status := GenerationRun.Status::Completed;
            GenerationRun."Ended At" := CurrentDateTime();
        end;
        GenerationRun.Modify();
        // Codeunit.Run with Boolean return commits business rows, ownership and counters together.
    end;

    local procedure CreateCustomer(var GenerationRun: Record "BCP Run")
    var
        Customer: Record Customer;
        Target: RecordRef;
        Scenario: Code[50];
    begin
        Customer.Init();
        Customer."No." := Policy.RecordNumber(GenerationRun."Run ID", 'C', GenerationRun.Customers + 1);
        Customer.Validate(Name, 'QA Customer ' + Customer."No.");
        Customer.Address := 'Synthetic Business Park 1';
        Customer.City := 'QA City';
        Customer."Post Code" := '10000';
        Customer."Phone No." := '+1 202 555 0100';
        Customer."E-Mail" := LowerCase(Customer."No.") + '@example.invalid';
        Customer."Credit Limit (LCY)" := 10000;
        Customer."Invoice Disc. Code" := Customer."No.";
        Target.GetTable(Customer);
        Config.Apply(Target, GenerationRun."Customer Config");
        Target.SetTable(Customer);
        if Policy.HasScenario(GenerationRun.Customers + 1, GenerationRun.Seed, GenerationRun."Error Rate") then begin
            Customer."E-Mail" := '';
            Scenario := 'CUSTOMERS_MISSING_EMAIL';
        end;
        // Controlled import: no contacts, number series, dimensions or template copying.
        Customer.UpdateReferencedIds();
        Customer."Last Modified Date Time" := CurrentDateTime();
        Customer."Last Date Modified" := Today();
        Customer.Insert(false);
        Target.GetTable(Customer);
        Track(GenerationRun, Target, Customer."No.", Scenario, false);
    end;

    local procedure CreateVendor(var GenerationRun: Record "BCP Run")
    var
        Vendor: Record Vendor;
        Target: RecordRef;
        Scenario: Code[50];
    begin
        Vendor.Init();
        Vendor."No." := Policy.RecordNumber(GenerationRun."Run ID", 'V', GenerationRun.Vendors + 1);
        Vendor.Validate(Name, 'QA Vendor ' + Vendor."No.");
        Vendor.Address := 'Synthetic Business Park 2';
        Vendor.City := 'QA City';
        Vendor."Post Code" := '10000';
        Vendor."Phone No." := '+1 202 555 0101';
        Vendor."E-Mail" := LowerCase(Vendor."No.") + '@example.invalid';
        Vendor."Invoice Disc. Code" := Vendor."No.";
        Target.GetTable(Vendor);
        Config.Apply(Target, GenerationRun."Vendor Config");
        Target.SetTable(Vendor);
        if Policy.HasScenario(GenerationRun.Vendors + 1, GenerationRun.Seed, GenerationRun."Error Rate") then begin
            Vendor."Phone No." := '';
            Scenario := 'VENDORS_MISSING_PHONE';
        end;
        Vendor.UpdateReferencedIds();
        Vendor."Last Modified Date Time" := CurrentDateTime();
        Vendor."Last Date Modified" := Today();
        Vendor.Insert(false);
        Target.GetTable(Vendor);
        Track(GenerationRun, Target, Vendor."No.", Scenario, false);
    end;

    local procedure CreateItem(var GenerationRun: Record "BCP Run")
    var
        Item: Record Item;
        ItemUOM: Record "Item Unit of Measure";
        Target: RecordRef;
        Scenario: Code[50];
    begin
        Item.Init();
        Item."No." := Policy.RecordNumber(GenerationRun."Run ID", 'I', GenerationRun.Items + 1);
        Item.Validate(Description, 'QA Item ' + Item."No.");
        Item."Unit Cost" := 10 + ((GenerationRun.Items + GenerationRun.Seed) mod 90);
        Item."Unit Price" := Item."Unit Cost" * 2;
        Item."Cost is Adjusted" := true;
        // Existing configuration is read, never modified; vendor belongs to this run.
        Item.Validate("Vendor No.", Policy.RecordNumber(GenerationRun."Run ID", 'V', 1 + (GenerationRun.Items mod GenerationRun."Vendor Target")));
        Target.GetTable(Item);
        Config.Apply(Target, GenerationRun."Item Config");
        Target.SetTable(Item);
        if Policy.HasScenario(GenerationRun.Items + 1, GenerationRun.Seed, GenerationRun."Error Rate") then
            if ((GenerationRun.Items div 100) mod 2) = 0 then begin
                Item."Unit Price" := 0;
                Scenario := 'ITEMS_WITHOUT_UNIT_PRICE';
            end else begin
                Item."Unit Cost" := 0;
                Scenario := 'ITEMS_WITHOUT_UNIT_COST';
            end;
        Item.Insert(false);
        ItemUOM.Init();
        ItemUOM.Validate("Item No.", Item."No.");
        ItemUOM.Validate(Code, Config.BaseUOM(GenerationRun."Item Config"));
        ItemUOM.Validate("Qty. per Unit of Measure", 1);
        ItemUOM.Insert(true);
        Item.Validate("Base Unit of Measure", ItemUOM.Code);
        Item.UpdateReferencedIds();
        Item.SetLastDateTimeModified();
        Item.Modify(false);
        ItemUOM.Get(Item."No.", ItemUOM.Code);
        Target.GetTable(ItemUOM);
        Track(GenerationRun, Target, Item."No.", '', true);
        Target.GetTable(Item);
        Track(GenerationRun, Target, Item."No.", Scenario, false);
    end;

    local procedure Track(var GenerationRun: Record "BCP Run"; var Target: RecordRef; Number: Code[20]; Scenario: Code[50]; Supporting: Boolean)
    var
        Owned: Record "BCP Owned Record";
        SystemField: FieldRef;
    begin
        Owned.Init();
        Owned."Run ID" := GenerationRun."Run ID";
        Owned."Table ID" := Target.Number;
        SystemField := Target.Field(Target.SystemIdNo);
        Owned."Record SystemId" := SystemField.Value;
        Owned."Record ID" := Target.RecordId;
        Owned."Record No." := Number;
        SystemField := Target.Field(Target.SystemModifiedAtNo);
        Owned."Modified At" := SystemField.Value;
        Owned.Scenario := Scenario;
        Owned.Supporting := Supporting;
        Owned.Insert();
        if Scenario <> '' then
            GenerationRun."Expected Scenarios" += 1;
    end;

    var
        Policy: Codeunit "BCP Policy";
        Config: Codeunit "BCP Config";
}
