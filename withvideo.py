"""
Infyspringboard Course Auto-Clicker
Automatically clicks through course slides via the next arrow button.
"""

from jaraco import context
from playwright.sync_api import sync_playwright
import time
import sys

# Configuration
DELAY = 4  # seconds between clicks (adjust as needed)
URL = "https://infyspringboard.onwingspan.com"

# Selectors to try in order
SELECTORS = [
    "[aria-label='next content']",       # Primary - confirmed working
    ".navigation-btn-frwd",              # Class-based fallback
    "button:has-text('arrow_forward_ios')",
    "button.next-btn",
    "[aria-label='Next']",
    "[aria-label='next']",
    ".right-arrow",
    ".navigate-right",
    ".slide-nav-right",
    ".content-nav button:last-child",
]

def handle_video_if_present(page, slide_num):
    """
    Checks if a video is present on the current slide.
    If yes, clicks play and waits for it to finish.
    Returns True if a video was found and handled, False otherwise.
    """
    try:
        video = page.query_selector("video")
        if not video:
            return False

        # Check if video is paused
        is_paused = page.evaluate("() => { const v = document.querySelector('video'); return v ? v.paused : true; }")

        if is_paused:
            print(f"🎬 Slide {slide_num}: Video detected, clicking play...")
            # Try clicking the play button overlay first, then the video itself
            play_btn = page.query_selector(".play-button, [aria-label='Play'], button.vjs-play-control, .ytp-play-button")
            if play_btn and play_btn.is_visible():
                play_btn.click()
            else:
                video.click()  # Click the video itself to play
            time.sleep(1)

        # Wait for video to finish
        print(f"⏳ Slide {slide_num}: Waiting for video to finish...")
        timeout = 3600  # max 1 hour wait
        elapsed = 0
        check_interval = 3  # check every 3 seconds

        while elapsed < timeout:
            time.sleep(check_interval)
            elapsed += check_interval
            ended = page.evaluate("""() => {
                const v = document.querySelector('video');
                if (!v) return true;
                return v.ended || (v.paused && v.currentTime > 0 && v.currentTime >= v.duration - 1);
            }""")
            current = page.evaluate("() => { const v = document.querySelector('video'); return v ? Math.floor(v.currentTime) : 0; }")
            duration = page.evaluate("() => { const v = document.querySelector('video'); return v ? Math.floor(v.duration) : 0; }")
            print(f"  ▶ {current}s / {duration}s", end="\r")

            if ended:
                print(f"\n✅ Slide {slide_num}: Video finished ({duration}s)")
                time.sleep(1)  # brief pause before next click
                return True

        print(f"\n⚠️  Slide {slide_num}: Video wait timed out, proceeding anyway.")
        return True

    except Exception as e:
        print(f"⚠️  Slide {slide_num}: Video handling error: {e}")
        return False


def find_and_click_arrow(page, slide_num):
    """
    Attempts to find and click the next arrow button using multiple selectors.
    
    Args:
        page: The Playwright page object
        slide_num: Current slide number for logging
        
    Returns:
        True if click was successful, False if arrow not found
    """
    for selector in SELECTORS:
        try:
            # Try to get the element
            element = page.query_selector(selector)
            
            if element and element.is_visible():
                # Element found and visible, click it
                element.click()
                print(f"✓ Slide {slide_num}: Clicked next arrow (selector: {selector})")
                return True
            elif element:
                # Element exists but may not be visible
                try:
                    element.click(force=True)
                    print(f"✓ Slide {slide_num}: Clicked next arrow via force (selector: {selector})")
                    return True
                except Exception as e:
                    # Element not clickable, try next selector
                    pass
                    
        except Exception as e:
            # Selector failed, try next one
            pass
    
    # No selector worked
    return False


def debug_dump_buttons(page):
    """Prints all buttons and clickable elements found on the page."""
    print("\n🔍 DEBUG: Scanning all buttons and clickable elements...\n")
    elements = page.query_selector_all("button, [role='button'], a, [class*='arrow'], [class*='next'], [class*='nav']")
    for el in elements:
        try:
            tag = el.evaluate("e => e.tagName")
            text = el.inner_text().strip()[:40]
            classes = el.get_attribute("class") or ""
            aria = el.get_attribute("aria-label") or ""
            visible = el.is_visible()
            print(f"  [{tag}] text='{text}' class='{classes[:60]}' aria='{aria}' visible={visible}")
        except:
            pass
    print("\n🔍 DEBUG DONE\n")


def main():
    """Main execution function."""
    print("=" * 60)
    print("Infyspringboard Course Auto-Clicker")
    print("=" * 60)
    print(f"Opening: {URL}")
    print(f"Delay between clicks: {DELAY} seconds")
    print(f"Total selectors to try: {len(SELECTORS)}")
    print()
    
    with sync_playwright() as p:
        # Launch browser using existing user data with login info
        import os
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0]  # use your existing tab
        
        # Open the URL
        page.goto(URL)
        
        print("📱 Browser opened. Please LOG IN and navigate to your course module.")
        print("⏳ Press ENTER in this terminal when ready to start auto-clicking...\n")
        
        # Wait for user to press Enter
        input()
        
        print("🚀 Starting auto-click sequence...\n")
        
        slide_count = 0
        consecutive_misses = 0
        max_consecutive_misses = 5
        
        try:
            while True:
                # Wait for the configured delay
                time.sleep(DELAY)
                
                slide_count += 1

                # Handle video if present on this slide
                handle_video_if_present(page, slide_count)

                # Try to find and click the next arrow
                success = find_and_click_arrow(page, slide_count)
                
                if success:
                    # Reset consecutive miss counter on successful click
                    consecutive_misses = 0
                else:
                    # Increment miss counter
                    consecutive_misses += 1
                    print(f"✗ Slide {slide_count}: Arrow not found ({consecutive_misses}/{max_consecutive_misses})")
                    
                    # Check if we've hit the threshold for missing the arrow
                    if consecutive_misses >= max_consecutive_misses:
                        print()
                        print("⚠️  Arrow button not found 5 times in a row!")
                        response = input("Continue trying? (y/n): ").strip().lower()
                        
                        if response != 'y':
                            print("\n🛑 User chose to quit.")
                            break
                        else:
                            print("✓ Continuing...\n")
                            consecutive_misses = 0  # Reset counter
        
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Interrupted by user (Ctrl+C)")
        
        finally:
            # Cleanup and summary
            print("\n" + "=" * 60)
            print(f"📊 Total slides clicked: {slide_count - 1}")
            print("=" * 60)
            
            # Close browser
            context.close()
            print("✓ Browser closed. Script ended.\n")


if __name__ == "__main__":
    main()