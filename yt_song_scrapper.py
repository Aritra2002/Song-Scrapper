import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from web_utils import setup_chrome_driver, safe_scroll_to_bottom

# Set this to your Brave User Data path if you want to stay logged in.
# Usually: r"C:\Users\<Username>\AppData\Local\BraveSoftware\Brave-Browser\User Data"
# WARNING: Brave must be COMPLETELY CLOSED for this to work.
USER_DATA_DIR = None  # Set this to your browser's user data path to stay logged in
PROFILE_DIRECTORY = "Default"
LIKED_SONGS_URL = "https://music.youtube.com/playlist?list=LM"
OUTPUT_FILE = "yt_songs.txt"


def scrape_liked_songs():
    """
    Scrapes liked songs from YouTube Music using existing browser profile for auto-login.
    """
    print(f"Initializing driver with profile: {PROFILE_DIRECTORY}")
    
    if USER_DATA_DIR and not os.path.exists(USER_DATA_DIR):
        print(f"WARNING: User data directory not found at {USER_DATA_DIR}")
        print("Please check the path in the script.")
        return

    # Setup the driver using utilities from web_utils.py
    driver = setup_chrome_driver(
        user_data_dir=USER_DATA_DIR,
        profile_directory=PROFILE_DIRECTORY,
        stealth_mode=True,
        start_maximized=True
    )

    try:
        print(f"Navigating to Liked Songs: {LIKED_SONGS_URL}")
        driver.get(LIKED_SONGS_URL)
        
        # Wait for the page to load initial content
        print("Waiting for page to load...")
        try:
            # Wait for at least one song row to be present
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ytmusic-responsive-list-item-renderer"))
            )
        except Exception:
            print("Timed out waiting for songs to load. Are you logged in?")
            print("If a login screen appeared, please log in manually in the opened browser.")
            input("Press Enter once you are on the Liked Songs page...")

        # YouTube Music uses lazy loading. Scroll to the bottom to load all songs.
        print("Scrolling to load all liked songs...")
        # Increase delay and attempts for large playlists
        safe_scroll_to_bottom(driver, max_attempts=150, scroll_delay=2.5)
        
        # Additional wait for the final batch of elements to render
        print("Finalizing page load...")
        time.sleep(5)
        
        # Extract song details
        song_elements = driver.find_elements(By.CSS_SELECTOR, "ytmusic-responsive-list-item-renderer")
        print(f"Total elements found in DOM: {len(song_elements)}")
        
        if not song_elements:
            print("No songs found. The page structure might have changed or content didn't load.")
            return

        print("Extracting song data and saving in real-time...")
        count = 0
        skipped_unavailable = 0
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for index, item in enumerate(song_elements):
                try:
                    # Robust title extraction with multiple fallback selectors
                    title = ""
                    title_selectors = [
                        "div.flex-columns yt-formatted-string.title",
                        "yt-formatted-string.title",
                        ".title",
                        "a.ytmusic-responsive-list-item-link"
                    ]
                    
                    for selector in title_selectors:
                        try:
                            title_elem = item.find_element(By.CSS_SELECTOR, selector)
                            title = " ".join(title_elem.text.split())
                            if title:
                                break
                        except Exception:
                            continue

                    if not title or "[Deleted video]" in title or "[Private video]" in title:
                        skipped_unavailable += 1
                        continue

                    # Secondary flex columns contain Artist, Album, etc.
                    secondary_flex = item.find_elements(By.CSS_SELECTOR, ".secondary-flex-columns yt-formatted-string")
                    
                    artist = "Unknown Artist"
                    album = "Unknown Album"
                    
                    if secondary_flex:
                        artist = " ".join(secondary_flex[0].text.split())
                        if len(secondary_flex) > 1:
                            album = " ".join(secondary_flex[1].text.split())
                    
                    # Extra safety: Ensure no hidden newlines in the final strings
                    title = title.replace("\n", " ").strip()
                    artist = artist.replace("\n", " ").strip()
                    album = album.replace("\n", " ").strip()
                    
                    # Write to file immediately
                    line = f"{count + 1}. {title} - {artist} ({album})\n"
                    f.write(line)
                    f.flush()
                    count += 1
                    
                    if (index + 1) % 100 == 0:
                        print(f"Processed {index + 1}/{len(song_elements)} elements...")
                        
                except Exception:
                    continue

        print(f"\nResults:")
        print(f" - Successfully saved: {count} songs")
        print(f" - Skipped (Deleted/Private/Unavailable): {skipped_unavailable}")
        print(f" - Total accounted for: {count + skipped_unavailable}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Closing browser in 5 seconds...")
        time.sleep(5)
        driver.quit()


if __name__ == "__main__":
    scrape_liked_songs()
