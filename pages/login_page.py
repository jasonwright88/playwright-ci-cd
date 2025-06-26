import os
from playwright.sync_api import Page

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        # Locators for login flow elements
        self.username_input = "input[data-qa='email-field']"
        self.username_continue_button = "button[data-qa='submit-auth-email']"
        self.password_input = "input[data-qa='password-field']"
        self.final_continue_button = "button[data-qa='sign-in']"
        self.auth_method_container = "div[data-qa='content-overlay-modal']"
        self.password_auth_option = 'div[data-qa="password-auth-option"]'
        self.auth_continue_button = "button[data-qa='submit-auth-option']"
        self.error_message = "text=We can't find a match"
        self.cookie_accept_button = "button#onetrust-accept-btn-handler"

    def goto(self):
        """Navigate to the SiriusXM login page."""
        self.page.goto("https://www.siriusxm.com/player/login")

    def submit_username(self, username: str):
        """Enter the username and handle cookie modal and error or auth method modal."""
        try:
            self.page.wait_for_selector(self.username_input, timeout=10000)
            self.page.fill(self.username_input, username)
            print(f"Filled username: {username}")

            self.page.locator(self.username_continue_button).click()
            print("Clicked continue after entering username...")

            self.page.wait_for_timeout(2000)  # Allow time for modals or cookies

            # Handle cookie banner if present
            if self.page.locator(self.cookie_accept_button).is_visible():
                print("Cookie banner detected. Accepting cookies...")
                self.page.click(self.cookie_accept_button)
                self.page.wait_for_timeout(1000)

                # Retry clicking the continue button to trigger the modal
                print("Re-clicking username continue to reopen modal...")
                self.page.locator(self.username_continue_button).click()
                self.page.wait_for_timeout(1000)

            # Confirm auth modal or error message appears
            if self.page.locator(self.auth_method_container).is_visible():
                print("Auth method modal is visible.")
            elif self.page.locator(self.error_message).is_visible():
                print("Invalid username error is shown.")
            else:
                raise Exception("Neither modal nor error message appeared after submitting username.")

        except Exception as e:
            # Capture screenshot if submission fails
            print("Failed to submit username. Saving screenshot for debugging.")
            screenshot_path = os.path.join(os.getcwd(), "debug_screenshots", "username_input_failure.png")
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            self.page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
            raise e

    def is_invalid_username(self) -> bool:
        """Check if the invalid username message is visible."""
        try:
            return self.page.locator(self.error_message).is_visible()
        except:
            return False

    def choose_password_method(self):
        """Select the 'Sign in with password' option and proceed to the password modal."""
        try:
            print("Waiting for auth method modal...")
            self.page.locator(self.auth_method_container).wait_for(state="visible", timeout=15000)

            print("Selecting password authentication option via data-qa selector...")
            password_option = self.page.locator(self.password_auth_option)
            password_option.wait_for(state="visible", timeout=5000)
            password_option.scroll_into_view_if_needed()
            password_option.click(force=True, timeout=5000)

            print("Clicking Continue to confirm auth method...")
            continue_button = self.page.locator(self.auth_continue_button)
            continue_button.wait_for(state="visible", timeout=5000)
            continue_button.click(force=True, timeout=5000)

            print("Waiting for password entry modal...")
            self.page.wait_for_selector("form[data-qa='password-auth-form']", timeout=10000)

        except Exception as e:
            print("Failed during auth method selection flow.")
            try:
                screenshot_path = os.path.join(os.getcwd(), "debug_screenshots", "auth_modal_continue_failure.png")
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                self.page.screenshot(path=screenshot_path, full_page=True)
                print(f"Screenshot saved to: {screenshot_path}")
            except:
                print("Could not save screenshot.")
            raise e

    def enter_password_and_submit(self, password: str):
        """Enter the password and click the final Continue button."""
        try:
            self.page.wait_for_selector(self.password_input, timeout=7000)
            self.page.fill(self.password_input, password)
            self.page.click(self.final_continue_button)
        except Exception as e:
            print("Password entry or submission failed. Saving screenshot.")
            screenshot_path = os.path.join(os.getcwd(), "debug_screenshots", "password_failure.png")
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            self.page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
            raise e
