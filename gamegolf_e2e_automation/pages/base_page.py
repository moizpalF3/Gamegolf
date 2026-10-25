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

    def scroll_to_top(self, max_scrolls=5):
        """
        Scrolls the current screen's list back to the top. The app keeps a
        screen's scroll position between launches, and Compose lists don't
        render off-screen items, so elements above the fold can't be found.
        """
        size = self.driver.get_window_size()
        area = {
            "left": int(size["width"] * 0.1), "top": int(size["height"] * 0.2),
            "width": int(size["width"] * 0.8), "height": int(size["height"] * 0.6),
        }
        for _ in range(max_scrolls):
            # scrollGesture returns False once there's nothing left to scroll.
            if not self.driver.execute_script(
                "mobile: scrollGesture", {**area, "direction": "up", "percent": 3.0}
            ):
                break

    def tap_relative(self, x_pct, y_pct):
        """
        Taps a point given as a fraction (0.0-1.0) of screen width/height,
        converted to actual pixels via the device's current window size.
        For icon-only Compose controls with no text/resource-id/content-desc
        to locate by (e.g. the round screen's 3-dot menu button) — prefer a
        real locator when one exists, this is a fallback.
        """
        size = self.driver.get_window_size()
        x = int(size["width"] * x_pct)
        y = int(size["height"] * y_pct)
        self.driver.execute_script("mobile: clickGesture", {"x": x, "y": y})
