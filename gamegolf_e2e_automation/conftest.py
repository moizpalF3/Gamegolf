import base64
import json
import re
import time
from pathlib import Path

import pytest

from appium_driver_factory import build_driver
from data_loader import load_overrides, load_play_golf_scenarios, merge_config
import device_utils

PROJECT_DIR = Path(__file__).parent


def pytest_addoption(parser):
    parser.addoption(
        "--test-config",
        action="store",
        default="test_config.json",
        help="Path to the test config JSON (copy test_config.example.json to get started)",
    )
    parser.addoption(
        "--test-data",
        action="store",
        default="test_data.xlsx",
        help="Excel file with credentials / club tag IDs that override test_config.json (skipped if missing)",
    )
    parser.addoption(
        "--device-serial",
        action="store",
        default=None,
        help="adb serial of the phone to use (default: auto-detect the connected phone)",
    )
    parser.addoption(
        "--run-dir",
        action="store",
        default=None,
        help="Folder for this run's report + screenshots (default: artifacts/runs/<timestamp>)",
    )


# ---------------------------------------------------------------------------
# Run folder + HTML report
# ---------------------------------------------------------------------------

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    run_dir = config.getoption("--run-dir")
    run_dir = Path(run_dir) if run_dir else PROJECT_DIR / "artifacts" / "runs" / time.strftime("%Y%m%d_%H%M%S")
    (run_dir / "screenshots").mkdir(parents=True, exist_ok=True)
    config._gg_run_dir = run_dir

    # Always write a self-contained HTML report (screenshots embedded) unless --html was given.
    if hasattr(config.option, "htmlpath"):
        if not config.option.htmlpath:
            config.option.htmlpath = str(run_dir / "report.html")
        config.option.self_contained_html = True


def pytest_html_report_title(report):
    report.title = "GameGolf Mobile Automation - Test Report"


def pytest_html_results_table_header(cells):
    cells.insert(1, "<th>Description</th>")


def pytest_html_results_table_row(report, cells):
    cells.insert(1, f"<td>{getattr(report, 'description', '')}</td>")


# ---------------------------------------------------------------------------
# Config + device
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def config(pytestconfig):
    config_path = Path(pytestconfig.getoption("--test-config"))
    if not config_path.exists():
        pytest.exit(
            f"Test config not found: {config_path}. "
            f"Copy test_config.example.json to {config_path.name} and fill it in."
        )
    with open(config_path, "r") as f:
        cfg = json.load(f)

    data_path = Path(pytestconfig.getoption("--test-data"))
    if data_path.exists():
        merge_config(cfg, load_overrides(data_path))

    if cfg["platform"].lower() == "android":
        _attach_connected_device(cfg, pytestconfig.getoption("--device-serial"))
    return cfg


def _attach_connected_device(cfg, requested_serial):
    """Points the Appium capabilities at the phone that's actually plugged in."""
    appium = cfg.setdefault("appium", {})
    devices = device_utils.connected_devices()
    if requested_serial:
        if requested_serial not in devices:
            pytest.exit(f"Device '{requested_serial}' isn't connected. Connected: {devices or 'none'}")
        serial = requested_serial
    elif devices:
        serial = devices[0]
    else:
        pytest.exit("No Android device connected. Plug in the phone with USB debugging on and check `adb devices`.")

    appium["udid"] = serial
    appium["device_name"] = serial
    version = device_utils.android_version(serial)
    if version:
        appium["platform_version"] = version
    print(f"\n[Device] Using {device_utils.device_model(serial) or 'device'} ({serial}), Android {version}")


def pytest_generate_tests(metafunc):
    """
    One test case per enabled row of the Scenarios sheet in the test data
    workbook, so `-k TC_PG_002` runs a single scenario. Without a Scenarios
    sheet, falls back to a single run from play_golf.holes_config_file.
    """
    if "scenario" not in metafunc.fixturenames:
        return
    data_path = Path(metafunc.config.getoption("--test-data"))
    scenarios = load_play_golf_scenarios(data_path) if data_path.exists() else []
    if scenarios:
        metafunc.parametrize("scenario", scenarios, ids=[s["id"] for s in scenarios])
    else:
        metafunc.parametrize("scenario", [None], ids=["TC_PG_001"])


@pytest.fixture(scope="session")
def platform(config):
    return config["platform"].lower()


@pytest.fixture
def driver(platform, config):
    """A fresh Appium session per test."""
    session = build_driver(platform, config.get("appium", {}))
    yield session
    session.quit()


# ---------------------------------------------------------------------------
# Screenshots
# ---------------------------------------------------------------------------

def _safe(name):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)[:120]


def _capture(driver, item, label):
    path = item.config._gg_run_dir / "screenshots" / f"{_safe(item.name)}__{_safe(label)}.png"
    driver.save_screenshot(str(path))
    item._gg_screenshots = getattr(item, "_gg_screenshots", []) + [(label, path)]
    return path


@pytest.fixture
def screenshot(request, driver):
    """
    Call inside a test to capture the current screen into the run folder and
    the HTML report:  screenshot("hole_1_score")
    """
    return lambda label: _capture(driver, request.node, label)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    scenario = getattr(item, "callspec", None) and item.callspec.params.get("scenario")
    if scenario:
        report.description = f"{scenario['id']} - {scenario['description']} ({scenario['course']})"
    else:
        report.description = (item.function.__doc__ or "").strip().split("\n")[0]

    if report.when != "call":
        return

    # Final-state screenshot for every test, pass or fail.
    driver = item.funcargs.get("driver")
    if driver is not None:
        try:
            _capture(driver, item, "FAILED_final" if report.failed else "final")
        except Exception as e:
            print(f"[Screenshot] Could not capture final screen: {e}")

    try:
        import pytest_html
    except ImportError:
        return
    extras = getattr(report, "extras", [])
    for label, path in getattr(item, "_gg_screenshots", []):
        if path.exists():
            encoded = base64.b64encode(path.read_bytes()).decode()
            extras.append(pytest_html.extras.png(encoded, name=label))
    report.extras = extras


@pytest.fixture
def unique_email(config):
    """A fresh email per test run so Sign Up tests don't collide with a prior run."""
    domain = config.get("signup", {}).get("email_domain", "example.com")
    return f"test.user.{int(time.time())}@{domain}"
