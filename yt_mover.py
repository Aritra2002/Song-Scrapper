import time
import random
import sys
import argparse
import os
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from web_utils import setup_chrome_driver


# ==========================================
# --- CONFIGURATION SECTION ---
# ==========================================

YOUTUBE_MUSIC_URL = "https://music.youtube.com"

# --- PERSISTENT PROFILE CONFIGURATION ---
# Set this to your Brave User Data path if you want to stay logged in.
# Usually: r"C:\Users\Aritra Naskar\AppData\Local\BraveSoftware\Brave-Browser\User Data"
# WARNING: Brave must be COMPLETELY CLOSED for this to work.
USER_DATA_DIR = None  # Set this to your browser's user data path to stay logged in 
PROFILE_NAME = "Default"

# Constants
MIN_SLEEP_TIME = 2
MAX_SLEEP_TIME = 4

# ==========================================


def get_songs(filename: str) -> List[str]:
    """
    Read and parse songs from a file.

    Args:
        filename: Path to the file containing songs

    Returns:
        List[str]: List of song names
    """
    clean_songs = []
    if not os.path.exists(filename):
        print(f"Error: Could not find {filename}.")
        sys.exit(1)

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
    return clean_songs


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
                    # Try the first 3 items
                    for idx, item in enumerate(items[:3]):
                        try:
                            # Check if this has title (song/video)
                            try:
                                title_elem = item.find_element(By.CSS_SELECTOR, ".title, .primary-text")
                                if not title_elem:
                                    continue
                            except Exception:
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
                                except Exception:
                                    continue

                            # Check if already liked
                            try:
                                remove_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Remove from liked')]")
                                for remove_elem in remove_elements:
                                    if remove_elem.is_displayed():
                                        return "skip"
                            except Exception:
                                pass

                            # Close menu
                            try:
                                driver.execute_script("document.body.click();")
                                time.sleep(0.5)
                            except Exception:
                                pass

                        except Exception as item_error:
                            print(f" -> Error with item {idx+1}: {item_error}")
                            # Close any open menu
                            try:
                                driver.execute_script("document.body.click();")
                                time.sleep(0.5)
                            except Exception:
                                pass
                            continue

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
    parser = argparse.ArgumentParser(description="Move songs to YouTube Music Liked Songs.")
    parser.add_argument("filename", help="Path to the text file containing songs")
    args = parser.parse_args()

    songs = get_songs(args.filename)
    if not songs:
        print(f"No songs found in {args.filename}.")
        return

    print(f"Loaded {len(songs)} songs from {args.filename}.")

    if USER_DATA_DIR and not os.path.exists(USER_DATA_DIR):
        print(f"WARNING: User data directory not found at {USER_DATA_DIR}")

    driver = setup_chrome_driver(
        user_data_dir=USER_DATA_DIR,
        profile_directory=PROFILE_NAME,
        stealth_mode=True,
        start_maximized=True,
        mute_audio=True
    )

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
                print(" -> [SUCCESS] Added to liked songs")
            elif result == "skip":
                print(" -> [SKIP] Already in liked songs")
            else:
                print(" -> [ERROR] Could not process")

            sleep_time = random.uniform(MIN_SLEEP_TIME, MAX_SLEEP_TIME)
            time.sleep(sleep_time)

    finally:
        print("\nAll done! Closing browser.")
        driver.quit()


if __name__ == "__main__":
    main()