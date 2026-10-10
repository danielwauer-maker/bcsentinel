codeunit 53197 "DH Notification I18n Mgt."
{
    procedure EnsureGermanDefaults()
    begin
        EnsureGermanTemplate('SCAN_COMPLETED', 'scan.completed', 'BCSentinel-Scan abgeschlossen', 'Ein Business-Central-Datenqualitäts-Scan wurde abgeschlossen. %1');
        EnsureGermanTemplate('SCAN_FAILED', 'scan.failed', 'BCSentinel-Scan fehlgeschlagen', 'Ein Business-Central-Datenqualitäts-Scan ist fehlgeschlagen. %1');
        EnsureGermanTemplate('FINDING_NEW_CRITICAL', 'finding.new_critical', 'BCSentinel: Kritisches Finding erkannt', 'Ein neues kritisches Finding wurde erkannt. %1');
        EnsureGermanTemplate('FINDING_REGRESSED', 'finding.regressed', 'BCSentinel: Finding hat sich verschlechtert', 'Ein zuvor verbessertes Finding hat sich wieder verschlechtert. %1');
        EnsureGermanTemplate('SCORE_DETERIORATED', 'monitoring.score_deteriorated', 'BCSentinel: Data Health Score verschlechtert', 'Der überwachte Data Health Score hat sich verschlechtert. %1');
        EnsureGermanTemplate('VALIDATION_COMPLETED', 'validation.completed', 'BCSentinel-Validierung abgeschlossen', 'Eine Validierung wurde abgeschlossen. %1');
        EnsureGermanTemplate('REMEDIATION_BLOCKED', 'remediation.blocked', 'BCSentinel-Maßnahme blockiert', 'Eine BCSentinel-Maßnahme ist blockiert. %1');
        EnsureGermanTemplate('REMEDIATION_OVERDUE', 'remediation.overdue', 'BCSentinel-Maßnahme überfällig', 'Eine BCSentinel-Maßnahme ist überfällig. %1');
    end;

    local procedure EnsureGermanTemplate(TemplateKey: Code[50]; EventType: Code[50]; SubjectTemplate: Text[250]; BodyTemplate: Text[2048])
    var
        Template: Record "DH Notification Template";
    begin
        // Never overwrite customer-edited templates. Defaults are inserted only
        // when the exact template/language record does not yet exist.
        if Template.Get(TemplateKey, 'de') then
            exit;

        Template.Init();
        Template."Template Key" := TemplateKey;
        Template."Event Type" := EventType;
        Template."Language Code" := 'de';
        Template."Subject Template" := SubjectTemplate;
        Template."Body Template" := BodyTemplate;
        Template."Template Version" := '1.0';
        Template.Enabled := true;
        Template.Insert(true);
    end;
}
