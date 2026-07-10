param(
    [string]$Version = "",
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"

# Resolve repository folders using this script's location.
$RepoRoot = Split-Path -Parent $PSScriptRoot
$BuildDir = Join-Path $RepoRoot "build"
$DistDir = Join-Path $RepoRoot "dist"
$ReleaseDir = Join-Path $RepoRoot "release_artifacts"
$InstallerScript = Join-Path $RepoRoot "installer\StankyTools.nsi"
$SpecFile = Join-Path $RepoRoot "StankyTools.spec"
$MainFile = Join-Path $RepoRoot "main.py"

Set-Location $RepoRoot

# Determine version.
if ([string]::IsNullOrWhiteSpace($Version)) {
    if (-not [string]::IsNullOrWhiteSpace($env:GITHUB_REF_NAME)) {
        $Version = $env:GITHUB_REF_NAME
    }
    else {
        $Version = "dev"
    }
}

$Version = $Version.Trim()
if ($Version.StartsWith("v")) {
    $Version = $Version.Substring(1)
}

Write-Host "Repository: $RepoRoot"
Write-Host "Version: $Version"
Write-Host "Dist folder: $DistDir"
Write-Host "Release folder: $ReleaseDir"

# Clean old build output.
foreach ($Path in @($BuildDir, $DistDir, $ReleaseDir)) {
    if (Test-Path $Path) {
        Remove-Item $Path -Recurse -Force
    }

    New-Item -ItemType Directory -Path $Path -Force | Out-Null
}

# Build with PyInstaller.
if (Test-Path $SpecFile) {
    Write-Host "Building from StankyTools.spec..."
    python -m PyInstaller `
        --clean `
        --noconfirm `
        --distpath $DistDir `
        --workpath $BuildDir `
        $SpecFile
}
elseif (Test-Path $MainFile) {
    Write-Host "No spec file found. Building from main.py..."

    python -m PyInstaller `
        --clean `
        --noconfirm `
        --windowed `
        --name "StankyTools" `
        --distpath $DistDir `
        --workpath $BuildDir `
        $MainFile
}
else {
    throw "Neither StankyTools.spec nor main.py was found."
}

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE."
}

# Locate the actual executable instead of assuming its location.
$AppExe = Get-ChildItem `
    -Path $DistDir `
    -Filter "StankyTools.exe" `
    -File `
    -Recurse |
    Select-Object -First 1

if (-not $AppExe) {
    Write-Host "Contents of dist:"
    Get-ChildItem -Path $DistDir -Recurse | ForEach-Object {
        Write-Host $_.FullName
    }

    throw "StankyTools.exe was not found anywhere under $DistDir."
}

Write-Host "Application executable: $($AppExe.FullName)"

# Get the executable path relative to dist.
$ExeRelativePath = [System.IO.Path]::GetRelativePath(
    $DistDir,
    $AppExe.FullName
)

Write-Host "Relative executable path: $ExeRelativePath"

# Build portable ZIP.
$PortableName = "StankyTools-Portable-v$Version.zip"
$PortablePath = Join-Path $ReleaseDir $PortableName

$ExeParent = Split-Path -Parent $AppExe.FullName

if ($ExeParent -eq $DistDir) {
    # One-file PyInstaller build.
    Compress-Archive `
        -Path $AppExe.FullName `
        -DestinationPath $PortablePath `
        -CompressionLevel Optimal `
        -Force
}
else {
    # One-folder PyInstaller build.
    Compress-Archive `
        -Path (Join-Path $ExeParent "*") `
        -DestinationPath $PortablePath `
        -CompressionLevel Optimal `
        -Force
}

Write-Host "Portable ZIP created: $PortablePath"

if (-not $SkipInstaller) {
    if (-not (Test-Path $InstallerScript)) {
        throw "NSIS script was not found: $InstallerScript"
    }

    $MakeNsisCandidates = @(
        (Get-Command "makensis.exe" -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
        "C:\Program Files (x86)\NSIS\makensis.exe",
        "C:\Program Files\NSIS\makensis.exe"
    ) | Where-Object {
        $_ -and (Test-Path $_)
    }

    $MakeNsis = $MakeNsisCandidates | Select-Object -First 1

    if (-not $MakeNsis) {
        throw "NSIS makensis.exe was not found. Install NSIS or run with -SkipInstaller."
    }

    Write-Host "Using NSIS: $MakeNsis"

    # Pass absolute paths into NSIS.
    & $MakeNsis `
        "/DAPP_VERSION=$Version" `
        "/DDIST_DIR=$DistDir" `
        "/DOUTPUT_DIR=$ReleaseDir" `
        "/DAPP_EXE_REL=$ExeRelativePath" `
        $InstallerScript

    if ($LASTEXITCODE -ne 0) {
        throw "NSIS failed with exit code $LASTEXITCODE."
    }
}

Write-Host ""
Write-Host "Release artifacts created in $ReleaseDir"

Get-ChildItem -Path $ReleaseDir -File | ForEach-Object {
    Write-Host " - $($_.Name) [$([math]::Round($_.Length / 1MB, 2)) MB]"
}