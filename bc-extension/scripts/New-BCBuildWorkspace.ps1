[CmdletBinding()]
param(
    [ValidateSet("DevCloud", "ReleaseCloud", "OnPremBc19")]
    [string]$Profile = "ReleaseCloud",

    [string]$OutputPath,

    [switch]$ReuseSymbolCache
)

$repoRoot = Split-Path -Parent $PSScriptRoot

$manifestByProfile = @{
    DevCloud = "app.cloud.json"
    ReleaseCloud = "app.json"
    OnPremBc19 = "app.onprem.bc19.json"
}

$manifestName = $manifestByProfile[$Profile]
$manifestPath = Join-Path $repoRoot $manifestName

if (-not (Test-Path -LiteralPath $manifestPath)) {
    throw "Manifest not found: $manifestPath"
}

if (-not $OutputPath) {
    $OutputPath = Join-Path $repoRoot ".build\$Profile"
}

$outputRoot = [System.IO.Path]::GetFullPath($OutputPath)
$repoRootFull = [System.IO.Path]::GetFullPath($repoRoot)

New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null

foreach ($path in @("app", ".alpackages", ".vscode", "app.json", "app.ruleset.json", "AppSourceCop.json")) {
    $generatedPath = Join-Path $outputRoot $path
    if ((Test-Path -LiteralPath $generatedPath) -and $outputRoot.StartsWith($repoRootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        Remove-Item -LiteralPath $generatedPath -Recurse -Force
    }
}

Copy-Item -LiteralPath (Join-Path $repoRoot "app") -Destination (Join-Path $outputRoot "app") -Recurse -Force
Copy-Item -LiteralPath $manifestPath -Destination (Join-Path $outputRoot "app.json") -Force

$rulesetPath = Join-Path $repoRoot "app.ruleset.json"
if (Test-Path -LiteralPath $rulesetPath) {
    Copy-Item -LiteralPath $rulesetPath -Destination (Join-Path $outputRoot "app.ruleset.json") -Force
}

$appSourceCopPath = Join-Path $repoRoot "AppSourceCop.json"
if (Test-Path -LiteralPath $appSourceCopPath) {
    Copy-Item -LiteralPath $appSourceCopPath -Destination (Join-Path $outputRoot "AppSourceCop.json") -Force
}

# Release builds must not silently reuse stale Microsoft symbols or package the
# BCSentinel extension itself as a dependency. Download fresh symbols in VS Code.
# ReuseSymbolCache is opt-in for offline development only; never copy own .app.
$packageCachePath = Join-Path $repoRoot ".alpackages"
if ($ReuseSymbolCache -and (Test-Path -LiteralPath $packageCachePath)) {
    $targetPackageCache = Join-Path $outputRoot ".alpackages"
    New-Item -ItemType Directory -Path $targetPackageCache -Force | Out-Null
    Get-ChildItem -LiteralPath $packageCachePath -File -Filter "*.app" | Where-Object {
        $_.Name -notmatch "BCSentinel"
    } | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $targetPackageCache -Force
    }
    Write-Warning "Reused external symbols on explicit request. Verify BC version before packaging."
} else {
    Write-Host "  Symbols: clean (download fresh symbols for the target BC environment)"
}

$launchPath = Join-Path $repoRoot ".vscode\launch.json"
if ($Profile -eq "DevCloud" -and (Test-Path -LiteralPath $launchPath)) {
    New-Item -ItemType Directory -Path (Join-Path $outputRoot ".vscode") -Force | Out-Null
    Copy-Item -LiteralPath $launchPath -Destination (Join-Path $outputRoot ".vscode\launch.json") -Force
}

$settingsPath = Join-Path $repoRoot ".vscode\settings.json"
if (Test-Path -LiteralPath $settingsPath) {
    New-Item -ItemType Directory -Path (Join-Path $outputRoot ".vscode") -Force | Out-Null
    Copy-Item -LiteralPath $settingsPath -Destination (Join-Path $outputRoot ".vscode\settings.json") -Force
}

Write-Host "Prepared build workspace:"
Write-Host "  Profile: $Profile"
Write-Host "  Manifest: $manifestName"
Write-Host "  Output: $outputRoot"
