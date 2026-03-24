# Infyspringboard Course Auto-Clicker

Automatically clicks through Infyspringboard course slides, handles videos by seeking to the end, and works inside iframes.

---

## Features

- Auto-clicks the next arrow button on every slide
- Detects videos and seeks to the last 3 seconds instead of watching fully
- Searches inside iframes (where Infyspringboard loads its course player)
- Handles the first slide with extra retries and a manual fallback
- Asks you what to do if the button goes missing mid-course
- Never closes your browser — only disconnects when done

---

## Requirements

- Python 3.8 or higher
- Google Chrome installed
- Windows / Mac / Linux

---

## Installation (One Time Only)

Open a terminal or Command Prompt and run:

```
pip install playwright
playwright install chromium
```

---

## How to Run

### Step 1 — Close Chrome completely

Open Task Manager (`Ctrl + Shift + Esc`), find any `chrome.exe` processes, and End Task on all of them.

### Step 2 — Launch Chrome with remote debugging

**Command Prompt (cmd) — recommended on Windows:**
```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

**PowerShell:**
```
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList "--remote-debugging-port=9222"
```

**Mac:**
```
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

**Linux:**
```
pkill chromium
chromium --remote-debugging-port=9222
```

Then in a second terminal:
```
cd ~/Dev/AutoCert
python withvideo.py
```

> ⚠️ Always use Command Prompt on Windows, not PowerShell, to avoid token errors with the `--` flags.

### Step 3 — Navigate to your course

In the Chrome window that opened, log in to Infyspringboard and open your course until you can see the first slide on screen.

### Step 4 — Run the script

Open a second terminal or Command Prompt window, navigate to the folder where `withvideo.py` is saved, and run:

```
python withvideo.py
```

### Step 5 — Press Enter

The script will connect to your browser and ask you to press Enter when ready. Press Enter and it will start clicking through slides automatically.

---

## Configuration

You can change these values at the top of `withvideo.py`:

| Setting | Default | Description |
|---|---|---|
| `DELAY` | `4` | Seconds to wait between slide clicks |
| `VIDEO_SEEK_OFFSET` | `3` | Seeks to this many seconds before the video ends |

---

## What Happens During a Run

- **Normal slide** — waits `DELAY` seconds, clicks next arrow, moves on
- **Slide with video** — starts the video, seeks to near the end, waits for it to finish, then clicks next
- **First slide** — retries up to 10 times over 20 seconds; if it still fails, asks you to click next manually once and then takes over
- **Arrow not found 5 times in a row** — pauses and gives you three options:
  - `y` — keep trying
  - `d` — debug dump (prints all buttons found on page and inside iframes)
  - `n` — quit

---

## Stopping the Script

Press `Ctrl + C` at any time to stop. The script will print how many slides were processed and disconnect from the browser without closing it.

---

## Troubleshooting

**"Unexpected token" error in PowerShell**
Use Command Prompt (`cmd`) instead, or use the `Start-Process` command shown in Step 2.

**Script says "connecting" but hangs**
Chrome was not launched with `--remote-debugging-port=9222`. Close Chrome fully and relaunch using the command in Step 2.

**Arrow not found on first slide**
The course player may take a few extra seconds to load. The script retries for 20 seconds automatically. If it still fails, it will ask you to click next once manually.

**Video is not being detected**
The video may be inside a nested iframe or loaded via an embed (YouTube, Vimeo). In that case the script will skip video handling and just click next after the normal delay.

---

## Notes

- This script connects to your existing browser session and does not open a new one
- It never logs in on your behalf — you handle login manually
- Your browser stays open after the script finishes or is stopped