param(
    [string]$Version = "dev",
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
python -m PyInstaller --clean --noconfirm StankyTools.spec

$OutDir = Join-Path $Root "release_artifacts"
New-Item -ItemType Directory -Force $OutDir | Out-Null

$Portable = Join-Path $OutDir "StankyTools-Portable-$Version.zip"
if (Test-Path $Portable) { Remove-Item $Portable -Force }
Compress-Archive -Path "dist/StankyTools/*" -DestinationPath $Portable -CompressionLevel Optimal

if (-not $SkipInstaller) {
    $Nsis = Get-Command makensis.exe -ErrorAction SilentlyContinue
    if (-not $Nsis) {
        throw "NSIS makensis.exe was not found. Install NSIS or run with -SkipInstaller."
    }

    & $Nsis.Source "/DVERSION=$Version" "installer/StankyTools.nsi"
}

Write-Host "Release artifacts created in $OutDir"
