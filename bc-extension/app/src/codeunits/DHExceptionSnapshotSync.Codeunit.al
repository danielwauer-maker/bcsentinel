codeunit 53181 "DH Exception Snapshot Sync"
{
    [EventSubscriber(ObjectType::Table, Database::"DH Deep Scan Run", 'OnAfterModifyEvent', '', false, false)]
    local procedure OnAfterDeepScanRunModify(var Rec: Record "DH Deep Scan Run"; var xRec: Record "DH Deep Scan Run"; RunTrigger: Boolean)
    var
        PersistedRun: Record "DH Deep Scan Run";
        Transport: Codeunit "DH Exception Snapshot Transport";
    begin
        if Rec.Status <> Rec.Status::Completed then
            exit;
        if Rec."Run ID" = '' then
            exit;
        if Rec."Exception Snapshot Captured" then
            exit;

        if not Transport.TrySend(Rec."Run ID") then
            exit;

        if PersistedRun.Get(Rec."Entry No.") then
            if not PersistedRun."Exception Snapshot Captured" then begin
                PersistedRun."Exception Snapshot Captured" := true;
                PersistedRun.Modify(false);
            end;
    end;
}
