from pages.base_page import BasePage
from locators import SIGNUP


class SignUpPage(BasePage):
    def __init__(self, driver, platform):
        super().__init__(driver, platform, SIGNUP)

    def fill_form(self, first_name, last_name, email, password, confirm_password=None):
        self.type_text("first_name_field", first_name)
        self.type_text("last_name_field", last_name)
        self.type_text("email_field", email)
        self.type_text("password_field", password)
        self.type_text(
            "confirm_password_field",
            confirm_password if confirm_password is not None else password,
        )

    def submit(self):
        self.click("signup_button")

    def sign_up(self, first_name, last_name, email, password, confirm_password=None):
        print(f"[SignUp] Signing up as {email}")
        self.fill_form(first_name, last_name, email, password, confirm_password)
        self.submit()
        self.find("signup_success_indicator", timeout=20)
        print("[SignUp] Signed up successfully")

    def go_to_login(self):
        self.click("login_link")

    def get_error_message(self, timeout=5):
        return self.find("error_message", timeout=timeout).text
