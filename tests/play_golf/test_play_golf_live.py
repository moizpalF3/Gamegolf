import re
import time
from pathlib import Path

import pytest

from framework.hardware import medallion
from framework.core.data_loader import apply_club_tags
from framework.pages.login_page import LoginPage
from framework.pages.connect_device_page import ConnectDevicePage
from framework.pages.course_search_page import CourseSearchPage
from framework.pages.golf_bag_page import GolfBagPage
from framework.pages.round_page import RoundPage


pytestmark = [pytest.mark.smoke, pytest.mark.regression, pytest.mark.play_golf]

PROJECT_DIR = Path(__file__).resolve().parents[2]


def _play_in_background(driver, app_package, cli, holes_config, holes_dict, hole_order, round_page,
                        screenshot, check, score_mismatches):
    """
    App-in-background scenario: send the app to the background (Home, not
    closed), play every hole's commands, bring the app back and tap Continue
    Round, then check:
      - the last step's expect_hole / expect_score once the shots have
        synced (e.g. on hole 5's tee, score 0), allowing time for the sync;
      - every earlier hole's score, by stepping back through the holes with
        the bottom bar's arrow (a screenshot of each shows its shots).
    """
    delay = holes_config.get("command_delay_seconds") or 3
    driver.press_keycode(3)  # Home: the app keeps running in the background
    time.sleep(3)
    assert driver.current_package != app_package, "The app didn't go to the background"
    print(f"[Background] App in background (front: {driver.current_package}); playing all shots")

    for hole_num in hole_order:
        label = medallion.hole_label_for(holes_config, hole_num)
        medallion.play_hole_commands(cli, holes_dict[hole_num], delay, label)

    driver.activate_app(app_package)
    print("[Background] App back in the foreground")
    # Coming back, the app asks to continue the open round: tap Continue Round.
    if round_page.is_visible("continue_round_button", timeout=20):
        screenshot("continue_round_prompt")
        round_page.click("continue_round_button")
        print("[Background] Tapped Continue Round")
    else:
        print("[Background] No Continue Round prompt - the app reopened the round screen directly")
    print("[Background] Waiting for the shots to sync")
    round_page.wait_for_round_started()
    screenshot("back_in_foreground")

    last_hole = hole_order[-1]
    last = holes_dict[last_hole][-1]
    expected_end = last.get("expect") or (
        last_hole, sum(1 for wp in holes_dict[last_hole] if "tag_id" in wp))
    check(f"after_sync_hole_{expected_end[0]}", *expected_end, last, wait=120)

    # Review the earlier holes without sending positions (that could switch
    # holes automatically): step back with the arrow and read each score.
    for hole_num in reversed(hole_order[:-1]):
        for _ in range(18):
            if round_page.get_current_hole() <= hole_num:
                break
            round_page.change_hole("previous")
        expected = sum(1 for wp in holes_dict[hole_num] if "tag_id" in wp)
        actual = round_page.wait_for_score(hole_num, expected, timeout=10)
        shot = screenshot(f"review_hole_{hole_num}")
        print(f"[Assert] review hole {hole_num}: expected score {expected}, "
              f"app shows hole {actual[0]} / score {actual[1]} ({shot})")
        if actual != (hole_num, expected):
            score_mismatches.append(f"review hole {hole_num}: expected score {expected}, app showed "
                                    f"hole {actual[0]} / score {actual[1]} (screenshot: {shot})")


def _safe_name(text):
    return re.sub(r"[^A-Za-z0-9]+", "_", text or "step").strip("_").lower()


def _connect_with_retry(cli, attempts=5, wait_seconds=3):
    """Opens the Medallion's serial port, retrying while another program briefly holds it."""
    for attempt in range(1, attempts + 1):
        try:
            cli.connect()
            return
        except Exception as e:
            if attempt == attempts:
                raise RuntimeError(
                    f"Couldn't open the Medallion's port {cli.port} after {attempts} tries: {e}. "
                    f"Close any serial monitor (PuTTY, Arduino IDE, another test run) using it."
                ) from e
            print(f"[Medallion] {cli.port} busy ({e}); retrying in {wait_seconds}s")
            time.sleep(wait_seconds)


@pytest.mark.live_hardware
class TestPlayGolfLiveScenario:
    """
    Full play-golf-live flow: log in, connect the Medallion, search + start a
    round at a course, pair clubs to tags, then play holes with real GPS/shot
    injection over the Medallion's serial CLI, and end the round.

    Needs a physically powered Medallion (and paired tags) in range, and
    `play_golf.medallion_port` / `play_golf.holes_config_file` set in the
    test config. Use --dry-run-medallion style config (`"dry_run": true`) to
    exercise the flow without a real serial connection.
    """

    def test_play_full_round(self, driver, platform, config, screenshot, scenario):
        """TC_PG_001 - Play a scenario's holes live; each hole's score must equal the shots played."""
        # `scenario` is one row of the Scenarios sheet (see conftest), or None
        # to play play_golf.holes_config_file from test_config.json.
        creds = config["login"]["valid_credentials"]
        golf = config["play_golf"]
        course_name = scenario["course"] if scenario else golf["course_name"]

        # Build the Medallion plan first, so a bad club name fails before a
        # round is started on the phone.
        if scenario:
            holes_config = scenario["holes_config"]
        else:
            holes_file = Path(golf["holes_config_file"])
            if not holes_file.is_absolute():
                holes_file = PROJECT_DIR / holes_file
            holes_config = medallion.load_config(holes_file)
        if golf.get("medallion_port"):
            holes_config["port"] = golf["medallion_port"]

        apply_club_tags(holes_config["waypoints"], golf["clubs"])

        holes_dict = medallion.group_waypoints_into_holes(holes_config)
        # A scenario plays its holes in the order they appear in the Shots sheet.
        hole_order = medallion.resolve_hole_order(
            holes_dict, list(holes_dict) if scenario else golf.get("holes")
        )

        steps = holes_config.get("steps_between_points", medallion.DEFAULT_STEPS_BETWEEN_POINTS)
        seconds_between_steps = holes_config.get(
            "seconds_between_points", medallion.DEFAULT_SECONDS_BETWEEN_STEPS
        )
        shot_settle = holes_config.get("shot_settle_seconds", medallion.DEFAULT_SHOT_SETTLE_SECONDS)

        cli = medallion.GameGolfCLI(port=holes_config["port"], dry_run=config.get("dry_run", False))
        _connect_with_retry(cli)

        # Stand the player on the first shot's spot (normally the first tee),
        # or the scenario's start_hole tee, before the round starts: Smart
        # Caddie only loads for the player's current position, and the
        # Medallion otherwise still reports wherever the previous run finished.
        start = holes_config.get("start") or holes_dict[hole_order[0]][0]
        stand_at_start = lambda: medallion.move_to(cli, start["lat"], start["lon"])
        stand_at_start()

        round_page = RoundPage(driver, platform)
        round_page.end_round_if_active()
        round_started = False
        score_mismatches = []
        try:
            LoginPage(driver, platform).ensure_logged_in(creds["email"], creds["password"])
            ConnectDevicePage(driver, platform).connect()

            search_page = CourseSearchPage(driver, platform)
            search_page.search_and_select_course(course_name)
            search_page.start_round()
            round_started = True

            golf_bag_page = GolfBagPage(driver, platform)
            golf_bag_page.pair_all_clubs(golf["clubs"])
            golf_bag_page.continue_to_round()
            round_page.wait_for_round_started()

            # Don't play any shots until Smart Caddie's loader reaches 100%.
            # It only progresses while GPS fixes keep arriving, so keep
            # reporting the start position while waiting.
            round_page.wait_for_smart_caddie(keep_alive=stand_at_start)
            screenshot("smart_caddie_loaded")

            delay = holes_config.get("command_delay_seconds")
            pause = delay or 3
            hold = holes_config.get("hold_seconds")

            def check(name, exp_hole, exp_score, position, wait):
                """
                Waits up to `wait` seconds for the app to show exp_hole /
                exp_score, re-reporting `position` meanwhile (the app reacts
                to fresh GPS fixes, e.g. an automatic hole switch). With
                hold_seconds, it then stays there that long and checks
                again, so something that must NOT happen (like a hole
                switch) has time to show up. Records any mismatch.
                """
                deadline = time.time() + wait
                while True:
                    actual = round_page.wait_for_score(exp_hole, exp_score, timeout=2)
                    if actual == (exp_hole, exp_score) or time.time() >= deadline:
                        break
                    medallion.move_to(cli, position["lat"], position["lon"])
                    time.sleep(pause)
                if hold and actual == (exp_hole, exp_score):
                    print(f"[Assert] {name}: holding at '{position.get('label')}' for {hold}s")
                    held_until = time.time() + hold
                    while time.time() < held_until:
                        medallion.move_to(cli, position["lat"], position["lon"])
                        time.sleep(pause)
                    actual = round_page.wait_for_score(exp_hole, exp_score, timeout=3)

                shot = screenshot(name)
                print(f"[Assert] {name}: expected hole {exp_hole} / score {exp_score}, "
                      f"app shows hole {actual[0]} / score {actual[1]} ({shot})")
                if actual != (exp_hole, exp_score):
                    score_mismatches.append(
                        f"{name}: expected hole {exp_hole} / score {exp_score}, app showed "
                        f"hole {actual[0]} / score {actual[1]} (screenshot: {shot})"
                    )

            def check_text(name, needle, position, wait):
                """
                Waits up to `wait` seconds for text containing `needle` (any
                case) to show on screen, e.g. a pop-up, re-reporting
                `position` meanwhile. Records a mismatch if it never shows,
                then dismisses the pop-up so the test can carry on.
                """
                deadline = time.time() + wait
                while True:
                    texts = re.findall(r'text="([^"]+)"', driver.page_source)
                    found = [t for t in texts if needle.lower() in t.lower()]
                    if found or time.time() >= deadline:
                        break
                    medallion.move_to(cli, position["lat"], position["lon"])
                    time.sleep(pause)
                shot = screenshot(name)
                print(f"[Assert] {name}: expected text containing '{needle}'; "
                      f"{'found ' + repr(found) if found else 'not found'}; screen shows: {sorted(set(texts))}")
                if not found:
                    score_mismatches.append(
                        f"{name}: no text containing '{needle}' showed within {wait}s (screenshot: {shot})"
                    )
                    return
                round_page.dismiss_popup()

            if holes_config.get("background"):
                _play_in_background(driver, config["appium"]["app_package"], cli, holes_config, holes_dict,
                                    hole_order, round_page, screenshot, check, score_mismatches)
                hole_order = []  # all played and checked above

            for hole_num in hole_order:
                waypoints = holes_dict[hole_num]
                label = medallion.hole_label_for(holes_config, hole_num)
                if delay:
                    # Command-script scenario: send the commands as written,
                    # checking the app after any step that states what it
                    # should show (expect_hole / expect_score in Shots).
                    for wp in waypoints:
                        if wp.get("action") in ("previous_hole", "next_hole"):
                            # Move there, tap the hole arrow in the app, then play the shot.
                            print(f"\n--- {label} - {wp.get('label')} ---")
                            medallion.move_to(cli, wp["lat"], wp["lon"])
                            time.sleep(delay)
                            round_page.change_hole(wp["action"].split("_")[0])
                            screenshot(f"hole_{hole_num}_{wp['action']}")
                            time.sleep(delay)
                            if "tag_id" in wp:
                                medallion.play_shot(cli, wp["tag_id"], delay)
                        elif wp.get("action"):
                            raise ValueError(f"Unknown action '{wp['action']}' (use previous_hole / next_hole)")
                        else:
                            medallion.play_hole_commands(cli, [wp], delay, f"{label} - {wp.get('label')}")
                        step = f"hole_{hole_num}_{_safe_name(wp.get('label'))}"
                        if "expect_text" in wp:
                            check_text(step + "_popup", wp["expect_text"], wp, wait=60)
                        if "expect" in wp:
                            check(step, *wp["expect"], wp, wait=60)
                else:
                    medallion.play_hole(cli, waypoints, steps, seconds_between_steps, shot_settle, label)

                # Unless the hole's last step already stated what the app
                # should show, every waypoint with a tag_id is one shot, so
                # that's what the app's score for this hole should read.
                if "expect" not in waypoints[-1] and "expect_text" not in waypoints[-1]:
                    expected_shots = sum(1 for wp in waypoints if "tag_id" in wp)
                    check(f"hole_{hole_num}_score", hole_num, expected_shots, waypoints[-1], wait=20)
        except Exception:
            # Don't leave a live round open on the account when play breaks
            # off part way (e.g. Smart Caddie never finishes loading).
            if round_started:
                try:
                    screenshot("at_failure")  # the end-of-test screenshot comes after the round is ended
                except Exception:
                    pass
                try:
                    round_page.end_round()
                except Exception as e:
                    print(f"[Cleanup] Could not end the round: {e}")
            raise
        finally:
            cli.disconnect()

        # Only fail after every hole was played and screenshotted, and the
        # round was ended, so one bad hole doesn't hide the others or leave
        # a live round open on the account.
        round_page.end_round()

        assert not round_page.is_visible("round_screen_root", timeout=5), (
            "Expected the round screen to close after ending the round"
        )
        assert not score_mismatches, "Score didn't match shots played:\n  " + "\n  ".join(score_mismatches)
