import re
import time
from playwright.sync_api import Page


class ForYouPage:
    def __init__(self, page: Page):
        self.page = page

    def click_for_you_nav(self):
        print("Clicking Music nav item to reset selection...")
        self.page.click('a[data-qa="content-nav-music"]')
        self.page.wait_for_timeout(500)

        print("Clicking For You nav item...")
        self.page.click('a[data-qa="content-nav-for-you"]')
        self.page.wait_for_timeout(1000)

        # Confirm UUID version of URL is loaded
        updated_href = self.page.locator('a[data-qa="content-nav-for-you"]').get_attribute("href")
        print(f"✅ For You nav href updated: {updated_href}")

    def click_channel_by_href(self, channel_slug: str, max_scrolls: int = 10) -> bool:
        """
        Clicks a channel with a matching slug and UUID-based href from any carousel.
        Example href: /player/channel-linear/siriusxm-hits-1/<uuid>
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
                    try:
                        link = links.nth(i)
                        element_handle = link.element_handle()
                        if not element_handle:
                            continue

                        href = element_handle.get_attribute("href") or ""
                        if not pattern.match(href):
                            continue

                        print(f"🔍 Clicking link: {href}")
                        self.page.evaluate(
                            """el => {
                                el.scrollIntoView({behavior: 'auto', block: 'center'});
                                el.click();
                            }""",
                            element_handle
                        )
                        return True
                    except Exception as err:
                        print(f"⚠️ Skipping link {i} due to error: {err}")
                        continue

                # Optional: try scrolling carousel forward if needed
                next_btn = carousel.locator('button:has(svg path[d*="M8.293"])')
                if next_btn.count() > 0 and next_btn.first.is_enabled():
                    print("➡️ Clicking Next button to scroll carousel.")
                    next_btn.first.click()
                    self.page.wait_for_timeout(500)
                else:
                    print("🚫 Next button not available or disabled.")
                    break

        print(f"❌ Channel with slug '{channel_slug}' not found in any carousel.")
        return False

    def click_first_player_link(self, max_scrolls: int = 10) -> bool:
        """
        Fallback: clicks the first visible link in any carousel that contains /player/ in href.
        """
        pattern = re.compile(r"/player/.+/.+")
        carousels = self.page.locator('[data-qa^="content-carousel"]')
        carousel_count = carousels.count()
        print(f"🔍 Fallback: searching carousels for any /player/ link.")

        for c in range(carousel_count):
            print(f"\n➡️ Checking carousel {c + 1} of {carousel_count}")
            carousel = carousels.nth(c)

            for attempt in range(max_scrolls):
                links = carousel.locator('a[href*="/player/"]')
                total_links = links.count()
                print(f"🔗 Found {total_links} links on scroll attempt {attempt + 1}")

                for i in range(total_links):
                    try:
                        link = links.nth(i)
                        element_handle = link.element_handle()
                        if not element_handle:
                            continue

                        href = element_handle.get_attribute("href") or ""
                        if not pattern.match(href):
                            continue

                        print(f"🔍 Clicking fallback link: {href}")
                        self.page.evaluate(
                            """el => {
                                el.scrollIntoView({behavior: 'auto', block: 'center'});
                                el.click();
                            }""",
                            element_handle
                        )
                        return True
                    except Exception as err:
                        print(f"⚠️ Skipping link {i} due to error: {err}")
                        continue

                # Attempt to scroll carousel forward
                next_btn = carousel.locator('button:has(svg path[d*="M8.293"])')
                if next_btn.count() > 0 and next_btn.first.is_enabled():
                    print("➡️ Clicking Next button to scroll carousel.")
                    next_btn.first.click()
                    self.page.wait_for_timeout(500)
                else:
                    print("🚫 Next button not available or disabled.")
                    break

        print("❌ No fallback clickable link found.")
        return False
    
    def channel_exists(self, channel_slug: str) -> bool:
        locator = self.page.locator(f'a[href*="/player/channel-linear/{channel_slug}/"]')
        return locator.count() > 0

    def get_channel_href(self, channel_slug: str) -> str:
        locator = self.page.locator(f'a[href*="/player/channel-linear/{channel_slug}/"]').first
        return locator.get_attribute("href")
    
    def force_dismiss_playback_stalled_modal(self) -> bool:
        try:
            modal = self.page.locator('[data-qa="content-overlay-modal"]')
            modal.wait_for(state="visible", timeout=3000)
            print("🧪 Modal is visible. Looking for 'Try again' button...")

            try_again_button = modal.locator("button", has_text="Try again")
            try_again_button.scroll_into_view_if_needed(timeout=2000)
            try_again_button.wait_for(state="visible", timeout=2000)
            try_again_button.click()
            print("✅ Clicked 'Try again' to dismiss modal.")
            return True
        except Exception as e:
            print(f"⚠️ Could not dismiss modal: {e}")
            return False






