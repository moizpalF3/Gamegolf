import time
from pathlib import Path

from selenium.common.exceptions import TimeoutException

from pages.base_page import BasePage
from locators import ROUND_ACTIVE


class RoundPage(BasePage):
    def __init__(self, driver, platform):
        super().__init__(driver, platform, ROUND_ACTIVE)

    def wait_for_round_started(self, timeout=20):
        print("[Round] Waiting for round screen to load...")
        self.find("round_screen_root", timeout=timeout)
        print("[Round] Round screen loaded")

    def wait_for_smart_caddie(self, timeout=10):
        """
        PRD requirement: Smart Caddie recommendations must load within
        3 seconds of hole transition. Default timeout here is generous
        to avoid flaking; tighten it if you're asserting the perf budget.
        """
        print("[Round] Waiting for Smart Caddie recommendation...")
        self.find("smart_caddie_recommendation", timeout=timeout)
        print("[Round] Smart Caddie recommendation loaded")

    def get_current_hole(self, timeout=10):
        return int(self.find("hole_number_value", timeout=timeout).text)

    def get_score(self, timeout=10):
        return int(self.find("score_value", timeout=timeout).text)

    def wait_for_score(self, expected_hole, expected_score, timeout=20, poll=1):
        """
        Polls the bottom bar until it shows expected_hole/expected_score or
        the timeout passes (shots take a moment to register in the app).
        Returns the last (hole, score) actually read, whether or not it
        matched, so the caller can assert and report the real values.
        """
        deadline = time.time() + timeout
        hole = score = None
        while True:
            try:
                hole, score = self.get_current_hole(timeout=3), self.get_score(timeout=3)
            except (TimeoutException, ValueError):
                pass
            if (hole, score) == (expected_hole, expected_score) or time.time() >= deadline:
                return hole, score
            time.sleep(poll)

    def save_screenshot(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.driver.save_screenshot(str(path))
        return path

    def end_round(self, timeout=15):
        """
        Opens the round's 3-dot menu (icon-only, addressed by relative
        screen position - see menu_button_relative in locators.py), taps
        "End Round" in the resulting "More Options" sheet, then confirms
        the "Do you want to end your game?" dialog.
        """
        print("[Round] Ending round...")
        x_pct, y_pct = self.locators["menu_button_relative"]
        self.tap_relative(x_pct, y_pct)
        self.click("end_round_option", timeout=timeout)
        self.click("end_round_confirm_button", timeout=timeout)
        print("[Round] Round ended")
