from playwright.sync_api import sync_playwright

def test_youtube_search():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.youtube.com/")
        page.fill("input#search", "Playwright Python")
        page.press("input#search", "Enter")
        page.wait_for_selector("ytd-video-renderer")  # Wait for search results
        assert page.locator("ytd-video-renderer").count() > 0
        browser.close()
