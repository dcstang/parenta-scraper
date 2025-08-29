#!/usr/bin/env python3
"""
macOS Intel build script for Parenta Scraper
Creates Intel x86_64 Mac app bundle and DMG installer specifically for Intel chipsets
Supports older Mac hardware from 2015+ with Intel processors
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    print("Building Parenta Scraper for macOS Intel (x86_64)...")
    
    # Paths
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"
    
    # Clean previous builds
    print("[CLEAN] Cleaning previous builds...")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Build with PyInstaller using Intel-specific spec
    print("[PACK] Building Intel x86_64 app bundle with PyInstaller...")
    spec_file = "build-scripts/macos-intel.spec"
    cmd = [sys.executable, "-m", "PyInstaller", spec_file, "--clean"]
    
    result = subprocess.run(cmd, cwd=root_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: PyInstaller failed:")
        print(result.stderr)
        return False
    
    print("SUCCESS: PyInstaller Intel build completed")
    
    # Verify Intel architecture
    print("[VERIFY] Checking architecture...")
    app_executable = dist_dir / "ParentaScraper.app" / "Contents" / "MacOS" / "ParentaScraper"
    if app_executable.exists():
        try:
            result = subprocess.run(["file", str(app_executable)], capture_output=True, text=True)
            if "x86_64" in result.stdout:
                print("✓ Confirmed Intel x86_64 architecture")
            else:
                print(f"WARNING: Architecture verification unclear: {result.stdout}")
        except Exception as e:
            print(f"WARNING: Could not verify architecture: {e}")
    
    # Create user documentation
    print("[DOC] Creating Intel-specific user documentation...")
    create_macos_intel_readme(dist_dir)
    create_chrome_intel_install_guide(dist_dir)
    
    # Create DMG (if hdiutil available)
    print("[DMG] Creating Intel DMG installer...")
    dmg_path = create_dmg_installer(dist_dir)
    
    if dmg_path:
        print(f"SUCCESS: macOS Intel build complete: {dmg_path}")
    else:
        print(f"SUCCESS: macOS Intel build complete: {dist_dir / 'ParentaScraper.app'}")
    
    print(f"Build directory: {dist_dir}")
    print("\n" + "="*50)
    print("INTEL MAC BUILD NOTES:")
    print("- Built specifically for Intel x86_64 processors")
    print("- Compatible with MacBook Air/Pro 2015-2020, iMac, Mac Mini Intel models")
    print("- Requires macOS 10.13 (High Sierra) or later")
    print("- Will also run on Apple Silicon Macs via Rosetta 2")
    print("="*50)
    
    return True

def create_macos_intel_readme(dist_dir):
    """Create README specifically for Intel Mac users"""
    readme_content = """# Parenta Scraper for macOS Intel

## Intel Mac Compatibility
This version is specifically built for Intel-based Mac computers including:
- MacBook Air (2015-2020)  
- MacBook Pro (2015-2019)
- iMac (2015-2020)
- iMac Pro (2017-2021)
- Mac Mini (2014-2020) 
- Mac Pro (2013-2019)

## Installation
1. Drag ParentaScraper.app to your Applications folder
2. Install Google Chrome (see Chrome-Install-Guide.txt)
3. Double-click ParentaScraper.app to run

## System Requirements
- **macOS 10.13 (High Sierra) or later**
- **Intel x86_64 processor** (Core i3, i5, i7, i9, or Xeon)
- **Google Chrome installed**
- **Internet connection**
- **Valid Parenta nursery account**

## Will this run on my Mac?
- ✓ Intel Mac (2015-2020): **Yes, this is designed for you!**
- ✓ Apple Silicon Mac (M1/M2): **Yes, via Rosetta 2**
- ✗ Very old Intel Macs (pre-2015): **May not work**

To check your Mac type:
1. Click  menu > About This Mac
2. Look at "Processor" line
3. If it says "Intel", this version is for you!

## Important: Chrome Required
This app requires Google Chrome to be installed at:
/Applications/Google Chrome.app

For Intel Macs, download Chrome from: https://www.google.com/chrome/
(Chrome will automatically detect your Intel processor)

## Quick Start
1. Open ParentaScraper from Applications
2. Enter your Parenta login credentials
3. Click "Test (Last 20)" to try it out
4. Click "Full Scrape" to download all your photos

## What it does
- Downloads all photos and videos from your Parenta nursery account
- Saves photos to your home directory in `Nursery_Downloads_[Mode]` folder
- Creates a CSV file with all the post data

## Security Note
When you first run the app, macOS may show a security warning because this is an Intel app.
To allow the app:
1. Go to System Preferences > Security & Privacy
2. Click "Allow" next to the blocked app message
3. Or right-click the app and select "Open"

## Troubleshooting
- **"App can't be opened"**: Right-click app > Open, then click Open in dialog
- **Chrome not found**: Install Chrome from https://www.google.com/chrome/
- **Slow performance**: This is normal - Intel apps run fine but may be slower on M1/M2 Macs
- **Internet issues**: Check your connection and firewall settings
- **Login problems**: Verify your Parenta credentials are correct
- **Photos location**: `/Users/[YourName]/Nursery_Downloads_[Mode]/`

## Performance Notes
- **Intel Macs**: Full native performance
- **Apple Silicon Macs**: Runs via Rosetta 2 - slightly slower but fully functional

## Support
For issues, visit: https://github.com/[your-username]/parenta-scraper/issues

Generated by Parenta Scraper Intel build system
Built specifically for Intel x86_64 processors
"""
    
    readme_path = dist_dir / "README-Intel.txt"
    readme_path.write_text(readme_content)

def create_chrome_intel_install_guide(dist_dir):
    """Create Chrome installation guide for Intel Macs"""
    guide_content = """# Installing Google Chrome for Intel Mac

## Chrome for Intel Processors
This guide is specifically for Intel-based Mac computers.

## Why Chrome is Required
Parenta Scraper uses Chrome to access the Parenta website and download your photos.
Chrome must be installed separately (we cannot bundle it on Mac).

## Installation Steps for Intel Mac

### Method 1: Direct Download (Recommended)
1. Visit: https://www.google.com/chrome/
2. Click "Download Chrome for Mac"
3. Chrome will automatically detect your Intel processor
4. Open the downloaded file (GoogleChrome.dmg)
5. Drag Chrome to your Applications folder
6. Done!

### Method 2: Using Homebrew (Advanced)
If you have Homebrew installed:
```
brew install --cask google-chrome
```

## Intel vs Apple Silicon
- **Intel Mac users**: Download will automatically get Intel version
- **M1/M2 Mac users**: You can use this Intel build, or get the regular Apple Silicon version

## Verification
After installation, you should see:
- Google Chrome.app in your Applications folder
- Path: /Applications/Google Chrome.app

To verify Chrome architecture (Intel Macs only):
1. Right-click Chrome in Applications
2. Get Info
3. Should show "Kind: Application (Intel)" or similar

## Troubleshooting
- **Chrome won't open**: Right-click > Open (bypasses security warning)
- **Parenta Scraper can't find Chrome**: Make sure Chrome is in /Applications/
- **Chrome crashes**: Try restarting your Mac, then Chrome
- **Slow Chrome**: Normal on older Intel Macs with limited RAM

## Alternative Browsers
If Chrome doesn't work, you can try Chromium:
- Download from: https://www.chromium.org/
- Or with Homebrew: `brew install --cask chromium`

The app will automatically detect either Chrome or Chromium.

## Intel Mac Performance Tips
- Close other apps while running Parenta Scraper
- Ensure you have at least 4GB free RAM
- Chrome may use significant CPU - this is normal
- Older MacBook Airs may run warm during scraping

## Supported Intel Mac Models
This Chrome installation works on:
- MacBook Air (2015-2020)
- MacBook Pro (2015-2019) 
- iMac (2015-2020)
- iMac Pro (2017-2021)
- Mac Mini (2014-2020)
- Mac Pro (2013-2019)

Generated by Parenta Scraper Intel build system
"""
    
    guide_path = dist_dir / "Chrome-Install-Guide-Intel.txt"
    guide_path.write_text(guide_content)

def create_dmg_installer(dist_dir):
    """Create DMG installer for Intel Mac distribution"""
    try:
        app_path = dist_dir / "ParentaScraper.app"
        dmg_path = dist_dir / "ParentaScraper-Mac-Intel.dmg"
        
        if not app_path.exists():
            print("ERROR: App bundle not found, skipping DMG creation")
            return None
        
        # Create DMG using hdiutil
        cmd = [
            "hdiutil", "create",
            "-srcfolder", str(app_path),
            "-volname", "Parenta Scraper Intel",
            "-format", "UDZO",
            "-o", str(dmg_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"WARNING: DMG creation failed (hdiutil not available): {result.stderr}")
            return None
        
        print("SUCCESS: Intel DMG created successfully")
        return dmg_path
        
    except Exception as e:
        print(f"WARNING: DMG creation failed: {e}")
        return None

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)