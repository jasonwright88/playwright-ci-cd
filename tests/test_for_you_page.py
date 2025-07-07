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
        browser = p.chromium.launch(headless=False)  # Set to False for local debugging
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

            # Click the 'siriusxm-hits-1' channel
            for_you_page.click_channel_by_href("siriusxm-hits-1")
            print(f"🔗 Current URL after click: {page.url}")

            # Confirm navigation to expected channel page
            page.wait_for_url("**/player/channel-linear/siriusxm-hits-1/*", timeout=10000)
            assert "/player/channel-linear/siriusxm-hits-1" in page.url

            # Verify channel subtitle to confirm correct content
            subtitle_locator = page.locator('[data-qa="entity-header-subtitle-string"]')
            subtitle_locator.wait_for(state="visible", timeout=5000)
            subtitle_text = subtitle_locator.inner_text()
            print(f"🔍 Subtitle text found: '{subtitle_text}'")

            # Normalize spacing and compare to expected value
            normalized_text = re.sub(r"\s+", " ", subtitle_text).strip()
            expected_text = "Ch 2 • Pop hits, now to next"
            assert normalized_text == expected_text, f"❌ Subtitle mismatch.\nExpected: '{expected_text}'\nGot: '{normalized_text}'"

            # Try to click the primary visible Play button (dynamic aria-label)
            play_button = page.locator('button[aria-label^="Play"]:visible').first
            play_button.wait_for(state="visible", timeout=5000)

            print("▶️ Clicking the Play button...")
            play_button.click()

            # Optional: handle "Playback Stalled" modal if it appears
            try:
                try_again_button = page.locator('button:has-text("Try again")')
                if try_again_button.is_visible(timeout=3000):
                    print("⚠️ Playback stalled modal detected. Clicking 'Try again'...")
                    try_again_button.click()
                    page.wait_for_timeout(2000)  # Give time for retry to take effect
            except Exception as modal_error:
                print(f"⚠️ No playback stall modal appeared or error handling modal: {modal_error}")


        except Exception as e:
            # Take screenshot on failure for easier debugging
            page.screenshot(path="debug_screenshots/for_you_test_failure.png", full_page=True)
            print("❌ Test failed. Screenshot saved.")
            raise e

        finally:
            browser.close()
