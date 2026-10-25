import time
from pathlib import Path

import pytest

import gamegolf_hole_simulator as medallion
from data_loader import apply_club_tags
from pages.login_page import LoginPage
from pages.connect_device_page import ConnectDevicePage
from pages.course_search_page import CourseSearchPage
from pages.golf_bag_page import GolfBagPage
from pages.round_page import RoundPage


pytestmark = [pytest.mark.smoke, pytest.mark.regression, pytest.mark.play_golf]


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
            holes_config = medallion.load_config(Path(golf["holes_config_file"]))
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

        # Stand the player on the first shot's spot (normally the first tee)
        # before the round starts: Smart Caddie only loads for the player's
        # current position, and the Medallion otherwise still reports wherever
        # the previous run finished.
        start = holes_dict[hole_order[0]][0]
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

            for hole_num in hole_order:
                waypoints = holes_dict[hole_num]
                label = medallion.hole_label_for(holes_config, hole_num)
                if holes_config.get("command_delay_seconds"):
                    # Command-script scenario: send the commands as written.
                    medallion.play_hole_commands(cli, waypoints, holes_config["command_delay_seconds"], label)
                else:
                    medallion.play_hole(cli, waypoints, steps, seconds_between_steps, shot_settle, label)

                # Every waypoint with a tag_id is one shot, so that's what the
                # app's score for this hole should read.
                expected_shots = sum(1 for wp in waypoints if "tag_id" in wp)
                actual_hole, actual_score = round_page.wait_for_score(hole_num, expected_shots)

                shot = screenshot(f"hole_{hole_num}_score")
                print(f"[Assert] Hole {hole_num}: expected score {expected_shots}, "
                      f"app shows hole {actual_hole} / score {actual_score} ({shot})")

                if (actual_hole, actual_score) != (hole_num, expected_shots):
                    score_mismatches.append(
                        f"hole {hole_num}: expected score {expected_shots}, app showed "
                        f"hole {actual_hole} / score {actual_score} (screenshot: {shot})"
                    )
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
