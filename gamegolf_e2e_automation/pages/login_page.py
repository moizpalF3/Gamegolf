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

    def go_to_signup(self):
        self.click("signup_link")

    def get_error_message(self, timeout=5):
        return self.find("error_message", timeout=timeout).text
