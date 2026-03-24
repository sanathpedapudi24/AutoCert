# Infyspringboard Course Auto-Clicker

Automatically clicks through Infyspringboard course slides, handles videos by skipping to the end, and works inside iframes.

---

## Features

- Auto-clicks the next arrow button on every slide  
- Detects videos and skips to the last few seconds  
- Works inside iframes (Infyspringboard player support)  
- Handles first slide with retries + manual fallback  
- Prompts user if navigation fails mid-course  
- Keeps your browser open (no auto-close)

---

## Requirements

- Python 3.8 or higher  
- Google Chrome installed  
- Windows OS  

---

## Installation (One Time)

Open Command Prompt (cmd) and run:

```
pip install playwright
playwright install chromium
```

---

## How to Run (Windows)

### Step 1 — Close Chrome completely

- Press Ctrl + Shift + Esc → Task Manager  
- End all chrome.exe processes  

---

### Step 2 — Start Chrome with debugging enabled

Open Command Prompt and run:

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chromium-debug-profile"
```

If Chrome isn't at that path, find it:

```
where chrome
```

Or right-click your Chrome shortcut → Properties → check "Target" path.

The `--user-data-dir` flag is important — it must point to a separate profile folder (not your default Chrome profile), otherwise Chrome will refuse to start a second instance.

---

### Step 3 — Verify it's running

Open your browser and go to:

```
http://localhost:9222/json
```

If you see JSON output, debugging is working correctly.

---

### Step 4 — Open your course

- In the Chrome window that opened  
- Log in to Infyspringboard  
- Open your course  
- Stay on the first slide  

---

### Step 5 — Run the script

Open another Command Prompt:

```
cd path\to\your\folder
python withvideo.py
```

---

### Step 6 — Start automation

- Press Enter when prompted  
- Script will begin auto-clicking slides  

---

## Configuration

Edit values inside `withvideo.py`:

| Setting | Default | Description |
|--------|--------|------------|
| DELAY | 4 | Time between slide clicks (seconds) |
| VIDEO_SEEK_OFFSET | 3 | Seconds before video end to skip to |

---

## Stop Script

Press Ctrl + C to stop safely.

---

## Notes

- Uses your existing browser session  
- Does NOT log in automatically  
- Browser stays open after execution  
`