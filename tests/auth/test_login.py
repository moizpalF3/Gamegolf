import pytest

from framework.pages.login_page import LoginPage


pytestmark = [pytest.mark.smoke, pytest.mark.regression, pytest.mark.login]


class TestLogin:
    def test_login_with_valid_credentials(self, driver, platform, config, screenshot):
        """TC_LOGIN_001 - Valid credentials log the user in and land on the home dashboard."""
        creds = config["login"]["valid_credentials"]
        login_page = LoginPage(driver, platform)
        login_page.ensure_logged_out()

        login_page.login(creds["email"], creds["password"])

        assert login_page.is_visible("logged_in_indicator"), (
            "Expected the home screen to load after a valid login"
        )

    def test_login_with_invalid_credentials_shows_error(self, driver, platform, config, screenshot):
        """TC_LOGIN_002 - Wrong credentials show 'Login Unsuccessful' and do not log in."""
        creds = config["login"]["invalid_credentials"]
        login_page = LoginPage(driver, platform)

        login_page.open_login_form()
        login_page.fill_credentials(creds["email"], creds["password"])
        login_page.submit()

        error_text = login_page.get_error_message()
        screenshot("login_error")
        assert "credentials" in error_text.lower(), f"Unexpected error message: {error_text!r}"
        assert login_page.is_visible("error_title", timeout=2), "Expected the 'Login Unsuccessful' title"

        login_page.dismiss_error()
        assert not login_page.is_logged_in(timeout=3), (
            "Should not reach the home screen with invalid credentials"
        )

    def test_login_button_disabled_until_credentials_entered(self, driver, platform, config, screenshot):
        """TC_LOGIN_003 - The Log In button stays disabled until both email and password are entered."""
        creds = config["login"]["valid_credentials"]
        login_page = LoginPage(driver, platform)

        login_page.open_login_form()
        login_page.fill_credentials("", "")
        assert not login_page.is_login_button_enabled(), "Log In should be disabled with both fields empty"

        login_page.type_text("email_field", creds["email"])
        login_page.hide_keyboard()
        assert not login_page.is_login_button_enabled(), "Log In should stay disabled without a password"

        login_page.type_text("password_field", "x")
        login_page.hide_keyboard()
        screenshot("login_button_enabled")
        assert login_page.is_login_button_enabled(), "Log In should be enabled once both fields have text"
        login_page.type_text("password_field", "")  # don't leave a partial password behind
