from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


DEFAULT_TIMEOUT = 15


class BasePage:
    def __init__(self, driver, platform, locators):
        self.driver = driver
        self.platform = platform
        self.locators = locators[platform]

    def _loc(self, key):
        if key not in self.locators:
            raise KeyError(f"No locator named '{key}' for platform '{self.platform}'")
        return self.locators[key]

    def find(self, key, timeout=DEFAULT_TIMEOUT):
        by, value = self._loc(key)
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def click(self, key, timeout=DEFAULT_TIMEOUT):
        by, value = self._loc(key)
        el = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        el.click()
        return el

    def type_text(self, key, text, timeout=DEFAULT_TIMEOUT):
        el = self.find(key, timeout=timeout)
        el.clear()
        el.send_keys(text)
        return el

    def is_visible(self, key, timeout=5):
        try:
            self.find(key, timeout=timeout)
            return True
        except TimeoutException:
            return False

    def find_templated(self, key, timeout=DEFAULT_TIMEOUT, **format_args):
        """For locators with a {placeholder} in the value, e.g. matching by course name."""
        by, template = self._loc(key)
        value = template.format(**format_args)
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def click_templated(self, key, timeout=DEFAULT_TIMEOUT, **format_args):
        by, template = self._loc(key)
        value = template.format(**format_args)
        el = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        el.click()
        return el

    def wait_until_gone(self, key, timeout=DEFAULT_TIMEOUT):
        by, value = self._loc(key)
        WebDriverWait(self.driver, timeout).until_not(
            EC.presence_of_element_located((by, value))
        )
