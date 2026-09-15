codeunit 53403 "BCP Management"
{
    Permissions = tabledata "BCP Run" = RIM;

    procedure CreateRun(var GenerationRun: Record "BCP Run"; CustomerNo: Code[20]; VendorNo: Code[20]; ItemNo: Code[20])
    var
        TempRequest: Record "BCP Run" temporary;
        Config: Codeunit "BCP Config";
    begin
        Policy.RequireSandbox();
        GenerationRun.TestField("Run ID", 0);
        // Public callers supply configuration only, never counters or lifecycle evidence.
        TempRequest := GenerationRun;
        GenerationRun.Init();
        GenerationRun.Profile := TempRequest.Profile;
        GenerationRun.Seed := TempRequest.Seed;
        GenerationRun."Error Rate" := TempRequest."Error Rate";
        GenerationRun."Batch Size" := TempRequest."Batch Size";
        GenerationRun."Customer Target" := TempRequest."Customer Target";
        GenerationRun."Vendor Target" := TempRequest."Vendor Target";
        GenerationRun."Item Target" := TempRequest."Item Target";
        GenerationRun."Schema Version" := 1;
        Policy.SetProfile(GenerationRun);
        Policy.ValidateRun(GenerationRun);
        GenerationRun."Customer Config" := Config.Snapshot(Database::Customer, CustomerNo);
        GenerationRun."Vendor Config" := Config.Snapshot(Database::Vendor, VendorNo);
        GenerationRun."Item Config" := Config.Snapshot(Database::Item, ItemNo);
        GenerationRun.Status := GenerationRun.Status::Pending;
        GenerationRun.Insert();
    end;

    procedure Execute(RunId: Integer; OneBatchOnly: Boolean)
    var
        GenerationRun: Record "BCP Run";
        Failure: Text;
    begin
        Policy.RequireSandbox();
        GenerationRun.Get(RunId);
        repeat
            Commit();
            ClearLastError();
            if not Codeunit.Run(Codeunit::"BCP Batch", GenerationRun) then begin
                Failure := GetLastErrorText();
                GenerationRun.LockTable();
                GenerationRun.Get(RunId);
                // Do not overwrite a concurrent cancellation or cleanup transition.
                if GenerationRun.Status in [GenerationRun.Status::Pending, GenerationRun.Status::Running, GenerationRun.Status::Failed] then begin
                    GenerationRun.Status := GenerationRun.Status::Failed;
                    GenerationRun."Error Text" := CopyStr(Failure, 1, MaxStrLen(GenerationRun."Error Text"));
                    GenerationRun."Failed Batches" += 1;
                    GenerationRun."Ended At" := CurrentDateTime();
                    GenerationRun.Modify();
                end;
                Commit();
                exit;
            end;
            GenerationRun.Get(RunId);
        until OneBatchOnly or (GenerationRun.Status <> GenerationRun.Status::Running);
    end;

    procedure Cancel(RunId: Integer)
    var
        GenerationRun: Record "BCP Run";
    begin
        Policy.RequireSandbox();
        GenerationRun.LockTable();
        GenerationRun.Get(RunId);
        if GenerationRun.Status in [GenerationRun.Status::Pending, GenerationRun.Status::Running, GenerationRun.Status::Failed] then begin
            GenerationRun.Status := GenerationRun.Status::Cancelled;
            GenerationRun."Ended At" := CurrentDateTime();
            GenerationRun.Modify();
        end;
    end;

    var
        Policy: Codeunit "BCP Policy";
}
