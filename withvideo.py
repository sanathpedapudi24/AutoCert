"""
Infyspringboard Course Auto-Clicker
Automatically clicks through course slides via the next arrow button.

Changes:
- Iframe support: searches inside iframes for next button
- Video seek: jumps to last 3 seconds instead of watching fully
- First slide fix: retries aggressively + manual fallback prompt
"""

from playwright.sync_api import sync_playwright
import time

# Configuration
DELAY = 4               # seconds between clicks (adjust as needed)
VIDEO_SEEK_OFFSET = 3   # seconds from end to seek to (e.g. 3 = last 3 seconds)
URL = "https://infyspringboard.onwingspan.com"

# Selectors to try in order
SELECTORS = [
    "[aria-label='next content']",
    ".navigation-btn-frwd",
    "button:has-text('arrow_forward_ios')",
    "button.next-btn",
    "[aria-label='Next']",
    "[aria-label='next']",
    ".right-arrow",
    ".navigate-right",
    ".slide-nav-right",
    ".content-nav button:last-child",
]


# ---------------------------------------------------------------------------
# Iframe helpers
# ---------------------------------------------------------------------------

def get_all_contexts(page):
    """
    Returns a list of searchable contexts: the main page + every iframe frame.
    This lets us find elements that live inside iframes.
    """
    contexts = [page]
    try:
        for frame in page.frames:
            if frame != page.main_frame:
                contexts.append(frame)
    except Exception:
        pass
    return contexts


def query_selector_all_contexts(page, selector):
    """
    Searches for a selector across the main page AND all iframes.
    Returns (element, frame) for the first visible match found.
    """
    contexts = get_all_contexts(page)
    for ctx in contexts:
        try:
            el = ctx.query_selector(selector)
            if el:
                return el, ctx
        except Exception:
            pass
    return None, None


# ---------------------------------------------------------------------------
# Video handling
# ---------------------------------------------------------------------------

def handle_video_if_present(page, slide_num):
    """
    Checks if a video is present on current slide (main page or iframe).
    Starts it if paused, then seeks to near the end so we don't wait.
    Returns True if a video was found and handled, False otherwise.
    """
    try:
        # Search for video in main page and all iframes
        video_frame = None
        for ctx in get_all_contexts(page):
            try:
                v = ctx.query_selector("video")
                if v:
                    video_frame = ctx
                    break
            except Exception:
                pass

        if not video_frame:
            return False

        # Check if paused
        is_paused = video_frame.evaluate("""() => {
            const v = document.querySelector('video');
            return v ? v.paused : true;
        }""")

        if is_paused:
            print(f"🎬 Slide {slide_num}: Video detected, starting playback...")

            clicked = False
            overlay_selectors = [
                ".play-icon", ".play-btn", ".play-button",
                "[class*='play-icon']", "[class*='play-btn']",
                "[class*='playButton']", "[class*='play_button']",
                "[aria-label='Play']", "button.vjs-play-control", ".ytp-play-button",
            ]
            for sel in overlay_selectors:
                try:
                    btn = video_frame.query_selector(sel)
                    if btn and btn.is_visible():
                        btn.click()
                        clicked = True
                        print(f"  ▶ Clicked overlay play button ({sel})")
                        break
                except Exception:
                    pass

            if not clicked:
                print(f"  ▶ Using JS video.play()...")
                video_frame.evaluate("() => { const v = document.querySelector('video'); if(v) v.play(); }")

            time.sleep(2)  # let it start buffering

        # --- SEEK TO NEAR END ---
        seek_result = video_frame.evaluate(f"""() => {{
            const v = document.querySelector('video');
            if (!v) return {{ skipped: false, reason: 'no video' }};
            const dur = v.duration;
            if (!dur || isNaN(dur) || dur < 5) return {{ skipped: false, reason: 'duration unknown or too short' }};
            const seekTo = Math.max(0, dur - {VIDEO_SEEK_OFFSET});
            v.currentTime = seekTo;
            return {{ skipped: true, seekTo: Math.floor(seekTo), duration: Math.floor(dur) }};
        }}""")

        if seek_result.get('skipped'):
            print(f"  ⏩ Slide {slide_num}: Seeked to {seek_result['seekTo']}s / {seek_result['duration']}s")
        else:
            print(f"  ⚠️  Slide {slide_num}: Could not seek ({seek_result.get('reason', '?')}), waiting for end...")

        # Wait for video to finish (now very short since we seeked to near end)
        print(f"⏳ Slide {slide_num}: Waiting for video to end...")
        timeout = 30   # max 30 seconds after seeking
        elapsed = 0
        check_interval = 1

        while elapsed < timeout:
            time.sleep(check_interval)
            elapsed += check_interval

            state = video_frame.evaluate("""() => {
                const v = document.querySelector('video');
                if (!v) return { ended: true, current: 0, duration: 0 };
                return {
                    ended: v.ended || (v.paused && v.currentTime > 0 && v.currentTime >= v.duration - 1),
                    current: Math.floor(v.currentTime),
                    duration: Math.floor(v.duration) || 0
                };
            }""")

            current = state['current']
            duration = state['duration']
            print(f"  ▶ {current}s / {duration}s        ", end="\r")

            if state['ended']:
                print(f"\n✅ Slide {slide_num}: Video done!")
                time.sleep(1)
                return True

        print(f"\n⚠️  Slide {slide_num}: Video wait timed out, proceeding anyway.")
        return True

    except Exception as e:
        print(f"⚠️  Slide {slide_num}: Video handling error: {e}")
        return False


# ---------------------------------------------------------------------------
# Arrow click
# ---------------------------------------------------------------------------

def find_and_click_arrow(page, slide_num, force=False):
    """
    Searches for the next arrow in main page + all iframes.
    Returns True if clicked successfully.
    """
    for selector in SELECTORS:
        element, frame = query_selector_all_contexts(page, selector)
        if element:
            try:
                if element.is_visible() or force:
                    element.click(force=force)
                    location = "iframe" if frame != page else "main page"
                    print(f"✓ Slide {slide_num}: Clicked next arrow [{location}] (selector: {selector})")
                    return True
            except Exception:
                try:
                    element.click(force=True)
                    print(f"✓ Slide {slide_num}: Force-clicked next arrow (selector: {selector})")
                    return True
                except Exception:
                    pass
    return False


# ---------------------------------------------------------------------------
# First slide bootstrap
# ---------------------------------------------------------------------------

def bootstrap_first_slide(page):
    """
    Handles the first slide more carefully.
    Waits longer, retries more aggressively, and offers a manual fallback.
    """
    print("🔍 Detecting first slide state...")

    # Wait a bit longer for the page to fully load
    time.sleep(3)

    # Retry up to 10 times with 2s gaps (20 seconds total)
    for attempt in range(1, 11):
        print(f"  Attempt {attempt}/10: looking for next button...", end=" ")
        success = find_and_click_arrow(page, slide_num=1)
        if success:
            print(f"✅ First slide navigated successfully!")
            return True
        else:
            print("not found yet.")
            time.sleep(2)

    # All retries failed — offer manual fallback
    print()
    print("⚠️  Could not auto-click the first slide after 10 attempts.")
    print("    This sometimes happens because the course player loads slowly")
    print("    or requires an interaction first (e.g. a 'Start' button).")
    print()
    print("👉 Please manually click NEXT in your browser to go to slide 2.")
    print("   Then press ENTER here and the script will take over from slide 2.")
    input()
    print("✅ Manual first slide done. Auto-clicking from slide 2 onwards...\n")
    return False


# ---------------------------------------------------------------------------
# Debug helper
# ---------------------------------------------------------------------------

def debug_dump_buttons(page):
    """Prints all buttons and clickable elements across main page + iframes."""
    print("\n🔍 DEBUG: Scanning all buttons and clickable elements...\n")
    for ctx in get_all_contexts(page):
        label = getattr(ctx, 'url', 'main')
        print(f"  [Context: {str(label)[:60]}]")
        try:
            elements = ctx.query_selector_all(
                "button, [role='button'], a, [class*='arrow'], [class*='next'], [class*='nav']"
            )
            for el in elements:
                try:
                    tag = el.evaluate("e => e.tagName")
                    text = el.inner_text().strip()[:40]
                    classes = el.get_attribute("class") or ""
                    aria = el.get_attribute("aria-label") or ""
                    visible = el.is_visible()
                    print(f"    [{tag}] text='{text}' class='{classes[:50]}' aria='{aria}' visible={visible}")
                except Exception:
                    pass
        except Exception as e:
            print(f"    (could not scan: {e})")
    print("\n🔍 DEBUG DONE\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("Infyspringboard Course Auto-Clicker")
    print("=" * 60)
    print(f"Site        : {URL}")
    print(f"Delay       : {DELAY}s between slides")
    print(f"Video seek  : last {VIDEO_SEEK_OFFSET}s of each video")
    print(f"Iframe support: YES")
    print()

    with sync_playwright() as p:
        print("🔌 Connecting to your existing Chromium browser...")
        print("   (Make sure Chromium was launched with --remote-debugging-port=9222)")
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]

        # Find Infyspringboard tab or fall back to first tab
        page = None
        for pg in context.pages:
            if "infyspringboard" in pg.url:
                page = pg
                break
        if not page:
            page = context.pages[0]

        print(f"✅ Connected! Active tab: {page.url[:80]}")
        print()
        print("⏳ Navigate to your course module page in the browser.")
        print("   When you're on the first slide and ready, press ENTER here.")
        input()

        print("\n🚀 Starting...\n")

        # --- Handle first slide specially ---
        bootstrap_first_slide(page)

        # --- Main loop (slide 2 onwards) ---
        slide_count = 1
        consecutive_misses = 0
        max_consecutive_misses = 5

        try:
            while True:
                time.sleep(DELAY)
                slide_count += 1

                # Handle video if present
                handle_video_if_present(page, slide_count)

                # Click next arrow
                success = find_and_click_arrow(page, slide_count)

                if success:
                    consecutive_misses = 0
                else:
                    consecutive_misses += 1
                    print(f"✗ Slide {slide_count}: Arrow not found ({consecutive_misses}/{max_consecutive_misses})")

                    if consecutive_misses >= max_consecutive_misses:
                        print()
                        print("⚠️  Arrow not found 5 times in a row!")
                        print("   Options:")
                        print("   [y] Keep trying")
                        print("   [d] Debug dump (show all buttons on page)")
                        print("   [n] Quit")
                        response = input("Choice (y/d/n): ").strip().lower()

                        if response == 'n':
                            print("\n🛑 Quitting.")
                            break
                        elif response == 'd':
                            debug_dump_buttons(page)
                            consecutive_misses = 0
                        else:
                            print("✓ Continuing...\n")
                            consecutive_misses = 0

        except KeyboardInterrupt:
            print(f"\n\n⏹️  Stopped by user (Ctrl+C)")

        finally:
            print("\n" + "=" * 60)
            print(f"📊 Total slides processed: {slide_count}")
            print("=" * 60)
            browser.close()
            print("✓ Disconnected from browser.\n")


if __name__ == "__main__":
    main()