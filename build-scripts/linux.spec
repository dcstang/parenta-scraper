# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Linux builds
Uses system Chrome/Chromium installations
"""
import os
import sys
from pathlib import Path

# Define paths relative to current directory
main_script = "simple_scraper.py"
batch_extractor = "batch_extractor.py"

a = Analysis(
    [main_script],
    pathex=[],
    binaries=[],
    datas=[
        # Include batch_extractor.py as data file
        (batch_extractor, '.'),
        # Include any other data files here
    ],
    hiddenimports=[
        # Selenium and webdriver-manager hidden imports
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.chrome.options', 
        'selenium.webdriver.common.by',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support.expected_conditions',
        'selenium.common.exceptions',
        'webdriver_manager.chrome',
        'webdriver_manager.core.utils',
        # CustomTkinter hidden imports
        'customtkinter',
        'tkinter',
        'tkinter.ttk',
        # PIL/Pillow hidden imports  
        'PIL._tkinter_finder',
        # Requests hidden imports
        'requests.packages.urllib3',
        'urllib3',
        # Standard library that might be missed
        'concurrent.futures',
        'threading',
        'platform',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib', 'numpy', 'scipy', 'pandas',
        'jupyter', 'IPython',
        'test', 'tests', 'testing',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ParentaScraper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Strip debug symbols on Linux
    upx=True,
    console=False,  # GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=[],
    name='ParentaScraper',
)

# Post-build information for build script
"""
After PyInstaller build completes, the build script should:

1. Create .tar.gz archive
2. Add install script for Chrome dependencies
3. Create .desktop file for GUI integration
4. Test the executable

Chrome Detection on Linux:
- App will look for system Chrome/Chromium installations
- Common locations: /usr/bin/google-chrome, /usr/bin/chromium-browser
- If not found, guides user to install via package manager
- Could potentially bundle Chrome Linux in the future

Directory structure after build:
dist/ParentaScraper/
├── ParentaScraper              # Main executable
├── batch_extractor.py          # Python module  
├── _internal/                  # PyInstaller dependencies
│   ├── base_library.zip
│   ├── *.so (shared libraries)
│   └── ... (dependencies)
├── install-chrome.sh           # Helper script (added by build script)
├── ParentaScraper.desktop      # Desktop integration file
└── README.txt                  # Usage instructions

Installation files to create:
- ParentaScraper.desktop for /usr/share/applications/
- install-chrome.sh with platform detection (apt/yum/pacman)
"""