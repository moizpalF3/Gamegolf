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
