## Setup Instructions (Windows)

First, clone this repository and follow the steps below.

### Prerequisites

1. Install **Python (3.8 or above)**
   Make sure Python is added to PATH.
   Check installation:

   ```bash
   python --version
   ```

2. Install **Google Chrome** (recommended)

3. Install Playwright:

   ```bash
   pip install playwright
   playwright install
   ```

---

### Steps to Run

1. Close all running Chrome instances (important).

2. Open Command Prompt and start Chrome with remote debugging:

   ```bash
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
   ```

   (Adjust path if Chrome is installed elsewhere)

3. A Chrome window will open. Log in to Infosys Springboard:
   https://infyspringboard.onwingspan.com/web/en/page/home

4. Navigate to your course module (where the next arrow is visible).

5. Open a new Command Prompt, go to the cloned repository folder:

   ```bash
   cd path\to\your\repo
   ```

6. Run the script:

   ```bash
   python withvideo.py
   ```

7. Press **ENTER** in the terminal after reaching the course page.

---

### Notes

* The script automatically:

  * Detects videos and plays them
  * Waits until the video finishes
  * Clicks the "Next" arrow button
* If the arrow is not found multiple times, you’ll be prompted to continue.

---

### Troubleshooting

* If Chrome path fails, try:

  ```bash
  chrome --remote-debugging-port=9222
  ```
* Ensure no other process is using port `9222`
* Run Command Prompt as Administrator if needed

---
