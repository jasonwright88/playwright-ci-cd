from playwright.sync_api import Page

# This class models the SiriusXM homepage using Page Object Model (POM)
class HomePage:
    def __init__(self, page):
        self.page = page
        self.global_nav = "nav[data-componenttype='Global Nav']"
        self.start_listening_button = "a:has(div.rl2_button-module_content_4PKD6:has-text('Start Listening'))"

    def goto(self):
        self.page.goto("https://www.siriusxm.com/")

    def is_nav_visible(self):
        self.page.wait_for_selector(self.global_nav, timeout=10000)
        return self.page.is_visible(self.global_nav)

    def click_start_listening(self):
        self.page.wait_for_selector(self.start_listening_button, timeout=10000)
        self.page.click(self.start_listening_button)

