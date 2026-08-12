codeunit 53201 "DH Generic Remediation"
{
    procedure PromptExclude(TableId: Integer; RecordSystemId: Guid; RecordNoText: Text; RecordCaptionText: Text)
    var
        ExceptionDialog: Page "DH Exception Dialog";
        IssueException: Record "DH Issue Exception";
        ConfirmedIssueCode: Code[50];
        Reason: Text[250];
        IssueCode: Code[50];
    begin
        IssueCode := GetIssueCode();
        ExceptionDialog.SetContext(CopyStr(RecordNoText, 1, 20), CopyStr(RecordCaptionText, 1, 100), IssueCode, '');
        if ExceptionDialog.RunModal() <> Action::OK then
            exit;

        ExceptionDialog.GetValues(ConfirmedIssueCode, Reason);
        if ConfirmedIssueCode = '' then
            ConfirmedIssueCode := IssueCode;

        Reason := CopyStr(Reason.Trim(), 1, MaxStrLen(IssueException.Reason));
        if Reason = '' then
            Error(ReasonRequiredErr);

        IssueException.Reset();
        IssueException.SetRange("Table ID", TableId);
        IssueException.SetRange("Record SystemId", RecordSystemId);
        IssueException.SetRange("Issue Code", ConfirmedIssueCode);
        IssueException.SetRange(Active, true);
        if IssueException.FindFirst() then
            Error(ExceptionAlreadyActiveErr, RecordNoText, ConfirmedIssueCode);

        IssueException.SetRange(Active, false);
        if IssueException.FindFirst() then begin
            IssueException.Active := true;
            IssueException.Reason := Reason;
            IssueException."Deactivated By User" := '';
            IssueException."Deactivated At" := 0DT;
            IssueException.Modify(true);
        end else begin
            IssueException.Init();
            IssueException."Table ID" := TableId;
            IssueException."Record SystemId" := RecordSystemId;
            IssueException."Record No." := CopyStr(RecordNoText, 1, MaxStrLen(IssueException."Record No."));
            IssueException."Record Caption" := CopyStr(RecordCaptionText, 1, MaxStrLen(IssueException."Record Caption"));
            IssueException."Issue Code" := ConfirmedIssueCode;
            IssueException.Reason := Reason;
            IssueException.Active := true;
            IssueException.Insert(true);
        end;

        InsertAction(TableId, RecordSystemId, RecordNoText, RecordCaptionText, ConfirmedIssueCode, 'EXCLUDED', Reason);
    end;

    procedure MarkCorrected(TableId: Integer; RecordSystemId: Guid; RecordNoText: Text; RecordCaptionText: Text)
    var
        IssueCode: Code[50];
    begin
        IssueCode := GetIssueCode();
        if IsCorrectionActive(TableId, RecordSystemId, IssueCode) then begin
            Message(AlreadyCorrectedMsg);
            exit;
        end;

        if not Confirm(MarkCorrectedQst, false, RecordNoText, IssueCode) then
            exit;

        InsertAction(TableId, RecordSystemId, RecordNoText, RecordCaptionText, IssueCode, 'CORRECTED', CorrectionCommentLbl);
        Message(CorrectionRecordedMsg);
    end;

    procedure ReopenCorrection(var ActionLog: Record "DH Issue Action Log")
    begin
        if not IsCorrectionActive(ActionLog."Table ID", ActionLog."Record SystemId", ActionLog."Issue Code") then
            Error(CorrectionAlreadyOpenErr);

        if not Confirm(ReopenCorrectionQst, false, ActionLog."Record No.", ActionLog."Issue Code") then
            exit;

        InsertAction(ActionLog."Table ID", ActionLog."Record SystemId", ActionLog."Record No.", ActionLog."Record Caption", ActionLog."Issue Code", 'REOPENED', ReopenCommentLbl);
    end;

    procedure IsCorrectionActive(TableId: Integer; RecordSystemId: Guid; IssueCode: Code[50]): Boolean
    var
        ActionLog: Record "DH Issue Action Log";
    begin
        ActionLog.SetCurrentKey("Table ID", "Record SystemId", "Action At");
        ActionLog.SetRange("Table ID", TableId);
        ActionLog.SetRange("Record SystemId", RecordSystemId);
        ActionLog.SetRange("Issue Code", IssueCode);
        ActionLog.SetFilter("Action Type", '%1|%2', 'CORRECTED', 'REOPENED');
        ActionLog.Ascending(false);
        if not ActionLog.FindFirst() then
            exit(false);

        exit(ActionLog."Action Type" = 'CORRECTED');
    end;

    procedure OpenHistory(TableId: Integer; RecordSystemId: Guid; IssueCode: Code[50])
    var
        ActionLog: Record "DH Issue Action Log";
    begin
        ActionLog.SetRange("Table ID", TableId);
        ActionLog.SetRange("Record SystemId", RecordSystemId);
        if IssueCode <> '' then
            ActionLog.SetRange("Issue Code", IssueCode);
        Page.Run(Page::"DH Issue Action Log", ActionLog);
    end;

    local procedure GetIssueCode(): Code[50]
    var
        Context: Codeunit "DH Remediation Context";
        IssueCode: Code[50];
    begin
        IssueCode := Context.GetIssueCode();
        if IssueCode = '' then
            Error(IssueContextMissingErr);
        exit(IssueCode);
    end;

    local procedure InsertAction(TableId: Integer; RecordSystemId: Guid; RecordNoText: Text; RecordCaptionText: Text; IssueCode: Code[50]; ActionType: Code[20]; CommentText: Text)
    var
        ActionLog: Record "DH Issue Action Log";
    begin
        ActionLog.Init();
        ActionLog."Table ID" := TableId;
        ActionLog."Record SystemId" := RecordSystemId;
        ActionLog."Record No." := CopyStr(RecordNoText, 1, MaxStrLen(ActionLog."Record No."));
        ActionLog."Record Caption" := CopyStr(RecordCaptionText, 1, MaxStrLen(ActionLog."Record Caption"));
        ActionLog."Issue Code" := IssueCode;
        ActionLog."Action Type" := ActionType;
        ActionLog.Comment := CopyStr(CommentText, 1, MaxStrLen(ActionLog.Comment));
        ActionLog.Insert(true);
    end;

    var
        ReasonRequiredErr: Label 'A reason is required for a DH exception.';
        ExceptionAlreadyActiveErr: Label 'An active DH exception already exists for record %1 and issue %2.', Comment = '%1 = record number, %2 = issue code';
        IssueContextMissingErr: Label 'No BCSentinel finding context is available. Open the record from the BCSentinel Findings page and try again.';
        MarkCorrectedQst: Label 'Mark record %1 as corrected for finding %2? This documents the correction only; future scans still evaluate the actual Business Central data.', Comment = '%1 = record number, %2 = issue code';
        ReopenCorrectionQst: Label 'Reopen correction status for record %1 and finding %2?', Comment = '%1 = record number, %2 = issue code';
        AlreadyCorrectedMsg: Label 'This record is already documented as corrected for the current finding.';
        CorrectionRecordedMsg: Label 'Correction status recorded. Future scans will still re-evaluate the actual Business Central data.';
        CorrectionAlreadyOpenErr: Label 'This correction is already reopened or no longer active.';
        CorrectionCommentLbl: Label 'Record manually documented as corrected. This status does not exclude the record from future scans.';
        ReopenCommentLbl: Label 'Correction status reopened. The finding remains subject to normal scan evaluation.';
}
