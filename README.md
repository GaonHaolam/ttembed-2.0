# TTEmbed 2.0

<p align="center">
  <b>Modern Cross-Platform OpenType & TrueType Font Embedding Permissions (<code>fsType</code>) Editor</b><br>
  <i>1-Click Embedding Unlock • Atomic In-Place Overwrites • Cross-Platform High-DPI GUI</i>
</p>

<p align="center">
  <a href="https://github.com/GaonHaolam/ttembed-2.0/releases/tag/v2.0.0">
    <img src="https://img.shields.io/badge/Release-v2.0.0-blue.svg?style=for-the-badge" alt="Release v2.0.0">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-emerald.svg?style=for-the-badge" alt="License">
  </a>
  <img src="https://img.shields.io/badge/Platform-Windows%20|%20macOS%20|%20Linux-indigo.svg?style=for-the-badge" alt="Platforms">
  <img src="https://img.shields.io/badge/Python-3.10+-yellow.svg?style=for-the-badge" alt="Python Version">
</p>

---

## ⚡ Instant Standalone Downloads

No setup or complex installation required. Click to download the standalone executable for your operating system:

<p align="center">
  <a href="https://github.com/GaonHaolam/ttembed-2.0/releases/download/v2.0.0/TTEmbed-2.0.exe">
    <img src="https://img.shields.io/badge/Download_for_Windows-TTEmbed--2.0.exe-0078D4?style=for-the-badge&logo=windows&logoColor=white" height="42" alt="Download for Windows">
  </a>
  &nbsp;&nbsp;
  <a href="https://github.com/GaonHaolam/ttembed-2.0/releases/download/v2.0.0/TTEmbed-2.0.dmg">
    <img src="https://img.shields.io/badge/Download_for_macOS-TTEmbed--2.0.dmg-000000?style=for-the-badge&logo=apple&logoColor=white" height="42" alt="Download for macOS">
  </a>
  &nbsp;&nbsp;
  <a href="https://github.com/GaonHaolam/ttembed-2.0/releases/download/v2.0.0/TTEmbed-2.0.AppImage">
    <img src="https://img.shields.io/badge/Download_for_Linux-TTEmbed--2.0.AppImage-FCC624?style=for-the-badge&logo=linux&logoColor=black" height="42" alt="Download for Linux">
  </a>
</p>

<p align="center">
  <sub>All binaries are standalone, single-file executables with zero external runtimes or installation needed.</sub>
</p>

---

## ✨ Features

- **🚀 1-Click Embedding Unlock (`0x0000`)**: Instantly clear restrictive licensing flags (`0x0002` Restricted, etc.) to restore full installable permissions.
- **🛡️ Safe Atomic In-Place Overwrites**: Automatically circumvents operating system font locks (e.g., Windows Font Cache, Adobe InDesign locks) using secure atomic staging and fallback swapping.
- **🎯 Full Font Format Support**:
  - TrueType (`.ttf`)
  - OpenType (`.otf`)
  - TrueType Collections (`.ttc`)
- **📂 Bulk Processing & Drag & Drop**: Drop individual font files or entire font directory trees directly into the hero zone or sidebar queue.
- **🖥️ High-DPI Modern UI**: Clean dark theme engineered with curved glass styling, real-time search filtering, and live animated feedback.
- **🔒 Multi-Bit Fine-Tuning**: Select exact permission combinations (Editable, Preview & Print, Installable, Restricted, No Subsetting, Bitmap Only) or enter custom 16-bit hex values directly.

---

## 📖 How to Use

1. **Launch the Application**:
   - Double-click the downloaded standalone binary for your OS.
2. **Import Fonts**:
   - Drag & drop your font files or folders into the **Drop Zone** or the **Queue Sidebar**.
   - Or click **"Choose Font File(s)"** to select files via the file dialog.
3. **Inspect Permissions**:
   - Click any font in the sidebar queue to inspect its name, family, PostScript identifier, format, and decoded `fsType` licensing category.
4. **Modify Permissions**:
   - Click the preset radio button:
     - **0x0000 (Installable)** — Full rights to embed and install across all applications and PDF generators.
     - **0x0008 (Editable)** — Embedding permitted; recipient may edit text.
     - **0x0004 (Preview & Print)** — Embedding permitted; recipient may view/print only.
     - **0x0002 (Restricted)** — Embedding prohibited without explicit license.
5. **Apply & Save**:
   - Click **"Save (In-Place Overwrite)"** to update the original font file safely.
   - Or click **"Export Unlocked Font..."** to write to a new destination file.
   - Or use **"Batch Unlock All"** to apply changes across all loaded fonts at once.

---

## 🛠️ Development & Building from Source

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/GaonHaolam/ttembed-2.0.git
cd ttembed-2.0
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the GUI Directly
```bash
python -m src
```

### 4. Build Standalone Distributables
To package standalone single-file executables for Windows (`.exe`), macOS (`.dmg`), and Linux (`.AppImage`):
```bash
python package.py
```
Compiled standalone outputs will be created directly in `dist/`.

---

## 📂 Repository Structure

```
ttembed-2.0/
├── assets/                  # High-resolution icons and vector branding
│   ├── splash.png           # Splash screen asset
│   ├── ttembed.ico          # Multi-resolution Windows icon (16x16 to 256x256)
│   ├── ttembed.png          # High-DPI 256x256 PNG
│   └── ttembed.icns         # Apple Icon for macOS
├── packaging/               # Platform packaging manifests and scripts
│   ├── windows/             # PyInstaller spec, Windows Manifest (PerMonitorV2 DPI)
│   ├── macos/               # Info.plist and DMG builders
│   └── linux/               # AppImage AppRun and desktop entry
├── src/                     # Core application source code
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Direct entry point
│   ├── app_assets.py        # Icon loader & high-DPI Windows integration
│   ├── app_gui.py           # Modern Qt6/PySide6 desktop interface
│   └── font_engine.py       # SFNT/OpenType binary table engine
├── LICENSE                  # MIT License
├── package.py               # 1-click cross-platform build orchestrator
├── requirements.txt         # Production dependencies
└── README.md                # Comprehensive documentation
```

---

## 🔒 Cryptographic Verification

| Platform | File | Format | SHA-256 Checksum |
| :--- | :--- | :--- | :--- |
| **Windows** | `TTEmbed-2.0.exe` | Portable Executable | `4111d9fcccac1e5b28beda3793a6c6f61858a79cc1298b2a605e43cdaecdd01d` |
| **macOS** | `TTEmbed-2.0.dmg` | Disk Image | `611e35ad5e06940e6a972cb0814712e25dd5c6c7006c8f3c1d8cbfecf651c6fd` |
| **Linux** | `TTEmbed-2.0.AppImage` | AppImage | `d864dd689b632c74fb529dc8aa972834046091bf9423083a8961765cf5785927` |

---

## ⚖️ Legal & EULA Disclaimer

Modifying font embedding permissions (`fsType`) alters technical binary file flags only. It does not grant, alter, or transfer copyright ownership, trademark rights, commercial usage rights, or foundry EULA permissions. Users remain strictly bound by the original font vendor's End User License Agreement (EULA). Always ensure you possess legitimate rights for commercial use or document distribution. **Use at your own risk.**

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
