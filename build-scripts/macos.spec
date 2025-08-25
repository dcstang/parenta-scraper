# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for macOS builds
Note: Chrome not bundled - users must install Chrome separately
"""
import os
import sys
from pathlib import Path

# Define paths relative to current directory
main_script = "simple_scraper.py"
batch_extractor = "batch_extractor.py"

a = Analysis(
    [main_script],
    pathex=[str(ROOT_DIR)],
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
    upx=False,  # UPX can cause issues on macOS
    console=False,  # GUI app, no terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Icon (add if you have one)
    # icon='assets/icon.icns',
)

# Create Mac app bundle
app = BUNDLE(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='ParentaScraper.app',
    # Icon for the app bundle
    # icon='assets/icon.icns',
    bundle_identifier='com.parentascraper.app',
    version='1.0.0',
    info_plist={
        'CFBundleName': 'Parenta Scraper',
        'CFBundleDisplayName': 'Parenta Scraper', 
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIdentifier': 'com.parentascraper.app',
        'LSMinimumSystemVersion': '10.15.0',  # macOS Catalina+
        'NSHighResolutionCapable': True,
        'LSApplicationCategoryType': 'public.app-category.utilities',
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': True,  # Allow HTTP requests for image downloads
        },
        'NSAppleEventsUsageDescription': 'This app needs to control Chrome for web scraping.',
        'NSNetworkVolumesUsageDescription': 'This app downloads images from the internet.',
    },
)

# Post-build information for build script
"""
After PyInstaller build completes, the build script should:

1. Create DMG installer with drag-to-Applications
2. Add README with Chrome installation instructions  
3. Test the .app bundle
4. Optional: Code sign the app for distribution

Chrome Detection on macOS:
- App will look for Chrome at /Applications/Google Chrome.app
- If not found, shows friendly error with download link
- No Chrome bundling on Mac (not feasible)

Directory structure after build:
dist/ParentaScraper.app/
├── Contents/
│   ├── Info.plist              # App metadata
│   ├── MacOS/
│   │   └── ParentaScraper      # Main executable
│   ├── Resources/              # App resources
│   │   ├── batch_extractor.py
│   │   └── ... (dependencies)  
│   └── Frameworks/             # Python framework (if needed)
"""