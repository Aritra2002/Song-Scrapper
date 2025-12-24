# Amazon Music to YouTube Music Transfer Tool

This project provides a set of Python scripts to scrape songs from an Amazon Music playlist and add them to your "Liked Songs" on YouTube Music. It uses Selenium with the Brave browser for automation.

## Components

1.  **`amazon_song_scrapper.py`**: Scrapes song titles and artists from an Amazon Music playlist. It handles auto-scrolling and parsing of the page content, saving the results to a text file.
2.  **`yt_mover.py`**: Reads the scraped song list and automates the process of searching for each song on YouTube Music and adding it to your "Liked Songs" library.
3.  **`web_utils.py`**: A utility module containing helper functions for WebDriver setup and scrolling (intended for shared use/refactoring).

## Prerequisites

*   Python 3.x
*   Any chromium based browser. (Selenium requires Chrome/Chromium drivers, `webdriver-manager` handles this, but having Chrome installed is often helpful. I have used [Brave Browser](https://brave.com/). To use any other browser please change BRAVE_PATH variable value with your browser's path.)

## Installation

1.  Clone this repository or download the source code.
2.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

**Important:** The scripts currently have a hardcoded path to the Brave browser executable.

*   **Default Path:** `C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe`

If your Brave installation is in a different location (or if you are on macOS/Linux), you **must** update the `BRAVE_PATH` variable in both `amazon_song_scrapper.py` and `yt_mover.py`.

## Usage

### Step 1: Scrape Songs from Amazon Music

1.  Run the scraper script:
    ```bash
    python amazon_song_scrapper.py
    ```
2.  A Brave browser window will open and navigate to Amazon Music.
3.  **Log in** to your Amazon account manually.
4.  Navigate to the specific **Playlist** you want to transfer.
5.  Return to your terminal/command prompt and press **ENTER**.
6.  The script will automatically scroll through the playlist to load all songs and then scrape the data.
7.  When finished, the songs will be saved to `amazon_songs_backup.txt`.
8.  Close the browser or press Enter if prompted.

### Step 2: Add Songs to YouTube Music

1.  Run the mover script:
    ```bash
    python yt_mover.py
    ```
2.  A Brave browser window will open and navigate to YouTube Music.
3.  **Log in** to your Google/YouTube account manually.
4.  Return to your terminal/command prompt and press **ENTER**.
5.  The script will read `amazon_songs_backup.txt` and process each song:
    *   It searches for the song on YouTube Music.
    *   It attempts to "Like" the first valid result.
    *   It skips songs that are already liked.
6.  Monitor the terminal for progress and any errors.

## Disclaimer

*   **Automation & Terms of Service:** Automated scraping and interaction with websites may violate their Terms of Service. Use this tool responsibly and at your own risk.
*   **Accuracy:** The matching process relies on search results. It may not always pick the exact version of the song you want (e.g., live versions vs. studio versions).
*   **Maintenance:** Web interface changes by Amazon or YouTube can break these scripts at any time.
