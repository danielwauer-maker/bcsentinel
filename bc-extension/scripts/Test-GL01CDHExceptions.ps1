$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$exceptionMgt = Get-Content -Raw (Join-Path $root 'app/src/codeunits/DHExceptionMgt.Codeunit.al')
$runner = Get-Content -Raw (Join-Path $root 'app/src/codeunits/DHDeepScanRunner.Codeunit.al')
$page = Get-Content -Raw (Join-Path $root 'app/src/pages/DHIssueExceptions.Page.al')
$permissions = Get-Content -Raw (Join-Path $root 'app/src/permissionsets/BCSentinelPermissionSets.al')

$contracts = @(
    @{ Name = 'Reason required'; Actual = $exceptionMgt; Pattern = "ReasonRequiredErr" },
    @{ Name = 'Active duplicate rejected'; Actual = $exceptionMgt; Pattern = "ExceptionAlreadyActiveErr" },
    @{ Name = 'Reactivation audited'; Actual = $exceptionMgt; Pattern = "ReactivateExceptionEntry" },
    @{ Name = 'Applied count payload'; Actual = $runner; Pattern = "Payload.Add('applied_exception_count'" },
    @{ Name = 'No page delete'; Actual = $page; Pattern = 'DeleteAllowed = false' },
    @{ Name = 'Viewer page access'; Actual = $permissions; Pattern = 'page "DH Issue Exceptions" = X' },
    @{ Name = 'Operator RIM'; Actual = $permissions; Pattern = 'tabledata "DH Issue Exception" = RIM' }
)

foreach ($contract in $contracts) {
    if ($contract.Actual -notmatch [regex]::Escape($contract.Pattern)) {
        throw "GL-01C contract failed: $($contract.Name)"
    }
}

Write-Host "GL-01C DH Exceptions source contracts passed: $($contracts.Count)"
