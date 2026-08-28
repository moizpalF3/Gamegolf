from pages.base_page import BasePage
from locators import LOGIN


class LoginPage(BasePage):
    def __init__(self, driver, platform):
        super().__init__(driver, platform, LOGIN)

    def login(self, email, password):
        print(f"[Login] Logging in as {email}")
        self.type_text("email_field", email)
        self.type_text("password_field", password)
        self.click("login_button")
        self.find("logged_in_indicator", timeout=20)
        print("[Login] Logged in successfully")

    def go_to_signup(self):
        self.click("signup_link")
