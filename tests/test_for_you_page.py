import os
import re
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage
from pages.for_you_page import ForYouPage

# Load environment variables from a .env file unless running in CI
if os.getenv("CI") != "true":
    load_dotenv()

def test_for_you_nav_redirect():
    """
    End-to-end test that verifies the 'For You' navigation updates with a UUID-based URL
    and that a specific channel ('siriusxm-hits-1') can be found and clicked.
    """
    # Retrieve credentials from environment variables
    username = os.getenv("SIRIUSXM_USERNAME")
    password = os.getenv("SIRIUSXM_PASSWORD")

    with sync_playwright() as p:
        # Launch browser in headless mode (switch to False for local debugging)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Start the login flow
        login_page = LoginPage(page)
        login_page.goto()
        login_page.submit_username(username)

        # Abort early if username is not recognized
        if login_page.is_invalid_username():
            assert False, "Username is not recognized."

        # Continue login with password method
        login_page.choose_password_method()
        login_page.enter_password_and_submit(password)

        # Confirm landing on the home page
        page.wait_for_url("**/player/home", timeout=10000)

        # Navigate to and verify the 'For You' section
        for_you_page = ForYouPage(page)
        for_you_page.click_for_you_nav()

        # Confirm the href has updated to include the UUID
        for_you_href = page.locator("a[data-qa='content-nav-for-you']").get_attribute("href")
        print(f"Final For You href: {for_you_href}")
        assert re.search(r"/player/home/for-you/[a-f0-9-]{36}", for_you_href)

        # Click the For You nav again for stability and capture screenshot
        for_you_page.click_for_you_nav()
        page.screenshot(path="debug_screenshots/after_nav_click.png", full_page=True)

        # Wait for the carousel section to be populated and visible
        page.wait_for_function(
            """() => {
                return Array.from(document.querySelectorAll('a[href*="channel-linear"]'))
                            .some(el => el.offsetParent !== null);
            }""",
            timeout=15000
        )

        # Attempt to find and click the desired channel
        for_you_page.click_channel_by_href("siriusxm-hits-1")
        print(f"🔗 Current URL after click: {page.url}")

        # Wait for redirect to channel page and validate URL
        page.wait_for_url("**/player/channel-linear/siriusxm-hits-1/*", timeout=10000)
        assert "/player/channel-linear/siriusxm-hits-1" in page.url
