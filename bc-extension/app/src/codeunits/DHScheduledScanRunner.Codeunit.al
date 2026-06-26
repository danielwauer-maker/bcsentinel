codeunit 53171 "DH Scheduled Scan Runner"
{
    trigger OnRun()
    var
        SchedulerMgt: Codeunit "DH Scan Scheduler Mgt.";
    begin
        SchedulerMgt.ExecuteScheduledRun();
    end;
}
