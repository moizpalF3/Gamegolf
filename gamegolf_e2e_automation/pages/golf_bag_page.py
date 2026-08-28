import time

from pages.base_page import BasePage
from locators import GOLF_BAG


class GolfBagPage(BasePage):
    def __init__(self, driver, platform):
        super().__init__(driver, platform, GOLF_BAG)

    def pair_club(self, club_name, tag_id, settle_seconds=2):
        """
        Taps a club slot, initiates pairing, selects the tag by its hex id,
        and confirms. The actual tag write (equipment ID written to the
        tag's memory over BLE) happens for real on confirm - the tag must
        be powered/awake and in range.
        """
        print(f"[GolfBag] Pairing '{club_name}' -> tag {tag_id}")
        self.click_templated("club_slot_template", club_name=club_name)
        self.click("pair_tag_button")
        self.click_templated("tag_row_template", tag_id=tag_id)
        self.click("confirm_pair_button")
        time.sleep(settle_seconds)  # allow BLE write to complete
        print(f"[GolfBag] '{club_name}' paired")

    def pair_all_clubs(self, clubs):
        """clubs: list of {"name": "Driver", "tag_id": "0x06A1FED3"}"""
        for club in clubs:
            self.pair_club(club["name"], club["tag_id"])

    def continue_to_round(self):
        print("[GolfBag] Tapping Continue")
        self.click("continue_button")
