# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Windows builds with Chrome Portable bundling
"""
import os
import sys
from pathlib import Path

# Define paths relative to current directory
import os
main_script = os.path.join(os.getcwd(), "simple_scraper.py")
batch_extractor = os.path.join(os.getcwd(), "batch_extractor.py")

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
    strip=False,
    upx=True,
    console=False,  # Windowed app, no console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Windows-specific options
    version=None,
    uac_admin=False,  # Don't require admin rights
    uac_uiaccess=False,
    # Icon (add if you have one)
    # icon='assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ParentaScraper',
    # This creates a directory with all files
    # chrome-portable will be copied here by build script
)

# Post-build hook information for build script
"""
After PyInstaller build completes, the build script should:

1. Create installer or zip file
2. Add Chrome installation guide
3. Test the executable

Directory structure after build:
dist/ParentaScraper/
├── ParentaScraper.exe           # Main executable  
├── batch_extractor.py           # Python module
├── _internal/                   # PyInstaller dependencies
│   ├── base_library.zip
│   ├── *.dll
│   └── ... (dependencies)
├── README.txt                   # Usage instructions
└── Install-Chrome-Guide.txt     # Chrome installation guide
"""