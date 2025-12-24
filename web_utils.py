"""
Common utilities for web scraping scripts.
"""
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# Constants
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
CHROME_VERSION = "143"


def setup_chrome_driver(
    binary_location: str = BRAVE_PATH,
    chrome_version: str = CHROME_VERSION,
    stealth_mode: bool = False,
    detach: bool = False,
    mute_audio: bool = False,
    start_maximized: bool = False
) -> webdriver.Chrome:
    """
    Set up and configure Chrome WebDriver with various options.
    
    Args:
        binary_location: Path to browser executable
        chrome_version: Chrome driver version to use
        stealth_mode: Enable stealth mode options
        detach: Keep browser open after script ends
        mute_audio: Mute browser audio
        start_maximized: Start browser maximized
        
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    options = Options()
    options.binary_location = binary_location
    
    if detach:
        options.add_experimental_option("detach", True)
    
    if mute_audio:
        options.add_argument("--mute-audio")
    
    if start_maximized:
        options.add_argument("--start-maximized")
    
    if stealth_mode:
        # STEALTH MODE options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

    try:
        # Try exact version first
        service = Service(ChromeDriverManager(driver_version=chrome_version).install())
    except Exception as e:
        print(f"Exact version {chrome_version} failed. Using default... Error: {e}")
        service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=options)
    
    if stealth_mode:
        # Additional stealth script
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
    
    return driver


def safe_scroll_to_bottom(
    driver: webdriver.Chrome,
    max_attempts: int = 50,
    scroll_delay: float = 3.0,
    final_scroll_delay: float = 2.0
) -> None:
    """
    Safely scroll to the bottom of a page with attempt limits.
    
    Args:
        driver: Chrome WebDriver instance
        max_attempts: Maximum number of scroll attempts
        scroll_delay: Delay between scrolls in seconds
        final_scroll_delay: Delay after scrolling back to top
    """
    print("Starting automatic scroll...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    attempts = 0
    while attempts < max_attempts:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_delay)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("Reached the bottom.")
            break
        last_height = new_height
        attempts += 1
    
    # Scroll back to top to ensure first elements are rendered
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(final_scroll_delay)


def wait_for_user_input(message: str = "Press ENTER to continue...") -> None:
    """
    Wait for user input with a custom message.
    
    Args:
        message: Message to display to user
    """
    input(message)