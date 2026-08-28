#!/usr/bin/env python3
"""
GameGolf Full End-to-End Round Automation
===========================================

Drives the real app UI via Appium (Android + iOS) through the complete flow:

    Sign up / Log in
    -> Connect Medallion
    -> Search for a golf course
    -> Start Round
    -> Golf Bag: pair tags to clubs
    -> Continue
    -> Wait for round to start
    -> Wait for Smart Caddie recommendations
    -> Play shots (Tee, Fairway, Green) per hole, using the Medallion's
       serial CLI to inject GPS movement + shot data (same mechanism as
       gamegolf_hole_simulator.py)
    -> End round

*** IMPORTANT ***
The locators.py file in this project is full of placeholder element IDs.
You MUST replace them with real values from your app before this will work
against a real screen. See locators.py for instructions on finding them.

Requirements:
    pip install -r requirements.txt
    An Appium server running (see appium_driver_factory.py for setup notes)
    The Medallion connected via USB serial for the live-play portion

Usage:
    python3 run_e2e_round.py --config round_config.json
    python3 run_e2e_round.py --config round_config.json --dry-run
    python3 run_e2e_round.py --config round_config.json --skip-ui   # only run the medallion/live-play part
"""

import argparse
import json
import sys
import time
from pathlib import Path

from appium_driver_factory import build_driver
from pages.login_page import LoginPage
from pages.connect_device_page import ConnectDevicePage
from pages.course_search_page import CourseSearchPage
from pages.golf_bag_page import GolfBagPage
from pages.round_page import RoundPage

import gamegolf_hole_simulator as medallion


def load_config(path):
    suffix = path.suffix.lower()
    if suffix == ".json":
        with open(path, "r") as f:
            return json.load(f)
    else:
        raise ValueError("E2E round config must be .json (holes/waypoints can still be .csv/.xlsx, see 'holes_config_file')")


def run_app_flow(driver, platform, config, args):
    """Drives the app UI from login through to round-active, and returns
    once the round has started and Smart Caddie has loaded."""

    creds = config["credentials"]
    login_page = LoginPage(driver, platform)
    login_page.login(creds["email"], creds["password"])

    connect_page = ConnectDevicePage(driver, platform)
    connect_page.connect()

    search_page = CourseSearchPage(driver, platform)
    search_page.search_and_select_course(config["course_name"])
    search_page.start_round()

    golf_bag_page = GolfBagPage(driver, platform)
    golf_bag_page.pair_all_clubs(config["clubs"])
    golf_bag_page.continue_to_round()

    round_page = RoundPage(driver, platform)
    round_page.wait_for_round_started()
    round_page.wait_for_smart_caddie()

    return round_page


def run_live_play(holes_config, requested_holes, dry_run):
    """Runs the Tee/Fairway/Green shot simulation for the requested holes,
    using the same serial CLI mechanism as gamegolf_hole_simulator.py."""

    medallion.validate_config(holes_config, argparse.Namespace(port=holes_config.get("port"), holes=requested_holes))

    port = holes_config["port"]
    baudrate = holes_config.get("baudrate", medallion.DEFAULT_BAUDRATE)
    steps = holes_config.get("steps_between_points", medallion.DEFAULT_STEPS_BETWEEN_POINTS)
    seconds_between_steps = holes_config.get("seconds_between_points", medallion.DEFAULT_SECONDS_BETWEEN_STEPS)
    shot_settle = holes_config.get("shot_settle_seconds", medallion.DEFAULT_SHOT_SETTLE_SECONDS)

    holes_dict = medallion.group_waypoints_into_holes(holes_config)
    hole_order = medallion.resolve_hole_order(holes_dict, requested_holes)

    print(f"\n[LivePlay] Holes to play, in order: {hole_order}")

    cli = medallion.GameGolfCLI(port=port, baudrate=baudrate, dry_run=dry_run)
    cli.connect()
    try:
        for hole_num in hole_order:
            waypoints = holes_dict[hole_num]
            label = medallion.hole_label_for(holes_config, hole_num)
            medallion.play_hole(cli, waypoints, steps, seconds_between_steps, shot_settle, label)
    finally:
        cli.disconnect()


def run_end_to_end(config, args):
    holes_config_path = Path(config["holes_config_file"])
    holes_config = medallion.load_config(holes_config_path)

    # Serial port for the medallion can be overridden at the top level of the
    # round config, otherwise falls back to whatever's in the holes file.
    if "medallion_port" in config:
        holes_config["port"] = config["medallion_port"]

    round_page = None

    if not args.skip_ui:
        if args.dry_run:
            print("[DRY RUN] Skipping real Appium session (use --skip-ui for a real device test of live-play only)")
        else:
            platform = config["platform"].lower()
            driver = build_driver(platform, config.get("appium", {}))
            try:
                round_page = run_app_flow(driver, platform, config, args)

                run_live_play(holes_config, args.holes, args.dry_run)

                round_page.end_round()
            finally:
                driver.quit()
            print("\nEnd-to-end round complete.")
            return

    # --skip-ui or --dry-run path: just run the live-play/medallion portion
    run_live_play(holes_config, args.holes, args.dry_run)
    print("\nLive-play simulation complete (UI flow skipped).")


def parse_holes_arg(value):
    if not value:
        return None
    return [int(x.strip()) for x in value.split(",") if x.strip() != ""]


def main():
    parser = argparse.ArgumentParser(description="Run the full GameGolf app flow end-to-end, including live play.")
    parser.add_argument("--config", required=True, help="Path to the E2E round config JSON")
    parser.add_argument("--holes", type=parse_holes_arg, default=None,
                         help="Comma-separated hole numbers to play, e.g. --holes 2,6 (default: all holes)")
    parser.add_argument("--dry-run", action="store_true", help="Print steps without driving a real app or serial port")
    parser.add_argument("--skip-ui", action="store_true",
                         help="Skip Appium entirely and only run the medallion/live-play portion (useful for testing that part alone)")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    try:
        config = load_config(config_path)
        run_end_to_end(config, args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
