import time

from pages.base_page import BasePage
from locators import LOGIN

# Screens the app can open on, checked in this order (the sign-up form comes
# before the Log In form because both have an "Email Address" field).
SCREENS = [
    ("home", "logged_in_indicator"),
    ("home", "home_tab"),
    ("signup_form", "signup_form_title"),
    ("login_form", "email_field"),
    ("entry", "sign_in_entry_button"),
]


class LoginPage(BasePage):
    def __init__(self, driver, platform):
        super().__init__(driver, platform, LOGIN)

    def current_screen(self, timeout=20):
        """
        Waits until one of the known screens shows and returns its name:
        "home" (logged in, any tab), "signup_form", "login_form" or "entry".
        The app can still be loading when a test starts, so a single quick
        check isn't enough to tell whether it's logged in.
        """
        from pages.round_page import RoundPage

        deadline = time.time() + timeout
        while True:
            # A round left open by an earlier run blocks Home with an
            # "Unfinished Round" dialog (or reopens the round screen); end it.
            round_page = RoundPage(self.driver, self.platform)
            if (self.driver.find_elements(*round_page._loc("unfinished_round_dialog"))
                    or self.driver.find_elements(*round_page._loc("round_screen_root"))):
                round_page.end_round_if_active()
            for name, key in SCREENS:
                if self.driver.find_elements(*self._loc(key)):
                    return name
            if time.time() >= deadline:
                raise AssertionError(f"App isn't on any known screen after {timeout}s")
            time.sleep(1)

    def is_logged_in(self, timeout=8):
        return self.current_screen(timeout=timeout) == "home"

    def sign_out(self):
        """My Profile tab -> Sign Out -> Confirm; the app then shows the Log In form."""
        print("[Login] Signing out")
        self.click("profile_tab")
        self.click("sign_out_button")
        self.click("sign_out_confirm_button")
        self._wait_until_logged_out()

    def _wait_until_logged_out(self, timeout=20):
        deadline = time.time() + timeout
        while self.current_screen(timeout=timeout) == "home":
            if time.time() >= deadline:
                raise AssertionError("Still logged in after signing out")
            time.sleep(1)

    def ensure_logged_out(self):
        """Signs out if logged in; returns the logged-out screen the app ends on."""
        screen = self.current_screen()
        if screen == "home":
            self.sign_out()
            screen = self.current_screen()
        return screen

    def open_login_form(self):
        """Gets to the Log In form from wherever the app is, signing out first if needed."""
        screen = self.ensure_logged_out()
        if screen == "signup_form":
            self.click("back_button")
            screen = self.current_screen()
        if screen == "entry":
            self.click("sign_in_entry_button")
        self.find("email_field")

    def fill_credentials(self, email, password):
        self.type_text("email_field", email)
        self.type_text("password_field", password)
        self.hide_keyboard()  # the keyboard covers the Log In button

    def is_login_button_enabled(self):
        return self.find("login_button").get_attribute("enabled") == "true"

    def submit(self):
        self.click("login_button")

    def login(self, email, password):
        print(f"[Login] Logging in as {email}")
        self.open_login_form()
        self.fill_credentials(email, password)
        self.submit()
        self.find("logged_in_indicator", timeout=30)
        print("[Login] Logged in successfully")

    def ensure_logged_in(self, email, password):
        """
        Skips the login form when the app is already logged in (on Home or on
        another tab), and leaves the app on the Home dashboard either way.
        """
        if self.is_logged_in(timeout=20):
            print("[Login] Already logged in - skipping login form")
        else:
            self.login(email, password)
        self.go_home()

    def go_home(self):
        """
        Switches to the Home dashboard via the bottom tab unless it's already
        showing, then scrolls it to the top (where the GPS Tracker widget is).
        """
        if not self.is_visible("logged_in_indicator", timeout=2):
            print("[Login] Switching to the Home tab")
            self.click("home_tab")
            self.find("logged_in_indicator")
        self.scroll_to_top()

    def go_to_signup(self):
        """Gets to the sign-up form from wherever the app is, signing out first if needed."""
        screen = self.ensure_logged_out()
        if screen == "signup_form":
            return
        if screen == "login_form":
            self.click("back_button")
        self.click("signup_entry_button")

    def get_error_message(self, timeout=15):
        return self.find("error_message", timeout=timeout).text

    def dismiss_error(self):
        self.click("error_dismiss_button")
