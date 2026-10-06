import re
import time

from pages.base_page import BasePage
from locators import GOLF_BAG


class GolfBagPage(BasePage):
    def __init__(self, driver, platform):
        super().__init__(driver, platform, GOLF_BAG)

    def get_connected_club_count(self, timeout=10):
        """
        Reads the "N/14 Clubs Connected" header. Returns N, or None if the
        header's text doesn't match the expected pattern.
        """
        text = self.find("clubs_connected_header", timeout=timeout).text
        match = re.search(r"(\d+)\s*/\s*\d+", text)
        return int(match.group(1)) if match else None

    def pair_club(self, club_name, tag_id, settle_seconds=2):
        """
        UNVERIFIED against real hardware. Real screen shows club-type chips
        (colored circle + loft label like "2W"/"8I" with a red "-" badge
        when a tag is already paired, or a grey circle + "+" badge when
        not) - only an already-fully-paired bag was ever exercised, so the
        tap-a-"+"-chip-then-scan-for-a-tag flow below (club_slot_template
        matching the full club_name, which doesn't match the real
        abbreviated chip labels either) is still a placeholder guess.
        Re-verify against real hardware with an unpaired club before
        trusting this.
        """
        print(f"[GolfBag] Pairing '{club_name}' -> tag {tag_id}")
        self.click_templated("club_slot_template", club_name=club_name)
        self.click("pair_tag_button")
        self.click_templated("tag_row_template", tag_id=tag_id)
        self.click("confirm_pair_button")
        time.sleep(settle_seconds)  # allow BLE write to complete
        print(f"[GolfBag] '{club_name}' paired")

    def pair_all_clubs(self, clubs):
        """
        clubs: list of {"name": "Driver", "tag_id": "0x06A1FED3"}.

        Skips pairing entirely when the bag already reports at least as
        many connected clubs as requested - the only case verified against
        real hardware. Only falls through to the unverified pair_club()
        flow when the bag genuinely needs more clubs paired.
        """
        connected = self.get_connected_club_count()
        if connected is not None and connected >= len(clubs):
            print(f"[GolfBag] {connected} clubs already connected (>= {len(clubs)} requested) - skipping pairing")
            return

        print(f"[GolfBag] Only {connected} clubs connected, need {len(clubs)} - attempting to pair (unverified flow)")
        for club in clubs:
            self.pair_club(club["name"], club["tag_id"])

    def continue_to_round(self):
        print("[GolfBag] Tapping Continue")
        self.click("continue_button")
