#!/usr/bin/env python3
"""
Simple Parenta Scraper with tkinter GUI
Works on Windows, macOS, and Linux (including WSL2)
"""

import customtkinter as ctk
import threading
import time
import os
import platform
import requests
import csv
from pathlib import Path
from PIL import Image
import io
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from batch_extractor import extract_all_posts_javascript, extract_all_posts_with_carousel_images_js
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# Configuration
LOGIN_URL = 'https://parentportal.parenta.com/carer-login'
USERNAME_FIELD_SELECTOR = "input[type='email'], input[placeholder*='Email'], input[name*='email'], input[data-id*='email']"
PASSWORD_FIELD_SELECTOR = "input[type='password'], input[placeholder*='Password'], input[name*='password'], input[data-id*='password']"
LOGIN_BUTTON_SELECTOR = "button[type='submit'], button:contains('Log in'), button[data-id*='login'], button[data-id*='Log-in']"
NEWSFEED_ITEM_SELECTOR = "div[data-id*='newsfeed-event-wrapper']"
DATE_SELECTOR = "div[data-id='newsfeed-event-date']"
TIME_SELECTOR = "span[data-id='newsfeed-event-time-mobile-only']"
CONTENT_SELECTOR = "span[data-id='newsfeed-event-title']"
EVENT_TYPE_SELECTOR = "span[data-id='newsfeed-event-type']"
MAIN_IMAGE_SELECTOR = "img"
GALLERY_INDICATOR_SELECTOR = "[class*='circle']"
PHOTO_CONTAINER_SELECTOR = "div[class*='photo'], div[class*='image-area']"

def show_error_dialog(parent, title, message):
    """Show a custom error dialog using customtkinter"""
    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
    y = (dialog.winfo_screenheight() // 2) - (200 // 2)
    dialog.geometry(f"400x200+{x}+{y}")
    
    # Error icon and message
    error_label = ctk.CTkLabel(dialog, text="❌", font=ctk.CTkFont(size=32))
    error_label.pack(pady=(20, 10))
    
    message_label = ctk.CTkLabel(dialog, text=message, font=ctk.CTkFont(size=14), wraplength=350)
    message_label.pack(pady=10, padx=20)
    
    # OK button
    ok_button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy, width=100)
    ok_button.pack(pady=20)
    
    # Focus on dialog
    dialog.focus_set()
    dialog.wait_window()

class ParentaScraper:
    def __init__(self, root):
        self.root = root
        self.root.title("Parenta Scraper")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Variables
        self.username_var = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.is_running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame with two columns
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left column for controls and status
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Right column for screenshot
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        
        # Title
        title_label = ctk.CTkLabel(left_frame, text="Parenta Scraper", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(20, 30))
        
        # Username frame
        username_frame = ctk.CTkFrame(left_frame)
        username_frame.pack(fill="x", padx=20, pady=10)
        
        username_label = ctk.CTkLabel(username_frame, text="Username:", font=ctk.CTkFont(size=14))
        username_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        username_entry = ctk.CTkEntry(username_frame, textvariable=self.username_var, width=400, height=35)
        username_entry.pack(padx=10, pady=(0, 10))
        
        # Password frame
        password_frame = ctk.CTkFrame(left_frame)
        password_frame.pack(fill="x", padx=20, pady=10)
        
        password_label = ctk.CTkLabel(password_frame, text="Password:", font=ctk.CTkFont(size=14))
        password_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        password_entry = ctk.CTkEntry(password_frame, textvariable=self.password_var, show="*", width=400, height=35)
        password_entry.pack(padx=10, pady=(0, 10))
        
        # Buttons frame
        button_frame = ctk.CTkFrame(left_frame)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        # Test button (first 50)
        self.test_button = ctk.CTkButton(
            button_frame, 
            text="Test (First 50)", 
            command=self.run_test,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.test_button.pack(side="left", padx=10, pady=10)
        
        # Full scrape button
        self.full_button = ctk.CTkButton(
            button_frame, 
            text="Full Scrape", 
            command=self.run_full,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.full_button.pack(side="left", padx=10, pady=10)
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(left_frame)
        self.progress.pack(fill="x", padx=20, pady=10)
        self.progress.set(0)
        
        # Status text frame
        status_frame = ctk.CTkFrame(left_frame)
        status_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        status_label = ctk.CTkLabel(status_frame, text="Status Log:", font=ctk.CTkFont(size=14, weight="bold"))
        status_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Status text with emoji-supporting font
        emoji_font = ctk.CTkFont(family="Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji, sans-serif", size=12)
        self.status_text = ctk.CTkTextbox(status_frame, width=500, height=300, font=emoji_font)
        self.status_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Screenshot display area
        screenshot_label = ctk.CTkLabel(right_frame, text="Browser View:", font=ctk.CTkFont(size=14, weight="bold"))
        screenshot_label.pack(pady=(20, 10))
        
        # Screenshot display
        self.screenshot_label = ctk.CTkLabel(right_frame, text="No screenshot yet", width=500, height=600)
        self.screenshot_label.pack(padx=10, pady=10)
        
    def log_message(self, message):
        """Add message to status text"""
        self.status_text.insert("end", f"{message}\n")
        self.status_text.see("end")
        self.root.update_idletasks()
        
    def take_screenshot(self, driver):
        """Take a screenshot and update the GUI"""
        try:
            # Take screenshot as PNG bytes
            screenshot_png = driver.get_screenshot_as_png()
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(screenshot_png))
            
            # Resize to fit in the GUI (500x600 area)
            image.thumbnail((500, 600), Image.Resampling.LANCZOS)
            
            # Convert to CTkImage for CustomTkinter
            photo = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
            
            # Update GUI in main thread
            self.root.after(0, self.update_screenshot, photo)
            
        except Exception as e:
            self.log_message(f"Screenshot failed: {e}")
    
    def update_screenshot(self, photo):
        """Update the screenshot in the GUI (must be called from main thread)"""
        try:
            self.screenshot_label.configure(image=photo, text="")
        except Exception as e:
            self.log_message(f"Screenshot update failed: {e}")
        
    def run_test(self):
        """Run test scrape (first 50 items)"""
        if self.is_running:
            return
        self.start_scraping("test")
        
    def run_full(self):
        """Run full scrape"""
        if self.is_running:
            return
        self.start_scraping("full")
        
    def start_scraping(self, mode):
        """Start scraping in a separate thread"""
        if not self.username_var.get() or not self.password_var.get():
            show_error_dialog(self.root, "Error", "Please enter username and password")
            return
            
        self.is_running = True
        self.test_button.configure(state='disabled')
        self.full_button.configure(state='disabled')
        self.progress.set(0)
        self.progress.start()
        
        # Clear status
        self.status_text.delete("1.0", "end")
        
        # Start scraping thread
        thread = threading.Thread(target=self.scraper_worker, args=(mode,))
        thread.daemon = True
        thread.start()
        
    def setup_platform_environment(self):
        """Setup environment based on platform detection"""
        platform_info = self.get_platform_info()
        
        if platform_info['is_wsl']:
            self.log_message("Setting up WSL2 environment...")
            # Set environment variables to avoid WSL2 issues
            os.environ['DISPLAY'] = ':0'
            os.environ['XDG_RUNTIME_DIR'] = '/tmp/runtime-root'
            
            # Create runtime directory if it doesn't exist
            try:
                os.makedirs('/tmp/runtime-root', exist_ok=True)
            except:
                pass
        elif platform_info['is_linux']:
            self.log_message("Setting up Linux environment...")
            # Native Linux might need DISPLAY set
            if not os.environ.get('DISPLAY'):
                os.environ['DISPLAY'] = ':0'
        else:
            self.log_message(f"Setting up {platform_info['system']} environment...")
            # Windows and Mac typically don't need special environment setup
            
    def create_chrome_options(self):
        """Create Chrome options for headed mode with screenshot capability"""
        chrome_options = Options()
        
        # Minimal options for WSL2 - keep only what's essential for the working configuration
        # chrome_options.add_argument("--headless")  # Confirmed: headless breaks ActionChains scrolling
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Window size and positioning
        chrome_options.add_argument("--window-size=800,1080")
        chrome_options.add_argument("--force-device-scale-factor=0.20")  # 20% zoom for content clarity
        chrome_options.add_argument("--start-minimized")  # Start minimized but still headed
        
        chrome_options.add_argument("--no-first-run")  # Skip first run setup
        chrome_options.add_argument("--no-default-browser-check")  # Skip default browser check
        chrome_options.add_argument("--disable-extensions")  # No extensions loading
        
        # Desktop user agent for proper infinite scroll behavior
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        return chrome_options
        
    def get_platform_info(self):
        """Get platform information for Chrome detection strategy"""
        system = platform.system().lower()
        return {
            'system': system,
            'is_windows': system == 'windows',
            'is_macos': system == 'darwin',
            'is_linux': system == 'linux',
            'is_wsl': 'microsoft' in platform.release().lower() if system == 'linux' else False
        }
    
    def find_chrome_binary(self):
        """Find Chrome/Chromium binary with platform-aware detection"""
        platform_info = self.get_platform_info()
        
        # Platform-specific Chrome paths in priority order
        if platform_info['is_windows']:
            chrome_paths = [
                "./chrome-portable/chrome.exe",  # Bundled portable Chrome (highest priority)
                "./chrome/chrome.exe",           # Alternative bundle location
                os.path.expandvars("$LOCALAPPDATA/Google/Chrome/Application/chrome.exe"),  # User install
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",              # System install
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",       # 32-bit system
            ]
        elif platform_info['is_macos']:
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # Standard Mac install
                "/Applications/Chromium.app/Contents/MacOS/Chromium",            # Chromium alternative
                os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),  # User install
            ]
        else:  # Linux/WSL
            chrome_paths = [
                "./chrome-linux/chrome",         # Bundled Chrome (if we add Linux bundling)
                "/usr/bin/google-chrome",        # apt/yum install
                "/usr/bin/chromium-browser",     # Ubuntu/Debian Chromium
                "/usr/bin/chromium",             # Other Linux distributions
                "/snap/bin/chromium",            # Snap package
                "/opt/google/chrome/chrome",     # Alternative install location
            ]
        
        self.log_message(f"Platform detected: {platform_info['system']} (WSL: {platform_info['is_wsl']})")
        
        for path in chrome_paths:
            if os.path.exists(path):
                self.log_message(f"Found Chrome at: {path}")
                return path
                
        # No Chrome found - provide platform-specific guidance
        self.show_chrome_install_guidance(platform_info)
        return None
    
    def show_chrome_install_guidance(self, platform_info):
        """Show user-friendly Chrome installation guidance"""
        if platform_info['is_windows']:
            message = ("Chrome not found!\n\n"
                      "Please install Google Chrome from:\n"
                      "https://www.google.com/chrome/\n\n"
                      "Or this app should include Chrome automatically.")
        elif platform_info['is_macos']:
            message = ("Chrome not found!\n\n"
                      "Please install Google Chrome from:\n" 
                      "https://www.google.com/chrome/\n\n"
                      "Download > Open > Drag to Applications folder")
        else:  # Linux
            message = ("Chrome/Chromium not found!\n\n"
                      "Install with:\n"
                      "Ubuntu/Debian: sudo apt install chromium-browser\n"
                      "Fedora: sudo dnf install chromium\n"
                      "Arch: sudo pacman -S chromium")
        
        self.log_message(f"Chrome guidance: {message}")
        # Don't show dialog yet - just log. We'll show dialog on actual failure
        
    def get_chromedriver_service(self):
        """Get ChromeDriver service using webdriver-manager for automatic management"""
        try:
            self.log_message("Setting up ChromeDriver automatically...")
            driver_path = ChromeDriverManager().install()
            self.log_message(f"ChromeDriver ready at: {driver_path}")
            return ChromeService(executable_path=driver_path)
        except Exception as e:
            self.log_message(f"Webdriver-manager failed: {e}")
            # Fallback to manual detection
            self.log_message("Falling back to manual ChromeDriver detection...")
            chromedriver_paths = [
                "/usr/bin/chromedriver",  # Linux/WSL2
                "chromedriver",           # System PATH
                "C:\\chromedriver.exe",   # Windows
            ]
            
            for path in chromedriver_paths:
                if os.path.exists(path):
                    self.log_message(f"Found ChromeDriver at: {path}")
                    return ChromeService(executable_path=path)
                    
            self.log_message("Warning: ChromeDriver not found, using system PATH")
            return ChromeService(executable_path="chromedriver")
        
    def scraper_worker(self, mode):
        """Main scraping logic with improved error handling"""
        driver = None
        try:
            self.log_message("Setting up platform environment...")
            self.setup_platform_environment()
            
            self.log_message("Starting mobile browser simulation...")
            
            # Create Chrome options
            chrome_options = self.create_chrome_options()
            
            # Find Chrome binary
            chrome_binary = self.find_chrome_binary()
            if chrome_binary:
                chrome_options.binary_location = chrome_binary
            
            # Get ChromeDriver service (auto-managed)
            service = self.get_chromedriver_service()
            
            # Create driver with better error handling
            try:
                driver = webdriver.Chrome(service=service, options=chrome_options)
                self.log_message("✅ Chrome browser started in headed mode!")
                self.log_message("📌 INFO: Chrome window opened - you can minimize it if it appears on screen")
            except WebDriverException as e:
                self.log_message(f"Failed to start Chrome with webdriver-manager: {e}")
                # Fallback: try without explicit service
                try:
                    driver = webdriver.Chrome(options=chrome_options)
                    self.log_message("✅ Chrome browser started in headed mode (fallback)!")
                    self.log_message("📌 INFO: Chrome window opened - you can minimize it if it appears on screen")
                except Exception as fallback_error:
                    raise Exception(f"Chrome startup failed completely: {e}. Fallback also failed: {fallback_error}")
            
            # Verify desktop mode is working
            try:
                driver.get("https://www.google.com")
                user_agent = driver.execute_script("return navigator.userAgent;")
                viewport_width = driver.execute_script("return window.innerWidth;")
                viewport_height = driver.execute_script("return window.innerHeight;")
                self.log_message(f"Desktop mode active - User Agent: {user_agent[:50]}...")
                self.log_message(f"Viewport size: {viewport_width}x{viewport_height}")
            except Exception as e:
                self.log_message(f"Warning: Could not verify desktop mode: {e}")
            
            self.log_message("Browser started successfully!")
            self.log_message("Navigating to login page...")
            
            # Navigate to login page with timeout
            driver.set_page_load_timeout(30)
            driver.set_script_timeout(30)
            driver.implicitly_wait(10)
            
            try:
                driver.get(LOGIN_URL)
                self.log_message("Login page loaded successfully")
                
                # Take initial screenshot
                self.take_screenshot(driver)
                
            except Exception as e:
                self.log_message(f"Error loading login page: {e}")
                # Try refreshing the page
                try:
                    driver.refresh()
                    time.sleep(3)
                    self.log_message("Page refreshed successfully")
                    self.take_screenshot(driver)
                except Exception as refresh_error:
                    raise Exception(f"Failed to load login page: {e}. Refresh also failed: {refresh_error}")
            
            self.log_message("Logging in...")
            
            # Wait for username field with longer timeout and try multiple selectors
            username_field = None
            username_selectors = [
                "input[type='email']",
                "input[placeholder*='Email']", 
                "input[name*='email']",
                "input[data-id*='email']",
                "input[data-id='form-field-emailAddress']"
            ]
            
            for selector in username_selectors:
                try:
                    self.log_message(f"Trying username selector: {selector}")
                    username_field = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    self.log_message(f"Found username field with selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not username_field:
                # Debug: log all input fields on the page
                all_inputs = driver.find_elements(By.TAG_NAME, "input")
                self.log_message(f"Found {len(all_inputs)} input fields on page:")
                for i, inp in enumerate(all_inputs):
                    input_type = inp.get_attribute('type') or 'no-type'
                    input_id = inp.get_attribute('id') or 'no-id'
                    input_name = inp.get_attribute('name') or 'no-name'
                    input_data_id = inp.get_attribute('data-id') or 'no-data-id'
                    input_placeholder = inp.get_attribute('placeholder') or 'no-placeholder'
                    self.log_message(f"  Input {i+1}: type='{input_type}', id='{input_id}', name='{input_name}', data-id='{input_data_id}', placeholder='{input_placeholder}'")
                raise Exception("Username field not found with any selector")
            
            username_field.clear()
            username_field.send_keys(self.username_var.get())
            self.log_message("Username entered")
            
            # Find and fill password field with multiple selectors
            password_field = None
            password_selectors = [
                "input[type='password']",
                "input[placeholder*='Password']",
                "input[name*='password']", 
                "input[data-id*='password']",
                "input[data-id='form-field-password']"
            ]
            
            for selector in password_selectors:
                try:
                    self.log_message(f"Trying password selector: {selector}")
                    password_field = driver.find_element(By.CSS_SELECTOR, selector)
                    self.log_message(f"Found password field with selector: {selector}")
                    break
                except:
                    continue
            
            if not password_field:
                raise Exception("Password field not found with any selector")
            
            password_field.clear()
            password_field.send_keys(self.password_var.get())
            self.log_message("Password entered")
            
            # Click login button with multiple selectors
            login_button = None
            login_selectors = [
                "button[type='submit']",
                "button:contains('Log in')",
                "button[data-id*='login']",
                "button[data-id*='Log-in']",
                "button[data-id='Log-in']"
            ]
            
            for selector in login_selectors:
                try:
                    self.log_message(f"Trying login button selector: {selector}")
                    login_button = driver.find_element(By.CSS_SELECTOR, selector)
                    button_text = login_button.text.strip()
                    self.log_message(f"Found login button with selector: {selector}, text: '{button_text}'")
                    break
                except:
                    continue
            
            if not login_button:
                # Debug: log all buttons on the page
                all_buttons = driver.find_elements(By.TAG_NAME, "button")
                self.log_message(f"Found {len(all_buttons)} buttons on page:")
                for i, btn in enumerate(all_buttons):
                    button_text = btn.text.strip() or 'no-text'
                    button_type = btn.get_attribute('type') or 'no-type'
                    button_data_id = btn.get_attribute('data-id') or 'no-data-id'
                    self.log_message(f"  Button {i+1}: text='{button_text}', type='{button_type}', data-id='{button_data_id}'")
                raise Exception("Login button not found with any selector")
            
            login_button.click()
            self.log_message("Login button clicked")
            
            # Take screenshot after login
            time.sleep(2)
            self.take_screenshot(driver)
            
            # Wait for successful login and dashboard to load
            try:
                # Wait for body to be present
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Wait for dashboard to load (look for dashboard elements)
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "pa-dashboard-tile, .dashboard, [data-id*='dashboard']"))
                    )
                    self.log_message("Dashboard loaded successfully!")
                except TimeoutException:
                    self.log_message("Dashboard elements not found, but proceeding...")
                
                # Additional wait for page to stabilize
                time.sleep(3)
                
                # Check if we're actually logged in
                current_url = driver.current_url
                self.log_message(f"Current URL after login: {current_url}")
                
                if "login" in current_url.lower():
                    self.log_message("Warning: Still on login page, login may have failed")
                else:
                    self.log_message("Login successful!")
                
                # Debug: Check what elements are available
                self.log_message("Checking available dashboard elements...")
                dashboard_tiles = driver.find_elements(By.CSS_SELECTOR, "pa-dashboard-tile")
                self.log_message(f"Found {len(dashboard_tiles)} dashboard tiles")
                
                for i, tile in enumerate(dashboard_tiles):
                    data_id = tile.get_attribute('data-id')
                    self.log_message(f"  Tile {i+1}: data-id='{data_id}'")
                
                # Navigate to newsfeed by clicking the newsfeed tile
                self.log_message("Navigating to newsfeed...")
                try:
                    newsfeed_tile = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "pa-dashboard-tile[data-id='newsfeed-tile']"))
                    )
                    newsfeed_tile.click()
                    self.log_message("Clicked newsfeed tile")
                    
                    # Wait for newsfeed to load
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    self.log_message("Newsfeed loaded successfully!")
                    
                except Exception as e:
                    self.log_message(f"Could not click newsfeed tile: {e}")
                    # Fallback: try direct URL navigation
                    self.log_message("Trying direct URL navigation...")
                    driver.get('https://parentportal.parenta.com/newsfeed')
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    self.log_message("Newsfeed loaded via direct URL")
                    
                # Take screenshot of newsfeed
                time.sleep(2)
                self.take_screenshot(driver)
                
            except TimeoutException:
                # Check if we're still on login page (login failed)
                if "login" in driver.current_url.lower():
                    raise Exception("Login failed - still on login page")
                else:
                    raise Exception("Login successful but newsfeed not found")
            
            # Setup CSV file for data export
            home_directory = Path.home()
            csv_filename = home_directory / f"Nursery_Data_{mode.capitalize()}.csv"
            
            # Create CSV file with headers
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['Date', 'Time', 'Event_Type', 'Content', 'Image_Count'])
            
            self.log_message(f"Created CSV file: {csv_filename}")
            
            # Initialize tracking variables
            processed_containers = set()  # Track processed container IDs
            total_scraped = 0
            total_images_downloaded = 0
            csv_batch = []  # Batch CSV writes
            image_batch = []  # Batch image downloads
            
            if mode == "full":
                self.log_message("Loading all history using simple infinite scroll...")
                
                # Simple infinite scroll approach - track containers, not just height
                last_height = driver.execute_script("return document.body.scrollHeight")
                initial_containers = driver.find_elements(By.CSS_SELECTOR, NEWSFEED_ITEM_SELECTOR)
                last_container_count = len(initial_containers)
                
                self.log_message(f"Initial page height: {last_height}")
                self.log_message(f"Initial container count: {last_container_count}")
                
                scroll_attempts = 0
                max_scroll_attempts = 80 
                no_new_content_attempts = 0
                max_no_content_attempts = 3  # Stop after 3 attempts with no new content
                
                while scroll_attempts < max_scroll_attempts:
                    # Get current scroll position and page info for debugging
                    current_scroll = driver.execute_script("return window.pageYOffset;")
                    viewport_height = driver.execute_script("return window.innerHeight;")
                    page_height = driver.execute_script("return document.body.scrollHeight;")
                    
                    self.log_message(f"Before scroll {scroll_attempts + 1}: scroll={current_scroll}, viewport={viewport_height}, page={page_height}")
                    
                    # Take screenshot before scrolling
                    if scroll_attempts % 50 == 0:  # Every 50 scrolls to avoid too many screenshots
                        self.take_screenshot(driver)
                    
                    scroll_success = False
                    
                    # Method 1: ActionChains scroll (most realistic user simulation)
                    self.log_message("Method 1: ActionChains scroll simulation...")
                    try:
                        # Get the page body element to scroll on
                        body = driver.find_element(By.TAG_NAME, "body")
                        
                        # ActionChains scroll - simulates real mouse wheel
                        actions = ActionChains(driver)
                        
                        # Move to center of the page and perform multiple scroll actions
                        actions.move_to_element(body).perform()
                        
                        for i in range(20):
                            actions.scroll_by_amount(0, 700).perform()
                            time.sleep(0.1)
                            
                        for i in range(8):
                            body.send_keys(Keys.PAGE_DOWN)
                            time.sleep(0.1)
                        
                        body.send_keys(Keys.END)
                        time.sleep(0.2)
                        
                        for i in range(20):
                            body.send_keys(Keys.ARROW_DOWN)
                            time.sleep(0.05)
                        
                        self.log_message("✓ Method 1: ActionChains + keyboard scroll completed")
                        scroll_success = True
                        
                    except Exception as e:
                        self.log_message(f"✗ Method 1 ActionChains failed: {e}")
                        
                        # Fallback to JavaScript wheel events
                        self.log_message("Method 1B: Fallback to JavaScript wheel events...")
                        try:
                            result = driver.execute_script("""
                                let scrollsBefore = window.pageYOffset;
                                
                                // Dispatch wheel events 
                                for (let i = 0; i < 10; i++) {
                                    window.dispatchEvent(new WheelEvent('wheel', {
                                        bubbles: true,
                                        cancelable: true,
                                        deltaY: 200,
                                        deltaMode: 0
                                    }));
                                    
                                    document.body.dispatchEvent(new WheelEvent('wheel', {
                                        bubbles: true,
                                        cancelable: true,
                                        deltaY: 200,
                                        deltaMode: 0
                                    }));
                                }
                                
                                let scrollsAfter = window.pageYOffset;
                                return {
                                    before: scrollsBefore,
                                    after: scrollsAfter,
                                    moved: scrollsAfter > scrollsBefore
                                };
                            """)
                            
                            self.log_message(f"✓ Method 1B: JavaScript fallback result: {result}")
                            if result and result.get('moved'):
                                scroll_success = True
                                
                        except Exception as e2:
                            self.log_message(f"✗ Method 1B fallback also failed: {e2}")
                    
                    # Wait for new containers to load using WebDriverWait
                    self.log_message("Waiting for new containers to load...")
                    try:
                        current_container_count = len(driver.find_elements(By.CSS_SELECTOR, NEWSFEED_ITEM_SELECTOR))
                        
                        # Wait up to 10 seconds for new containers to appear
                        wait = WebDriverWait(driver, 10)
                        wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, NEWSFEED_ITEM_SELECTOR)) > current_container_count)
                        
                        new_container_count = len(driver.find_elements(By.CSS_SELECTOR, NEWSFEED_ITEM_SELECTOR))
                        self.log_message(f"✓ WebDriverWait: Containers increased from {current_container_count} to {new_container_count}")
                        scroll_success = True
                        
                    except TimeoutException:
                        self.log_message("⚠ WebDriverWait: Timed out waiting for new containers")
                    except Exception as e:
                        self.log_message(f"✗ WebDriverWait failed: {e}")
                    
                    # Wait a moment and check new position
                    time.sleep(2)
                    new_scroll = driver.execute_script("return window.pageYOffset;")
                    self.log_message(f"After scroll: position={new_scroll}")
                    
                    # Wait for new content to load
                    time.sleep(3)  # Wait for lazy loading
                    
                    # Calculate new scroll height and compare with last scroll height
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    self.log_message(f"Height: {last_height} -> {new_height}")
                    
                    # Check how many containers we have now
                    current_containers = driver.find_elements(By.CSS_SELECTOR, NEWSFEED_ITEM_SELECTOR)
                    current_container_count = len(current_containers)
                    self.log_message(f"Found {current_container_count} containers after scroll")
                    
                    # Check if we got new containers (this is more reliable than height)
                    if current_container_count > last_container_count:
                        new_containers_loaded = current_container_count - last_container_count
                        self.log_message(f"✅ SUCCESS! Loaded {new_containers_loaded} new containers ({last_container_count} -> {current_container_count})")
                        last_container_count = current_container_count
                        no_new_content_attempts = 0  # Reset counter
                        
                        # Take screenshot when new content is loaded
                        self.take_screenshot(driver)
                        
                    else:
                        no_new_content_attempts += 1
                        self.log_message(f"No new containers loaded (attempt {no_new_content_attempts}/{max_no_content_attempts})")
                        
                        if no_new_content_attempts >= max_no_content_attempts:
                            self.log_message("Reached maximum attempts with no new content - stopping")
                            break
                    
                    last_height = new_height
                    scroll_attempts += 1
                
                self.log_message("Finished loading all content, now processing with batch extractor...")
                
                # Take final screenshot of all loaded content
                self.take_screenshot(driver)
                
                # Use batch extractor for fast data extraction with carousel support
                self.log_message("Using JavaScript batch extraction with enhanced carousel image support...")
                all_posts_data = extract_all_posts_with_carousel_images_js(driver, NEWSFEED_ITEM_SELECTOR)
                self.log_message(f"Batch extracted {len(all_posts_data)} posts")
                
                # Process extracted data
                for i, post_data in enumerate(all_posts_data):
                    try:
                        if post_data and post_data.get('id') not in processed_containers:
                            processed_containers.add(post_data.get('id', f'post_{i}'))
                            
                            # Batch CSV data for faster writing
                            csv_batch.append([
                                post_data.get('date', ''),
                                post_data.get('time', ''),
                                post_data.get('event_type', ''),
                                post_data.get('content', ''),
                                len(post_data.get('image_urls', []))
                            ])
                            
                            # Batch image URLs for parallel download later
                            if post_data.get('image_urls'):
                                # Log carousel information if available
                                if post_data.get('has_carousel'):
                                    self.log_message(f"Carousel detected: {post_data.get('carousel_count', 0)} images in {post_data.get('event_type', 'unknown')}")
                                
                                for j, url in enumerate(post_data['image_urls']):
                                    post_date = post_data.get('date', '').replace('/', '-').replace(':', '-')[:20] if post_data.get('date') else f"post_{total_scraped}"
                                    post_type = post_data.get('event_type', '') if post_data.get('event_type') else "unknown"
                                    url_filename = url.split('/')[-1].split('?')[0]
                                    if not url_filename or '.' not in url_filename:
                                        url_filename = f"image_{j}.jpg"
                                    filename = f"{post_date}_{post_type}_{total_scraped}_{j}_{url_filename}"
                                    image_batch.append((url, filename))
                            
                            total_scraped += 1
                            
                            # Batch write every 50 posts for better performance
                            if len(csv_batch) >= 50:
                                with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                                    csv_writer = csv.writer(csvfile)
                                    csv_writer.writerows(csv_batch)
                                csv_batch.clear()
                                self.log_message(f"Batch saved {total_scraped} posts so far...")
                            
                            # Progress logging less frequently
                            if total_scraped % 50 == 0:
                                self.log_message(f"Processed {total_scraped} posts, {len(image_batch)} images queued")
                        
                    except Exception as e:
                        self.log_message(f"Error processing extracted post {i+1}: {str(e)[:200]}")
                        continue
                    
            else:
                # Test mode: process first 50 items using batch extractor
                self.log_message("Test mode: Processing first 50 items with batch extractor...")
                time.sleep(3)
                
                # Use batch extractor for fast data extraction with carousel support
                all_posts_data = extract_all_posts_with_carousel_images_js(driver, NEWSFEED_ITEM_SELECTOR)
                test_posts_data = all_posts_data[:50] if len(all_posts_data) > 50 else all_posts_data
                
                self.log_message(f"Processing {len(test_posts_data)} posts in test mode...")
                
                for i, post_data in enumerate(test_posts_data):
                    try:
                        if post_data:
                            # Save to CSV
                            with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                                csv_writer = csv.writer(csvfile)
                                csv_writer.writerow([
                                    post_data.get('date', ''),
                                    post_data.get('time', ''),
                                    post_data.get('event_type', ''),
                                    post_data.get('content', ''),
                                    len(post_data.get('image_urls', []))
                                ])
                            
                            # Download images immediately in test mode
                            if post_data.get('image_urls'):
                                downloaded_count = self.download_post_images_from_data(post_data, i, mode)
                                total_images_downloaded += downloaded_count
                            
                            total_scraped += 1
                            self.log_message(f"  Processed post {total_scraped}: {post_data.get('event_type', 'unknown')} - {len(post_data.get('image_urls', []))} images")
                    
                    except Exception as e:
                        self.log_message(f"  Error processing post {i+1}: {str(e)[:200]}")
                        self.log_message(f"  Error type: {type(e).__name__}")
                        continue
            

            # Final batch processing
            self.log_message("Processing final batches...")
            
            # Write any remaining CSV data
            if csv_batch:
                with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerows(csv_batch)
                self.log_message(f"Final CSV batch: {len(csv_batch)} posts saved")
            
            # Download all images in parallel batches
            if image_batch:
                self.log_message(f"Starting parallel download of {len(image_batch)} images...")
                total_images_downloaded = self.download_images_parallel(image_batch, mode)
            
            self.log_message(f"✅ Scraping complete! Processed {total_scraped} posts, downloaded {total_images_downloaded} images")
            self.log_message(f"Data saved to: {csv_filename}")
            self.log_message("🎉 SUCCESS: You can now safely close this application")
            
            # Stop indeterminate animation and fill progress bar to 100% completion
            self.progress.stop()
            self.progress.set(1.0)
            
        except Exception as e:
            self.log_message(f"❌ Error: {e}")
            self.log_message(f"Error type: {type(e).__name__}")
            if hasattr(e, '__traceback__'):
                import traceback
                self.log_message(f"Traceback: {traceback.format_exc()}")
            show_error_dialog(self.root, "Error", f"An error occurred: {e}")
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            self.is_running = False
            self.test_button.configure(state='normal')
            self.full_button.configure(state='normal')
            self.progress.stop()
            
    def download_post_images_from_data(self, post_data, post_index, mode):
        """Download images for a single post from extracted data"""
        if not post_data.get('image_urls'):
            return 0
            
        try:
            # Create download directory (single folder for all images)
            home_directory = Path.home()
            download_dir_name = f"Nursery_Downloads_{mode.capitalize()}"
            download_dir = home_directory / download_dir_name
            os.makedirs(download_dir, exist_ok=True)
            
            downloaded_count = 0
            for j, url in enumerate(post_data['image_urls']):
                try:
                    # Extract filename from URL
                    url_filename = url.split('/')[-1].split('?')[0]
                    if not url_filename or '.' not in url_filename:
                        url_filename = f"image_{j}.jpg"
                    
                    # Create descriptive filename with post info
                    post_date = post_data.get('date', '').replace('/', '-').replace(':', '-')[:20] if post_data.get('date') else f"post_{post_index}"
                    post_type = post_data.get('event_type', '') if post_data.get('event_type') else "unknown"
                    
                    # Flat filename structure: date_type_postindex_imageindex_originalname
                    filename = download_dir / f"{post_date}_{post_type}_{post_index}_{j}_{url_filename}"
                    
                    # Download image
                    res = requests.get(url, stream=True, timeout=30)
                    res.raise_for_status()
                    
                    with open(filename, 'wb') as f:
                        f.write(res.content)
                    
                    downloaded_count += 1
                    
                except Exception as e:
                    self.log_message(f"  Could not download {url}: {e}")
                    continue
            
            return downloaded_count
            
        except Exception as e:
            self.log_message(f"Error downloading images for post {post_index}: {e}")
            return 0
    
    def download_images_parallel(self, image_batch, mode):
        """Download images in parallel batches for much better performance"""
        import concurrent.futures
        import threading
        
        # Create download directory
        home_directory = Path.home()
        download_dir_name = f"Nursery_Downloads_{mode.capitalize()}"
        download_dir = home_directory / download_dir_name
        os.makedirs(download_dir, exist_ok=True)
        
        def download_single_image(url_filename_tuple):
            """Download a single image - thread-safe function"""
            url, filename = url_filename_tuple
            try:
                full_path = download_dir / filename
                
                # Skip if file already exists
                if full_path.exists():
                    return True
                
                # Download with timeout
                response = requests.get(url, stream=True, timeout=15)
                response.raise_for_status()
                
                # Save image
                with open(full_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                return True
            except Exception as e:
                self.log_message(f"Failed to download {filename}: {str(e)[:50]}")
                return False
        
        # Download in parallel batches of 10 images to avoid overwhelming the server
        downloaded_count = 0
        batch_size = 10
        
        for i in range(0, len(image_batch), batch_size):
            batch = image_batch[i:i + batch_size]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                results = list(executor.map(download_single_image, batch))
                batch_success = sum(results)
                downloaded_count += batch_success
                
                # Progress update
                self.log_message(f"Downloaded batch {i//batch_size + 1}: {batch_success}/{len(batch)} images successful")
        
        return downloaded_count

def main():
    root = ctk.CTk()
    app = ParentaScraper(root)
    root.mainloop()

if __name__ == "__main__":
    main()
