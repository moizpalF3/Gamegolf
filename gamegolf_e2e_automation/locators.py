"""
Locators for every screen in the GameGolf app flow.

*** YOU MUST FILL THESE IN WITH REAL VALUES FROM YOUR APP ***

I don't have access to the actual GameGolf app UI, so every value below is a
placeholder. Replace them with real element identifiers before running.

How to find real locators:
  Android: run the app, then `adb shell uiautomator dump` and pull the XML,
           or use the Appium Inspector app (https://github.com/appium/appium-inspector)
           connected to your running session. Android locators are usually
           resource-id (e.g. "com.gamegolf.app:id/login_button") or
           accessibility id (contentDescription).
  iOS:     use Appium Inspector, or Xcode's Accessibility Inspector
           (Xcode > Open Developer Tool > Accessibility Inspector). iOS
           locators are usually accessibility id (the `accessibilityIdentifier`
           set by the iOS dev team) or a predicate string.

Each screen below has an "android" and "ios" locator using Appium's By
strategy. Use By.ID / By.ACCESSIBILITY_ID / AppiumBy.IOS_PREDICATE /
AppiumBy.ANDROID_UIAUTOMATOR as appropriate — swap the strategy per element
if accessibility id doesn't exist for something.
"""

from appium.webdriver.common.appiumby import AppiumBy


# ---------------------------------------------------------------------------
# Login / Sign up screen
# ---------------------------------------------------------------------------
LOGIN = {
    "android": {
        "email_field": (AppiumBy.ID, "com.gamegolf.app:id/TODO_email_field"),
        "password_field": (AppiumBy.ID, "com.gamegolf.app:id/TODO_password_field"),
        "login_button": (AppiumBy.ID, "com.gamegolf.app:id/TODO_login_button"),
        "signup_link": (AppiumBy.ID, "com.gamegolf.app:id/TODO_signup_link"),
        "logged_in_indicator": (AppiumBy.ID, "com.gamegolf.app:id/TODO_home_screen_root"),
        "error_message": (AppiumBy.ID, "com.gamegolf.app:id/TODO_login_error_message"),
    },
    "ios": {
        "email_field": (AppiumBy.ACCESSIBILITY_ID, "TODO_email_field"),
        "password_field": (AppiumBy.ACCESSIBILITY_ID, "TODO_password_field"),
        "login_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_login_button"),
        "signup_link": (AppiumBy.ACCESSIBILITY_ID, "TODO_signup_link"),
        "logged_in_indicator": (AppiumBy.ACCESSIBILITY_ID, "TODO_home_screen_root"),
        "error_message": (AppiumBy.ACCESSIBILITY_ID, "TODO_login_error_message"),
    },
}

# ---------------------------------------------------------------------------
# Sign up screen
# ---------------------------------------------------------------------------
SIGNUP = {
    "android": {
        "first_name_field": (AppiumBy.ID, "com.gamegolf.app:id/TODO_first_name_field"),
        "last_name_field": (AppiumBy.ID, "com.gamegolf.app:id/TODO_last_name_field"),
        "email_field": (AppiumBy.ID, "com.gamegolf.app:id/TODO_signup_email_field"),
        "password_field": (AppiumBy.ID, "com.gamegolf.app:id/TODO_signup_password_field"),
        "confirm_password_field": (AppiumBy.ID, "com.gamegolf.app:id/TODO_confirm_password_field"),
        "signup_button": (AppiumBy.ID, "com.gamegolf.app:id/TODO_signup_button"),
        "login_link": (AppiumBy.ID, "com.gamegolf.app:id/TODO_signup_login_link"),
        "signup_success_indicator": (AppiumBy.ID, "com.gamegolf.app:id/TODO_home_screen_root"),
        "error_message": (AppiumBy.ID, "com.gamegolf.app:id/TODO_signup_error_message"),
    },
    "ios": {
        "first_name_field": (AppiumBy.ACCESSIBILITY_ID, "TODO_first_name_field"),
        "last_name_field": (AppiumBy.ACCESSIBILITY_ID, "TODO_last_name_field"),
        "email_field": (AppiumBy.ACCESSIBILITY_ID, "TODO_signup_email_field"),
        "password_field": (AppiumBy.ACCESSIBILITY_ID, "TODO_signup_password_field"),
        "confirm_password_field": (AppiumBy.ACCESSIBILITY_ID, "TODO_confirm_password_field"),
        "signup_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_signup_button"),
        "login_link": (AppiumBy.ACCESSIBILITY_ID, "TODO_signup_login_link"),
        "signup_success_indicator": (AppiumBy.ACCESSIBILITY_ID, "TODO_home_screen_root"),
        "error_message": (AppiumBy.ACCESSIBILITY_ID, "TODO_signup_error_message"),
    },
}

# ---------------------------------------------------------------------------
# Connect Medallion screen
# ---------------------------------------------------------------------------
CONNECT_DEVICE = {
    "android": {
        "connect_button": (AppiumBy.ID, "com.gamegolf.app:id/TODO_connect_medallion_button"),
        "connected_indicator": (AppiumBy.ID, "com.gamegolf.app:id/TODO_device_connected_label"),
    },
    "ios": {
        "connect_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_connect_medallion_button"),
        "connected_indicator": (AppiumBy.ACCESSIBILITY_ID, "TODO_device_connected_label"),
    },
}

# ---------------------------------------------------------------------------
# Course search screen
# ---------------------------------------------------------------------------
COURSE_SEARCH = {
    "android": {
        "search_field": (AppiumBy.ID, "com.gamegolf.app:id/TODO_course_search_field"),
        # Template for a search-result row; format with the course name at
        # runtime, e.g. ANDROID_RESULT_TEMPLATE.format(course_name="Gort Golf Club")
        "result_row_template": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("{course_name}")',
        ),
        "start_round_button": (AppiumBy.ID, "com.gamegolf.app:id/TODO_start_round_button"),
    },
    "ios": {
        "search_field": (AppiumBy.ACCESSIBILITY_ID, "TODO_course_search_field"),
        "result_row_template": (
            AppiumBy.IOS_PREDICATE,
            'label CONTAINS "{course_name}"',
        ),
        "start_round_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_start_round_button"),
    },
}

# ---------------------------------------------------------------------------
# Golf bag / tag pairing screen
# ---------------------------------------------------------------------------
GOLF_BAG = {
    "android": {
        # Template for a club slot by name, e.g. "Driver", "3 Wood", "7 Iron"
        "club_slot_template": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("{club_name}")',
        ),
        "pair_tag_button": (AppiumBy.ID, "com.gamegolf.app:id/TODO_pair_tag_button"),
        # Row for a discovered/nearby tag, matched by its hex tag id
        "tag_row_template": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("{tag_id}")',
        ),
        "confirm_pair_button": (AppiumBy.ID, "com.gamegolf.app:id/TODO_confirm_pair_button"),
        "continue_button": (AppiumBy.ID, "com.gamegolf.app:id/TODO_golf_bag_continue_button"),
    },
    "ios": {
        "club_slot_template": (AppiumBy.IOS_PREDICATE, 'label CONTAINS "{club_name}"'),
        "pair_tag_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_pair_tag_button"),
        "tag_row_template": (AppiumBy.IOS_PREDICATE, 'label CONTAINS "{tag_id}"'),
        "confirm_pair_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_confirm_pair_button"),
        "continue_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_golf_bag_continue_button"),
    },
}

# ---------------------------------------------------------------------------
# Active round screen (Live Shot Tracking + Smart Caddie)
# ---------------------------------------------------------------------------
ROUND_ACTIVE = {
    "android": {
        "round_screen_root": (AppiumBy.ID, "com.gamegolf.app:id/TODO_round_map_root"),
        "smart_caddie_recommendation": (AppiumBy.ID, "com.gamegolf.app:id/TODO_smart_caddie_club_label"),
        "menu_button": (AppiumBy.ID, "com.gamegolf.app:id/TODO_round_menu_button"),
        "end_round_option": (AppiumBy.ID, "com.gamegolf.app:id/TODO_end_round_menu_item"),
        "end_round_confirm_button": (AppiumBy.ID, "com.gamegolf.app:id/TODO_end_round_confirm_button"),
    },
    "ios": {
        "round_screen_root": (AppiumBy.ACCESSIBILITY_ID, "TODO_round_map_root"),
        "smart_caddie_recommendation": (AppiumBy.ACCESSIBILITY_ID, "TODO_smart_caddie_club_label"),
        "menu_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_round_menu_button"),
        "end_round_option": (AppiumBy.ACCESSIBILITY_ID, "TODO_end_round_menu_item"),
        "end_round_confirm_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_end_round_confirm_button"),
    },
}
