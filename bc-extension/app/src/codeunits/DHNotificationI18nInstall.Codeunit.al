codeunit 53302 "DH Notification I18n Install"
{
    Subtype = Install;

    trigger OnInstallAppPerCompany()
    var
        NotificationI18nMgt: Codeunit "DH Notification I18n Mgt.";
    begin
        NotificationI18nMgt.EnsureGermanDefaults();
    end;
}
