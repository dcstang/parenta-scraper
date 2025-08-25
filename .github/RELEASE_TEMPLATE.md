# Parenta Scraper Release Template

Use this template when creating manual releases.

## Release Checklist

### Before Release
- [ ] Test the app manually on WSL2/Linux
- [ ] Verify all dependencies in requirements.txt
- [ ] Update version in pyproject.toml if needed
- [ ] Test build scripts locally (optional)

### Creating Release
1. Go to GitHub → Releases → "Create a new release"
2. Tag: `v1.0.0` (increment version number)
3. Title: `Parenta Scraper v1.0.0`
4. Use description template below
5. Click "Publish release"
6. GitHub Actions will automatically build all platforms

### Release Description Template

```markdown
## Parenta Scraper Release v1.0.0

Download your child's photos from Parenta nursery portal with one click!

### 📥 Downloads
- **Windows**: `ParentaScraper-Windows.zip` (requires Chrome installation)
- **macOS**: `ParentaScraper-Mac.dmg` (requires Chrome installation) 
- **Linux**: `ParentaScraper-Linux.tar.gz` (requires Chrome/Chromium)

### 🚀 Quick Start
1. Download the file for your operating system
2. Install Google Chrome (if not already installed)
3. Extract/install and run the application
4. Enter your Parenta login credentials
5. Click "Test (Last 20)" or "Full Scrape"

### 📋 Requirements
- Google Chrome browser
- Valid Parenta nursery account
- Internet connection

### 🆕 What's New in v1.0.0
- Initial release
- Cross-platform executable (Windows, macOS, Linux)
- Automatic ChromeDriver management
- Fast JavaScript-based data extraction
- Parallel image downloading
- Parent-friendly error messages

### 🛠️ Troubleshooting
- **Chrome not found**: Install Chrome first from https://www.google.com/chrome/
- **Login issues**: Check your credentials at https://parentportal.parenta.com/
- **No photos found**: Try "Test (Last 20)" first to verify setup

Built with ❤️ for parents who want their memories back!
```

### After Release
- [ ] Verify all 3 platform downloads work
- [ ] Test downloads on different machines if possible
- [ ] Monitor GitHub Issues for user reports
- [ ] Consider announcing in relevant communities

## Manual Build Testing (Optional)

If you want to test builds locally before release:

```bash
# Test current platform
python build-scripts/build-all.py

# Test specific platform (if you have the environment)
python build-scripts/build-windows.py
python build-scripts/build-macos.py  
python build-scripts/build-linux.py
```

## Hotfix Process

For critical bugs requiring immediate fix:

1. Fix the bug in code
2. Create hotfix release: `v1.0.1`
3. GitHub Actions will rebuild automatically
4. Notify users in GitHub Issues if needed