"""
Element locators for every screen, per platform.

Each platform has its own module (android.py, ios.py) with one dict per
screen; this package exposes each screen as {"android": {...}, "ios": {...}}
so page objects pick the dict for the platform under test:

    from framework.locators import LOGIN
    LoginPage(driver, "android")   # uses android.LOGIN

To support a screen on iOS, fill in the same keys in ios.py; the page objects
and tests are shared. missing_keys("ios") lists what's still missing.
"""

from framework.locators import android, ios

PLATFORMS = {"android": android, "ios": ios}
SCREENS = ["LOGIN", "SIGNUP", "CONNECT_DEVICE", "COURSE_SEARCH", "GOLF_BAG", "ROUND_ACTIVE"]

LOGIN = {p: m.LOGIN for p, m in PLATFORMS.items()}
SIGNUP = {p: m.SIGNUP for p, m in PLATFORMS.items()}
CONNECT_DEVICE = {p: m.CONNECT_DEVICE for p, m in PLATFORMS.items()}
COURSE_SEARCH = {p: m.COURSE_SEARCH for p, m in PLATFORMS.items()}
GOLF_BAG = {p: m.GOLF_BAG for p, m in PLATFORMS.items()}
ROUND_ACTIVE = {p: m.ROUND_ACTIVE for p, m in PLATFORMS.items()}


def missing_keys(platform, reference="android"):
    """{screen: [locator keys the reference platform has but `platform` doesn't]}."""
    missing = {}
    for screen in SCREENS:
        ref = getattr(PLATFORMS[reference], screen)
        have = getattr(PLATFORMS[platform], screen)
        gaps = sorted(k for k in ref if k not in have)
        if gaps:
            missing[screen] = gaps
    return missing
