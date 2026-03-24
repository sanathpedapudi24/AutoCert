"""
Infyspringboard Course Auto-Clicker
Automatically clicks through course slides via the next arrow button.
"""

from playwright.sync_api import sync_playwright
import time
import sys

# Configuration
DELAY = 4  # seconds between clicks (adjust as needed)
URL = "https://infyspringboard.onwingspan.com"

# Selectors to try in order
SELECTORS = [
    "button.next-btn",
    "[aria-label='Next']",
    "[aria-label='next']",
    ".right-arrow",
    ".navigate-right",
    ".slide-nav-right",
    "button:has-text('Next')",
    ".content-nav button:last-child",
]

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
        # Launch browser (headless=False for visible window)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
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
            browser.close()
            print("✓ Browser closed. Script ended.\n")


if __name__ == "__main__":
    main()
