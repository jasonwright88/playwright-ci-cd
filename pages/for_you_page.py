from playwright.sync_api import Page
import time
import re

class ForYouPage:
    def __init__(self, page: Page):
        self.page = page
        self.for_you_nav = "a[data-qa='content-nav-for-you']"
        self.music_nav = "a[data-qa='content-nav-music']"

    def click_for_you_nav(self):
        """
        Navigates to the For You tab by first clicking the Music tab to reset state.
        Then waits for the For You nav to update its href with a UUID path.
        """
        try:
            print("Clicking Music nav item to reset selection...")
            music_nav = self.page.locator(self.music_nav)
            music_nav.wait_for(state="visible", timeout=10000)
            music_nav.click(force=True)
            time.sleep(1)  # Give UI time to register selection

            print("Clicking For You nav item...")
            for_you_nav = self.page.locator(self.for_you_nav)
            for_you_nav.wait_for(state="visible", timeout=10000)
            for_you_nav.click(force=True)

            # Wait for the href to update with a UUID (indicating navigation occurred)
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

    def click_channel_by_href(self, channel_slug: str, max_scrolls: int = 10):
        """
        Searches all carousels for a channel link with href format:
        /player/channel-linear/{slug}/{uuid}
        and clicks it using JS if necessary.
        """
        pattern = re.compile(rf"/player/channel-linear/{re.escape(channel_slug)}/[a-f0-9-]+")
        print(f"🔍 Looking for hrefs matching regex: {pattern.pattern}")

        carousels = self.page.locator('[data-qa^="content-carousel"]')
        carousel_count = carousels.count()
        print(f"🎠 Found {carousel_count} carousels.")

        for c in range(carousel_count):
            print(f"\n➡️ Checking carousel {c + 1} of {carousel_count}")
            carousel = carousels.nth(c)

            for attempt in range(max_scrolls):
                links = carousel.locator('a[href*="/player/channel-linear/"]')
                total_links = links.count()
                print(f"🔗 Found {total_links} potential link(s) on scroll attempt {attempt + 1}")

                for i in range(total_links):
                    link = links.nth(i)
                    href = link.get_attribute("href") or ""
                    if not pattern.match(href):
                        continue

                    print(f"🔍 Link {i} href: {href}")

                    # Force scroll into view and JS click to ensure interaction
                    element_handle = link.element_handle()
                    if element_handle:
                        print("📜 Forcing scroll into view and JS click...")
                        self.page.evaluate(
                            """el => {
                                el.scrollIntoView({behavior: 'auto', block: 'center'});
                                el.click();
                            }""",
                            element_handle
                        )
                        return
                    else:
                        print("❌ Could not resolve ElementHandle. Skipping.")
                        continue

                # Scroll carousel forward if Next button is available
                next_btn = carousel.locator('button:has(svg path[d*="M8.293"])')
                if next_btn.count() > 0 and next_btn.first.is_enabled():
                    print("➡️ Clicking Next button to scroll carousel.")
                    next_btn.first.click()
                    self.page.wait_for_timeout(500)
                else:
                    print("🚫 Next button not available or disabled.")
                    break

        raise TimeoutError(f"❌ Channel with slug '{channel_slug}' not found in any carousel.")
