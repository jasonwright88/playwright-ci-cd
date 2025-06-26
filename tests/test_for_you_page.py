import os
import re
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage
from pages.for_you_page import ForYouPage

if os.getenv("CI") != "true":
    from dotenv import load_dotenv
    load_dotenv()

def test_for_you_nav_redirect():
    # Load environment variables for username/password
    load_dotenv()
    username = os.getenv("SIRIUSXM_USERNAME")
    password = os.getenv("SIRIUSXM_PASSWORD")

    with sync_playwright() as p:
        # Launch browser in headed mode for debugging (set headless=True for CI)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Start login flow
        login_page = LoginPage(page)
        login_page.goto()
        login_page.submit_username(username)

        # Fail fast if the username is invalid
        if login_page.is_invalid_username():
            assert False, "Username is not recognized."

        login_page.choose_password_method()
        login_page.enter_password_and_submit(password)

        # Confirm we have landed on the SiriusXM player home page
        page.wait_for_url("**/player/home", timeout=10000)

        # Instantiate the ForYouPage object which includes nav selectors
        for_you_page = ForYouPage(page)

        # Interact with the For You nav via a controlled flow
        for_you_page.click_for_you_nav()

        # Validate that the href of the "For You" link now includes the user-specific UUID path
        for_you_href = page.locator("a[data-qa='content-nav-for-you']").get_attribute("href")
        print(f"Final For You href: {for_you_href}")

        # The href should now contain the full path to /player/home/for-you/<uuid>
        assert re.search(r"/player/home/for-you/[a-f0-9-]{36}", for_you_href)
