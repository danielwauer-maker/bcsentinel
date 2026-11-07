codeunit 53194 "DH Remediation Mgt."
{
    procedure ValidateStatusTransition(OldStatus: Enum "DH Remediation Status"; NewStatus: Enum "DH Remediation Status")
    begin
        if OldStatus = NewStatus then
            exit;

        case OldStatus of
            OldStatus::Open:
                if not (NewStatus in [NewStatus::InProgress, NewStatus::Blocked, NewStatus::Cancelled]) then
                    InvalidTransition(OldStatus, NewStatus);
            OldStatus::InProgress:
                if not (NewStatus in [NewStatus::Blocked, NewStatus::Completed, NewStatus::Cancelled]) then
                    InvalidTransition(OldStatus, NewStatus);
            OldStatus::Blocked:
                if not (NewStatus in [NewStatus::InProgress, NewStatus::Cancelled]) then
                    InvalidTransition(OldStatus, NewStatus);
            OldStatus::Completed:
                if NewStatus <> NewStatus::InProgress then
                    InvalidTransition(OldStatus, NewStatus);
            OldStatus::Cancelled:
                if NewStatus <> NewStatus::Open then
                    InvalidTransition(OldStatus, NewStatus);
        end;
    end;

    procedure WriteAudit(RemediationAction: Record "DH Remediation Action"; ChangeName: Text[50]; PreviousValue: Text; NewValue: Text)
    var
        Audit: Record "DH Remediation Audit";
    begin
        if IsNullGuid(RemediationAction."Action ID") then
            exit;

        Audit.Init();
        Audit."Action ID" := RemediationAction."Action ID";
        Audit."Changed At UTC" := CurrentDateTime();
        Audit."Changed By Principal ID" := UserSecurityId();
        Audit."Tenant ID" := RemediationAction."Tenant ID";
        Audit."Company ID" := RemediationAction."Company ID";
        Audit."Changed Field or Status" := ChangeName;
        Audit."Previous Value" := CopyStr(PreviousValue, 1, MaxStrLen(Audit."Previous Value"));
        Audit."New Value" := CopyStr(NewValue, 1, MaxStrLen(Audit."New Value"));
        Audit.Insert(true);
    end;

    procedure SeedFromDashboardIssue(var RemediationAction: Record "DH Remediation Action"; DashboardIssue: Record "DH Dashboard Issue")
    begin
        RemediationAction.Init();
        RemediationAction."Finding Key" := CopyStr(DashboardIssue."Issue Code", 1, MaxStrLen(RemediationAction."Finding Key"));
        RemediationAction.Title := DashboardIssue.Title;
        RemediationAction.Description := DashboardIssue."Recommendation Preview";
        RemediationAction."Recommendation Ref" := CopyStr(StrSubstNo('dashboard-issue:%1', DashboardIssue."Entry No."), 1, MaxStrLen(RemediationAction."Recommendation Ref"));
        RemediationAction.Source := RemediationAction.Source::Recommendation;
        RemediationAction.Priority := MapSeverityToPriority(DashboardIssue.Severity);
        RemediationAction.Insert(true);
    end;

    procedure LinkValidationResult(var RemediationAction: Record "DH Remediation Action"; ValidationResultRef: Text[100])
    var
        PreviousValue: Text[100];
    begin
        PreviousValue := RemediationAction."Validation Result Ref";
        RemediationAction."Validation Result Ref" := ValidationResultRef;
        RemediationAction.Modify(true);
        WriteAudit(RemediationAction, 'validation_result_ref', PreviousValue, ValidationResultRef);
    end;

    local procedure MapSeverityToPriority(Severity: Code[20]): Enum "DH Remediation Priority"
    var
        Priority: Enum "DH Remediation Priority";
    begin
        case LowerCase(Severity) of
            'critical': exit(Priority::Critical);
            'high': exit(Priority::High);
            'low': exit(Priority::Low);
        end;
        exit(Priority::Medium);
    end;

    local procedure InvalidTransition(OldStatus: Enum "DH Remediation Status"; NewStatus: Enum "DH Remediation Status")
    begin
        Error('Remediation status transition from %1 to %2 is not allowed.', Format(OldStatus), Format(NewStatus));
    end;
}
