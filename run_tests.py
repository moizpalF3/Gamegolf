#!/usr/bin/env python3
"""
GameGolf mobile test runner.

Checks the phone is connected, starts Appium if it isn't already running,
runs the chosen suite on the phone, and writes an HTML report with
screenshots to artifacts/runs/<timestamp>_<platform>_<suite>/report.html.

Examples:
    python run_tests.py --suite smoke
    python run_tests.py --suite play_golf
    python run_tests.py --suite regression --no-hardware
    python run_tests.py --suite all --device R5CR321EVPX --open
    python run_tests.py --platform ios --suite login
    python run_tests.py --suite smoke -- -k login      (anything after -- goes to pytest)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from framework.core import device_utils

PROJECT_DIR = Path(__file__).parent

SUITES = {
    "smoke": "smoke",
    "regression": "regression",
    "play_golf": "play_golf",
    "login": "login",
    "signup": "signup",
    "all": None,
}


def appium_is_up(url):
    try:
        with urllib.request.urlopen(f"{url.rstrip('/')}/status", timeout=3) as r:
            return json.load(r).get("value", {}).get("ready", False)
    except Exception:
        return False


def start_appium(url, log_path):
    appium = shutil.which("appium.cmd") or shutil.which("appium")
    if not appium:
        sys.exit("Appium isn't installed or not on PATH. Install it with: npm install -g appium")

    parsed = urlparse(url)
    env = dict(os.environ)
    sdk = device_utils.android_sdk_root()
    if sdk:
        env.setdefault("ANDROID_HOME", sdk)
        env.setdefault("ANDROID_SDK_ROOT", sdk)

    print(f"[Runner] Starting Appium on {url} (log: {log_path})")
    proc = subprocess.Popen(
        [appium, "--address", parsed.hostname or "127.0.0.1", "--port", str(parsed.port or 4723),
         "--log", str(log_path)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env,
    )
    for _ in range(60):
        if appium_is_up(url):
            return proc
        if proc.poll() is not None:
            sys.exit(f"Appium exited during startup - check {log_path}")
        time.sleep(1)
    stop_appium(proc)
    sys.exit(f"Appium didn't become ready within 60s - check {log_path}")


def stop_appium(proc):
    if proc and proc.poll() is None:
        if os.name == "nt":
            # appium on Windows is a .cmd wrapper around node; kill the whole tree.
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
        else:
            proc.terminate()


def main():
    parser = argparse.ArgumentParser(description="Run GameGolf mobile tests on the connected phone.")
    parser.add_argument("--suite", choices=SUITES, default="smoke", help="Which suite to run (default: smoke)")
    parser.add_argument("--platform", choices=["android", "ios"],
                        help="Platform to run on (default: 'platform' in the test config)")
    parser.add_argument("--device", help="adb serial to use (default: the first connected phone)")
    parser.add_argument("--no-hardware", action="store_true",
                        help="Skip tests that need the physical Medallion (live_hardware)")
    parser.add_argument("--test-config", default="config/test_config.json")
    parser.add_argument("--test-data", default="test_data/test_data.xlsx")
    parser.add_argument("--open", action="store_true", help="Open the HTML report when the run finishes")
    args, pytest_extra = parser.parse_known_args()
    if pytest_extra[:1] == ["--"]:
        pytest_extra = pytest_extra[1:]

    os.chdir(PROJECT_DIR)

    try:
        with open(args.test_config) as f:
            test_config = json.load(f)
    except FileNotFoundError:
        sys.exit(f"{args.test_config} not found - copy config/test_config.example.json to it and fill it in.")
    platform = (args.platform or test_config.get("platform", "android")).lower()

    # 1. Phone (Android: found through adb; iOS: the udid in the test config)
    serial = None
    if platform == "android":
        devices = device_utils.connected_devices()
        if not devices:
            sys.exit("No Android device connected. Plug in the phone with USB debugging on, "
                     "then check `adb devices`.")
        serial = args.device or devices[0]
        if serial not in devices:
            sys.exit(f"Device '{serial}' isn't connected. Connected: {devices}")
        print(f"[Runner] Device: {device_utils.device_model(serial)} ({serial}), "
              f"Android {device_utils.android_version(serial)}")
    else:
        print("[Runner] Platform: iOS (device from the 'appium.ios' block of the test config)")

    # 2. Run folder
    run_dir = PROJECT_DIR / "artifacts" / "runs" / f"{time.strftime('%Y%m%d_%H%M%S')}_{platform}_{args.suite}"
    run_dir.mkdir(parents=True, exist_ok=True)
    report = run_dir / "report.html"

    # 3. Appium
    url = test_config.get("appium", {}).get("appium_server_url", "http://127.0.0.1:4723")
    appium_proc = None if appium_is_up(url) else start_appium(url, run_dir / "appium.log")

    # 4. pytest
    marker = SUITES[args.suite]
    if args.no_hardware:
        marker = f"({marker}) and not live_hardware" if marker else "not live_hardware"
    cmd = [sys.executable, "-m", "pytest", "--platform", platform,
           "--test-config", args.test_config, "--test-data", args.test_data,
           "--run-dir", str(run_dir), f"--html={report}", "--self-contained-html", "-v"]
    if serial:
        cmd += ["--device-serial", serial]
    if marker:
        cmd += ["-m", marker]
    cmd += pytest_extra

    print(f"[Runner] Platform: {platform}  Suite: {args.suite}" + (f"  (-m \"{marker}\")" if marker else ""))
    try:
        result = subprocess.run(cmd)
    finally:
        stop_appium(appium_proc)

    print(f"\n[Runner] HTML report: {report}")
    print(f"[Runner] Screenshots: {run_dir / 'screenshots'}")
    if args.open and report.exists():
        if os.name == "nt":
            os.startfile(report)
        else:
            subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", str(report)])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
