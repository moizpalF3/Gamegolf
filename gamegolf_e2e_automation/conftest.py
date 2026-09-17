import json
import time
from pathlib import Path

import pytest

from appium_driver_factory import build_driver


def pytest_addoption(parser):
    parser.addoption(
        "--test-config",
        action="store",
        default="test_config.json",
        help="Path to the test config JSON (copy test_config.example.json to get started)",
    )


@pytest.fixture(scope="session")
def config(pytestconfig):
    config_path = Path(pytestconfig.getoption("--test-config"))
    if not config_path.exists():
        pytest.exit(
            f"Test config not found: {config_path}. "
            f"Copy test_config.example.json to {config_path.name} and fill it in."
        )
    with open(config_path, "r") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def platform(config):
    return config["platform"].lower()


@pytest.fixture
def driver(platform, config):
    """A fresh Appium session per test."""
    session = build_driver(platform, config.get("appium", {}))
    yield session
    session.quit()


@pytest.fixture
def unique_email(config):
    """A fresh email per test run so Sign Up tests don't collide with a prior run."""
    domain = config.get("signup", {}).get("email_domain", "example.com")
    return f"test.user.{int(time.time())}@{domain}"
