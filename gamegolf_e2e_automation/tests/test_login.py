import pytest

from pages.login_page import LoginPage


pytestmark = [pytest.mark.smoke, pytest.mark.regression, pytest.mark.login]


class TestLogin:
    def test_login_with_valid_credentials(self, driver, platform, config):
        """TC_LOGIN_001 - Valid credentials log the user in and land on the home dashboard."""
        creds = config["login"]["valid_credentials"]
        login_page = LoginPage(driver, platform)

        login_page.login(creds["email"], creds["password"])

        assert login_page.is_visible("logged_in_indicator"), (
            "Expected the home screen to load after a valid login"
        )

    def test_login_with_invalid_credentials_shows_error(self, driver, platform, config):
        """TC_LOGIN_002 - Wrong password shows an error and does not log in."""
        creds = config["login"]["invalid_credentials"]
        login_page = LoginPage(driver, platform)

        login_page.fill_credentials(creds["email"], creds["password"])
        login_page.submit()

        error_text = login_page.get_error_message()
        assert error_text, "Expected an error message for invalid login credentials"
        assert not login_page.is_visible("logged_in_indicator", timeout=3), (
            "Should not reach the home screen with invalid credentials"
        )

    def test_login_with_empty_credentials_shows_error(self, driver, platform, config):
        """TC_LOGIN_003 - Submitting empty email/password shows an error."""
        login_page = LoginPage(driver, platform)

        login_page.fill_credentials("", "")
        login_page.submit()

        error_text = login_page.get_error_message()
        assert error_text, "Expected an error message when submitting empty credentials"
