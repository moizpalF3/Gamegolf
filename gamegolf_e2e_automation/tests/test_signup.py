from pages.login_page import LoginPage
from pages.signup_page import SignUpPage


class TestSignUp:
    def test_signup_with_valid_new_user(self, driver, platform, config, unique_email):
        signup_data = config["signup"]

        LoginPage(driver, platform).go_to_signup()

        signup_page = SignUpPage(driver, platform)
        signup_page.sign_up(
            first_name=signup_data["first_name"],
            last_name=signup_data["last_name"],
            email=unique_email,
            password=signup_data["password"],
        )

        assert signup_page.is_visible("signup_success_indicator"), (
            "Expected the home screen to load after a successful sign up"
        )

    def test_signup_with_existing_email_shows_error(self, driver, platform, config):
        signup_data = config["signup"]

        LoginPage(driver, platform).go_to_signup()

        signup_page = SignUpPage(driver, platform)
        signup_page.fill_form(
            first_name=signup_data["first_name"],
            last_name=signup_data["last_name"],
            email=signup_data["existing_email"],
            password=signup_data["password"],
        )
        signup_page.submit()

        error_text = signup_page.get_error_message()
        assert error_text, "Expected an error message when signing up with an email already in use"

    def test_signup_with_mismatched_passwords_shows_error(self, driver, platform, config, unique_email):
        signup_data = config["signup"]

        LoginPage(driver, platform).go_to_signup()

        signup_page = SignUpPage(driver, platform)
        signup_page.fill_form(
            first_name=signup_data["first_name"],
            last_name=signup_data["last_name"],
            email=unique_email,
            password=signup_data["password"],
            confirm_password=signup_data["password"] + "x",
        )
        signup_page.submit()

        error_text = signup_page.get_error_message()
        assert error_text, "Expected an error message when password and confirm-password don't match"
