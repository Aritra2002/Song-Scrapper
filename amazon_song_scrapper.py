import time
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

# --- CONFIGURATION ---
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
OUTPUT_FILE = "amazon_songs_backup.txt"
AMAZON_MUSIC_URL = "https://music.amazon.in/"

# Constants
SCROLL_DELAY = 5
FINAL_SCROLL_DELAY = 4


def setup_driver() -> webdriver.Chrome:
    """
    Set up and configure Chrome WebDriver for Brave browser.

    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance

    Raises:
        Exception: If driver setup fails
    """
    print("Setting up Brave Browser Driver...")
    options = Options()
    options.binary_location = BRAVE_PATH
    options.add_experimental_option("detach", True)

    try:
        # Selenium (4.6+) automatically manages the matching driver version
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Error initializing driver: {e}")
        raise

    return driver


def auto_scroll(driver: webdriver.Chrome) -> None:
    """
    Automatically scroll the page to load all content.
    
    Args:
        driver: Chrome WebDriver instance
    """
    print("Starting automatic scroll...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_DELAY)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("Reached the bottom.")
            break
        last_height = new_height
    
    # Scroll back to top to ensure first elements are rendered
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(FINAL_SCROLL_DELAY)

def get_artist_via_js(driver: webdriver.Chrome, element: WebElement) -> str:
    """
    Uses JavaScript to pierce the Shadow DOM and look for hidden text.
    
    Args:
        driver: Chrome WebDriver instance
        element: Web element to extract artist information from
        
    Returns:
        str: Artist name or empty string if not found
    """
    return driver.execute_script("""
        var item = arguments[0];
        var artist = "";
        
        // 1. Try to find text in the Shadow Root (Hidden Area)
        if (item.shadowRoot) {
            // Look for generic 'col2' which is often the artist column
            var col2 = item.shadowRoot.querySelector('.col2');
            if (col2) return col2.innerText;
            
            // Look for any links inside the shadow root
            var links = item.shadowRoot.querySelectorAll('a, music-link');
            for (var i = 0; i < links.length; i++) {
                var txt = links[i].innerText || links[i].getAttribute('title');
                // If the link text exists and is NOT the song title (passed in args), return it
                if (txt && txt.length > 1) return txt;
            }
        }
        return "";
    """, element)

def scrape_songs() -> None:
    driver = None
    try:
        driver = setup_driver()
        print("Opening Amazon Music...")
        try:
            driver.get(AMAZON_MUSIC_URL)
        except Exception as nav_e:
            if "net::ERR_NAME_NOT_RESOLVED" in str(nav_e):
                print("\n[!] Error: Could not resolve Amazon Music URL. Please check your internet connection or DNS settings.")
            else:
                print(f"\n[!] Navigation Error: {nav_e}")
            return

        print("\n" + "="*60)
        print("INSTRUCTIONS:")
        print("1. Log in manually.")
        print("2. Navigate to the Playlist.")
        print("3. DO NOT scroll manually.")
        print("="*60 + "\n")
        
        input("Press ENTER here to start...")

        # 1. Scroll
        auto_scroll(driver)

        # 2. Scrape
        print("Scraping songs...")
        found_songs = []
        
        # Grab main list items
        items = driver.find_elements(By.CSS_SELECTOR, "music-responsive-list-item, music-image-row")
        
        # Fallback if list is empty
        if not items:
            items = driver.find_elements(By.CSS_SELECTOR, ".col1")

        print(f"Processing {len(items)} items...")

        for item in items:
            title = ""
            artist = ""
            
            try:
                # --- GET TITLE ---
                title = item.get_attribute("primary-text")
                if not title:
                    raw_text = item.text.split("\n")
                    if raw_text: title = raw_text[0]
                
                # Clean title
                if title: title = title.strip()
                if title and title.upper() == "TITLE": continue # Skip header

                # --- GET ARTIST (Advanced Methods) ---
                
                # Method 1: Standard Attribute
                if not artist:
                    artist = item.get_attribute("secondary-text-1")

                # Method 2: Aria-Label Parsing (The "Screen Reader" Trick)
                # The label might say "SongName by ArtistName"
                if not artist:
                    aria_label = item.get_attribute("aria-label")
                    if aria_label and " by " in aria_label:
                        # Split "Shape of You by Ed Sheeran" -> ["Shape of You", "Ed Sheeran"]
                        parts = aria_label.split(" by ")
                        if len(parts) > 1:
                            artist = parts[-1] # Take the last part

                # Method 3: JavaScript Shadow DOM (The "Nuclear" Option)
                if not artist:
                    artist = get_artist_via_js(driver, item)
                    # Use a safeguard: if the JS returns the title again, ignore it
                    if artist == title: 
                        artist = ""

                # Method 4: Visible Text Fallback
                if not artist:
                     raw_text = item.text.split("\n")
                     for line in raw_text:
                         if line == title: continue
                         if line in ["E", "Lyrics", "HD"]: continue
                         artist = line
                         break

                # --- SAVE ---
                if title:
                    if artist:
                        entry = f"{title} by {artist.strip()}"
                    else:
                        entry = f"{title}"
                    
                    found_songs.append(entry)

            except Exception:
                continue

        # Save to file
        if found_songs:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                for index, song in enumerate(found_songs, start=1):
                    f.write(f"{index}. {song}\n")
            print(f"\nSuccess! Saved {len(found_songs)} songs.")
        else:
            print("No songs found.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if driver:
            input("Press ENTER to close browser...")
            driver.quit()

if __name__ == "__main__":
    scrape_songs()