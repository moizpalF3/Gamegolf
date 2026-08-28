# GameGolf End-to-End Round Automation

Drives the complete app flow — login, connect Medallion, search course, start
round, pair tags, play holes, end round — using Appium for the UI and the
Medallion's serial CLI for live GPS/shot simulation.

## ⚠️ Before this will work: fill in real locators

I don't have access to your actual app UI, so **every element identifier in
`locators.py` is a placeholder** (`TODO_...`). This project won't find a
single button until you replace them with real values.

How to get real locators:
- **Android**: run the app, then either use [Appium Inspector](https://github.com/appium/appium-inspector)
  connected to a live session, or `adb shell uiautomator dump` and pull the
  resulting XML to see `resource-id` / `content-desc` values.
- **iOS**: use Appium Inspector, or Xcode's Accessibility Inspector
  (Xcode → Open Developer Tool → Accessibility Inspector) to read each
  element's `accessibilityIdentifier`.

Every locator in `locators.py` has a comment explaining what screen/element
it's for. Go through it screen by screen.

## What's real vs. simulated here

- **UI navigation** (login, search, tapping buttons) — real, via Appium
  driving an actual device/simulator/emulator.
- **Medallion connection** — the UI tap is real, and the actual Bluetooth
  connection between phone and Medallion happens for real; the Medallion
  needs to be physically powered on and in range.
- **Tag pairing** — same idea: UI is real, and the actual BLE write of the
  Club ID to the tag's memory happens for real when you confirm.
- **GPS movement + shots during play** — simulated, using the same
  `nmea fake_coordinates` / `storage_service_v2 shot_add` commands sent over
  USB serial to the Medallion (this is the same mechanism from
  `gamegolf_hole_simulator.py`), since you can't easily fake this by
  physically walking a course during automated testing.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Install and start Appium:
   ```
   npm install -g appium
   appium driver install uiautomator2   # for Android
   appium driver install xcuitest       # for iOS
   appium
   ```
3. Fill in `locators.py` with real values (see above).
4. Copy `round_config.example.json` to `round_config.json` and fill in:
   - `platform`: `"android"` or `"ios"`
   - `appium`: device name, app package/bundle id or app path, platform version
   - `credentials`: a real test account (email/password)
   - `course_name`: must match what's searchable in-app
   - `clubs`: club name → tag ID pairs, matching your golf bag screen
   - `medallion_port`: the Medallion's serial port (e.g. `COM4`)
   - `holes_config_file`: path to a hole waypoints file — reuse anything
     built with `gamegolf_hole_simulator.py` (JSON/CSV/XLSX all work)

## Running it

Preview the live-play portion only, no serial port or Appium needed:
```
python3 run_e2e_round.py --config round_config.json --skip-ui --dry-run
```

Run just the live-play/medallion part against a real Medallion (useful while
you're still filling in UI locators):
```
python3 run_e2e_round.py --config round_config.json --skip-ui --holes 1,2,3
```

Run the full flow — real app UI + real Medallion:
```
python3 run_e2e_round.py --config round_config.json
```

Run only specific holes:
```
python3 run_e2e_round.py --config round_config.json --holes 4,5,6
```

## Project structure

```
run_e2e_round.py          Orchestrator - the full flow, top to bottom
appium_driver_factory.py  Builds the Appium session for iOS/Android
locators.py                Element locators (FILL THESE IN)
pages/
  base_page.py              Shared find/click/wait helpers
  login_page.py              Sign up / log in
  connect_device_page.py     Connect Medallion
  course_search_page.py      Search + select course, start round
  golf_bag_page.py            Pair tags to clubs, continue
  round_page.py                Wait for round start / Smart Caddie, end round
gamegolf_hole_simulator.py  Reused as-is: GPS movement + shot injection over serial
round_config.example.json  Sample config - copy to round_config.json
```

## Extending it

- **Smart Caddie strategy switching / Live Edit / Live Scorecard**: not yet
  covered by the flow you described, but each would just be another page
  object following the same pattern as the ones here.
- **Resume Round**: if you want to test the interrupted-round failsafe,
  that'd be a separate flow (kill the app mid-round, relaunch, assert the
  "Round already active" modal) — happy to add a page object + script for
  that specifically if useful.
- **Verifying shots landed correctly in the UI** (not just via the CLI's
  `shot_view_shots` command): add locators for whatever the Live Shot
  Tracking map/shot list shows, and assert against them after each
  `play_hole()` call in `run_live_play()`.
