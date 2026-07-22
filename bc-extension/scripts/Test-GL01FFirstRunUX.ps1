$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$sourceRoot = Join-Path $projectRoot 'app\src'

function Require-Text {
    param(
        [Parameter(Mandatory = $true)][string] $Content,
        [Parameter(Mandatory = $true)][string] $Expected,
        [Parameter(Mandatory = $true)][string] $FailureMessage
    )

    if (-not $Content.Contains($Expected)) {
        throw $FailureMessage
    }
}

function Get-Section {
    param(
        [Parameter(Mandatory = $true)][string] $Content,
        [Parameter(Mandatory = $true)][string] $StartText,
        [Parameter(Mandatory = $true)][string] $EndText
    )

    $startIndex = $Content.IndexOf($StartText, [StringComparison]::Ordinal)
    if ($startIndex -lt 0) { throw "Section start not found: $StartText" }
    $endIndex = $Content.IndexOf($EndText, $startIndex + $StartText.Length, [StringComparison]::Ordinal)
    if ($endIndex -lt 0) { throw "Section end not found: $EndText" }
    return $Content.Substring($startIndex, $endIndex - $startIndex)
}

$setupTable = Get-Content -Raw (Join-Path $sourceRoot 'tables\DHSetup.Table.al')
$setupPage = Get-Content -Raw (Join-Path $sourceRoot 'pages\DHSetup.Page.al')
$scheduler = Get-Content -Raw (Join-Path $sourceRoot 'codeunits\DHScanSchedulerMgt.Codeunit.al')
$deepScanMgt = Get-Content -Raw (Join-Path $sourceRoot 'codeunits\DHDeepScanMgt.Codeunit.al')

Require-Text $setupTable 'procedure IsRegistrationReady(): Boolean' 'Central registration readiness is missing.'
Require-Text $setupTable 'not Registered and' 'Registration readiness does not exclude registered tenants.'
Require-Text $setupTable 'HasValidContactEmail() and' 'Registration readiness does not reuse the existing email validation.'
Require-Text $setupTable '"Data Processing Consent" and' 'Registration readiness does not require the existing consent field.'

foreach ($requiredText in @(
    "Caption = 'Prepare registration';",
    "RegistrationRequirementsPendingLbl: Label 'The following information is required before registration:';",
    "RegistrationRequirementsCompletedLbl: Label 'All registration requirements have been completed. You can now register BCSentinel.';",
    "EnterContactEmailAddressLbl: Label 'Enter a contact email address';",
    "ContactEmailAddressInvalidLbl: Label 'The contact email address is invalid.';",
    "AcceptPrivacyConsentLbl: Label 'Accept the privacy consent';"
)) {
    Require-Text $setupPage $requiredText "Registration guidance contract is missing: $requiredText"
}

Require-Text $setupPage 'CanRegisterTenant := Rec.IsRegistrationReady();' 'Register Enabled does not use the central readiness method.'
Require-Text $setupPage 'ShowRegisterTenant := not Rec.Registered;' 'Register visibility is not tied to registration state.'
Require-Text $setupPage 'ShowOpenLatestFindings := Rec.Registered;' 'Findings visibility is not restored only after registration.'
Require-Text $setupPage 'RunTenantRegistration();' 'The Register action does not use the central page procedure.'
Require-Text $setupPage 'RegistrationMessage := ApiClient.RegisterTenant(Rec);' 'The existing registration API path was changed or removed.'

$contactField = Get-Section $setupPage 'field("Contact Email"; Rec."Contact Email")' 'field("Tenant ID"; Rec."Tenant ID")'
$consentField = Get-Section $setupPage 'field("Data Processing Consent"; Rec."Data Processing Consent")' 'field(DataProcessingNotice;'
Require-Text $contactField 'CurrPage.Update(false);' 'Contact email changes do not refresh the page state.'
Require-Text $consentField 'CurrPage.Update(false);' 'Consent changes do not refresh the page state.'

$runNowAction = Get-Section $setupPage 'action(RunScheduledScanNow)' 'group(AdministrativeActions)'
Require-Text $runNowAction 'EntryNo := SchedulerMgt.RunNow(Rec);' 'Run Now no longer uses the scheduler manager.'
Require-Text $runNowAction 'Message(DataHealthScanStartedMsg);' 'Run Now success message is missing.'
if ($runNowAction.Contains('Confirm(')) { throw 'Run Now must remain dialog-free.' }
if ($runNowAction.Contains('Page.Run(') -or $runNowAction.Contains('RunModal(')) { throw 'Run Now still blocks on a page call.' }

$manualRun = Get-Section $scheduler 'procedure RunNow' 'procedure ExecuteScheduledRun'
Require-Text $manualRun 'exit(StartManualScheduledScan(Setup));' 'Manual Run Now is not separated from automatic scheduling.'
Require-Text $scheduler 'exit(DeepScanMgt.QueueDeepScanInBackground(Setup));' 'The automatic scheduler execution path changed.'
Require-Text $scheduler 'exit(DeepScanMgt.QueueDeepScanInNewSession(Setup));' 'Manual Run Now does not use the new session path.'
Require-Text $deepScanMgt 'Session.StartSession(SessionId, Codeunit::"DH Deep Scan Runner", CompanyName(), DeepScanRun)' 'The existing Deep Scan Runner is not started in a background session.'
Require-Text $deepScanMgt 'Enum::"DH Scan Trigger Context"::Scheduled, false, true' 'The manual scheduled start must remain dialog-free.'

[xml] $germanTranslation = Get-Content -Raw (Join-Path $projectRoot 'Translations\BCSentinel.de-DE.xlf')
$translationUnits = @($germanTranslation.xliff.file.body.group.'trans-unit')
$requiredTranslationIds = @(
    'Codeunit 950078217 - NamedType 90913039',
    'Page 392523509 - NamedType 1057253054',
    'Page 392523509 - NamedType 2203164331',
    'Page 392523509 - NamedType 3338555729',
    'Page 392523509 - NamedType 2459285653',
    'Page 392523509 - NamedType 1252211916',
    'Page 392523509 - NamedType 4263455781',
    'Page 392523509 - NamedType 2669963486',
    'Page 392523509 - NamedType 712347612',
    'Page 392523509 - Control 1702379372 - Property 2879900210'
)
foreach ($translationId in $requiredTranslationIds) {
    $unit = $translationUnits | Where-Object { $_.id -eq $translationId } | Select-Object -First 1
    if ($null -eq $unit -or [string]::IsNullOrWhiteSpace([string] $unit.target.InnerText)) {
        throw "German translation is missing or empty: $translationId"
    }
}

Write-Output 'GL-01F AL source contract checks passed.'
