#!/usr/bin/env python3
"""
GameGolf Full Hole Simulation Script
=====================================

Combines GPS movement simulation (based on MovementSimulation5Points.py /
MovementSimulation2Points.py) with shot injection, so a full hole can be
played from a single JSON config: just provide the hole's waypoint
coordinates and which club (tag ID) is used at each point.

Flow per hole:
    1. Set position at waypoint 1 (tee)
    2. Play the shot for waypoint 1 (storage_service_v2 shot_add <tag_id> gamegolf)
    3. Interpolate/move from waypoint 1 -> waypoint 2 (simulates ball flight / walking)
    4. Play the shot for waypoint 2
    5. ... repeat ...
    N. Play the final shot (e.g. the putt) at the last waypoint. No movement after.

A waypoint with no "tag_id" is just a movement point (no shot played there).

Each waypoint can also carry a "hole" number (defaults to 1 if omitted), so a
single file can hold an entire round. Use --holes to pick which hole(s) to
actually run, e.g. --holes 2,6 runs only hole 2 then hole 6, in that order.
Omit --holes to run every hole found, in ascending order.

Config can be provided as JSON, CSV, or XLSX (--config round.json / round.csv / round.xlsx):

  JSON: {"port": ..., "waypoints": [{"hole", "label", "lat", "lon", "tag_id"}, ...]}
        "hole" is optional per waypoint (default 1). Optional per-hole display
        info via "holes_info": {"1": {"course": ..., "name": ...}, "2": {...}}.
        (A single-hole config can still just use top-level "hole": {...} as before.)

  CSV: one row per waypoint, columns: hole, label, lat, lon, tag_id (hole and
       tag_id optional; hole defaults to 1, tag_id blank for movement-only
       points). Connection settings (port, baudrate, etc.) come from
       --port/--baudrate flags or script defaults, since a CSV can't hold two
       separate tables.

  XLSX: a "Waypoints" sheet with the same columns as the CSV above, plus an
        optional "Settings" sheet of key/value pairs (port, baudrate,
        steps_between_points, seconds_between_points, shot_settle_seconds,
        course, hole_name). If the workbook has only one sheet, it's treated
        as the Waypoints sheet.

Requirements:
    pip install pyserial pandas openpyxl

Usage:
    python3 gamegolf_hole_simulator.py --config round.json
    python3 gamegolf_hole_simulator.py --config round.csv --port COM4
    python3 gamegolf_hole_simulator.py --config round.xlsx --dry-run
    python3 gamegolf_hole_simulator.py --config round.xlsx --holes 2,6
"""

import argparse
import json
import sys
import time
from pathlib import Path

try:
    import serial
except ImportError:
    serial = None

try:
    import pandas as pd
except ImportError:
    pd = None


DEFAULT_BAUDRATE = 115200
DEFAULT_STEPS_BETWEEN_POINTS = 10
DEFAULT_SECONDS_BETWEEN_STEPS = 2
DEFAULT_SHOT_SETTLE_SECONDS = 1.0  # pause after a shot before moving on


def interpolate(start, end, steps):
    """Same linear interpolation as the original movement scripts."""
    return [start + (end - start) * i / steps for i in range(steps + 1)]


class GameGolfCLI:
    """Serial wrapper for the GPS Tracker's CLI (movement + shots)."""

    def __init__(self, port, baudrate=DEFAULT_BAUDRATE, dry_run=False):
        self.port = port
        self.baudrate = baudrate
        self.dry_run = dry_run
        self.conn = None

    def connect(self):
        if self.dry_run:
            print(f"[DRY RUN] Would open {self.port} @ {self.baudrate} baud")
            return
        if serial is None:
            raise RuntimeError("pyserial is not installed. Run: pip install pyserial")
        self.conn = serial.Serial(self.port, self.baudrate, timeout=1)
        time.sleep(2)  # match original scripts' settle time after opening the port

    def disconnect(self):
        if self.conn and self.conn.is_open:
            self.conn.close()

    def send_command(self, command):
        print(f"Sending: {command}")
        if self.dry_run:
            return
        self.conn.write((command + "\r\n").encode("utf-8"))


def move_to(cli, lat, lon):
    command = f"nmea fake_coordinates {lat:.9f} {lon:.9f}"
    cli.send_command(command)
    print(f"Moved to: {lat:.9f}, {lon:.9f}")


def move_between_points(cli, start_point, end_point, steps, seconds_between_steps):
    start_lat, start_lon = start_point
    end_lat, end_lon = end_point

    lat_points = interpolate(start_lat, end_lat, steps)
    lon_points = interpolate(start_lon, end_lon, steps)

    # Skip the first point (i=0) since it's identical to where we already are
    for lat, lon in list(zip(lat_points, lon_points))[1:]:
        move_to(cli, lat, lon)
        if not cli.dry_run:
            time.sleep(seconds_between_steps)


def play_shot(cli, tag_id, settle_seconds):
    command = f"storage_service_v2 shot_add {tag_id} gamegolf"
    cli.send_command(command)
    if not cli.dry_run:
        time.sleep(settle_seconds)


def _row_to_waypoint(row):
    """Turn one table row (dict-like, from CSV or XLSX) into a waypoint dict."""
    if "lat" not in row or "lon" not in row:
        raise ValueError("each waypoint row needs 'lat' and 'lon' columns")

    wp = {
        "lat": float(row["lat"]),
        "lon": float(row["lon"]),
    }
    label = row.get("label")
    if label is not None and str(label).strip() != "" and str(label).lower() != "nan":
        wp["label"] = str(label).strip()

    tag_id = row.get("tag_id")
    if tag_id is not None and str(tag_id).strip() != "" and str(tag_id).lower() != "nan":
        wp["tag_id"] = str(tag_id).strip()

    club = row.get("club")
    if club is not None and str(club).strip() != "" and str(club).lower() != "nan":
        wp["club"] = str(club).strip()

    hole = row.get("hole")
    if hole is not None and str(hole).strip() != "" and str(hole).lower() != "nan":
        wp["hole"] = int(float(hole))
    else:
        wp["hole"] = 1

    return wp


def load_config_from_csv(path):
    if pd is None:
        raise RuntimeError("pandas is not installed. Run: pip install pandas")

    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    waypoints = [_row_to_waypoint(row) for row in df.to_dict(orient="records")]

    return {"waypoints": waypoints}


def load_config_from_xlsx(path):
    if pd is None:
        raise RuntimeError("pandas is not installed. Run: pip install pandas openpyxl")

    xls = pd.ExcelFile(path)
    sheet_names = {name.strip().lower(): name for name in xls.sheet_names}

    waypoints_sheet = sheet_names.get("waypoints")
    if waypoints_sheet is None:
        # Only one sheet in the workbook -> treat it as the waypoints table
        if len(xls.sheet_names) == 1:
            waypoints_sheet = xls.sheet_names[0]
        else:
            raise ValueError(
                f"Could not find a 'Waypoints' sheet. Sheets found: {xls.sheet_names}"
            )

    wp_df = pd.read_excel(xls, sheet_name=waypoints_sheet)
    wp_df.columns = [c.strip().lower() for c in wp_df.columns]
    waypoints = [_row_to_waypoint(row) for row in wp_df.to_dict(orient="records")]

    config = {"waypoints": waypoints}

    settings_sheet = sheet_names.get("settings")
    if settings_sheet is not None:
        settings_df = pd.read_excel(xls, sheet_name=settings_sheet, header=None)
        settings = {}
        for _, row in settings_df.iterrows():
            if len(row) < 2:
                continue
            key, value = row[0], row[1]
            if pd.isna(key) or pd.isna(value):
                continue
            settings[str(key).strip().lower()] = value

        if "port" in settings:
            config["port"] = str(settings["port"]).strip()
        if "baudrate" in settings:
            config["baudrate"] = int(settings["baudrate"])
        if "steps_between_points" in settings:
            config["steps_between_points"] = int(settings["steps_between_points"])
        if "seconds_between_points" in settings:
            config["seconds_between_points"] = float(settings["seconds_between_points"])
        if "shot_settle_seconds" in settings:
            config["shot_settle_seconds"] = float(settings["shot_settle_seconds"])

        hole = {}
        if "course" in settings:
            hole["course"] = str(settings["course"]).strip()
        if "hole_name" in settings:
            hole["name"] = str(settings["hole_name"]).strip()
        if hole:
            config["hole"] = hole

    return config


def load_config(path):
    suffix = path.suffix.lower()

    if suffix == ".json":
        with open(path, "r") as f:
            config = json.load(f)
        # Normalize: every waypoint gets a "hole" number, defaulting to 1
        for wp in config.get("waypoints", []):
            wp.setdefault("hole", 1)
        return config
    elif suffix == ".csv":
        return load_config_from_csv(path)
    elif suffix in (".xlsx", ".xlsm"):
        return load_config_from_xlsx(path)
    else:
        raise ValueError(f"Unsupported config file type '{suffix}'. Use .json, .csv, or .xlsx")


def group_waypoints_into_holes(config):
    """
    Group the flat waypoints list into an ordered dict of
    {hole_number: [waypoints...]}, preserving first-seen order of hole
    numbers and of waypoints within each hole.
    """
    holes = {}
    for wp in config["waypoints"]:
        hole_num = wp.get("hole", 1)
        holes.setdefault(hole_num, []).append(wp)
    return holes


def hole_label_for(config, hole_num):
    """Build a display label for a hole, using holes_info/hole config if present."""
    holes_info = config.get("holes_info", {})
    info = holes_info.get(str(hole_num)) or holes_info.get(hole_num)

    if info is None and hole_num == 1:
        # Backward-compat: single-hole configs used a top-level "hole" key
        info = config.get("hole")

    if not info:
        return f"Hole {hole_num}"

    parts = [str(v) for v in [info.get("course"), info.get("name")] if v]
    label = " - ".join(parts) if parts else f"Hole {hole_num}"
    return f"Hole {hole_num} ({label})" if parts else label


def validate_config(config, args):
    errors = []

    if "waypoints" not in config or not isinstance(config["waypoints"], list) or len(config["waypoints"]) < 1:
        errors.append("config must contain a non-empty 'waypoints' list")
    else:
        for i, wp in enumerate(config["waypoints"], start=1):
            for field in ("lat", "lon"):
                if field not in wp:
                    errors.append(f"waypoint #{i} is missing required field '{field}'")

    if "port" not in config and not args.port:
        errors.append(
            "no serial port specified. Add 'port' to the config, or pass --port "
            "(--port is required for .csv files, since a CSV can't hold settings)"
        )

    if errors:
        raise ValueError("Invalid config:\n  - " + "\n  - ".join(errors))


def play_hole(cli, waypoints, steps, seconds_between_steps, shot_settle, hole_label):
    print(f"\n=== Playing {hole_label} ===")

    # Step 1: set initial position at the first waypoint
    first = waypoints[0]
    print(f"\n--- {first.get('label', 'Waypoint 1')} (start) ---")
    move_to(cli, first["lat"], first["lon"])

    if "tag_id" in first:
        print(f"Playing shot with club {first['tag_id']}")
        play_shot(cli, first["tag_id"], shot_settle)

    # Step 2+: move to each subsequent waypoint, then play its shot (if any)
    for i in range(1, len(waypoints)):
        prev_wp = waypoints[i - 1]
        wp = waypoints[i]
        label = wp.get("label", f"Waypoint {i + 1}")

        print(f"\n--- Moving to {label} ---")
        move_between_points(
            cli,
            (prev_wp["lat"], prev_wp["lon"]),
            (wp["lat"], wp["lon"]),
            steps,
            seconds_between_steps,
        )

        if "tag_id" in wp:
            print(f"--- {label}: playing shot with club {wp['tag_id']} ---")
            play_shot(cli, wp["tag_id"], shot_settle)
        else:
            print(f"--- {label}: no shot configured (movement only) ---")

    print(f"\n{hole_label} complete.")


def resolve_hole_order(holes_dict, requested_holes):
    """
    Decide which holes to run and in what order.
    - If the user passed --holes, use exactly that list, in that order,
      after validating every requested hole actually exists.
    - Otherwise, run every hole found, in ascending order.
    """
    available = set(holes_dict.keys())

    if requested_holes:
        missing = [h for h in requested_holes if h not in available]
        if missing:
            raise ValueError(
                f"Requested hole(s) {missing} not found in config. "
                f"Available holes: {sorted(available)}"
            )
        return requested_holes

    return sorted(available)


def run(config, args):
    validate_config(config, args)

    port = args.port or config["port"]
    baudrate = args.baudrate or config.get("baudrate", DEFAULT_BAUDRATE)
    steps = config.get("steps_between_points", DEFAULT_STEPS_BETWEEN_POINTS)
    seconds_between_steps = config.get("seconds_between_points", DEFAULT_SECONDS_BETWEEN_STEPS)
    shot_settle = config.get("shot_settle_seconds", DEFAULT_SHOT_SETTLE_SECONDS)

    holes_dict = group_waypoints_into_holes(config)
    hole_order = resolve_hole_order(holes_dict, args.holes)

    course = config.get("hole", {}).get("course")
    if course:
        print(f"=== Course: {course} ===")
    print(f"Holes to play, in order: {hole_order}\n")

    cli = GameGolfCLI(port=port, baudrate=baudrate, dry_run=args.dry_run)
    cli.connect()

    try:
        for hole_num in hole_order:
            waypoints = holes_dict[hole_num]
            label = hole_label_for(config, hole_num)
            play_hole(cli, waypoints, steps, seconds_between_steps, shot_settle, label)
    finally:
        cli.disconnect()

    print("\nRound simulation complete.")
    print("Verify with: storage_service_v2 shot_view_shots gamegolf")


def parse_holes_arg(value):
    if not value:
        return None
    try:
        return [int(x.strip()) for x in value.split(",") if x.strip() != ""]
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"--holes must be a comma-separated list of numbers, e.g. '2,6' (got '{value}')"
        )


def main():
    parser = argparse.ArgumentParser(description="Simulate a full GameGolf round or specific holes (movement + shots).")
    parser.add_argument("--config", required=True, help="Path to round config file (.json, .csv, or .xlsx)")
    parser.add_argument("--port", help="Override/serial port (required for .csv, since it can't hold settings)")
    parser.add_argument("--baudrate", type=int, help="Override baud rate from config")
    parser.add_argument("--holes", type=parse_holes_arg, default=None,
                         help="Comma-separated hole numbers to run, e.g. --holes 2,6 (default: all holes, ascending)")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without opening the serial port")
    parser.add_argument("--test-data", default="test_data.xlsx",
                         help="Excel file whose Clubs sheet maps waypoint 'club' names to tag IDs (default: test_data.xlsx)")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    try:
        config = load_config(config_path)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if any("club" in wp and "tag_id" not in wp for wp in config.get("waypoints", [])):
            from data_loader import apply_club_tags, load_overrides
            clubs = load_overrides(args.test_data).get("play_golf", {}).get("clubs", []) if Path(args.test_data).exists() else []
            apply_club_tags(config["waypoints"], clubs)
        run(config, args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
