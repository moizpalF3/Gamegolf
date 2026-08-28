"""
Builds an Appium driver session for either platform.

You'll need an Appium server running first:
    npm install -g appium
    appium driver install uiautomator2   # for Android
    appium driver install xcuitest       # for iOS
    appium

Fill in the capabilities below (device name, app path/bundle id, platform
version) for your actual setup. These are placeholders.
"""

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions


def build_driver(platform, config):
    """
    platform: "android" or "ios"
    config: dict with capability overrides, e.g.
        {
          "appium_server_url": "http://localhost:4723",
          "device_name": "Pixel_7_API_34",
          "app_path": "/path/to/gamegolf.apk",
          "platform_version": "14",
          "app_package": "com.gamegolf.app",          # android only, if app already installed
          "app_activity": ".MainActivity",              # android only
          "bundle_id": "com.gamegolf.app",              # ios only, if app already installed
          "udid": "..."                                  # ios only, real device
        }
    """
    server_url = config.get("appium_server_url", "http://localhost:4723")

    if platform == "android":
        options = UiAutomator2Options()
        options.device_name = config.get("device_name", "TODO_device_name")
        if config.get("platform_version"):
            options.platform_version = config["platform_version"]

        if config.get("app_path"):
            options.app = config["app_path"]
        elif config.get("app_package") and config.get("app_activity"):
            options.app_package = config["app_package"]
            options.app_activity = config["app_activity"]
        else:
            raise ValueError(
                "config needs either 'app_path' (an .apk to install) or "
                "'app_package' + 'app_activity' (an already-installed app)"
            )

        options.no_reset = config.get("no_reset", False)
        return webdriver.Remote(server_url, options=options)

    elif platform == "ios":
        options = XCUITestOptions()
        options.device_name = config.get("device_name", "TODO_device_name")
        if config.get("platform_version"):
            options.platform_version = config["platform_version"]
        if config.get("udid"):
            options.udid = config["udid"]

        if config.get("app_path"):
            options.app = config["app_path"]
        elif config.get("bundle_id"):
            options.bundle_id = config["bundle_id"]
        else:
            raise ValueError(
                "config needs either 'app_path' (a .app/.ipa to install) or "
                "'bundle_id' (an already-installed app)"
            )

        options.no_reset = config.get("no_reset", False)
        return webdriver.Remote(server_url, options=options)

    else:
        raise ValueError(f"Unknown platform '{platform}'. Use 'android' or 'ios'.")
