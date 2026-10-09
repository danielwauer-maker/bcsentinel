codeunit 53170 "DH Notification Mgt."
{
    Permissions =
        tabledata "DH Notification Setup" = RIM,
        tabledata "DH Notification Event" = RIM,
        tabledata "DH Notification Rule" = RIMD,
        tabledata "DH Notification Recipient" = RIMD,
        tabledata "DH Notification Template" = RIMD,
        tabledata "DH Notification Delivery" = RIM,
        tabledata "DH Notification Config Audit" = RI,
        tabledata "DH Remediation Action" = R;

    procedure EnsureSetupAndDefaults()
    begin
        EnsureSetup();
        EnsureDefaultTemplateAndRule('scan.completed', 'SCAN_COMPLETED', 'BCSentinel scan completed', 'A Business Central data-quality scan completed. %1');
        EnsureDefaultTemplateAndRule('scan.failed', 'SCAN_FAILED', 'BCSentinel scan failed', 'A Business Central data-quality scan failed. %1');
        EnsureDefaultTemplateAndRule('finding.new_critical', 'FINDING_NEW_CRITICAL', 'BCSentinel critical finding detected', 'A new critical finding was detected. %1');
        EnsureDefaultTemplateAndRule('finding.regressed', 'FINDING_REGRESSED', 'BCSentinel finding regressed', 'A previously improved finding has regressed. %1');
        EnsureDefaultTemplateAndRule('monitoring.score_deteriorated', 'SCORE_DETERIORATED', 'BCSentinel Data Health Score deteriorated', 'The monitored Data Health Score deteriorated. %1');
        EnsureDefaultTemplateAndRule('validation.completed', 'VALIDATION_COMPLETED', 'BCSentinel validation completed', 'A validation run completed. %1');
        EnsureDefaultTemplateAndRule('remediation.blocked', 'REMEDIATION_BLOCKED', 'BCSentinel remediation blocked', 'A remediation action is blocked. %1');
        EnsureDefaultTemplateAndRule('remediation.overdue', 'REMEDIATION_OVERDUE', 'BCSentinel remediation overdue', 'A remediation action is overdue. %1');
    end;

    procedure RaiseEvent(EventType: Code[50]; SourceRef: Text[150]; CorrelationKey: Text[150]; Summary: Text[250]; Severity: Code[20]; FindingKey: Code[100]; ActionId: Guid; ScanId: Code[50]; ValidationRef: Text[100]): Guid
    var
        Event: Record "DH Notification Event";
        Setup: Record "DH Notification Setup";
        EventId: Guid;
    begin
        ValidateEventType(EventType);
        EnsureSetupAndDefaults();
        Setup.Get();
        if not Setup.Enabled then
            exit(EmptyGuid());

        Event.SetRange("Tenant ID", Setup."Tenant ID");
        Event.SetRange("Company ID", Setup."Company ID");
        Event.SetRange("Event Type", EventType);
        Event.SetRange("Correlation Key", CorrelationKey);
        if Event.FindFirst() then
            exit(Event."Event ID");

        Event.Init();
        Event."Event ID" := CreateGuid();
        Event."Tenant ID" := Setup."Tenant ID";
        Event."Company ID" := Setup."Company ID";
        Event."Event Type" := EventType;
        Event."Occurred At UTC" := CurrentDateTime();
        Event."Correlation Key" := CorrelationKey;
        Event."Source Ref" := SourceRef;
        Event.Severity := Severity;
        Event."Finding Key" := FindingKey;
        Event."Action ID" := ActionId;
        Event."Scan ID" := ScanId;
        Event."Validation Ref" := ValidationRef;
        Event.Summary := Summary;
        Event."Metadata Version" := 'v1';
        Event.Insert(true);
        EventId := Event."Event ID";
        QueueEventDeliveries(Event);
        exit(EventId);
    end;

    procedure ProcessQueuedDeliveries(MaxDeliveries: Integer)
    var
        Delivery: Record "DH Notification Delivery";
        Setup: Record "DH Notification Setup";
        Processed: Integer;
    begin
        if MaxDeliveries <= 0 then
            MaxDeliveries := 50;
        EnsureSetupAndDefaults();
        CheckOverdueRemediations();
        Setup.Get();
        if not Setup.Enabled then
            exit;

        RequeueDueFailures();
        Delivery.SetRange(Status, 'queued');
        if Delivery.FindSet() then
            repeat
                ProcessDelivery(Delivery);
                Processed += 1;
            until (Delivery.Next() = 0) or (Processed >= MaxDeliveries);

        Setup."Last Processing At UTC" := CurrentDateTime();
        Setup.Modify(false);
    end;

    procedure NotifyFindingRegressed(FindingKey: Code[100]; SourceRef: Text[150]; Summary: Text[250])
    begin
        RaiseEvent('finding.regressed', SourceRef, SourceRef + '|regressed', Summary, 'critical', FindingKey, EmptyGuid(), '', '');
    end;

    procedure NotifyMonitoringScoreDeteriorated(SourceRef: Text[150]; Summary: Text[250])
    begin
        RaiseEvent('monitoring.score_deteriorated', SourceRef, SourceRef + '|score-deteriorated', Summary, 'high', '', EmptyGuid(), '', '');
    end;

    procedure NotifyValidationCompleted(ValidationRef: Text[100]; SourceRef: Text[150]; Summary: Text[250])
    begin
        RaiseEvent('validation.completed', SourceRef, SourceRef + '|validation-completed', Summary, '', '', EmptyGuid(), '', ValidationRef);
    end;

    procedure WriteConfigAudit(ObjectType: Code[30]; ObjectRef: Text[150]; ChangedField: Code[50]; PreviousValue: Text[250]; NewValue: Text[250])
    var
        Audit: Record "DH Notification Config Audit";
        CoreSetup: Record "DH Setup";
    begin
        Audit.Init();
        Audit."Object Type" := ObjectType;
        Audit."Object Ref" := ObjectRef;
        Audit."Changed Field" := ChangedField;
        Audit."Previous Value" := PreviousValue;
        Audit."New Value" := NewValue;
        Audit."Changed At UTC" := CurrentDateTime();
        Audit."Changed By" := UserSecurityId();
        if CoreSetup.Get() then
            Audit."Tenant ID" := CoreSetup."Tenant ID";
        Audit."Company ID" := CopyStr(CompanyName(), 1, MaxStrLen(Audit."Company ID"));
        Audit.Insert(false);
    end;

    local procedure EnsureSetup()
    var
        Setup: Record "DH Notification Setup";
    begin
        if Setup.Get() then
            exit;
        Setup.Init();
        Setup."Primary Key" := '';
        Setup.Enabled := true;
        Setup."Preferred Language" := 'en';
        Setup."Delivery Evidence Retention Days" := 365;
        Setup.Insert(true);
    end;

    local procedure EnsureDefaultTemplateAndRule(EventType: Code[50]; TemplateKey: Code[50]; SubjectTemplate: Text[250]; BodyTemplate: Text[2048])
    var
        Template: Record "DH Notification Template";
        Rule: Record "DH Notification Rule";
    begin
        if not Template.Get(TemplateKey, 'en') then begin
            Template.Init();
            Template."Template Key" := TemplateKey;
            Template."Event Type" := EventType;
            Template."Language Code" := 'en';
            Template."Subject Template" := SubjectTemplate;
            Template."Body Template" := BodyTemplate;
            Template."Template Version" := '1.0';
            Template.Enabled := true;
            Template.Insert(true);
        end;

        Rule.SetRange("Event Type", EventType);
        if Rule.IsEmpty() then begin
            Rule.Init();
            Rule."Rule ID" := CreateGuid();
            Rule."Event Type" := EventType;
            Rule.Enabled := true;
            Rule.Channel := 'email';
            Rule."Template Key" := TemplateKey;
            Rule.Insert(true);
        end;
    end;

    local procedure QueueEventDeliveries(Event: Record "DH Notification Event")
    var
        Rule: Record "DH Notification Rule";
        Recipient: Record "DH Notification Recipient";
        Delivery: Record "DH Notification Delivery";
    begin
        Rule.SetRange("Tenant ID", Event."Tenant ID");
        Rule.SetRange("Company ID", Event."Company ID");
        Rule.SetRange("Event Type", Event."Event Type");
        Rule.SetRange(Enabled, true);
        Rule.SetRange(Channel, 'email');
        if not Rule.FindSet() then
            exit;

        repeat
            Recipient.SetRange("Tenant ID", Event."Tenant ID");
            Recipient.SetRange("Company ID", Event."Company ID");
            Recipient.SetRange(Enabled, true);
            if Recipient.FindSet() then
                repeat
                    Delivery.Reset();
                    Delivery.SetRange("Event ID", Event."Event ID");
                    Delivery.SetRange("Rule ID", Rule."Rule ID");
                    Delivery.SetRange("Recipient ID", Recipient."Recipient ID");
                    if Delivery.IsEmpty() then begin
                        Delivery.Init();
                        Delivery."Delivery ID" := CreateGuid();
                        Delivery."Event ID" := Event."Event ID";
                        Delivery."Rule ID" := Rule."Rule ID";
                        Delivery."Recipient ID" := Recipient."Recipient ID";
                        Delivery.Channel := 'email';
                        Delivery.Status := 'queued';
                        Delivery."Attempt No." := 1;
                        Delivery.Insert(true);
                    end;
                until Recipient.Next() = 0;
        until Rule.Next() = 0;
    end;

    local procedure ProcessDelivery(var Delivery: Record "DH Notification Delivery")
    var
        Event: Record "DH Notification Event";
        Rule: Record "DH Notification Rule";
        Recipient: Record "DH Notification Recipient";
        Template: Record "DH Notification Template";
        Setup: Record "DH Notification Setup";
        LanguageCode: Code[10];
        SubjectText: Text;
        BodyText: Text;
        SafeError: Text[250];
    begin
        if Delivery.Status <> 'queued' then
            exit;
        if not Setup.Get() or not Setup.Enabled then begin
            SetDeliveryStatus(Delivery, 'suppressed', 'tenant notifications disabled');
            exit;
        end;
        if not Event.Get(Delivery."Event ID") then begin
            SetDeliveryStatus(Delivery, 'suppressed', 'event unavailable');
            exit;
        end;
        if not Rule.Get(Delivery."Rule ID") or not Rule.Enabled then begin
            SetDeliveryStatus(Delivery, 'suppressed', 'rule disabled');
            exit;
        end;
        if not Recipient.Get(Delivery."Recipient ID") or not Recipient.Enabled then begin
            SetDeliveryStatus(Delivery, 'suppressed', 'recipient disabled');
            exit;
        end;

        LanguageCode := Recipient."Language Code";
        if LanguageCode = '' then
            LanguageCode := Setup."Preferred Language";
        if LanguageCode = '' then
            LanguageCode := 'en';
        if not Template.Get(Rule."Template Key", LanguageCode) then
            if not Template.Get(Rule."Template Key", 'en') then begin
                SetDeliveryStatus(Delivery, 'suppressed', 'template unavailable');
                exit;
            end;
        if not Template.Enabled then begin
            SetDeliveryStatus(Delivery, 'suppressed', 'template disabled');
            exit;
        end;

        SetDeliveryStatus(Delivery, 'sending', '');
        SubjectText := StrSubstNo(Template."Subject Template", Event.Summary);
        BodyText := StrSubstNo(Template."Body Template", Event.Summary);
        if TrySendEmail(Recipient."Email Address", SubjectText, BodyText) then begin
            Delivery.Status := 'sent';
            Delivery."Sent At UTC" := CurrentDateTime();
            Delivery."Updated At UTC" := CurrentDateTime();
            Delivery."Error Code" := '';
            Delivery."Error Message Safe" := '';
            Delivery."Next Retry At UTC" := 0DT;
            Delivery.Modify(false);
        end else begin
            SafeError := CopyStr(GetLastErrorText(), 1, MaxStrLen(SafeError));
            Delivery.Status := 'failed';
            Delivery."Error Code" := 'email_send_failed';
            Delivery."Error Message Safe" := SafeError;
            Delivery."Next Retry At UTC" := CurrentDateTime() + (15 * 60 * 1000);
            Delivery."Updated At UTC" := CurrentDateTime();
            Delivery.Modify(false);
        end;
    end;

    local procedure SetDeliveryStatus(var Delivery: Record "DH Notification Delivery"; NewStatus: Code[20]; SuppressionReason: Text[150])
    begin
        ValidateDeliveryTransition(Delivery.Status, NewStatus);
        Delivery.Status := NewStatus;
        Delivery."Updated At UTC" := CurrentDateTime();
        if NewStatus = 'suppressed' then
            Delivery."Suppression Reason" := SuppressionReason;
        Delivery.Modify(false);
    end;

    local procedure RequeueDueFailures()
    var
        Delivery: Record "DH Notification Delivery";
    begin
        Delivery.SetRange(Status, 'failed');
        if Delivery.FindSet() then
            repeat
                if (Delivery."Next Retry At UTC" <> 0DT) and (Delivery."Next Retry At UTC" <= CurrentDateTime()) then begin
                    ValidateDeliveryTransition('failed', 'queued');
                    Delivery.Status := 'queued';
                    Delivery."Attempt No." += 1;
                    Delivery."Updated At UTC" := CurrentDateTime();
                    Delivery.Modify(false);
                end;
            until Delivery.Next() = 0;
    end;

    local procedure CheckOverdueRemediations()
    var
        Action: Record "DH Remediation Action";
    begin
        Action.SetFilter("Due At UTC", '<>%1&<%2', 0DT, CurrentDateTime());
        if Action.FindSet() then
            repeat
                if (Action.Status <> Action.Status::Completed) and (Action.Status <> Action.Status::Cancelled) then
                    RaiseEvent('remediation.overdue', Format(Action."Action ID"), Format(Action."Action ID") + '|overdue', CopyStr(Action.Title, 1, 250), Format(Action.Priority), Action."Finding Key", Action."Action ID", '', '');
            until Action.Next() = 0;
    end;

    local procedure ValidateEventType(EventType: Code[50])
    begin
        case EventType of
            'scan.completed',
            'scan.failed',
            'finding.new_critical',
            'finding.regressed',
            'monitoring.score_deteriorated',
            'validation.completed',
            'remediation.blocked',
            'remediation.overdue':
                exit;
        end;
        Error('Unsupported BCSentinel notification event type: %1', EventType);
    end;

    local procedure ValidateDeliveryTransition(OldStatus: Code[20]; NewStatus: Code[20])
    begin
        if OldStatus = NewStatus then
            exit;
        case OldStatus of
            'queued':
                if NewStatus in ['sending', 'suppressed'] then exit;
            'sending':
                if NewStatus in ['sent', 'failed'] then exit;
            'failed':
                if NewStatus = 'queued' then exit;
        end;
        Error('Invalid notification delivery transition from %1 to %2.', OldStatus, NewStatus);
    end;

    [TryFunction]
    local procedure TrySendEmail(RecipientAddress: Text; SubjectText: Text; BodyText: Text)
    var
        Email: Codeunit Email;
        EmailMessage: Codeunit "Email Message";
    begin
        EmailMessage.Create(RecipientAddress, SubjectText, BodyText, false);
        if not Email.Send(EmailMessage, Enum::"Email Scenario"::Default) then
            Error('Email provider rejected the message.');
    end;

    local procedure EmptyGuid(): Guid
    var
        Empty: Guid;
    begin
        exit(Empty);
    end;

    [EventSubscriber(ObjectType::Table, Database::"DH Deep Scan Run", 'OnAfterModifyEvent', '', false, false)]
    local procedure OnDeepScanRunModified(var Rec: Record "DH Deep Scan Run"; RunTrigger: Boolean)
    begin
        case Rec.Status of
            Rec.Status::Completed:
                RaiseEvent('scan.completed', Rec."Run ID", Rec."Run ID" + '|completed', CopyStr(Rec.Headline, 1, 250), '', '', EmptyGuid(), Rec."Run ID", '');
            Rec.Status::Failed:
                RaiseEvent('scan.failed', Rec."Run ID", Rec."Run ID" + '|failed', 'Scan failed. Review the protected scan details in Business Central.', '', '', EmptyGuid(), Rec."Run ID", '');
        end;
    end;

    [EventSubscriber(ObjectType::Table, Database::"DH Deep Scan Finding", 'OnAfterInsertEvent', '', false, false)]
    local procedure OnDeepScanFindingInserted(var Rec: Record "DH Deep Scan Finding"; RunTrigger: Boolean)
    var
        SourceRef: Text[150];
    begin
        if LowerCase(Rec.Severity) <> 'critical' then
            exit;
        SourceRef := CopyStr(StrSubstNo('%1|%2', Rec."Deep Scan Entry No.", Rec."Issue Code"), 1, MaxStrLen(SourceRef));
        RaiseEvent('finding.new_critical', SourceRef, SourceRef + '|new-critical', CopyStr(Rec.Title, 1, 250), Rec.Severity, Rec."Issue Code", EmptyGuid(), '', '');
    end;

    [EventSubscriber(ObjectType::Table, Database::"DH Remediation Action", 'OnAfterModifyEvent', '', false, false)]
    local procedure OnRemediationActionModified(var Rec: Record "DH Remediation Action"; RunTrigger: Boolean)
    begin
        if Rec.Status = Rec.Status::Blocked then
            RaiseEvent('remediation.blocked', Format(Rec."Action ID"), Format(Rec."Action ID") + '|blocked', CopyStr(Rec."Blocked Reason", 1, 250), Format(Rec.Priority), Rec."Finding Key", Rec."Action ID", '', '');
    end;
}
