[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$translationsPath = Join-Path $projectRoot 'Translations\BCSentinel.de-DE.xlf'

function Assert-Contract {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )

    if (-not $Condition) {
        throw "FULL-FIX-01 contract failed: $Message"
    }
}

function Assert-FindingsPage {
    param([Parameter(Mandatory = $true)][string]$Path)

    $content = Get-Content -LiteralPath $Path -Raw
    $pageName = Split-Path -Leaf $Path

    Assert-Contract -Condition ($content -match 'AccessText:\s+Text\[250\];') `
        -Message "$pageName must reserve enough capacity for the access label."
    Assert-Contract -Condition ($content -notmatch 'AccessText:\s+Text\[80\];') `
        -Message "$pageName still contains the unsafe Text[80] declaration."
    Assert-Contract -Condition ($content -match 'if AccessGuard\.HasFreshFullOrMonitoringAccess\(\) then begin') `
        -Message "$pageName must retain the existing Full/Monitoring access decision."
    Assert-Contract -Condition ($content -match 'AccessText := UnlockedLbl;') `
        -Message "$pageName must keep the unlocked access text."
    Assert-Contract -Condition ($content -match 'end else begin\s+ShowPremiumDetails := false;\s+ShowFreeSummary := true;\s+AccessText := FullAssessmentRequiredLbl;') `
        -Message "$pageName must keep the Free/locked state in the guarded else branch."

    $updateStart = $content.IndexOf('local procedure UpdateAccessState()')
    $nextTrigger = $content.IndexOf('trigger OnAfterGetCurrRecord()', $updateStart)
    Assert-Contract -Condition ($updateStart -ge 0 -and $nextTrigger -gt $updateStart) `
        -Message "$pageName has no isolated UpdateAccessState procedure."
    $updateSection = $content.Substring($updateStart, $nextTrigger - $updateStart)
    $guardIndex = $updateSection.IndexOf('if AccessGuard.HasFreshFullOrMonitoringAccess() then begin')
    $fallbackIndex = $updateSection.IndexOf('AccessText := FullAssessmentRequiredLbl;')
    Assert-Contract -Condition ($guardIndex -ge 0 -and $fallbackIndex -gt $guardIndex) `
        -Message "$pageName assigns the long fallback text before evaluating access."
}

Assert-FindingsPage -Path (Join-Path $projectRoot 'app\src\pages\DHDeepScanFindings.Page.al')
Assert-FindingsPage -Path (Join-Path $projectRoot 'app\src\pages\DHDeepScanFindingsList.Page.al')

[xml]$translations = Get-Content -LiteralPath $translationsPath -Raw
$unlockedTranslations = @(
    $translations.xliff.file.body.group.'trans-unit' |
        Where-Object { $_.source -eq 'Unlocked' -and $_.target -eq 'Freigeschaltet' }
)
Assert-Contract -Condition ($unlockedTranslations.Count -ge 2) `
    -Message 'German Unlocked translations for both Findings pages are missing.'

Write-Output 'FULL-FIX-01 Findings access-text regression contracts passed.'
