import pytest

from pages.login_page import LoginPage
from pages.signup_page import SignUpPage


pytestmark = [pytest.mark.smoke, pytest.mark.regression, pytest.mark.signup]


class TestSignUp:
    def _sign_up_new_user(self, driver, platform, config, email, screenshot):
        """Signs up a new account and waits for the onboarding screen that follows."""
        signup_data = config["signup"]
        LoginPage(driver, platform).go_to_signup()

        signup_page = SignUpPage(driver, platform)
        signup_page.fill_form(
            first_name=signup_data["first_name"],
            last_name=signup_data["last_name"],
            email=email,
            password=signup_data["password"],
        )
        print(f"[SignUp] Submitting as {email}")
        signup_page.submit()

        assert signup_page.is_visible("onboarding_screen", timeout=30), (
            "Expected the 'Set up your device / Swipe to Continue' screen after signing up"
        )
        screenshot("onboarding")
        signup_page.swipe_to_continue()
        return signup_page

    def test_signup_with_valid_new_user(self, driver, platform, config, unique_email, screenshot):
        """TC_SIGNUP_001 - New user signs up, taps 'I have a device', skips the golf bag and reaches Home."""
        login_page = LoginPage(driver, platform)
        signup_page = self._sign_up_new_user(driver, platform, config, unique_email, screenshot)

        signup_page.choose_have_device()
        assert signup_page.is_visible("skip_button", timeout=30), (
            "Expected the golf bag screen with SKIP after tapping 'I have a device'"
        )
        screenshot("golf_bag_with_skip")
        signup_page.skip_golf_bag()

        assert login_page.is_visible("logged_in_indicator", timeout=60), "Expected Home after tapping SKIP"
        screenshot("home_after_signup")

        # Log the new account out, so the next test starts logged out.
        login_page.sign_out()
        assert not login_page.is_logged_in(timeout=10), "Expected to be logged out"

    def test_signup_without_device_opens_marketplace(self, driver, platform, config, unique_email, screenshot):
        """TC_SIGNUP_004 - New user taps "I don't have a device"; the KZN AI marketplace opens in the browser."""
        app_package = config["appium"]["app_package"]
        login_page = LoginPage(driver, platform)
        signup_page = self._sign_up_new_user(driver, platform, config, unique_email, screenshot)

        signup_page.choose_dont_have_device()
        browser, texts = signup_page.wait_for_browser(app_package)
        screenshot("marketplace")
        print(f"[SignUp] Opened in: {browser}; page texts: {texts[:10]}")

        try:
            assert browser, "The app didn't open a browser after tapping \"I don't have a device\""
            assert any("kzn" in t.lower() for t in texts), (
                f"A browser opened ({browser}) but not on the KZN AI marketplace. Page texts: {texts[:10]}"
            )
        finally:
            # Back to the app, finish onboarding and log the new account out,
            # so the next test starts logged out.
            try:
                driver.activate_app(app_package)
                if signup_page.is_visible("onboarding_screen", timeout=5):
                    signup_page.swipe_to_continue()
                if signup_page.is_visible("have_device_button", timeout=5):
                    signup_page.choose_have_device()
                    signup_page.skip_golf_bag()
                login_page.ensure_logged_out()
            except Exception as e:
                print(f"[Cleanup] Could not log the new account out: {e}")

    def test_signup_with_existing_email_shows_error(self, driver, platform, config, screenshot):
        """TC_SIGNUP_002 - Signing up with an already registered email shows an error."""
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
        screenshot("signup_error")
        print(f"[SignUp] Error shown: {error_text!r}")
        assert signup_page.is_visible("error_title", timeout=2), "Expected the 'Registration Unsuccessful' title"
        assert "already exists" in error_text.lower(), f"Unexpected error message: {error_text!r}"
        LoginPage(driver, platform).dismiss_error()  # same "Try again" button as the Log In error

    def test_signup_continue_disabled_until_terms_accepted(self, driver, platform, config, unique_email,
                                                           screenshot):
        """TC_SIGNUP_003 - Continue stays disabled until all fields are filled and the terms are accepted."""
        signup_data = config["signup"]
        LoginPage(driver, platform).go_to_signup()

        signup_page = SignUpPage(driver, platform)
        assert not signup_page.is_continue_enabled(), "Continue should be disabled on an empty form"

        signup_page.fill_form(
            first_name=signup_data["first_name"],
            last_name=signup_data["last_name"],
            email=unique_email,
            password=signup_data["password"],
            accept_terms=False,
        )
        assert not signup_page.is_continue_enabled(), "Continue should stay disabled until the terms are accepted"

        signup_page.click("terms_checkbox")
        screenshot("terms_accepted")
        assert signup_page.is_continue_enabled(), "Continue should be enabled once the terms are accepted"
