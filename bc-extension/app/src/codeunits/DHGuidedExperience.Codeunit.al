codeunit 53180 "DH Guided Experience"
{
    [EventSubscriber(ObjectType::Codeunit, Codeunit::"Guided Experience", 'OnRegisterAssistedSetup', '', true, true)]
    local procedure OnRegisterAssistedSetup()
    var
        AssistedSetup: Codeunit "Guided Experience";
        GuidedExperienceType: Enum "Guided Experience Type";
        AssistedSetupGroup: Enum "Assisted Setup Group";
        VideoCategory: Enum "Video Category";
    begin
        if AssistedSetup.Exists(GuidedExperienceType::"Assisted Setup", ObjectType::Page, Page::"DH Setup") then
            exit;

        AssistedSetup.InsertAssistedSetup(
            'Set up BCSentinel',
            'Set up BCSentinel',
            'Connect BCSentinel, review data processing consent, register the tenant, and prepare scan access.',
            5,
            ObjectType::Page,
            Page::"DH Setup",
            AssistedSetupGroup::BCSentinel,
            '',
            VideoCategory::Uncategorized,
            'https://bcsentinel.com');
    end;
}
