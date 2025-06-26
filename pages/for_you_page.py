from playwright.sync_api import Page
import time
import re

class ForYouPage:
    def __init__(self, page):
        self.page = page
        self.for_you_nav = "a[data-qa='content-nav-for-you']"
        self.music_nav = "a[data-qa='content-nav-music']"

    def click_for_you_nav(self):
        try:
            print("Clicking Music nav item to reset selection...")
            music_nav = self.page.locator(self.music_nav)
            music_nav.wait_for(state="visible", timeout=10000)
            music_nav.click(force=True)
            time.sleep(1)

            print("Clicking For You nav item...")
            for_you_nav = self.page.locator(self.for_you_nav)
            for_you_nav.wait_for(state="visible", timeout=10000)
            for_you_nav.click(force=True)

            # Wait for href on For You to contain a UUID (indicating routing triggered)
            timeout = 10
            start_time = time.time()
            while time.time() - start_time < timeout:
                href = for_you_nav.get_attribute("href")
                if href and re.search(r"/player/home/for-you/[a-f0-9-]{36}", href):
                    print(f"✅ For You nav href updated: {href}")
                    return
                time.sleep(0.5)

            raise TimeoutError("❌ For You nav href did not update with UUID.")

        except Exception as e:
            print("❌ Failed to verify For You nav href behavior.")
            screenshot_path = "debug_screenshots/for_you_nav_failure.png"
            self.page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
            raise e
