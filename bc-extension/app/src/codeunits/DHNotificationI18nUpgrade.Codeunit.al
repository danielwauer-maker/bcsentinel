codeunit 53199 "DH Notification I18n Upgrade"
{
    Subtype = Upgrade;

    trigger OnUpgradePerCompany()
    var
        NotificationI18nMgt: Codeunit "DH Notification I18n Mgt.";
    begin
        NotificationI18nMgt.EnsureGermanDefaults();
    end;
}
