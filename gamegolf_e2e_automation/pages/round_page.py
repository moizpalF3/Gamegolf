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
        print("[Round] Ending round...")
        self.click("menu_button")
        self.click("end_round_option")
        self.click("end_round_confirm_button")
        print("[Round] Round ended")
