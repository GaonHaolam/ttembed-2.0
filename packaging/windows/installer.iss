; ==============================================================================
; Inno Setup 6 Script for TTEmbed Studio 2.0 (Pro)
; Generates standard Windows Setup Wizard (Setup.exe) with Desktop & Start Menu
; ==============================================================================

#define MyAppName "TTEmbed Studio"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "TTEmbed Studio Development Team"
#define MyAppURL "https://github.com/font-tools/ttembed-studio"
#define MyAppExeName "TTEmbedGUI.exe"
#define MyAppId "{{8B264E25-0FD4-4C59-9E28-8681E73C8A01}}"

[Setup]
; App Identity
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Destination Directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=dist\README.txt

; Output Settings
OutputDir=dist
OutputBaseFilename=TTEmbed_Studio_v2.0_Setup
SetupIconFile=ttembed.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Compression
Compression=lzma2/max
SolidCompression=yes

; Architecture (64-bit AMD64)
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible

; Privileges (per-user or administrative elevation)
PrivilegesRequiredOverridesAllowed=dialog commandline
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "contextmenu"; Description: "Add 'Open with TTEmbed Studio' to font context menu"; GroupDescription: "File Associations:"

[Files]
; Main Executable
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Assets & Documentation
Source: "ttembed.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "splash.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\README.txt"; DestDir: "{app}"; Flags: ignoreversion

; Test Fonts Folder
Source: "dist\test_fonts\*"; DestDir: "{app}\test_fonts"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\ttembed.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\ttembed.ico"; Tasks: desktopicon

[Registry]
; Context Menu for .ttf files
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.ttf\shell\TTEmbedStudio"; ValueType: string; ValueName: ""; ValueData: "Open with TTEmbed Studio"; Tasks: contextmenu; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.ttf\shell\TTEmbedStudio"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\ttembed.ico"""; Tasks: contextmenu; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.ttf\shell\TTEmbedStudio\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: contextmenu; Flags: uninsdeletekey

; Context Menu for .otf files
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.otf\shell\TTEmbedStudio"; ValueType: string; ValueName: ""; ValueData: "Open with TTEmbed Studio"; Tasks: contextmenu; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.otf\shell\TTEmbedStudio"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\ttembed.ico"""; Tasks: contextmenu; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.otf\shell\TTEmbedStudio\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: contextmenu; Flags: uninsdeletekey

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
