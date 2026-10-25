from pages.base_page import BasePage
from locators import LOGIN


class LoginPage(BasePage):
    def __init__(self, driver, platform):
        super().__init__(driver, platform, LOGIN)

    def fill_credentials(self, email, password):
        self.type_text("email_field", email)
        self.type_text("password_field", password)

    def submit(self):
        self.click("login_button")

    def login(self, email, password):
        print(f"[Login] Logging in as {email}")
        self.fill_credentials(email, password)
        self.submit()
        self.find("logged_in_indicator", timeout=20)
        print("[Login] Logged in successfully")

    def ensure_logged_in(self, email, password):
        """
        Skips the login form when the app is already logged in (on Home or on
        another tab), and leaves the app on the Home dashboard either way.
        """
        if self.is_visible("logged_in_indicator", timeout=8) or self.is_visible("home_tab", timeout=2):
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
        self.click("signup_link")

    def get_error_message(self, timeout=5):
        return self.find("error_message", timeout=timeout).text
