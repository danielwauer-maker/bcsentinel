from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "bc-extension" / "app" / "src"


def text(relative: str) -> str:
    path = BASE / relative
    assert path.exists(), f"Missing notification artifact: {relative}"
    return path.read_text(encoding="utf-8-sig")


def require(haystack: str, *needles: str) -> None:
    for needle in needles:
        assert needle in haystack, f"Missing required notification contract fragment: {needle}"


def main() -> None:
    setup = text("tables/DHNotificationSetup.Table.al")
    event = text("tables/DHNotificationEvent.Table.al")
    rule = text("tables/DHNotificationRule.Table.al")
    recipient = text("tables/DHNotificationRecipient.Table.al")
    template = text("tables/DHNotificationTemplate.Table.al")
    delivery = text("tables/DHNotificationDelivery.Table.al")
    audit = text("tables/DHNotificationConfigAudit.Table.al")
    mgt = text("codeunits/DHNotificationMgt.Codeunit.al")
    i18n = text("codeunits/DHNotificationI18nMgt.Codeunit.al")
    i18n_install = text("codeunits/DHNotificationI18nInstall.Codeunit.al")
    i18n_upgrade = text("codeunits/DHNotificationI18nUpgrade.Codeunit.al")
    setup_page = text("pages/DHNotificationSetup.Page.al")
    delivery_page = text("pages/DHNotificationDeliveries.Page.al")
    events_page = text("pages/DHNotificationEvents.Page.al")
    permissions = text("permissionsets/BCSentinelPermissionSets.al")

    require(setup, '"Tenant ID"', '"Company ID"', 'Enabled', '"Preferred Language"',
            '"Delivery Evidence Retention Days"', 'CoreSetup."Tenant ID"', 'CompanyName()')

    for field in [
        '"Event ID"', '"Tenant ID"', '"Company ID"', '"Event Type"', '"Occurred At UTC"',
        '"Correlation Key"', '"Source Ref"', 'Severity', '"Finding Key"', '"Action ID"',
        '"Scan ID"', '"Validation Ref"', 'Summary', '"Metadata Version"'
    ]:
        assert field in event, f"Missing notification event field: {field}"
    require(event, 'Notification events are immutable', 'retained as delivery evidence')

    require(rule, '"Rule ID"', '"Event Type"', 'Enabled', 'Channel', '"Template Key"',
            '"Minimum Severity"', '"Module Scope"', '"Business Area"', '"Quiet Hours Policy"', '"Digest Policy"')
    require(recipient, '"Recipient ID"', '"Display Name"', '"Email Address"', 'Enabled',
            '"Principal ID"', '"Language Code"', '"Recipient Role"', 'WriteConfigAudit')
    require(template, '"Template Key"', '"Event Type"', '"Language Code"', '"Subject Template"',
            '"Body Template"', '"Template Version"', 'Enabled')

    for field in [
        '"Delivery ID"', '"Event ID"', '"Rule ID"', '"Recipient ID"', 'Channel', 'Status',
        '"Attempt No."', '"Created At UTC"', '"Updated At UTC"', '"Sent At UTC"',
        '"Provider Message ID"', '"Error Code"', '"Error Message Safe"', '"Next Retry At UTC"',
        '"Suppression Reason"'
    ]:
        assert field in delivery, f"Missing delivery field: {field}"
    require(delivery, 'delivery evidence is retained', 'cannot be deleted')

    require(audit, '"Object Type"', '"Object Ref"', '"Changed At UTC"', '"Changed By"',
            '"Tenant ID"', '"Company ID"', 'immutable')

    canonical_events = [
        'scan.completed', 'scan.failed', 'finding.new_critical', 'finding.regressed',
        'monitoring.score_deteriorated', 'validation.completed', 'remediation.blocked', 'remediation.overdue'
    ]
    for event_type in canonical_events:
        assert event_type in mgt, f"Missing canonical event type: {event_type}"
        assert event_type in i18n, f"Missing German default for event type: {event_type}"

    require(mgt,
            'EnsureSetupAndDefaults', 'RaiseEvent', 'QueueEventDeliveries', 'ProcessQueuedDeliveries',
            'RequeueDueFailures', 'ValidateDeliveryTransition', 'TrySendEmail', 'Codeunit Email',
            'Codeunit "Email Message"', 'Enum::"Email Scenario"::Default',
            "'queued'", "'sending'", "'sent'", "'failed'", "'suppressed'",
            'Recipient."Language Code"', 'Setup."Preferred Language"', "Template.Get(Rule.\"Template Key\", 'en')")

    require(i18n,
            'EnsureGermanDefaults', "Template.Get(TemplateKey, 'de')", "Template.\"Language Code\" := 'de'",
            'Never overwrite customer-edited templates',
            'BCSentinel-Scan abgeschlossen', 'BCSentinel-Maßnahme überfällig')
    require(i18n_install, 'Subtype = Install', 'OnInstallAppPerCompany', 'EnsureGermanDefaults')
    require(i18n_upgrade, 'Subtype = Upgrade', 'OnUpgradePerCompany', 'EnsureGermanDefaults')

    raise_section = mgt.split('procedure RaiseEvent', 1)[1].split('procedure ProcessQueuedDeliveries', 1)[0]
    assert "Status := 'sent'" not in raise_section
    assert 'QueueEventDeliveries(Event)' in raise_section

    require(mgt, "Delivery.Status := 'queued'", 'Delivery."Attempt No." += 1')
    assert 'retry_creates_new_event' not in mgt.lower()

    require(mgt,
            'OnDeepScanRunModified', 'OnDeepScanFindingInserted', 'OnRemediationActionModified',
            'NotifyFindingRegressed', 'NotifyMonitoringScoreDeteriorated', 'NotifyValidationCompleted')

    lowered = mgt.lower()
    for forbidden in ['api token', 'password reset', 'stripe secret', 'client secret']:
        assert forbidden not in lowered, f"Forbidden sensitive/service-email concept in notification engine: {forbidden}"

    require(setup_page, 'PageType = Card', 'Recipients', 'Event Rules', 'Templates', 'Event Log', 'Delivery Log')
    require(delivery_page, 'Editable = false', 'InsertAllowed = false', 'ModifyAllowed = false', 'DeleteAllowed = false')
    require(events_page, 'Editable = false', 'InsertAllowed = false', 'ModifyAllowed = false', 'DeleteAllowed = false')

    require(permissions,
            'tabledata "DH Notification Setup" = R,',
            'tabledata "DH Notification Setup" = RIM,',
            'tabledata "DH Notification Recipient" = RIMD,',
            'tabledata "DH Notification Rule" = RIMD,',
            'tabledata "DH Notification Template" = RIMD,',
            'tabledata "DH Notification Delivery" = R,',
            'page "DH Notification Setup" = X',
            'page "DH Notification Recipients" = X',
            'page "DH Notification Rules" = X',
            'page "DH Notification Templates" = X',
            'page "DH Notification Events" = X',
            'page "DH Notification Deliveries" = X',
            'codeunit "DH Notification Mgt." = X')

    print("BC notification implementation contract: PASS")


if __name__ == "__main__":
    main()
