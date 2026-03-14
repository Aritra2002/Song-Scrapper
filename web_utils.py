"""
Common utilities for web scraping scripts.
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


# Constants
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"


def setup_chrome_driver(
    binary_location: str = BRAVE_PATH,
    stealth_mode: bool = False,
    detach: bool = False,
    mute_audio: bool = False,
    start_maximized: bool = False,
    user_data_dir: str = None,
    profile_directory: str = "Default"
) -> webdriver.Chrome:
    """
    Set up and configure Chrome WebDriver with various options.
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
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36")

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