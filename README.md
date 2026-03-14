# Amazon Music to YouTube Music Transfer Tool 

A set of Python scripts to scrape your liked songs/playlists from Amazon Music and automatically add them to your YouTube Music "Liked Songs".

## 🛠️ Prerequisites

1.  **Python 3.7+** installed.
2.  **Any chromium based browser**. (Selenium requires Chrome/Chromium drivers, `webdriver-manager` handles this, but having Chrome installed is often helpful. I have used [Brave Browser](https://brave.com/). To use any other browser please change BRAVE_PATH variable value with your browser's path.) 
3.  **Dependencies**: Install required packages via terminal:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Setup & Usage

### 1. Scrape Amazon Music
Run the scrapper to generate a list of your songs.
```bash
python amazon_song_scrapper.py
```
- A Brave window will open.
- **Action Required**: Log in to Amazon Music and navigate to your desired playlist/liked songs.
- Return to the terminal and press **ENTER**.
- The script will scroll and save your songs to `amazon_songs_backup.txt`.

### 2. Move to YouTube Music
Run the mover to search and "Like" these songs on YouTube Music.
```bash
python yt_mover.py
```
- **Action Required**: Log in to YouTube Music if prompted.
- The script will search for each song and click "Add to liked songs".

---

## 🛡️ Bypassing "Automated Browser" Detection (YouTube)

YouTube often blocks logins from automated browsers. To fix this, we use your **Real Brave Profile**.

### Step 1: Find your User Data Path
On Windows, your Brave User Data path is usually:
`C:\Users\<YourUsername>\AppData\Local\BraveSoftware\Brave-Browser\User Data`

### Step 2: Update `yt_mover.py`
Open `yt_mover.py` and update the `USER_DATA_DIR` variable:
```python
# Example for user
USER_DATA_DIR = r"C:\Users\<YourUsername>\AppData\Local\BraveSoftware\Brave-Browser\User Data"
```

### Step 3: Close Brave Completely
**CRITICAL**: You must close all open Brave windows before running `yt_mover.py`. If Brave is open, the script will fail to load your profile.

---

## 📝 Troubleshooting

- **Driver Errors**: The scripts use Selenium's built-in Manager to automatically match your Brave version. Ensure you have an active internet connection on the first run.
- **DNS/Network Errors**: If you see `ERR_NAME_NOT_RESOLVED`, check your internet connection or VPN settings.
- **Song Not Found**: The mover tries to find the best match. If a song is very obscure, it may skip it.
