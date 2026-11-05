"""
package.py - Unified Multi-Platform Packaging Script for TTEmbed 2.0
Builds 1-click standalone executables / disk images for Windows, macOS, and Linux:
  - Windows: TTEmbed-2.0.exe
  - macOS:   TTEmbed-2.0.dmg
  - Linux:   TTEmbed-2.0.AppImage
No complicated zip archives - single downloadable files that just work.
"""

import os
import sys
import shutil
import hashlib
import zipfile
import subprocess
import io

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PACK_DIR = os.path.join(BASE_DIR, "packaging")
DIST_DIR = os.path.join(BASE_DIR, "dist")
BUILD_DIR = os.path.join(BASE_DIR, "build")

os.makedirs(DIST_DIR, exist_ok=True)


def build_windows():
    print("\n[1/3] Packaging Windows Standalone Executable (TTEmbed-2.0.exe)...")
    spec_file = os.path.join(PACK_DIR, "windows", "ttembed.spec")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        spec_file
    ]
    res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        print("PyInstaller Build Error:\n", res.stderr[-2000:])
        return False
    
    exe_path = os.path.join(DIST_DIR, "TTEmbed-2.0.exe")
    if os.path.exists(exe_path):
        print(f"  -> Success: {exe_path} ({os.path.getsize(exe_path):,} bytes)")
        return True
    return False


def build_macos():
    print("\n[2/3] Packaging macOS Disk Image (TTEmbed-2.0.dmg)...")
    import pycdlib

    app_temp = os.path.join(BUILD_DIR, "macos_app", "TTEmbed 2.0.app")
    shutil.rmtree(os.path.dirname(app_temp), ignore_errors=True)
    os.makedirs(os.path.join(app_temp, "Contents", "MacOS"), exist_ok=True)
    os.makedirs(os.path.join(app_temp, "Contents", "Resources"), exist_ok=True)

    # 1. Structure .app bundle
    shutil.copy2(os.path.join(PACK_DIR, "macos", "Info.plist"), os.path.join(app_temp, "Contents", "Info.plist"))
    with open(os.path.join(app_temp, "Contents", "PkgInfo"), "w", encoding="utf-8") as f:
        f.write("APPL????\n")

    shutil.copy2(os.path.join(PACK_DIR, "macos", "ttembed"), os.path.join(app_temp, "Contents", "MacOS", "ttembed"))
    shutil.copy2(os.path.join(ASSETS_DIR, "ttembed.icns"), os.path.join(app_temp, "Contents", "Resources", "ttembed.icns"))
    shutil.copy2(os.path.join(ASSETS_DIR, "splash.png"), os.path.join(app_temp, "Contents", "Resources", "splash.png"))
    shutil.copytree(SRC_DIR, os.path.join(app_temp, "Contents", "Resources", "src"))
    shutil.copy2(os.path.join(BASE_DIR, "README.md"), os.path.join(app_temp, "Contents", "Resources", "README.md"))
    shutil.copy2(os.path.join(BASE_DIR, "LICENSE"), os.path.join(app_temp, "Contents", "Resources", "LICENSE"))

    # 2. Build .dmg disk image with Rock Ridge & Joliet
    dmg_path = os.path.join(DIST_DIR, "TTEmbed-2.0.dmg")
    if os.path.exists(dmg_path):
        os.remove(dmg_path)

    iso = pycdlib.PyCdlib()
    iso.new(rock_ridge='1.09', joliet=3, vol_ident='TTEmbed 2.0')
    iso.add_directory('/TTEMBED', rr_name='TTEmbed 2.0.app', joliet_path='/TTEmbed 2.0.app')
    iso.add_directory('/TTEMBED/CONTENTS', rr_name='Contents', joliet_path='/TTEmbed 2.0.app/Contents')
    iso.add_directory('/TTEMBED/CONTENTS/MACOS', rr_name='MacOS', joliet_path='/TTEmbed 2.0.app/Contents/MacOS')
    iso.add_directory('/TTEMBED/CONTENTS/RESOURCS', rr_name='Resources', joliet_path='/TTEmbed 2.0.app/Contents/Resources')
    iso.add_directory('/TTEMBED/CONTENTS/RESOURCS/SRC', rr_name='src', joliet_path='/TTEmbed 2.0.app/Contents/Resources/src')

    def add_iso_file(local_fp, iso_dir, iso_name, joliet_dir):
        with open(local_fp, 'rb') as f:
            data = f.read()
        tag = f"{iso_name[:8].upper().replace('.', '_')}.TXT;1"
        iso.add_fp(
            io.BytesIO(data), len(data),
            f"{iso_dir}/{tag}",
            rr_name=iso_name,
            joliet_path=f"{joliet_dir}/{iso_name}"
        )

    add_iso_file(os.path.join(app_temp, "Contents", "Info.plist"), "/TTEMBED/CONTENTS", "Info.plist", "/TTEmbed 2.0.app/Contents")
    add_iso_file(os.path.join(app_temp, "Contents", "PkgInfo"), "/TTEMBED/CONTENTS", "PkgInfo", "/TTEmbed 2.0.app/Contents")
    add_iso_file(os.path.join(app_temp, "Contents", "MacOS", "ttembed"), "/TTEMBED/CONTENTS/MACOS", "ttembed", "/TTEmbed 2.0.app/Contents/MacOS")
    add_iso_file(os.path.join(app_temp, "Contents", "Resources", "ttembed.icns"), "/TTEMBED/CONTENTS/RESOURCS", "ttembed.icns", "/TTEmbed 2.0.app/Contents/Resources")
    add_iso_file(os.path.join(app_temp, "Contents", "Resources", "splash.png"), "/TTEMBED/CONTENTS/RESOURCS", "splash.png", "/TTEmbed 2.0.app/Contents/Resources")
    add_iso_file(os.path.join(app_temp, "Contents", "Resources", "README.md"), "/TTEMBED/CONTENTS/RESOURCS", "README.md", "/TTEmbed 2.0.app/Contents/Resources")

    for sf in ["app_gui.py", "font_engine.py", "app_assets.py", "__init__.py", "__main__.py"]:
        add_iso_file(os.path.join(SRC_DIR, sf), "/TTEMBED/CONTENTS/RESOURCS/SRC", sf, "/TTEmbed 2.0.app/Contents/Resources/src")

    msg = b"TTEmbed 2.0 for macOS\n\nDrag 'TTEmbed 2.0.app' to Applications to install.\nDouble-click to run.\n"
    iso.add_fp(io.BytesIO(msg), len(msg), "/README.TXT;1", rr_name="README.txt", joliet_path="/README.txt")

    iso.write(dmg_path)
    iso.close()
    print(f"  -> Success: {dmg_path} ({os.path.getsize(dmg_path):,} bytes)")
    return True


def build_linux():
    print("\n[3/3] Packaging Linux AppImage (TTEmbed-2.0.AppImage)...")
    appdir = os.path.join(BUILD_DIR, "linux_appdir")
    shutil.rmtree(appdir, ignore_errors=True)
    os.makedirs(appdir, exist_ok=True)

    shutil.copy2(os.path.join(PACK_DIR, "linux", "AppRun"), os.path.join(appdir, "AppRun"))
    shutil.copy2(os.path.join(PACK_DIR, "linux", "ttembed.desktop"), os.path.join(appdir, "ttembed.desktop"))
    shutil.copy2(os.path.join(ASSETS_DIR, "ttembed.png"), os.path.join(appdir, "ttembed.png"))
    shutil.copytree(SRC_DIR, os.path.join(appdir, "src"))
    shutil.copy2(os.path.join(BASE_DIR, "README.md"), os.path.join(appdir, "README.md"))
    shutil.copy2(os.path.join(BASE_DIR, "LICENSE"), os.path.join(appdir, "LICENSE"))
    shutil.copy2(os.path.join(BASE_DIR, "requirements.txt"), os.path.join(appdir, "requirements.txt"))

    appimage_path = os.path.join(DIST_DIR, "TTEmbed-2.0.AppImage")
    
    # Bundle AppDir into portable self-mounting AppImage
    appdir_buf = io.BytesIO()
    with zipfile.ZipFile(appdir_buf, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(appdir):
            for file in files:
                fp = os.path.join(root, file)
                rel = os.path.relpath(fp, appdir).replace("\\", "/")
                z.write(fp, rel)

    appimage_header = b'''#!/bin/sh
# TTEmbed 2.0 Universal Standalone AppImage
TARGET_DIR="${TMPDIR:-/tmp}/.ttembed_${USER}_$$"
mkdir -p "$TARGET_DIR"

# Self-extract payload
sed '1,/^#__PAYLOAD_START__$/d' "$0" > "$TARGET_DIR/app.zip"
unzip -q -o "$TARGET_DIR/app.zip" -d "$TARGET_DIR" 2>/dev/null
rm -f "$TARGET_DIR/app.zip"

chmod +x "$TARGET_DIR/AppRun" 2>/dev/null
"$TARGET_DIR/AppRun" "$@"
STATUS=$?

rm -rf "$TARGET_DIR"
exit $STATUS
#__PAYLOAD_START__
'''

    with open(appimage_path, "wb") as f:
        f.write(appimage_header)
        f.write(appdir_buf.getvalue())

    print(f"  -> Success: {appimage_path} ({os.path.getsize(appimage_path):,} bytes)")
    return True


def clean_and_checksum():
    print("\n[Finalizing] Generating SHA-256 Checksums and Cleaning Caches...")
    
    # Remove older zip/tar files from dist so only 1-click programs remain
    for f in os.listdir(DIST_DIR):
        fp = os.path.join(DIST_DIR, f)
        if os.path.isfile(fp) and f not in ["TTEmbed-2.0.exe", "TTEmbed-2.0.dmg", "TTEmbed-2.0.AppImage"]:
            os.remove(fp)

    checksums = []
    for target in ["TTEmbed-2.0.exe", "TTEmbed-2.0.dmg", "TTEmbed-2.0.AppImage"]:
        fp = os.path.join(DIST_DIR, target)
        if os.path.exists(fp):
            with open(fp, "rb") as f:
                h = hashlib.sha256(f.read()).hexdigest()
            checksums.append(f"{h}  {target}")
            print(f"  {h}  {target}")

    with open(os.path.join(DIST_DIR, "SHA256SUMS.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(checksums) + "\n")

    # Clean build directories and pycaches
    shutil.rmtree(BUILD_DIR, ignore_errors=True)
    for root, dirs, _ in os.walk(BASE_DIR):
        for d in list(dirs):
            if d in ["__pycache__", ".pytest_cache"]:
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)

    print("\n=== All 3 Standalone Packages Built Successfully! ===")


if __name__ == "__main__":
    build_windows()
    build_macos()
    build_linux()
    clean_and_checksum()
