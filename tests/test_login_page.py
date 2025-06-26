from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage
from dotenv import load_dotenv
import os

if os.getenv("CI") != "true":
    from dotenv import load_dotenv
    load_dotenv()

def test_full_login_flow():
    """Test the end-to-end login flow for SiriusXM using Playwright."""
    
    # Load credentials from .env
    load_dotenv()
    username = os.getenv("SIRIUSXM_USERNAME")
    password = os.getenv("SIRIUSXM_PASSWORD")

    # Ensure required credentials are present
    assert username, "Missing env var: SIRIUSXM_USERNAME"
    assert password, "Missing env var: SIRIUSXM_PASSWORD"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set to False to watch the test
        page = browser.new_page()
        login_page = LoginPage(page)

        # Step 1: Navigate to login page
        login_page.goto()

        # Step 2: Submit username
        login_page.submit_username(username)

        # Step 3: Check for invalid username
        if login_page.is_invalid_username():
            assert False, "Username is not recognized."

        # Step 4: Select password method and continue
        login_page.choose_password_method()

        # Step 5: Enter password and submit
        login_page.enter_password_and_submit(password)

        # Step 6: Confirm navigation to /player
        page.wait_for_load_state("networkidle")
        assert "player" in page.url.lower(), f"Unexpected post-login URL: {page.url}"

        # Step 7: Wait and confirm user is on /player/home
        page.wait_for_url("**/player/home", timeout=10000)
        assert page.url.startswith("https://www.siriusxm.com/player/home"), \
            f"Expected to land on /player/home but got {page.url}"

        browser.close()

