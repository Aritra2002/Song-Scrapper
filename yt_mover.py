import time
import random
import sys
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ==========================================
# --- CONFIGURATION SECTION ---
# ==========================================

BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
SONG_FILE = "amazon_songs_backup.txt"
YOUTUBE_MUSIC_URL = "https://music.youtube.com"

# Constants
MIN_SLEEP_TIME = 2
MAX_SLEEP_TIME = 4
WAIT_TIMEOUT = 10

# ==========================================

def get_songs(filename: str) -> List[str]:
    """
    Read and parse songs from a file.
    
    Args:
        filename: Path to the file containing songs
        
    Returns:
        List[str]: List of song names
        
    Raises:
        SystemExit: If file is not found
    """
    clean_songs = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        parts = line.strip().split(' ', 1)
                        if len(parts) > 1:
                            clean_songs.append(parts[1])
                        else:
                            clean_songs.append(line.strip())
                    except Exception as e:
                        print(f"Error parsing line: {e}")
                        continue
    except FileNotFoundError:
        print(f"Error: Could not find {filename}.")
        sys.exit(1)
    return clean_songs

def setup_driver() -> webdriver.Chrome:
    """
    Set up and configure Chrome WebDriver for Brave browser with stealth options.
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    options = Options()
    options.binary_location = BRAVE_PATH
    options.add_argument("--mute-audio") 
    options.add_argument("--start-maximized")
    
    # STEALTH MODE
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    print("Initializing Driver for Brave (Version ~143)...")
    try:
        driver_path = ChromeDriverManager(driver_version="143.0.7499.110").install()
    except Exception as e:
        print(f" -> Exact version match failed. Trying generic version 143... Error: {e}")
        driver_path = ChromeDriverManager(driver_version="143").install()
        
    service_obj = Service(driver_path)
    driver = webdriver.Chrome(service=service_obj, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def add_to_liked_songs(driver: webdriver.Chrome, song: str) -> str:
    """
    Search for a song and add first result to liked songs.
    
    Args:
        driver: Chrome WebDriver instance
        song: Song name to search for
        
    Returns:
        str: 'success', 'skip', or 'error'
    """
    try:
        # Search for the song
        driver.get(f"{YOUTUBE_MUSIC_URL}/search?q={song}")
        time.sleep(3)  # Wait for search results to load
        
        # Find the first content item that has a menu
        content_selectors = [
            "ytmusic-shelf-renderer ytmusic-responsive-list-item-renderer",
            "ytmusic-list-item-renderer", 
            "ytmusic-responsive-list-item-renderer"
        ]
        
        for selector in content_selectors:
            try:
                items = driver.find_elements(By.CSS_SELECTOR, selector)
                if items:
                    success = False
                    # Try the first 3 items
                    for idx, item in enumerate(items[:3]):
                        try:
                            # Check if this has title (song/video) - duration check is optional
                            try:
                                title_elem = item.find_element(By.CSS_SELECTOR, ".title, .primary-text")
                                if not title_elem:
                                    continue
                            except:
                                continue
                            
                            title = title_elem.text[:50]
                            item_text = item.text.lower()
                            content_type = "video" if ('video' in item_text or 'mv' in item_text) else "song"
                            
                            print(f" -> Trying {content_type} #{idx+1}: {title}...")
                            
                            # Find and click the menu button
                            menu_button = item.find_element(By.XPATH, ".//ytmusic-menu-renderer//button")
                            
                            driver.execute_script("arguments[0].scrollIntoView(true);", menu_button)
                            time.sleep(0.5)
                            driver.execute_script("arguments[0].click();", menu_button)
                            time.sleep(2)
                            
                            # Try to find and click "Add to liked songs"
                            success = False
                            
                            # Try to find and click "Add to liked songs"
                            success = False
                            add_selectors = [
                                "//yt-formatted-string[contains(text(), 'Add to liked songs')]",
                                "//yt-formatted-string[contains(text(), 'Add to liked')]",
                                "//*[contains(text(), 'Add to liked songs')]",
                                "//*[contains(text(), 'Add to liked')]"
                            ]
                            
                            for add_selector in add_selectors:
                                try:
                                    add_elements = driver.find_elements(By.XPATH, add_selector)
                                    for add_elem in add_elements:
                                        if add_elem.is_displayed():
                                            add_elem.click()
                                            return "success"
                                    # Continue trying if this selector didn't work
                                except:
                                    continue
                            
                            # Check if already liked
                            if not success:
                                try:
                                    remove_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Remove from liked')]")
                                    for remove_elem in remove_elements:
                                        if remove_elem.is_displayed():
                                            return "skip"  # Return skip since it's already liked
                                except:
                                    pass
                            
                            # Close menu
                            try:
                                driver.execute_script("document.body.click();")
                                time.sleep(0.5)
                            except:
                                pass
                            
                            if success:
                                return "success"
                                
                        except Exception as item_error:
                            print(f" -> Error with item {idx+1}: {item_error}")
                            # Close any open menu
                            try:
                                driver.execute_script("document.body.click();")
                                time.sleep(0.5)
                            except:
                                pass
                            continue
                            
                    if success:
                        return "success"
                        
            except Exception as selector_error:
                print(f" -> Selector {selector} failed: {selector_error}")
                continue
                
        return "error"
        
    except Exception as e:
        print(f" -> Error in add_to_liked_songs: {e}")
        return "error"

def main() -> None:
    """
    Main function to process songs and add them to YouTube Music liked songs.
    """
    songs = get_songs(SONG_FILE)
    if not songs:
        print("No songs found.")
        return

    print(f"Loaded {len(songs)} songs.")
    driver = setup_driver()

    try:
        driver.get(YOUTUBE_MUSIC_URL)
        
        print("\n" + "="*50)
        print("ACTION REQUIRED: Log in manually.")
        input(">>> When logged in, press ENTER here to start <<<")
        print("="*50 + "\n")

        for i, song in enumerate(songs):
            print(f"[{i+1}/{len(songs)}] Processing: {song}")
            
            result = add_to_liked_songs(driver, song)
            
            if result == "success":
                print(f" -> [SUCCESS] Added to liked songs")
            elif result == "skip":
                print(f" -> [SKIP] Already in liked songs")
            else:
                print(f" -> [ERROR] Could not process")

            sleep_time = random.uniform(MIN_SLEEP_TIME, MAX_SLEEP_TIME)
            time.sleep(sleep_time)

    finally:
        print("\nAll done! Closing browser.")
        driver.quit()

if __name__ == "__main__":
    main()