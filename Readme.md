## Setup Instructions

First, clone this repository and follow the steps below.

### For Linux-based Systems

1. Install Chromium browser:

   ```bash
   sudo apt install chromium
   ```

2. Kill any running Chromium processes:

   ```bash
   pkill chromium
   ```

3. Start Chromium with remote debugging enabled:

   ```bash
   chromium --remote-debugging-port=9222
   ```

4. A Chromium window will open. Log in to Infosys Springboard:
   https://infyspringboard.onwingspan.com/web/en/page/home

5. After logging in, navigate to your course (where you can see the arrows).

6. Open a new terminal, go to the cloned repository folder, and run:

   ```bash
   python withvideo.py
   ```
