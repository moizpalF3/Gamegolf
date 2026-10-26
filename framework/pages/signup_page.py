import time

from framework.pages.base_page import BasePage
from framework.locators import SIGNUP


class SignUpPage(BasePage):
    def __init__(self, driver, platform):
        super().__init__(driver, platform, SIGNUP)

    def fill_form(self, first_name, last_name, email, password, accept_terms=True):
        self.find("form_title")
        self.type_text("first_name_field", first_name)
        self.type_text("last_name_field", last_name)
        self.type_text("email_field", email)
        self.type_text("password_field", password)
        self.hide_keyboard()  # the keyboard covers the terms checkbox and Continue
        if accept_terms:
            self.click("terms_checkbox")

    def is_continue_enabled(self):
        return self.find("signup_button").get_attribute("enabled") == "true"

    def submit(self):
        self.click("signup_button")

    def is_on_form(self, timeout=3):
        return self.is_visible("form_title", timeout=timeout)

    def swipe_to_continue(self):
        """Swipes up on the "Set up your device / Swipe to Continue" screen shown after sign-up."""
        self.find("onboarding_screen", timeout=30)
        print("[SignUp] Onboarding: swiping up to continue")
        size = self.driver.get_window_size()
        self.driver.execute_script("mobile: swipeGesture", {
            "left": int(size["width"] * 0.2), "top": int(size["height"] * 0.3),
            "width": int(size["width"] * 0.6), "height": int(size["height"] * 0.5),
            "direction": "up", "percent": 0.75,
        })

    def choose_have_device(self):
        print("[SignUp] Onboarding: tapping 'Start Setup' (I have a device)")
        self.click("have_device_button", timeout=20)

    def choose_dont_have_device(self):
        print("[SignUp] Onboarding: tapping 'I don't have a device'")
        self.click("dont_have_device_button", timeout=20)

    def skip_golf_bag(self, timeout=30):
        """Taps SKIP (top right) on the golf bag screen that follows "I have a device"."""
        print("[SignUp] Golf bag: waiting for SKIP")
        self.click("skip_button", timeout=timeout)
        print("[SignUp] Golf bag: tapped SKIP")

    def wait_for_browser(self, app_package, timeout=30):
        """
        Waits for another app (the browser) to come to the front instead of
        app_package. Returns (browser package, texts on its screen), the
        texts including the address bar's URL.
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            package = self.driver.current_package
            if package and package != app_package:
                time.sleep(3)  # let the page and its address bar load
                texts = [el.text for el in self.driver.find_elements(
                    "xpath", "//android.widget.EditText | //android.widget.TextView") if el.text]
                return package, texts
            time.sleep(1)
        return None, []

    def get_error_message(self, timeout=15):
        return self.find("error_message", timeout=timeout).text
