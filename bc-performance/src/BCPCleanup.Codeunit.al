codeunit 53406 "BCP Cleanup"
{
    Permissions = tabledata "BCP Run" = RM;

    procedure Preview(RunId: Integer): Integer
    var
        Owned: Record "BCP Owned Record";
        Policy: Codeunit "BCP Policy";
    begin
        Policy.RequireSandbox();
        if RunId <> 0 then
            Owned.SetRange("Run ID", RunId);
        exit(Owned.Count());
    end;

    procedure Clean(RunId: Integer)
    var
        GenerationRun: Record "BCP Run";
        Policy: Codeunit "BCP Policy";
        Failure: Text;
    begin
        Policy.RequireSandbox();
        GenerationRun.LockTable();
        GenerationRun.Get(RunId);
        if not (GenerationRun.Status in [GenerationRun.Status::Completed, GenerationRun.Status::Cancelled, GenerationRun.Status::Failed, GenerationRun.Status::Cleaning]) then
            Error(StateErr);
        GenerationRun.Status := GenerationRun.Status::Cleaning;
        GenerationRun.Modify();
        repeat
            Commit();
            ClearLastError();
            if not Codeunit.Run(Codeunit::"BCP Cleanup Batch", GenerationRun) then begin
                Failure := GetLastErrorText();
                GenerationRun.LockTable();
                GenerationRun.Get(RunId);
                GenerationRun."Error Text" := CopyStr(Failure, 1, MaxStrLen(GenerationRun."Error Text"));
                GenerationRun."Failed Batches" += 1;
                GenerationRun.Modify();
                Commit();
                exit;
            end;
            GenerationRun.Get(RunId);
        until GenerationRun.Status = GenerationRun.Status::Cleaned;
    end;

    var
        StateErr: Label 'Cancel an active run before cleanup. Only completed, cancelled, failed or cleaning runs can be cleaned.';
}
