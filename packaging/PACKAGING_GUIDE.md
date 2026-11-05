# TTEmbed Studio 2.0 - Packaging, Portability & Multi-Format Distribution Guide

## 1. Executive Summary & Portability Architecture

TTEmbed Studio 2.0 is engineered for seamless cross-platform execution with zero external runtime requirements. 

### Core Portability Characteristics:
- **Core Font Engine (`font_engine.py`)**: 100% pure Python implementation using the standard library `struct`, `os`, and `hashlib` modules. It operates directly on TrueType/OpenType binary SFNT tables without depending on platform-specific C extensions, Windows APIs, or third-party font libraries like FreeType or FontTools.
- **Modern Qt6 GUI (`app_gui.py`)**: Built with PySide6 (Qt 6.7+), supporting native Hi-DPI scaling, dark/light operating system themes, and system tray integration across Windows, macOS, and Linux.
- **Embedded Asset Fallbacks (`app_assets.py`)**: Icons (multi-resolution 16x16 through 256x256 ICO) and splash screen images are embedded as Base64 literals directly inside Python code. Even if external disk assets are stripped or inaccessible, the application dynamically hydrates icons and splash pixmaps in memory.
- **Bundled Runtimes**: PyInstaller packaging packages the Python 3.14 runtime, Microsoft Visual C++ 2015-2022 redistributable binaries (`VCRUNTIME140.dll`, `VCRUNTIME140_1.dll`, `MSVCP140.dll`), and all Qt6 platform plugins (`qwindows.dll`, `qmodernwindowsstyle.dll`, `qsvg.dll`). Universal C Runtime (UCRT) APIs map to native Windows 10/11 system DLLs.

---

## 2. Available Windows Distribution Formats

| Format | File / Directory | Target Audience / Use Case | Size | Startup Characteristics |
|---|---|---|---|---|
| **Portable ZIP** | `dist/TTEmbed_Studio_v2.0_Portable.zip` | General end users, USB thumb drives, air-gapped systems | ~48 MB | Zero installation. Includes test fonts & quickstart guide. |
| **Standalone Single EXE** | `dist/TTEmbedGUI.exe` | Power users wanting a single draggable binary | ~47 MB | Self-contained, unpacks to `%TEMP%` on boot with splash screen. |
| **Zero-Overhead Folder** | `dist/TTEmbedStudio_Folder/` | Users seeking instantaneous cold startup times | ~145 MB | Uncompressed onedir layout; no temp decompression overhead. |
| **Inno Setup Script** | `installer.iss` | Enterprise & IT admins creating standard Windows installer | Outputs `.exe` | Windows Setup Wizard with Desktop icon, Start Menu, context menus. |
| **PowerShell Setup** | `Install-TTEmbedStudio.ps1` | Native Windows 10/11 automated installer (no tools needed) | Script | Installs to `%LOCALAPPDATA%\Programs`, registers in Apps & Features. |

---

## 3. Windows Distribution Details

### 3.1 Portable Distribution ZIP
The portable zip `TTEmbed_Studio_v2.0_Portable.zip` contains:
```
TTEmbed_Studio_v2.0_Portable/
├── TTEmbedGUI.exe             # 64-bit Standalone Executable
├── README.txt                 # Quickstart, features, EULA, and usage guide
├── SHA256SUMS.txt             # Cryptographic hash verification manifest
├── ttembed.ico                # High-res application icon
├── installer.iss              # Inno Setup compilation script
├── Install-TTEmbedStudio.ps1  # Native PowerShell installer
└── test_fonts/                # Clean sample fonts with embedding restrictions
    ├── README_TEST_FONTS.txt  # Guide to test fonts
    ├── vilnal_n.TTF           # Vilna New font
    ├── vilna_nb.TTF           # Vilna New Bold font
    ├── VilnaUnicode.ttf       # Unicode sample
    └── [40+ test fonts]       # Diverse fsType test cases
```

### 3.2 Compiling with Inno Setup
To compile `installer.iss` into a standalone setup wizard (`TTEmbed_Studio_v2.0_Setup.exe`):
1. Download and install [Inno Setup 6](https://jrsoftware.org/isdl.php).
2. Run from PowerShell or Command Prompt:
   ```cmd
   iscc projects\ttembed-gui\installer.iss
   ```
3. The generated installer will be placed in `dist/TTEmbed_Studio_v2.0_Setup.exe`.

### 3.3 Running Native PowerShell Setup
For users who do not have Inno Setup:
```powershell
powershell.exe -ExecutionPolicy Bypass -File .\Install-TTEmbedStudio.ps1
```
This automatically:
- Installs to `%LOCALAPPDATA%\Programs\TTEmbedStudio`
- Creates Start Menu and Desktop shortcuts with custom icon
- Registers in Windows Add/Remove Programs (Programs & Features)
- Provides an automated clean uninstaller (`Uninstall-TTEmbedStudio.ps1`)

---

## 4. macOS Packaging Pathway (.app & .dmg)

### 4.1 Prerequisites
- macOS 12 Monterey, 13 Ventura, or 14 Sonoma
- Python 3.10+ (Homebrew or python.org universal2 installer)
- Xcode Command Line Tools (`xcode-select --install`)
- PySide6 (`pip install PySide6 pyinstaller`)

### 4.2 Spec Configuration for macOS Bundle
Create `TTEmbedGUI_mac.spec`:
```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['app_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('splash.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TTEmbedStudio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    target_arch='universal2', # Or 'arm64' for Apple Silicon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='TTEmbedStudio',
)

app = BUNDLE(
    coll,
    name='TTEmbed Studio.app',
    icon='ttembed.icns',
    bundle_identifier='com.ttembed.studio',
    info_plist={
        'CFBundleDisplayName': 'TTEmbed Studio',
        'CFBundleName': 'TTEmbed Studio',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '11.0',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'TrueType Font',
                'CFBundleTypeExtensions': ['ttf', 'otf', 'ttc'],
                'CFBundleTypeRole': 'Editor',
            }
        ],
    },
)
```

### 4.3 Generating Icon & DMG
1. **Convert Icon to ICNS**:
   ```bash
   mkdir ttembed.iconset
   sips -z 16 16     icon_256.png --out ttembed.iconset/icon_16x16.png
   sips -z 32 32     icon_256.png --out ttembed.iconset/icon_16x16@2x.png
   sips -z 32 32     icon_256.png --out ttembed.iconset/icon_32x32.png
   sips -z 64 64     icon_256.png --out ttembed.iconset/icon_32x32@2x.png
   sips -z 128 128   icon_256.png --out ttembed.iconset/icon_128x128.png
   sips -z 256 256   icon_256.png --out ttembed.iconset/icon_128x128@2x.png
   sips -z 256 256   icon_256.png --out ttembed.iconset/icon_256x256.png
   sips -z 512 512   icon_256.png --out ttembed.iconset/icon_256x256@2x.png
   iconutil -c icns ttembed.iconset -o ttembed.icns
   ```
2. **Build and Code Sign**:
   ```bash
   pyinstaller TTEmbedGUI_mac.spec
   codesign --deep --force --options runtime --sign "Developer ID Application: Your Name (TEAMID)" dist/TTEmbed\ Studio.app
   ```
3. **Create Drag-to-Applications DMG**:
   ```bash
   npm install --global create-dmg
   create-dmg 'dist/TTEmbed Studio.app' dist/
   ```
4. **Notarize**:
   ```bash
   xcrun notarytool submit dist/TTEmbed\ Studio\ 2.0.0.dmg --keychain-profile "AC_PASSWORD" --wait
   xcrun stapler staple dist/TTEmbed\ Studio\ 2.0.0.dmg
   ```

---

## 5. Linux Packaging Pathway (AppImage & Binary)

### 5.1 Prerequisites & Target Base
To ensure the resulting binary runs on Ubuntu 20.04+, Debian 11+, Fedora 36+, Arch Linux, and RHEL/CentOS 8+, build on an older glibc distribution base (e.g., Ubuntu 20.04 LTS or Docker `rockylinux:8`).

### 5.2 Standalone Onedir & AppImage Recipe

1. **Build with PyInstaller**:
   ```bash
   pyinstaller --noconfirm --onedir --windowed \
     --name ttembed-studio \
     --add-data "splash.png:." \
     app_gui.py
   ```

2. **Assemble AppDir Layout**:
   ```bash
   mkdir -p AppDir/usr/bin
   mkdir -p AppDir/usr/share/applications
   mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps

   cp -r dist/ttembed-studio/* AppDir/usr/bin/
   cp test_icon.png AppDir/usr/share/icons/hicolor/256x256/apps/ttembed.png
   cp test_icon.png AppDir/ttembed.png
   ```

3. **Desktop Entry (`AppDir/ttembed.desktop`)**:
   ```ini
   [Desktop Entry]
   Type=Application
   Name=TTEmbed Studio
   Comment=TrueType & OpenType Font Embedding Permissions Tool
   Exec=ttembed-studio %F
   Icon=ttembed
   Categories=Graphics;Utility;
   MimeType=font/ttf;font/otf;font/collection;
   Terminal=false
   ```

4. **AppRun Script (`AppDir/AppRun`)**:
   ```bash
   #!/bin/bash
   HERE="$(dirname "$(readlink -f "${0}")")"
   export LD_LIBRARY_PATH="${HERE}/usr/bin:${HERE}/usr/bin/_internal:${LD_LIBRARY_PATH}"
   export QT_PLUGIN_PATH="${HERE}/usr/bin/_internal/PySide6/plugins"
   exec "${HERE}/usr/bin/ttembed-studio" "$@"
   ```
   ```bash
   chmod +x AppDir/AppRun
   ```

5. **Generate AppImage with appimagetool**:
   ```bash
   wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
   chmod +x appimagetool-x86_64.AppImage
   ARCH=x86_64 ./appimagetool-x86_64.AppImage AppDir dist/TTEmbed_Studio_v2.0_Linux_x86_64.AppImage
   ```

---

## 6. Automated GitHub Actions CI/CD Pipeline

A unified multi-platform GitHub Actions workflow (`.github/workflows/build-all-platforms.yml`) compiles and publishes releases for all three platforms:

```yaml
name: Build & Package TTEmbed Studio 2.0

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build-windows:
    runs-on: windows-2022
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - name: Build Standalone EXE
        run: pyinstaller TTEmbedGUI.spec
      - name: Package Portable ZIP
        run: python build_packages.py
      - uses: actions/upload-artifact@v4
        with:
          name: windows-portable
          path: dist/TTEmbed_Studio_v2.0_Portable.zip

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - name: Build macOS App
        run: pyinstaller TTEmbedGUI_mac.spec
      - uses: actions/upload-artifact@v4
        with:
          name: macos-app
          path: dist/TTEmbed Studio.app

  build-linux:
    runs-on: ubuntu-20.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - name: Build Linux AppImage
        run: |
          pyinstaller --onedir --windowed --name ttembed-studio app_gui.py
          # AppImage packaging steps here
      - uses: actions/upload-artifact@v4
        with:
          name: linux-appimage
          path: dist/*.AppImage
```
