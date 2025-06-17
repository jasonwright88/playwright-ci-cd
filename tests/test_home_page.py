from playwright.sync_api import sync_playwright  # Sync API for Playwright
from pages.home_page import HomePage            # Import the HomePage object

# Test function using pytest naming convention (must start with 'test_')
def test_homepage_nav_and_start_listening():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # optional: see what's happening
        page = browser.new_page()
        homepage = HomePage(page)
        homepage.goto()

        assert homepage.is_nav_visible()
        homepage.click_start_listening()

        # Validate the new URL or action after clicking "Start Listening"
        assert "player" in page.url.lower() or "siriusxm" in page.url.lower()

        browser.close()
