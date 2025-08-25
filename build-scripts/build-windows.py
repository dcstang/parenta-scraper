#!/usr/bin/env python3
"""
Windows build script for Parenta Scraper
Downloads Chrome Portable and creates Windows distribution
"""
import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

def main():
    print("Building Parenta Scraper for Windows...")
    
    # Paths
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"
    
    # Clean previous builds
    print("Cleaning previous builds...")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Build with PyInstaller
    print("Building executable with PyInstaller...")
    spec_file = "build-scripts/windows.spec"
    cmd = [sys.executable, "-m", "PyInstaller", spec_file, "--clean"]
    
    result = subprocess.run(cmd, cwd=root_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print("ERROR: PyInstaller failed:")
        print(result.stderr)
        return False
    
    print("SUCCESS: PyInstaller build completed")
    
    # Create Chrome installation guide  
    print("Creating Chrome installation guide...")
    create_chrome_install_guide(dist_dir / "ParentaScraper")
    
    # Create user-friendly files
    print("Creating user documentation...")
    create_windows_readme(dist_dir / "ParentaScraper")
    
    # Create ZIP package
    print("Creating ZIP package...")
    zip_path = dist_dir / "ParentaScraper-Windows.zip"
    create_zip_package(dist_dir / "ParentaScraper", zip_path)
    
    print(f"SUCCESS: Windows build complete: {zip_path}")
    print(f"Build directory: {dist_dir / 'ParentaScraper'}")
    
    return True

def create_chrome_install_guide(app_dir):
    """Create Chrome installation guide for Windows users"""
    guide_content = """# Installing Google Chrome for Parenta Scraper

## Why Chrome is Required
Parenta Scraper uses Chrome to access the Parenta website and download your photos.

## Installation Steps

### Method 1: Direct Download (Recommended)
1. Visit: https://www.google.com/chrome/
2. Click "Download Chrome"
3. Run the downloaded installer
4. Follow the installation wizard
5. Done!

### Method 2: Using Windows Package Manager (Advanced)
If you have winget installed:
```
winget install Google.Chrome
```

## Verification
After installation, Chrome should be available at one of these locations:
- C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe
- C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe
- %LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe

## Troubleshooting
- **"Chrome not found"**: Make sure Chrome is fully installed
- **Installation blocked**: Check Windows SmartScreen settings
- **Alternative**: Install Microsoft Edge (Chromium) instead - it also works

## Alternative Browsers
Parenta Scraper also works with:
- Microsoft Edge (pre-installed on Windows 10/11)
- Chromium (free, open-source version)

The app will automatically detect any compatible browser.

## First Run
When you first run Parenta Scraper:
1. It will automatically find your Chrome installation
2. If Chrome isn't found, you'll see a helpful error message
3. Install Chrome using the steps above, then try again

## Support
- Chrome download: https://www.google.com/chrome/
- For app issues: https://github.com/[your-username]/parenta-scraper/issues
"""
    
    guide_path = app_dir / "Install-Chrome-Guide.txt"
    guide_path.write_text(guide_content)

def create_windows_readme(app_dir):
    """Create README for Windows users"""
    readme_content = """# Parenta Scraper for Windows

## Quick Start
1. Double-click `ParentaScraper.exe` to run
2. Enter your Parenta login credentials  
3. Click "Test (Last 20)" to try it out
4. Click "Full Scrape" to download all your photos

## What it does
- Downloads all photos and videos from your Parenta nursery account
- Saves photos to your home directory in `Nursery_Downloads_[Mode]` folder
- Creates a CSV file with all the post data

## Requirements
- Windows 10 or later
- Google Chrome browser (see Install-Chrome-Guide.txt)
- Internet connection  
- Valid Parenta nursery account

## First-Time Setup
1. Install Google Chrome (if not already installed)
   - See `Install-Chrome-Guide.txt` for detailed instructions
   - Or visit: https://www.google.com/chrome/
2. Double-click `ParentaScraper.exe`
3. Enter your credentials and start downloading!

## Files
- `ParentaScraper.exe` - Main application
- `Install-Chrome-Guide.txt` - Chrome installation instructions
- `_internal/` - Application dependencies (don't modify)

## Troubleshooting
- **"Chrome not found"**: Install Chrome first (see Install-Chrome-Guide.txt)
- **Chrome fails to start**: Try running as administrator
- Check your internet connection
- Make sure your Parenta credentials are correct
- Photos are saved to: `C:\\Users\\[YourName]\\Nursery_Downloads_[Mode]\\`

## Support
For issues, visit: https://github.com/[your-username]/parenta-scraper/issues

Generated by Parenta Scraper build system
"""
    
    readme_path = app_dir / "README.txt"
    readme_path.write_text(readme_content)

def create_zip_package(source_dir, zip_path):
    """Create ZIP package for distribution"""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in source_dir.rglob('*'):
            if file_path.is_file():
                arc_name = file_path.relative_to(source_dir)
                zipf.write(file_path, arc_name)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)