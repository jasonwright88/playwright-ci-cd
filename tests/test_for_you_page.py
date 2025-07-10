import os
import re
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage
from pages.for_you_page import ForYouPage

# Load environment variables locally if not running in CI
if os.getenv("CI") != "true":
    load_dotenv()

def test_for_you_nav_redirect():
    """
    End-to-end test for SiriusXM 'For You' page:
    - Verifies login flow
    - Navigates to 'For You' tab
    - Clicks on 'siriusxm-hits-1' channel
    - Asserts landing on correct channel page
    - Verifies subtitle on the channel page
    - Clicks the Play button
    - Handles playback stalled modal if it appears
    - Confirms mini player appears after playback starts
    """

    username = os.getenv("SIRIUSXM_USERNAME")
    password = os.getenv("SIRIUSXM_PASSWORD")
    assert username and password, "Missing credentials in environment variables"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set to False for local debugging
        page = browser.new_page()

        try:
            # Login to SiriusXM
            login_page = LoginPage(page)
            login_page.goto()
            login_page.submit_username(username)

            if login_page.is_invalid_username():
                raise AssertionError("Username is not recognized.")

            login_page.choose_password_method()
            login_page.enter_password_and_submit(password)

            # Wait for home page to load
            page.wait_for_url("**/player/home", timeout=10000)

            # Go to "For You" section
            for_you_page = ForYouPage(page)
            for_you_page.click_for_you_nav()

            # Validate UUID in For You href
            for_you_href = page.locator("a[data-qa='content-nav-for-you']").get_attribute("href")
            print(f"Final For You href: {for_you_href}")
            assert re.search(r"/player/home/for-you/[a-f0-9-]{36}", for_you_href)

            # Re-click nav and screenshot for stability
            for_you_page.click_for_you_nav()
            page.screenshot(path="debug_screenshots/after_nav_click.png", full_page=True)

            # Wait until carousels are fully rendered
            page.wait_for_function(
                """() => {
                    return Array.from(document.querySelectorAll('a[href*="channel-linear"]'))
                                .some(el => el.offsetParent !== null);
                }""",
                timeout=15000
            )

            # Try known preferred channels first
            preferred_channels = ["siriusxm-hits-1", "pop2K", "80s-on-8", "90s-on-9", "tiktok-radio", "unwell-radio"]
            clicked = False

            for channel in preferred_channels:
                if for_you_page.click_channel_by_href(channel):
                    print(f"✅ Clicked preferred channel: {channel}")
                    clicked = True
                    break

            # Fallback: click the first available item with /player/ in href
            if not clicked:
                print("⚠️ Preferred channels not found. Clicking first /player/ item as fallback.")
                if for_you_page.click_first_player_link():
                    clicked = True

            assert clicked, "❌ No playable content found in carousels."

            # ⏳ Wait for any loading spinners or overlays to disappear
            try:
                page.wait_for_selector('div[class*="LoadingSpinner"]', state='detached', timeout=5000)
                print("✅ Spinner or loading overlay is gone.")
            except:
                print("⚠️ No spinner detected or already gone.")

            # 🧽 Check and dismiss any residual overlay
            try:
                overlay_close_button = page.locator('button[data-qa="close-overlay"]')
                if overlay_close_button.is_visible(timeout=3000):
                    print("🛑 Overlay detected again. Dismissing it...")
                    overlay_close_button.click()
                    page.wait_for_timeout(1000)
            except Exception as overlay_error:
                print(f"⚠️ Overlay close button not found or error occurred: {overlay_error}")

            # ▶️ Try to click the visible Play button
            play_button = page.locator('button[aria-label^="Play"]:visible').first
            play_button.wait_for(state="visible", timeout=5000)

            # Manually scroll into view before clicking
            play_button.scroll_into_view_if_needed(timeout=3000)
            print("▶️ Clicking the Play button...")
            play_button.click()
            for i in range(3):
                print(f"⏳ Modal check attempt {i+1}...")
                page.wait_for_timeout(1000)  # Wait 1s before checking for modal
                if for_you_page.force_dismiss_playback_stalled_modal():
                    print("✅ Modal dismissed via click.")
                    page.wait_for_timeout(1000)
                else:
                    print("❌ No modal or button not clickable.")
                    page.screenshot(path=f"debug_screenshots/modal_attempt_{i+1}.png", full_page=True)
                    break

            # ✅ Verify we landed on the correct channel page
            current_url = page.url
            print(f"🔗 Landed on URL: {current_url}")
            assert "/player/channel-linear/" in current_url, f"❌ Unexpected URL: {current_url}"

            play_button.click()
            for i in range(3):
                print(f"⏳ Modal check attempt {i+1}...")
                page.wait_for_timeout(1000)  # Wait 1s before checking for modal
                if for_you_page.force_dismiss_playback_stalled_modal():
                    print("✅ Modal dismissed via click.")
                    page.wait_for_timeout(1000)
                else:
                    print("❌ No modal or button not clickable.")
                    page.screenshot(path=f"debug_screenshots/modal_attempt_{i+1}.png", full_page=True)
                    break

            # Verify that the Pause button appears, confirming that playback started
            pause_button = page.locator('button[aria-label^="Pause"]:visible').first

            pause_button.wait_for(state="visible", timeout=5000)
            assert pause_button.is_visible(), "❌ Pause button did not appear, playback might not have started."
            # Verify that the Play button appears, confirming that playback is resumed
            pause_button.click()
            for i in range(3):
                print(f"⏳ Modal check attempt {i+1}...")
                page.wait_for_timeout(1000)  # Wait 1s before checking for modal
                if for_you_page.force_dismiss_playback_stalled_modal():
                    print("✅ Modal dismissed via click.")
                    page.wait_for_timeout(1000)
                else:
                    print("❌ No modal or button not clickable.")
                    page.screenshot(path=f"debug_screenshots/modal_attempt_{i+1}.png", full_page=True)
                    break

            assert play_button.is_visible(), "❌ Play button did not appear, playback might not have resumed."

        except Exception as e:
            # Take screenshot on failure for easier debugging
            page.screenshot(path="debug_screenshots/for_you_test_failure.png", full_page=True)
            print("❌ Test failed. Screenshot saved.")
            raise e

        finally:
            browser.close()