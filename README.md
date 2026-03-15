
[![Vibe Coding](https://img.shields.io/badge/Built%20with-Vibe%20Coding-bc13fe?style=for-the-badge&logo=google-gemini)](https://gemini.google.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

# Music Transfer & Scraping Tools

A collection of Python scripts designed to scrape, transfer, and manage your music libraries across Amazon Music, YouTube Music, and Spotify. 

This project was developed by **vive coding** using **Gemini 3 Pro** to automate the tedious process of migrating playlists between streaming platforms.

---

## ⚠️ Disclaimer
**Important:** These scripts use web automation (Selenium) to interact with music platforms. 
- Results are **not 100% accurate** due to differences in song metadata across platforms.
- **Human intervention is required** to review the final results of every script (e.g., checking if the correct song was "Liked" or after scrapping songs all the songs were added in produced text file or has the right name and other details).
- Use these tools responsibly and ensure you are logged in to the respective platforms.

---

## 🛠️ Prerequisites

Before running the scripts, ensure you have the following:

1.  **Python 3.7+**: [Download Python](https://www.python.org/downloads/)
2.  **Brave Browser**: The scripts are configured for Brave by default.
    - If you use Chrome or another Chromium browser, update the `BRAVE_PATH` in `web_utils.py`.
3.  **Dependencies**: Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Browser Profile (Optional but Recommended)**: 
    - To stay logged in and bypass automation detection, you can provide your browser's `User Data` path in the script configurations. This is usually: r"C:\Users\<Username>\AppData\Local\BraveSoftware\Brave-Browser\User Data".
    - **Note:** The browser must be **completely closed** for the profile to load successfully.

---

## 🚀 Usage Instructions

### 1. Scraping Your Music
Extract your "Liked Songs" or playlists into a text file.

*   **Amazon Music**: Run `amazon_song_scrapper.py`. 
    - Log in and navigate to your playlist when prompted.
*   **YouTube Music**: Run `yt_song_scrapper.py`.
    - It will automatically attempt to scrape your "Liked Songs" using your profile.

### 2. Moving Your Music
Transfer songs from a text file to a new platform.

*   **To YouTube Music**: Run `yt_mover.py <filename.txt>`.
    - Example: `python yt_mover.py amazon_songs.txt`
*   **To Spotify**: Run `spotify_mover.py <filename.txt>`.
    - Example: `python spotify_mover.py yt_songs.txt`

---

## ⚙️ Configuration

Each script contains a **Configuration Section** at the top. You may need to update:
- `USER_DATA_DIR`: Path to your browser's user data (e.g., `C:\Users\<Username>\AppData\Local\BraveSoftware\Brave-Browser\User Data`).
- `PROFILE_DIRECTORY`: Usually `"Default"`.
- `OUTPUT_FILE`: The name of the text file where songs will be saved.

---

## 📝 Troubleshooting
- **Automation Detection**: If a platform blocks you, ensure `stealth_mode=True` is set in the script (it is by default).
- **Driver Issues**: Selenium 4.6+ handles drivers automatically. Ensure you have an active internet connection on the first run.
- **Selector Errors**: Web structures change frequently. If a script fails to find buttons, the CSS selectors may need updating.
