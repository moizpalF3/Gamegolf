# GameGolf Mobile Automation

End-to-end UI tests for the GameGolf mobile app, written in Python with
**Appium + pytest** using the **Page Object Model**. Play Golf tests also drive
a real **GameGolf Medallion** over USB serial to simulate GPS movement and
shots, so complete rounds are played end to end.

- Runs on a real Android phone today; structured so iOS can be added without
  duplicating tests.
- Test data, Play Golf scenarios and course coordinates live in an Excel
  workbook, so new Play Golf cases need no code.
- Every run produces a self-contained HTML report with screenshots.

**To run the tests, see [docs/HOW_TO_EXECUTE.md](docs/HOW_TO_EXECUTE.md).**

```
python run_tests.py --suite smoke
```

## Repository layout

```
.
├── run_tests.py              One-command runner: finds the phone, starts Appium,
│                             runs a suite, writes the HTML report
├── conftest.py               pytest setup: options (--platform, --test-config, ...),
│                             driver fixture, screenshots, report, scenario loading
├── pytest.ini                Test paths and markers (smoke, regression, play_golf, android, ios, ...)
├── requirements.txt
│
├── framework/                Reusable automation code (no tests here)
│   ├── core/
│   │   ├── driver_factory.py   Builds the Appium session for Android or iOS
│   │   ├── device_utils.py     adb helpers: connected phones, model, Android version
│   │   └── data_loader.py      Reads test_data.xlsx: credentials, clubs, Play Golf scenarios
│   ├── hardware/
│   │   └── medallion.py        Medallion serial CLI: GPS positions and shots
│   ├── locators/
│   │   ├── android.py          Android locators, one dict per screen
│   │   ├── ios.py              iOS locators, same keys (placeholders for now)
│   │   └── __init__.py         Picks the platform's locators for the page objects
│   └── pages/                  Page objects, shared by Android and iOS
│       ├── base_page.py
│       ├── login_page.py, signup_page.py
│       ├── connect_device_page.py, course_search_page.py, golf_bag_page.py
│       └── round_page.py
│
├── tests/                    Test cases, grouped by feature
│   ├── auth/
│   │   ├── test_login.py       TC_LOGIN_001-003
│   │   └── test_signup.py      TC_SIGNUP_001-004
│   └── play_golf/
│       └── test_play_golf_live.py   One test, run once per scenario in the Excel
│                                    Scenarios sheet (TC_PG_001, TC_PG_004 ... TC_PG_007)
│
├── config/
│   ├── test_config.example.json   Template: Appium server, per-platform capabilities
│   └── test_config.json           Your copy (git-ignored)
├── test_data/
│   ├── test_data.xlsx             Credentials, clubs, courses, scenarios, shots (git-ignored)
│   └── waypoints/                 Waypoint files for the fallback Play Golf run
├── docs/
│   └── HOW_TO_EXECUTE.md          Setup, running suites, reports, adding scenarios
├── tools/
│   └── run_e2e_round.py           Stand-alone orchestrator for one full round (no pytest)
└── artifacts/                     Run output: reports, screenshots, Appium logs (git-ignored)
```

## Test cases

`tests/` has three files but **12 test cases**: each file holds several test
functions, and the Play Golf test runs once for every enabled row of the
Excel Scenarios sheet.

| ID | Area | Test case |
|---|---|---|
| TC_LOGIN_001 | Login | Valid credentials log in and land on Home |
| TC_LOGIN_002 | Login | Wrong credentials show "Login Unsuccessful" |
| TC_LOGIN_003 | Login | Log In stays disabled until both fields are filled |
| TC_SIGNUP_001 | Sign Up | New user: Start Setup > golf bag Skip > Home > log out |
| TC_SIGNUP_002 | Sign Up | Registered email shows "Email already exists" |
| TC_SIGNUP_003 | Sign Up | Continue stays disabled until Terms are accepted |
| TC_SIGNUP_004 | Sign Up | "Don't have a Device" opens the KZN AI marketplace |
| TC_PG_001 | Play Golf | Holes 1-3, each hole's score equals its shots |
| TC_PG_004 | Play Golf | Hole completed: no auto hole switch back to hole 1 |
| TC_PG_005 | Play Golf | Hole open: auto hole switch back to hole 1 |
| TC_PG_006 | Play Golf | Hole completed: "Shot Not Saved" pop-up |
| TC_PG_007 | Play Golf | App in background: shots sync, ends on hole 5 |

List them yourself with `pytest --collect-only -q`.

## Android and iOS

- **Page objects and tests are shared.** A page object asks for a locator by
  name (e.g. `"login_button"`), and `framework/locators` returns the Android or
  iOS value for the platform under test.
- **Locators are per platform:** `framework/locators/android.py` and
  `framework/locators/ios.py` have the same screens and keys. To bring a
  screen to iOS, fill in its keys in `ios.py`;
  `python -c "from framework.locators import missing_keys; print(missing_keys('ios'))"`
  lists what's still missing.
- **Capabilities are per platform:** `config/test_config.json` has an
  `appium.android` and an `appium.ios` block.
- **Choose the platform per run:** `python run_tests.py --platform ios --suite login`.
- **Platform-only behaviour:** mark the test `@pytest.mark.android` or
  `@pytest.mark.ios`; it's skipped automatically on the other platform. For
  flows that differ a lot, add a platform-specific page method or test file
  next to the shared one (e.g. `tests/auth/test_login_ios.py`).

## Adding test cases

- **Play Golf:** add rows to the Excel Courses / Scenarios / Shots sheets (see
  [docs/HOW_TO_EXECUTE.md](docs/HOW_TO_EXECUTE.md)); no code needed.
- **Other features:** add a page object in `framework/pages/` (locators in
  `framework/locators/android.py` and `ios.py`) and a test module in
  `tests/<feature>/`, with a `TC_<AREA>_NNN - description` docstring and the
  `smoke` / `regression` / feature markers.
