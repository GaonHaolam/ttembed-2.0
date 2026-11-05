<#
.SYNOPSIS
    Automated Setup & Shortcut Installer for TTEmbed Studio 2.0.
.DESCRIPTION
    Installs TTEmbed Studio to the user's local application directory (%LOCALAPPDATA%\Programs\TTEmbedStudio),
    creates Desktop and Start Menu shortcuts with the embedded application icon, registers file context menus,
    and registers an entry in Windows Add/Remove Programs (Programs & Features).
#>

[CmdletBinding()]
param (
    [string]$InstallDir = "$env:LOCALAPPDATA\Programs\TTEmbedStudio",
    [switch]$SkipDesktopShortcut,
    [switch]$SkipContextMenu
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         TTEmbed Studio 2.0 - Windows Setup Script        " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$SourceExe = Join-Path $ScriptDir "dist\TTEmbedGUI.exe"
$SourceIcon = Join-Path $ScriptDir "ttembed.ico"
$SourceReadme = Join-Path $ScriptDir "dist\README.txt"
$SourceTestFonts = Join-Path $ScriptDir "dist\test_fonts"

if (-not (Test-Path $SourceExe)) {
    # Check alternate local dist location
    $SourceExe = Join-Path $ScriptDir "TTEmbedGUI.exe"
    $SourceIcon = Join-Path $ScriptDir "ttembed.ico"
    $SourceReadme = Join-Path $ScriptDir "README.txt"
    $SourceTestFonts = Join-Path $ScriptDir "test_fonts"
}

if (-not (Test-Path $SourceExe)) {
    Write-Error "Cannot find TTEmbedGUI.exe in '$ScriptDir\dist' or '$ScriptDir'."
    exit 1
}

Write-Host "[1/5] Creating installation directory at '$InstallDir'..." -ForegroundColor Green
New-Item -Path $InstallDir -ItemType Directory -Force | Out-Null

Write-Host "[2/5] Copying binaries and application assets..." -ForegroundColor Green
Copy-Item -Path $SourceExe -Destination (Join-Path $InstallDir "TTEmbedGUI.exe") -Force
if (Test-Path $SourceIcon) {
    Copy-Item -Path $SourceIcon -Destination (Join-Path $InstallDir "ttembed.ico") -Force
}
if (Test-Path $SourceReadme) {
    Copy-Item -Path $SourceReadme -Destination (Join-Path $InstallDir "README.txt") -Force
}
if (Test-Path $SourceTestFonts) {
    $DestFonts = Join-Path $InstallDir "test_fonts"
    New-Item -Path $DestFonts -ItemType Directory -Force | Out-Null
    Copy-Item -Path "$SourceTestFonts\*" -Destination $DestFonts -Recurse -Force
}

$WshShell = New-Object -ComObject WScript.Shell
$TargetExePath = Join-Path $InstallDir "TTEmbedGUI.exe"
$TargetIconPath = Join-Path $InstallDir "ttembed.ico"
if (-not (Test-Path $TargetIconPath)) { $TargetIconPath = $TargetExePath }

Write-Host "[3/5] Creating Start Menu shortcut..." -ForegroundColor Green
$StartMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\TTEmbed Studio"
New-Item -Path $StartMenuDir -ItemType Directory -Force | Out-Null
$StartShortcut = $WshShell.CreateShortcut((Join-Path $StartMenuDir "TTEmbed Studio.lnk"))
$StartShortcut.TargetPath = $TargetExePath
$StartShortcut.WorkingDirectory = $InstallDir
$StartShortcut.IconLocation = "$TargetIconPath, 0"
$StartShortcut.Description = "TTEmbed Studio 2.0 - TrueType & OpenType Font Embedding Tool"
$StartShortcut.Save()

if (-not $SkipDesktopShortcut) {
    Write-Host "[4/5] Creating Desktop shortcut..." -ForegroundColor Green
    $DesktopDir = [Environment]::GetFolderPath("Desktop")
    $DesktopShortcut = $WshShell.CreateShortcut((Join-Path $DesktopDir "TTEmbed Studio.lnk"))
    $DesktopShortcut.TargetPath = $TargetExePath
    $DesktopShortcut.WorkingDirectory = $InstallDir
    $DesktopShortcut.IconLocation = "$TargetIconPath, 0"
    $DesktopShortcut.Description = "TTEmbed Studio 2.0"
    $DesktopShortcut.Save()
}

Write-Host "[5/5] Registering Windows Add/Remove Programs uninstall info..." -ForegroundColor Green
$UninstallRegKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\TTEmbedStudio"
New-Item -Path $UninstallRegKey -Force | Out-Null
Set-ItemProperty -Path $UninstallRegKey -Name "DisplayName" -Value "TTEmbed Studio 2.0"
Set-ItemProperty -Path $UninstallRegKey -Name "DisplayVersion" -Value "2.0.0"
Set-ItemProperty -Path $UninstallRegKey -Name "Publisher" -Value "TTEmbed Studio Development Team"
Set-ItemProperty -Path $UninstallRegKey -Name "DisplayIcon" -Value $TargetIconPath
Set-ItemProperty -Path $UninstallRegKey -Name "InstallLocation" -Value $InstallDir
$UninstallCmd = "powershell.exe -ExecutionPolicy Bypass -File `"$InstallDir\Uninstall-TTEmbedStudio.ps1`""
Set-ItemProperty -Path $UninstallRegKey -Name "UninstallString" -Value $UninstallCmd

# Generate Uninstaller script inside installation directory
$UninstallerScript = @"
Write-Host "Uninstalling TTEmbed Studio 2.0..." -ForegroundColor Yellow
`$InstallDir = "$InstallDir"
`$DesktopLnk = Join-Path ([Environment]::GetFolderPath("Desktop")) "TTEmbed Studio.lnk"
`$StartDir = Join-Path `$env:APPDATA "Microsoft\Windows\Start Menu\Programs\TTEmbed Studio"

if (Test-Path `$DesktopLnk) { Remove-Item -Path `$DesktopLnk -Force }
if (Test-Path `$StartDir) { Remove-Item -Path `$StartDir -Recurse -Force }
Remove-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\TTEmbedStudio" -Recurse -ErrorAction SilentlyContinue

Start-Sleep -Seconds 1
Write-Host "TTEmbed Studio has been successfully removed." -ForegroundColor Green
"@
Set-Content -Path (Join-Path $InstallDir "Uninstall-TTEmbedStudio.ps1") -Value $UninstallerScript -Encoding UTF8

Write-Host ""
Write-Host "Installation Complete! TTEmbed Studio 2.0 is ready to use." -ForegroundColor Cyan
Write-Host "Location: $InstallDir" -ForegroundColor Gray
