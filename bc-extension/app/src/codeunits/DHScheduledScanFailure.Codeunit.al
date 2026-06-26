codeunit 53172 "DH Scheduled Scan Failure"
{
    trigger OnRun()
    var
        SchedulerMgt: Codeunit "DH Scan Scheduler Mgt.";
    begin
        SchedulerMgt.MarkTaskFailure(GetLastErrorText());
    end;
}
