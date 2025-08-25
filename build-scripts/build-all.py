#!/usr/bin/env python3
"""
Master build script for Parenta Scraper
Builds for current platform or all platforms (if running in CI)
"""
import os
import sys
import platform
import subprocess
from pathlib import Path

def main():
    print("🔨 Parenta Scraper Master Build Script")
    
    script_dir = Path(__file__).parent
    current_platform = platform.system().lower()
    
    # Detect platform and run appropriate build
    if current_platform == "windows":
        print("🪟 Building for Windows...")
        return run_build_script(script_dir / "build-windows.py")
    elif current_platform == "darwin":
        print("🍎 Building for macOS...")
        return run_build_script(script_dir / "build-macos.py")
    elif current_platform == "linux":
        print("🐧 Building for Linux...")
        return run_build_script(script_dir / "build-linux.py")
    else:
        print(f"❌ Unsupported platform: {current_platform}")
        return False

def run_build_script(script_path):
    """Run a build script and return success status"""
    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run build script: {e}")
        return False

def show_usage():
    """Show usage information"""
    print("""
Usage: python build-all.py

This script automatically detects your platform and runs the appropriate build:
- Windows: Builds .exe with Chrome Portable bundling
- macOS: Builds .app bundle with DMG installer  
- Linux: Builds executable with Chrome install helpers

Individual platform builds:
- python build-windows.py
- python build-macos.py
- python build-linux.py

Requirements:
- Python 3.12+
- PyInstaller installed (pip install pyinstaller)
- Platform-specific tools:
  - Windows: 7zip (for Chrome Portable extraction)
  - macOS: hdiutil (for DMG creation, built-in)
  - Linux: tar (built-in)
""")

if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        show_usage()
        sys.exit(0)
    
    success = main()
    
    if success:
        print("✅ Build completed successfully!")
        print("📦 Check the 'dist/' directory for your platform's build")
    else:
        print("❌ Build failed")
    
    sys.exit(0 if success else 1)