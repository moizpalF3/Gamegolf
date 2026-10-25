import re
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

    def wait_for_smart_caddie(self, timeout=240, appear_timeout=15, poll=1, keep_alive=None,
                              done_from_pct=95):
        """
        Waits for the Smart Caddie widget, then for its bottom-left loader
        ("Loading NN%") to reach 100%. Logs each new percentage. Counts as
        loaded when it reads 100%, or when the loader disappears after
        reaching done_from_pct (it can vanish between two polls at the end).
        Disappearing earlier is a failure: that's what happens when the app
        stops getting GPS fixes. Returns the last percentage read (None if the
        loader never showed, i.e. Smart Caddie was already loaded).

        The loader only advances while GPS fixes keep arriving (roughly 1% a
        second, so about 2 minutes in total); keep_alive is called on every
        poll to send one, e.g. by re-reporting the player's position.
        """
        print("[Round] Waiting for Smart Caddie...")
        self.find("smart_caddie_recommendation", timeout=appear_timeout)

        start = time.time()
        last_pct = None
        while True:
            if keep_alive:
                keep_alive()
            try:
                text = self.find("smart_caddie_progress", timeout=2).text
                match = re.search(r"(\d+)\s*%", text)
                pct = int(match.group(1)) if match else None
            except TimeoutException:
                pct = None

            if pct is not None and pct != last_pct:
                print(f"[Round] Smart Caddie loading {pct}% ({time.time() - start:.0f}s)")
                last_pct = pct
            if pct is not None and pct >= 100:
                break
            if pct is None:
                if last_pct is not None and last_pct >= done_from_pct:
                    break  # loader was nearly done and has now gone, i.e. done
                if last_pct is not None:
                    raise AssertionError(
                        f"Smart Caddie loader disappeared at {last_pct}% without reaching 100% "
                        f"(after {time.time() - start:.0f}s) - is the Medallion sending GPS fixes?"
                    )
                if time.time() - start >= appear_timeout:
                    print("[Round] No Smart Caddie loader showing - already loaded")
                    return None
            if time.time() - start >= timeout:
                raise AssertionError(
                    f"Smart Caddie didn't reach 100% within {timeout}s (stuck at {last_pct}%)"
                )
            time.sleep(poll)

        print(f"[Round] Smart Caddie loaded in {time.time() - start:.0f}s")
        return last_pct

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
        self._wait_for_round_closed()
        print("[Round] Round ended")

    def _wait_for_round_closed(self, timeout=60, retries=3):
        """
        Ending a round saves it to the server (a spinner shows meanwhile), so
        wait for the round screen to actually close. If saving fails the app
        shows an "unexpected error" dialog, whose Confirm retries.
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.is_visible("end_round_error", timeout=1):
                if retries == 0:
                    raise AssertionError("The app kept failing to save the ended round (unexpected error dialog)")
                retries -= 1
                print("[Round] App couldn't save the ended round (unexpected error) - tapping Confirm to retry")
                self.click("end_round_confirm_button")
            elif not self.is_visible("round_screen_root", timeout=1):
                return
            time.sleep(2)
        raise AssertionError(f"The round screen was still open {timeout}s after ending the round")

    def end_round_if_active(self):
        """Ends a round left open by an earlier, interrupted run, so the test starts from Home."""
        if self.is_visible("round_screen_root", timeout=5) or self.is_visible("end_round_error", timeout=1):
            print("[Round] A round is still open from an earlier run - ending it first")
            if self.is_visible("end_round_error", timeout=1):
                self.click("end_round_confirm_button")
                self._wait_for_round_closed()
            else:
                self.end_round()
