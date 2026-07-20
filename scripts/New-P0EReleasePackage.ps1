[CmdletBinding()]
param(
    [string]$AppPath = ".build/bc-extension/ReleaseCloud/BCSentinel.app",
    [string]$OutputRoot = ".build/bc-extension/release"
)

$ErrorActionPreference = "Stop"
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$alProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $repoRoot "bc-extension")).TrimEnd('\', '/')
$resolvedApp = [System.IO.Path]::GetFullPath((Join-Path $repoRoot $AppPath))
$resolvedOutputRoot = [System.IO.Path]::GetFullPath((Join-Path $repoRoot $OutputRoot)).TrimEnd('\', '/')
$repoRoot = $repoRoot.TrimEnd('\', '/')
$comparison = [System.StringComparison]::OrdinalIgnoreCase
$repoPrefix = $repoRoot + [System.IO.Path]::DirectorySeparatorChar
$alProjectPrefix = $alProjectRoot + [System.IO.Path]::DirectorySeparatorChar

if (-not (Test-Path -LiteralPath $resolvedApp)) {
    throw "Compiled app not found: $resolvedApp"
}
if (-not $resolvedOutputRoot.StartsWith($repoPrefix, $comparison)) {
    throw "OutputRoot must be a child of the repository workspace."
}
if ($resolvedOutputRoot.Equals($alProjectRoot, $comparison) -or
    $resolvedOutputRoot.StartsWith($alProjectPrefix, $comparison)) {
    throw "OutputRoot must not be inside the AL project root."
}

$manifest = Get-Content (Join-Path $repoRoot "bc-extension/app.json") -Raw | ConvertFrom-Json
$commit = (& git -C $repoRoot rev-parse HEAD).Trim()
$dirty = -not [string]::IsNullOrWhiteSpace((& git -C $repoRoot status --porcelain))
$qualifier = if ($dirty) { "-dirty" } else { "" }
$packageName = "BCSentinel-$($manifest.version)-p0e-$($commit.Substring(0, 7))$qualifier"
$stage = Join-Path $resolvedOutputRoot $packageName
$zipPath = Join-Path $resolvedOutputRoot "$packageName.zip"

if (Test-Path -LiteralPath $stage) {
    Remove-Item -LiteralPath $stage -Recurse -Force
}
if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}
New-Item -ItemType Directory -Path $stage -Force | Out-Null

Copy-Item -LiteralPath $resolvedApp -Destination (Join-Path $stage "BCSentinel_$($manifest.version).app")
$documents = @(
    "docs/GL_EXT_P0E_SANDBOX_RELEASE_GATE.md",
    "docs/BC_EXTENSION_ROLE_PERMISSION_MATRIX.md",
    "docs/BC_EXTENSION_UPGRADE_TEST_REPORT.md",
    "docs/BC_EXTENSION_POSTGRESQL_STAGING_REPORT.md",
    "docs/BC_EXTENSION_RELEASE_PACKAGE.md"
)
foreach ($document in $documents) {
    Copy-Item -LiteralPath (Join-Path $repoRoot $document) -Destination $stage
}

$metadata = [ordered]@{
    name = $manifest.name
    publisher = $manifest.publisher
    version = $manifest.version
    source_commit = $commit
    working_tree_dirty = $dirty
    signed = $false
    runtime = $manifest.runtime
    application = $manifest.application
    platform = $manifest.platform
    generated_at_utc = [DateTime]::UtcNow.ToString("o")
}
$metadata | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $stage "RELEASE-METADATA.json") -Encoding UTF8

$checksumLines = Get-ChildItem -LiteralPath $stage -File | Sort-Object Name | ForEach-Object {
    $hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    "$hash  $($_.Name)"
}
$checksumLines | Set-Content -LiteralPath (Join-Path $stage "CHECKSUMS.sha256") -Encoding ASCII

Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $zipPath -CompressionLevel Optimal
$zipHash = (Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash.ToLowerInvariant()
"$zipHash  $([System.IO.Path]::GetFileName($zipPath))" | Set-Content -LiteralPath "$zipPath.sha256" -Encoding ASCII

Write-Host "Release candidate: $zipPath"
Write-Host "SHA256: $zipHash"
Write-Host "Dirty: $dirty"
