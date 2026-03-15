"""
Common utilities for web scraping scripts.
"""
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


# Constants
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"


def setup_chrome_driver(
    binary_location: str = BRAVE_PATH,
    stealth_mode: bool = False,
    detach: bool = False,
    mute_audio: bool = False,
    start_maximized: bool = False,
    user_data_dir: Optional[str] = None,
    profile_directory: str = "Default"
) -> webdriver.Chrome:
    """
    Set up and configure Chrome WebDriver with various options.

    Args:
        binary_location: Path to the browser binary.
        stealth_mode: Whether to enable stealth mode to avoid detection.
        detach: Whether to keep the browser open after the script finishes.
        mute_audio: Whether to mute audio in the browser.
        start_maximized: Whether to start the browser maximized.
        user_data_dir: Path to the user data directory.
        profile_directory: Name of the profile directory.

    Returns:
        A configured instance of webdriver.Chrome.
    """
    options = Options()
    options.binary_location = binary_location
    
    if detach:
        options.add_experimental_option("detach", True)
    
    if mute_audio:
        options.add_argument("--mute-audio")
    
    if start_maximized:
        options.add_argument("--start-maximized")
    
    if user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument(f"--profile-directory={profile_directory}")
    
    if stealth_mode:
        # Advanced Stealth: Disable automation flags
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        # Use a modern, non-headless User Agent
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/146.0.0.0 Safari/537.36"
        )

    # Let Selenium (4.6+) automatically manage the matching driver version
    driver = webdriver.Chrome(options=options)
    
    if stealth_mode:
        # Advanced Stealth: Execute CDP command to hide 'navigator.webdriver' before any page loads
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
    
    return driver


def safe_scroll_to_bottom(
    driver: webdriver.Chrome,
    max_attempts: int = 50,
    scroll_delay: float = 3.0,
    final_scroll_delay: float = 2.0
) -> None:
    """
    Safely scroll to the bottom of a page.
    Attempts window scroll first, then tries to find and scroll internal containers.

    Args:
        driver: The Chrome WebDriver instance.
        max_attempts: Maximum number of scroll attempts.
        scroll_delay: Delay between scrolls.
        final_scroll_delay: Delay after the final scroll.
    """
    print("Starting automatic scroll...")
    
    # 1. Try Window Scroll
    last_height = driver.execute_script("return document.body.scrollHeight")
    attempts = 0
    while attempts < 10:  # Short attempt for window
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_delay)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        attempts += 1

    # 2. Aggressive Key-based Scroll (Works best for Amazon/Spotify internal containers)
    print("Applying aggressive key-based scrolling...")
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        for _ in range(max_attempts):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(1.0)  # Faster internal scroll
    except Exception as e:
        print(f"Key-based scroll failed: {e}")
    
    # Scroll back to top
    try:
        body.send_keys(Keys.HOME)
    except Exception:
        driver.execute_script("window.scrollTo(0, 0);")
        
    time.sleep(final_scroll_delay)


def wait_for_user_input(message: str = "Press ENTER to continue...") -> None:
    """
    Wait for user input with a custom message.
    
    Args:
        message: Message to display to user
    """
    input(message)
