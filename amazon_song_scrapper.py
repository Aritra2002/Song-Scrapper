import time
import os
from web_utils import setup_chrome_driver

# --- CONFIGURATION ---
# Set this to your Brave User Data path if you want to stay logged in.
# Usually: r"C:\Users\<Username>\AppData\Local\BraveSoftware\Brave-Browser\User Data"
# WARNING: Brave must be COMPLETELY CLOSED for this to work.
USER_DATA_DIR = None  # Set this to your browser's user data path to stay logged in
PROFILE_DIRECTORY = "Default"
AMAZON_MUSIC_URL = "https://music.amazon.in/"
OUTPUT_FILE = "amazon_songs.txt"


def scrape_amazon_songs():
    """
    Precision Scraper: Uses small jumps and double-scraping to ensure 100% capture.
    """
    print(f"Initializing driver with profile: {PROFILE_DIRECTORY}")
    
    if USER_DATA_DIR and not os.path.exists(USER_DATA_DIR):
        print(f"WARNING: User data directory not found at {USER_DATA_DIR}")
        return

    driver = setup_chrome_driver(
        user_data_dir=USER_DATA_DIR,
        profile_directory=PROFILE_DIRECTORY,
        stealth_mode=True,
        start_maximized=True
    )

    try:
        print(f"Navigating to Amazon Music: {AMAZON_MUSIC_URL}")
        driver.get(AMAZON_MUSIC_URL)
        
        print("\n" + "="*60)
        print("ACTION REQUIRED:")
        print("1. Log in and navigate to your Playlist.")
        print("2. Ensure you are at the VERY TOP of the list.")
        print("="*60 + "\n")
        
        input(">>> Press ENTER here once the playlist is loaded <<<")
        print("Starting precision capture...")
        time.sleep(2)

        # 1. Container Discovery
        container = driver.execute_script("""
            function findScrollable() {
                let all = document.querySelectorAll('*');
                for (let el of all) {
                    if (el.scrollHeight > el.clientHeight + 200) {
                        let old = el.scrollTop;
                        el.scrollTop += 10;
                        if (el.scrollTop !== old) {
                            el.scrollTop = old;
                            return el;
                        }
                    }
                }
                return document.documentElement;
            }
            return findScrollable();
        """)

        all_songs_dict = {}
        last_max_index = 0
        stable_count = 0
        
        # Scrape script: Recursive Shadow DOM pierce
        scrape_js = """
            function ultraScrape() {
                let results = [];
                function pierce(root) {
                    let items = root.querySelectorAll('music-responsive-list-item, [role="row"], div, section');
                    items.forEach(el => {
                        let text = el.innerText || "";
                        let lines = text.split('\\n').map(s => s.trim()).filter(s => s.length > 0);
                        
                        let indexIdx = lines.findIndex(l => /^\\d+[.]?$/.test(l));
                        
                        if (indexIdx !== -1 && lines.length > indexIdx + 2) {
                            results.push({
                                index: parseInt(lines[indexIdx].replace(/[.]/g, '')),
                                title: lines[indexIdx + 1],
                                artist: lines[indexIdx + 2]
                            });
                        }
                    });
                    root.querySelectorAll('*').forEach(el => {
                        if (el.shadowRoot) pierce(el.shadowRoot);
                    });
                }
                pierce(document);
                return results;
            }
            return ultraScrape();
        """
        
        for _ in range(800):
            batch = driver.execute_script(scrape_js)
            for s in batch:
                if s['index'] not in all_songs_dict:
                    all_songs_dict[s['index']] = f"{s['title']} by {s['artist']}"
            
            time.sleep(0.5)
            batch = driver.execute_script(scrape_js)
            for s in batch:
                if s['index'] not in all_songs_dict:
                    all_songs_dict[s['index']] = f"{s['title']} by {s['artist']}"

            if all_songs_dict:
                current_max = max(all_songs_dict.keys())
                if current_max > last_max_index:
                    print(f"Progress: Captured up to song #{current_max}...")
                    last_max_index = current_max
                    stable_count = 0
                else:
                    stable_count += 1
            
            is_at_bottom = driver.execute_script("""
                let c = arguments[0];
                return (c.scrollTop + c.clientHeight) >= (c.scrollHeight - 10);
            """, container)
            
            if is_at_bottom and stable_count >= 10:
                print("Finalizing capture...")
                for _ in range(3):
                    time.sleep(1.5)
                    final_batch = driver.execute_script(scrape_js)
                    for s in final_batch:
                        all_songs_dict[s['index']] = f"{s['title']} by {s['artist']}"
                break
            
            driver.execute_script("arguments[0].scrollBy(0, 350);", container)
            time.sleep(1.2)

        print("Scraping complete. Scrolling back to the top...")
        driver.execute_script("arguments[0].scrollTo(0, 0);", container)
        time.sleep(2)

        if all_songs_dict:
            sorted_indices = sorted(all_songs_dict.keys())
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                for idx in sorted_indices:
                    f.write(f"{idx}. {all_songs_dict[idx]}\n")
            print(f"\nSuccess! Saved {len(all_songs_dict)} songs to {OUTPUT_FILE}.")
        else:
            print("No songs captured.")

    except Exception as e:
        print(f"Critical Error: {e}")
    finally:
        print("Closing browser in 5 seconds...")
        time.sleep(5)
        driver.quit()


if __name__ == "__main__":
    scrape_amazon_songs()
