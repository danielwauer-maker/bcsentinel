codeunit 53170 "DH Scan Scheduler Mgt."
{
    procedure CalculateNextRun(var Setup: Record "DH Setup"): DateTime
    var
        NextRun: DateTime;
    begin
        Setup.EnsureSchedulerDefaults();
        NextRun := CalculateNextRunFrom(Setup, CurrentDateTime());
        Setup."Next Scheduled Scan" := NextRun;
        Setup.Modify(true);
        exit(NextRun);
    end;

    procedure Reschedule(var Setup: Record "DH Setup")
    var
        NotBefore: DateTime;
        SchedulerUnavailableMsg: Label 'The next scheduled scan was calculated, but automatic TaskScheduler planning is not available in this client context. Use Run now or schedule from an active Business Central session.';
    begin
        EnsureMonitoringForScheduler(Setup);

        if not Setup."Scheduled Scans Enabled" then
            Error('Scheduled scans are not enabled.');

        NotBefore := CalculateNextRun(Setup);
        if not TryCreateSchedulerTask(NotBefore) then
            Message(SchedulerUnavailableMsg);
    end;

    procedure DisableScheduler(var Setup: Record "DH Setup")
    begin
        Setup."Scheduled Scans Enabled" := false;
        Setup."Scheduled Scan Task ID" := CreateGuid();
        Setup.Modify(true);
    end;

    procedure RunNow(var Setup: Record "DH Setup"): Integer
    begin
        EnsureMonitoringForScheduler(Setup);
        EnsureScanConfiguration(Setup);
        exit(StartScheduledScan(Setup));
    end;

    procedure ExecuteScheduledRun()
    var
        Setup: Record "DH Setup";
        StartedAt: DateTime;
        EntryNo: Integer;
        ErrorTxt: Text[250];
    begin
        if not Setup.Get('SETUP') then
            exit;

        Setup.EnsureSchedulerDefaults();
        StartedAt := CurrentDateTime();

        if not Setup."Scheduled Scans Enabled" then
            exit;

        if not Setup."Monitoring Active" then begin
            Setup."Last Scheduled Scan" := StartedAt;
            Setup."Last Scheduled Scan Result" := Setup."Last Scheduled Scan Result"::SkippedMonitoringInactive;
            Setup."Last Scheduled Scan Error" := 'Scheduled scans require an active Monitoring subscription.';
            Setup."Scheduled Scan Failure Count" += 1;
            Setup."Next Scheduled Scan" := CalculateNextRunFrom(Setup, StartedAt);
            Setup.Modify(true);
            exit;
        end;

        if not Setup.HasAnyModuleEnabled() then begin
            Setup."Last Scheduled Scan" := StartedAt;
            Setup."Last Scheduled Scan Result" := Setup."Last Scheduled Scan Result"::SkippedConfiguration;
            Setup."Last Scheduled Scan Error" := 'No scan module is active.';
            Setup."Scheduled Scan Failure Count" += 1;
            Setup."Next Scheduled Scan" := CalculateNextRunFrom(Setup, StartedAt);
            Setup.Modify(true);
            exit;
        end;

        if TryStartScheduledScan(Setup, EntryNo) then begin
            Setup.Get('SETUP');
            Setup."Last Scheduled Scan" := StartedAt;
            Setup."Last Scheduled Scan Result" := Setup."Last Scheduled Scan Result"::Queued;
            Setup."Last Scheduled Scan Duration" := CurrentDateTime() - StartedAt;
            Setup."Last Scheduled Scan Error" := '';
        end else begin
            ErrorTxt := CopyStr(GetLastErrorText(), 1, MaxStrLen(Setup."Last Scheduled Scan Error"));
            Setup.Get('SETUP');
            Setup."Last Scheduled Scan" := StartedAt;
            Setup."Last Scheduled Scan Result" := Setup."Last Scheduled Scan Result"::Failed;
            Setup."Last Scheduled Scan Duration" := CurrentDateTime() - StartedAt;
            Setup."Last Scheduled Scan Error" := ErrorTxt;
            Setup."Scheduled Scan Failure Count" += 1;
        end;

        Setup."Next Scheduled Scan" := CalculateNextRunFrom(Setup, CurrentDateTime());
        Setup.Modify(true);

        if Setup."Scheduled Scans Enabled" and Setup."Monitoring Active" then
            if TryCreateSchedulerTask(Setup."Next Scheduled Scan") then;
    end;

    procedure GetActiveChecksSummary(var Setup: Record "DH Setup"): Text[100]
    var
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
    begin
        exit(StrSubstNo('%1 / %2 active', ScanCheckMgt.GetExpectedChecksCount(Setup), ScanCheckMgt.GetTotalModuleChecksCount(Setup)));
    end;

    procedure GetActiveModulesSummary(var Setup: Record "DH Setup"): Text[100]
    begin
        exit(StrSubstNo('%1 / 10 active', Setup.GetEnabledDeepScanModuleCount()));
    end;

    local procedure StartScheduledScan(var Setup: Record "DH Setup"): Integer
    var
        DeepScanMgt: Codeunit "DH Deep Scan Mgt.";
    begin
        exit(DeepScanMgt.QueueDeepScan(Setup));
    end;

    [TryFunction]
    local procedure TryStartScheduledScan(var Setup: Record "DH Setup"; var EntryNo: Integer)
    begin
        EntryNo := StartScheduledScan(Setup);
    end;

    local procedure EnsureMonitoringForScheduler(var Setup: Record "DH Setup")
    begin
        if not Setup."Monitoring Active" then
            Error('Scheduled scans require an active Monitoring subscription.');
    end;

    local procedure EnsureScanConfiguration(var Setup: Record "DH Setup")
    var
        ScanCheckMgt: Codeunit "DH Scan Check Mgt.";
    begin
        if not Setup.HasAnyModuleEnabled() then
            Error('Please enable at least one scan module on the BCSentinel setup page.');

        ScanCheckMgt.RequireEnabledChecksForMonitoring();
    end;

    local procedure CalculateNextRunFrom(var Setup: Record "DH Setup"; ReferenceDateTime: DateTime): DateTime
    var
        CandidateDate: Date;
        CandidateDateTime: DateTime;
        Counter: Integer;
    begin
        CandidateDate := DT2Date(ReferenceDateTime);

        case Setup."Schedule Frequency" of
            Setup."Schedule Frequency"::Daily:
                begin
                    CandidateDateTime := CreateDateTime(CandidateDate, Setup."Schedule Time");
                    if CandidateDateTime <= ReferenceDateTime then
                        CandidateDateTime := CreateDateTime(CandidateDate + 1, Setup."Schedule Time");
                    exit(CandidateDateTime);
                end;
            Setup."Schedule Frequency"::Weekly:
                begin
                    for Counter := 0 to 7 do begin
                        CandidateDateTime := CreateDateTime(CandidateDate + Counter, Setup."Schedule Time");
                        if (CandidateDateTime > ReferenceDateTime) and IsScheduledWeekday(Setup, CandidateDate + Counter) then
                            exit(CandidateDateTime);
                    end;
                    exit(CreateDateTime(CandidateDate + 1, Setup."Schedule Time"));
                end;
            Setup."Schedule Frequency"::Monthly:
                begin
                    CandidateDate := GetMonthlyCandidateDate(Setup, CandidateDate);
                    CandidateDateTime := CreateDateTime(CandidateDate, Setup."Schedule Time");
                    if CandidateDateTime <= ReferenceDateTime then begin
                        CandidateDate := CalcDate('<+1M>', CandidateDate);
                        CandidateDate := GetMonthlyCandidateDate(Setup, CandidateDate);
                        CandidateDateTime := CreateDateTime(CandidateDate, Setup."Schedule Time");
                    end;
                    exit(CandidateDateTime);
                end;
        end;

        exit(CreateDateTime(CandidateDate + 1, Setup."Schedule Time"));
    end;

    local procedure IsScheduledWeekday(var Setup: Record "DH Setup"; DateValue: Date): Boolean
    var
        DayNo: Integer;
    begin
        DayNo := Date2DWY(DateValue, 1);
        case DayNo of
            1:
                exit(Setup."Schedule Monday");
            2:
                exit(Setup."Schedule Tuesday");
            3:
                exit(Setup."Schedule Wednesday");
            4:
                exit(Setup."Schedule Thursday");
            5:
                exit(Setup."Schedule Friday");
            6:
                exit(Setup."Schedule Saturday");
            7:
                exit(Setup."Schedule Sunday");
        end;
        exit(false);
    end;

    local procedure GetMonthlyCandidateDate(var Setup: Record "DH Setup"; ReferenceDate: Date): Date
    var
        YearNo: Integer;
        MonthNo: Integer;
        DayNo: Integer;
        LastDayInMonth: Integer;
    begin
        YearNo := Date2DMY(ReferenceDate, 3);
        MonthNo := Date2DMY(ReferenceDate, 2);
        DayNo := Setup."Monthly Schedule Day";
        if DayNo < 1 then
            DayNo := 1;

        LastDayInMonth := Date2DMY(CalcDate('<CM>', ReferenceDate), 1);
        if DayNo > LastDayInMonth then
            DayNo := LastDayInMonth;

        exit(DMY2Date(DayNo, MonthNo, YearNo));
    end;

    [TryFunction]
    local procedure TryCreateSchedulerTask(NotBefore: DateTime)
    begin
        TaskScheduler.CreateTask(Codeunit::"DH Scheduled Scan Runner", Codeunit::"DH Scheduled Scan Runner", true, CompanyName(), NotBefore);
    end;
}
