from playwright.sync_api import sync_playwright

def test_siriusxm_homepage():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.siriusxm.com/")
        assert "SiriusXM" in page.title()
        browser.close()
