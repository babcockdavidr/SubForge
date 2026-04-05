# subforge.spec
# PyInstaller build specification for SubForge.
#
# Usage (run from the repo root):
#   Windows:  python -m PyInstaller subforge.spec --clean
#   macOS:    python -m PyInstaller subforge.spec --clean
#   Linux:    python -m PyInstaller subforge.spec --clean
#
# Always use --clean to avoid stale cache issues from previous builds.
#
# Output:
#   dist/SubForge/          one-folder build (use this for testing)
#   dist/SubForge.exe       Windows one-file build  (after --onefile, not used here)
#
# We use onedir (not onefile) because:
#   - Startup is instant — no extraction step on every launch
#   - Easier to debug if something is missing
#   - The GitHub Actions workflow zips the folder for distribution
#
# PyInstaller docs: https://pyinstaller.org/en/stable/spec-files.html

import sys
from pathlib import Path

HERE = Path(SPECPATH)   # repo root — PyInstaller sets SPECPATH automatically

# ---------------------------------------------------------------------------
# Data files to bundle (read-only assets that live inside the bundle)
# ---------------------------------------------------------------------------
# Format: (source_path, dest_path_inside_bundle)
# dest_path is relative to sys._MEIPASS at runtime.

added_data = [
    # Regex profiles — read by core/cleaner.py and gui/regex_editor.py
    # Source: regex_profiles/default/  →  Bundle: regex_profiles/default/
    (str(HERE / "regex_profiles" / "default"), "regex_profiles/default"),
]

# ---------------------------------------------------------------------------
# Analysis — PyInstaller traces all imports from the entry point
# ---------------------------------------------------------------------------

a = Analysis(
    [str(HERE / "subforge.py")],        # entry point
    pathex=[str(HERE)],                  # add repo root to import search path
    binaries=[],                         # no extra native binaries needed
    datas=added_data,
    hiddenimports=[
        # PyQt6 platform plugins are loaded dynamically and not always
        # detected by PyInstaller's static analysis — list them explicitly.
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.sip",
        # pysubs2 parsers are imported by name at runtime
        "pysubs2",
        "pysubs2.formats",
        "pysubs2.formats.subrip",
        "pysubs2.formats.advanced_substation_alpha",
        "pysubs2.formats.substation_alpha",
        "pysubs2.formats.webvtt",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy stdlib modules we don't use — keeps bundle smaller
        "tkinter",
        "unittest",
        "pydoc",
    ],
    noarchive=False,
)

# ---------------------------------------------------------------------------
# PYZ — compressed bytecode archive
# ---------------------------------------------------------------------------

pyz = PYZ(a.pure)

# ---------------------------------------------------------------------------
# EXE — the actual executable
# ---------------------------------------------------------------------------

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,          # onedir mode — binaries go in COLLECT
    name="SubForge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                       # compress with UPX if available (optional)
    console=False,                  # no terminal window on Windows/macOS
    disable_windowed_traceback=False,
    # icon= — add per-platform below once an icon file exists
    # Windows: icon="assets/subforge.ico"
    # macOS:   icon="assets/subforge.icns"
)

# ---------------------------------------------------------------------------
# COLLECT — gather everything into dist/SubForge/
# ---------------------------------------------------------------------------

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SubForge",                # output folder name: dist/SubForge/
)

# ---------------------------------------------------------------------------
# macOS .app bundle (ignored on Windows/Linux)
# ---------------------------------------------------------------------------

app = BUNDLE(
    coll,
    name="SubForge.app",
    # icon="assets/subforge.icns",  # uncomment when icon exists
    bundle_identifier="com.babcockdavidr.subforge",
    info_plist={
        "CFBundleShortVersionString": "0.9.0",
        "CFBundleVersion":            "0.9.0",
        "NSHighResolutionCapable":    True,
        "LSMinimumSystemVersion":     "10.15",  # macOS Catalina+
    },
)
