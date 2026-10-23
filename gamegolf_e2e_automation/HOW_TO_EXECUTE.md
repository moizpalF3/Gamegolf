# GameGolf Mobile Automation — How to Execute

This suite runs automated tests on a real Android phone running the GameGolf
app. For Play Golf scenarios it also drives a real GameGolf Medallion, so
GPS movement and shots are simulated end to end. Every run produces an HTML
report with a pass/fail result and screenshots for each test case.

---

## 1. What you need

| Item | Details |
|---|---|
| Windows PC | Python 3.11+, Node.js 20+ |
| Android phone | USB debugging on, GameGolf staging app installed (`org.gameyourgame.kzn.dev`), logged in |
| USB cable | Phone connected to the PC; it must show as `device` in `adb devices` |
| Medallion (Play Golf tests only) | Powered on, connected to the PC by USB (serial port, e.g. `COM4`) and in Bluetooth range of the phone |
| Android SDK platform-tools | Provides `adb` |
| Appium 3 + UiAutomator2 driver | Drives the phone |

## 2. One-time setup

Run these from the `gamegolf_e2e_automation` folder.

1. Install the Python packages:
   ```
   pip install -r requirements.txt
   ```
2. Install Appium and the Android driver:
   ```
   npm install -g appium
   appium driver install uiautomator2
   ```
3. Create your config from the template, then set the app package/activity
   and the Medallion `medallion_port` (the phone is detected automatically):
   ```
   copy test_config.example.json test_config.json
   ```
4. Create your test data workbook and fill it in:
   ```
   copy test_data.example.xlsx test_data.xlsx
   ```
   | Sheet | What to enter |
   |---|---|
   | Credentials | `valid` and `invalid` login rows (email, password) |
   | Signup | Data used by the sign-up tests |
   | Clubs | Each club name and its tag ID (e.g. `Driver` / `0xD5B7817D`) |

   `test_config.json` and `test_data.xlsx` hold your device details and
   passwords, so they are never committed to git.

## 3. Running tests

1. Plug in the phone and confirm it is listed:
   ```
   adb devices
   ```
2. Run a suite:
   ```
   python run_tests.py --suite smoke
   ```

The runner then:
- detects the connected phone, its model and its Android version
- starts the Appium server if it isn't already running, and stops it afterwards
- runs the selected suite on the phone
- writes the HTML report and screenshots to `artifacts/runs/<date_time>_<suite>/`

### Choosing what to run

| Command | Runs |
|---|---|
| `python run_tests.py --suite smoke` | Quick core checks, for every build |
| `python run_tests.py --suite regression` | The full suite |
| `python run_tests.py --suite play_golf` | Play Golf Live scenarios only |
| `python run_tests.py --suite login` | Login cases only |
| `python run_tests.py --suite signup` | Sign-up cases only |
| `python run_tests.py --suite all` | Everything, regardless of tags |

Useful options:

| Option | Effect |
|---|---|
| `--no-hardware` | Skip tests that need the Medallion |
| `--device R5CR321EVPX` | Pick a phone when more than one is connected |
| `--open` | Open the HTML report when the run finishes |
| `-- -k TC_PG_001` | Run a single test case by its ID (anything after `--` goes to pytest) |

Examples:
```
python run_tests.py --suite regression --no-hardware --open
python run_tests.py --suite play_golf -- -k TC_PG_001
```

## 4. Results

Each run gets its own folder:

```
artifacts/runs/20261022_143005_smoke/
  report.html        <- open this in any browser
  screenshots/       <- every screenshot as a PNG
  appium.log         <- only if the runner started Appium itself
```

The **HTML report** shows:
- a summary of passed, failed and skipped tests, with total duration
- one row per test case, with its ID, description, result and duration
- screenshots under each test (click the row to expand):
  - `final`: the phone screen at the end of every test, pass or fail
  - `FAILED_final`: the screen at the moment a test failed
  - step screenshots taken during a test, e.g. `hole_1_score` after each hole
- the failure message and log for any failed test

The report is a single self-contained file, so it can be emailed or attached
as is.

## 5. Test suites

| Marker | Purpose |
|---|---|
| `smoke` | Fast, high-value checks to run on every build |
| `regression` | Every test case; run before a release |
| `login` / `signup` / `play_golf` | Feature areas, for focused runs |
| `live_hardware` | Needs the physical Medallion; excluded by `--no-hardware` |

Every test case has an ID (e.g. `TC_PG_001`) shown in its description in the
report.

## 6. Troubleshooting

| Symptom | Fix |
|---|---|
| `No Android device connected` | Reconnect the USB cable, unlock the phone, accept the "Allow USB debugging" prompt, then check `adb devices` |
| `Appium didn't become ready` | Open `appium.log` in the run folder; check `appium driver list --installed` shows uiautomator2 |
| `Neither ANDROID_HOME nor ANDROID_SDK_ROOT` | Set `ANDROID_HOME` to your SDK folder (e.g. `%LOCALAPPDATA%\Android\Sdk`) |
| A test fails with `NoSuchElement` / `Timeout` | The screen didn't show what the test expected; check that test's screenshots in the report |
| Play Golf: Start Round stays grey | The Medallion isn't connected to the phone; power it on and keep it near the phone |
| Play Golf: serial port error | Check the Medallion's COM port in Device Manager and update `medallion_port` in `test_config.json` |

## 7. Running without the runner (advanced)

Start Appium yourself, then call pytest directly from `gamegolf_e2e_automation`:
```
appium --address 127.0.0.1 --port 4723
pytest -m smoke
pytest -m "regression and not live_hardware"
pytest -k TC_LOGIN_001
```
Reports and screenshots go to `artifacts/runs/<timestamp>/` in the same way.
