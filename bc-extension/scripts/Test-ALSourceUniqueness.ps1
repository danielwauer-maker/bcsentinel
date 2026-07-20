[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$canonicalSourceRoot = [System.IO.Path]::GetFullPath((Join-Path $projectRoot "app\src"))
$violations = [System.Collections.Generic.List[string]]::new()
$comparison = [System.StringComparison]::OrdinalIgnoreCase

function Get-RelativeProjectPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    return $Path.Substring($projectRoot.Length).TrimStart(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
}

function Add-PathViolation {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [Parameter(Mandatory = $true)][System.IO.FileSystemInfo]$Item
    )

    $violations.Add("${Message}: $(Get-RelativeProjectPath -Path $Item.FullName)")
}

$projectBuildRoot = Join-Path $projectRoot ".build"
if (Test-Path -LiteralPath $projectBuildRoot -PathType Container) {
    Get-ChildItem -LiteralPath $projectBuildRoot -Recurse -Filter *.al -File | ForEach-Object {
        Add-PathViolation -Message "AL source exists below bc-extension/.build" -Item $_
    }
}

Get-ChildItem -LiteralPath $projectRoot -Recurse -Directory | ForEach-Object {
    $directory = $_
    $fullName = [System.IO.Path]::GetFullPath($directory.FullName)

    if ($directory.Name.Equals("bc-extension", $comparison)) {
        Add-PathViolation -Message "Nested bc-extension directory detected" -Item $directory
    }

    if ($directory.Name.Equals("src", $comparison) -and
        $directory.Parent -and $directory.Parent.Name.Equals("app", $comparison) -and
        -not $fullName.Equals($canonicalSourceRoot, $comparison)) {
        Add-PathViolation -Message "Second app/src source root detected" -Item $directory
    }

    if ($directory.Name.Equals(".build", $comparison)) {
        Get-ChildItem -LiteralPath $directory.FullName -Recurse -Directory -Force |
            Where-Object { $_.Name.Equals(".build", $comparison) } |
            ForEach-Object { Add-PathViolation -Message "Recursive .build directory detected" -Item $_ }
    }
}

Get-ChildItem -LiteralPath $projectRoot -Recurse -Filter app.json -File | ForEach-Object {
    $manifest = $_
    $canonicalManifest = [System.IO.Path]::GetFullPath((Join-Path $projectRoot "app.json"))
    if (-not $manifest.FullName.Equals($canonicalManifest, $comparison)) {
        Add-PathViolation -Message "Generated or duplicate app.json detected" -Item $manifest
    }
}

$packageCache = Join-Path $projectRoot ".alpackages"
if (Test-Path -LiteralPath $packageCache -PathType Container) {
    Get-ChildItem -LiteralPath $packageCache -Filter *.app -File | Where-Object {
        $_.BaseName -match '(?i)bcsentinel'
    } | ForEach-Object {
        Add-PathViolation -Message "Own BCSentinel package exists in .alpackages" -Item $_
    }
}

$objectTypes = @(
    "tableextension",
    "pageextension",
    "permissionsetextension",
    "enumextension",
    "reportextension",
    "controladdin",
    "permissionset",
    "codeunit",
    "interface",
    "xmlport",
    "query",
    "report",
    "table",
    "page",
    "enum"
) -join "|"
$declarationPattern = '(?im)^\s*(?<type>' + $objectTypes + ')\s+(?<id>\d+)\s+(?<name>"(?:""|[^"])+"|[A-Za-z_][\w.]*)'
$objects = [System.Collections.Generic.List[object]]::new()

Get-ChildItem -LiteralPath $projectRoot -Recurse -Filter *.al -File | ForEach-Object {
    $file = $_
    $content = Get-Content -LiteralPath $file.FullName -Raw
    $withoutBlockComments = [System.Text.RegularExpressions.Regex]::Replace($content, '(?s)/\*.*?\*/', '')
    $withoutComments = [System.Text.RegularExpressions.Regex]::Replace($withoutBlockComments, '(?m)//.*$', '')

    [System.Text.RegularExpressions.Regex]::Matches($withoutComments, $declarationPattern) | ForEach-Object {
        $objects.Add([pscustomobject]@{
            Type = $_.Groups['type'].Value.ToLowerInvariant()
            Id = [int]$_.Groups['id'].Value
            Name = $_.Groups['name'].Value.Trim('"').Replace('""', '"').ToLowerInvariant()
            DisplayName = $_.Groups['name'].Value.Trim('"').Replace('""', '"')
            Path = Get-RelativeProjectPath -Path $file.FullName
        })
    }
}

$objects | Group-Object { "$($_.Type)|$($_.Id)" } | Where-Object Count -gt 1 | ForEach-Object {
    $detail = ($_.Group | Sort-Object Path | ForEach-Object { "$($_.Type) $($_.Id) '$($_.DisplayName)' [$($_.Path)]" }) -join "; "
    $violations.Add("Duplicate AL object type + ID: $detail")
}

$objects | Group-Object { "$($_.Type)|$($_.Name)" } | Where-Object Count -gt 1 | ForEach-Object {
    $detail = ($_.Group | Sort-Object Path | ForEach-Object { "$($_.Type) $($_.Id) '$($_.DisplayName)' [$($_.Path)]" }) -join "; "
    $violations.Add("Duplicate AL object type + name: $detail")
}

if ($violations.Count -gt 0) {
    Write-Host "AL source uniqueness guard failed with $($violations.Count) violation(s):" -ForegroundColor Red
    $violations | ForEach-Object { Write-Host "  - $_" }
    Write-Host "Remediation: keep one canonical object below bc-extension/app/src, remove generated source trees from bc-extension, and build only below the repository-root .build directory."
    exit 1
}

Write-Host "AL source uniqueness guard passed: $($objects.Count) object declaration(s), one canonical app/src tree, and no generated AL source below bc-extension."
exit 0
