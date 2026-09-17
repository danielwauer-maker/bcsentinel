[CmdletBinding()]
param(
    [ValidateSet("DevCloud", "ReleaseCloud", "OnPremBc19", "DiagnosticsQA", "FindingTestsQA")]
    [string]$Profile = "ReleaseCloud",

    [string]$OutputPath,
    [string]$SymbolSourcePath
)

$ErrorActionPreference = "Stop"

function Get-NormalizedPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [string]$BasePath
    )

    $candidate = if ([System.IO.Path]::IsPathRooted($Path)) {
        $Path
    }
    else {
        Join-Path $BasePath $Path
    }

    return [System.IO.Path]::GetFullPath($candidate).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
}

function Test-IsSameOrChildPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Candidate,
        [Parameter(Mandatory = $true)]
        [string]$Parent
    )

    $comparison = [System.StringComparison]::OrdinalIgnoreCase
    if ($Candidate.Equals($Parent, $comparison)) {
        return $true
    }

    $parentWithSeparator = $Parent + [System.IO.Path]::DirectorySeparatorChar
    return $Candidate.StartsWith($parentWithSeparator, $comparison)
}

$alProjectRoot = Get-NormalizedPath -Path ".." -BasePath $PSScriptRoot
$repositoryRoot = Get-NormalizedPath -Path ".." -BasePath $alProjectRoot

if ($Profile -eq 'FindingTestsQA') {
    $testOutput = Join-Path $repositoryRoot '.build\bc-extension\FindingTestsQA'
    if ($OutputPath -and (Get-NormalizedPath -Path $OutputPath -BasePath $repositoryRoot) -ne $testOutput) {
        throw 'FindingTestsQA output must be .build/bc-extension/FindingTestsQA.'
    }
    New-Item -ItemType Directory -Path $testOutput -Force | Out-Null
    foreach ($entry in @('src', 'Translations', 'app.json')) {
        Copy-Item -LiteralPath (Join-Path $repositoryRoot "bc-finding-tests\$entry") -Destination $testOutput -Recurse -Force
    }
    Write-Host "Prepared temporary-record AL test workspace: $testOutput"
    return
}

if ($Profile -eq 'DiagnosticsQA') {
    $diagnosticsRoot = Join-Path $repositoryRoot 'bc-diagnostics'
    $diagnosticsOutput = Join-Path $repositoryRoot '.build\bc-extension\DiagnosticsQA'
    if ($OutputPath -and (Get-NormalizedPath -Path $OutputPath -BasePath $repositoryRoot) -ne $diagnosticsOutput) {
        throw 'DiagnosticsQA output must be .build/bc-extension/DiagnosticsQA.'
    }
    New-Item -ItemType Directory -Path $diagnosticsOutput -Force | Out-Null
    foreach ($entry in @('src', 'Translations', 'app.json')) {
        $source = Join-Path $diagnosticsRoot $entry
        if (Test-Path -LiteralPath $source) {
            Copy-Item -LiteralPath $source -Destination $diagnosticsOutput -Recurse -Force
        }
    }
    $symbols = Join-Path $diagnosticsOutput '.alpackages'
    New-Item -ItemType Directory -Path $symbols -Force | Out-Null
    if ($SymbolSourcePath) {
        Get-ChildItem -LiteralPath $SymbolSourcePath -Filter '*.app' -File | ForEach-Object {
            $target = Join-Path $symbols $_.Name
            if (-not (Test-Path -LiteralPath $target)) { Copy-Item -LiteralPath $_.FullName -Destination $target }
        }
    }
    Write-Host "Prepared read-only diagnostics build workspace: $diagnosticsOutput"
    return
}

$manifestByProfile = @{
    DevCloud = "app.cloud.json"
    ReleaseCloud = "app.json"
    OnPremBc19 = "app.onprem.bc19.json"
}

$manifestName = $manifestByProfile[$Profile]
$manifestPath = Join-Path $alProjectRoot $manifestName

if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Manifest not found: $manifestPath"
}

if (-not $OutputPath) {
    $OutputPath = Join-Path $repositoryRoot ".build\bc-extension\$Profile"
}

$outputRoot = Get-NormalizedPath -Path $OutputPath -BasePath $repositoryRoot

# The guard must run before New-Item or Remove-Item. It rejects the project itself,
# every project child (including app and .alpackages), and project ancestors.
if ((Test-IsSameOrChildPath -Candidate $outputRoot -Parent $alProjectRoot) -or
    (Test-IsSameOrChildPath -Candidate $alProjectRoot -Parent $outputRoot)) {
    throw "Unsafe OutputPath '$outputRoot'. Build workspaces must be outside the AL project root '$alProjectRoot' and must not contain it."
}

New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null

# Only these generated entries are managed. No repository or project tree is copied recursively.
$managedEntries = @(
    "app",
    "Translations",
    ".alpackages",
    ".vscode",
    "app.json",
    "app.ruleset.json",
    "AppSourceCop.json"
)
foreach ($path in $managedEntries) {
    $generatedPath = Join-Path $outputRoot $path
    if (Test-Path -LiteralPath $generatedPath) {
        Remove-Item -LiteralPath $generatedPath -Recurse -Force
    }
}

Copy-Item -LiteralPath (Join-Path $alProjectRoot "app") -Destination (Join-Path $outputRoot "app") -Recurse -Force
Copy-Item -LiteralPath $manifestPath -Destination (Join-Path $outputRoot "app.json") -Force

foreach ($fileName in @("app.ruleset.json", "AppSourceCop.json")) {
    $sourcePath = Join-Path $alProjectRoot $fileName
    if (Test-Path -LiteralPath $sourcePath -PathType Leaf) {
        Copy-Item -LiteralPath $sourcePath -Destination (Join-Path $outputRoot $fileName) -Force
    }
}

foreach ($directoryName in @("Translations", ".alpackages")) {
    $sourcePath = Join-Path $alProjectRoot $directoryName
    if (Test-Path -LiteralPath $sourcePath -PathType Container) {
        Copy-Item -LiteralPath $sourcePath -Destination (Join-Path $outputRoot $directoryName) -Recurse -Force
    }
}

$settingsPath = Join-Path $alProjectRoot ".vscode\settings.json"
if (Test-Path -LiteralPath $settingsPath -PathType Leaf) {
    New-Item -ItemType Directory -Path (Join-Path $outputRoot ".vscode") -Force | Out-Null
    Copy-Item -LiteralPath $settingsPath -Destination (Join-Path $outputRoot ".vscode\settings.json") -Force
}

$launchPath = Join-Path $alProjectRoot ".vscode\launch.json"
if ($Profile -eq "DevCloud" -and (Test-Path -LiteralPath $launchPath -PathType Leaf)) {
    New-Item -ItemType Directory -Path (Join-Path $outputRoot ".vscode") -Force | Out-Null
    Copy-Item -LiteralPath $launchPath -Destination (Join-Path $outputRoot ".vscode\launch.json") -Force
}

Write-Host "Prepared build workspace:"
Write-Host "  Profile: $Profile"
Write-Host "  Manifest: $manifestName"
Write-Host "  Output: $outputRoot"
