"""
iOS locators, one dict per screen (used through framework/locators).

Placeholders only (TODO_): the iOS app hasn't been automated yet. Fill these
in with accessibility ids (the dev team's accessibilityIdentifier) or
predicate strings, found with Appium Inspector or Xcode's Accessibility
Inspector. Every key the Android dict for a screen has should exist here too,
so the shared page objects work on both platforms.
"""

from appium.webdriver.common.appiumby import AppiumBy


# ---------------------------------------------------------------------------
# Login / Sign up screen
# ---------------------------------------------------------------------------
LOGIN = {
    "email_field": (AppiumBy.ACCESSIBILITY_ID, "TODO_email_field"),
    "password_field": (AppiumBy.ACCESSIBILITY_ID, "TODO_password_field"),
    "login_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_login_button"),
    "signup_link": (AppiumBy.ACCESSIBILITY_ID, "TODO_signup_link"),
    "logged_in_indicator": (AppiumBy.ACCESSIBILITY_ID, "TODO_home_screen_root"),
    "error_message": (AppiumBy.ACCESSIBILITY_ID, "TODO_login_error_message"),
}

# ---------------------------------------------------------------------------
# Sign up screen
# ---------------------------------------------------------------------------
SIGNUP = {
    "first_name_field": (AppiumBy.ACCESSIBILITY_ID, "TODO_first_name_field"),
    "last_name_field": (AppiumBy.ACCESSIBILITY_ID, "TODO_last_name_field"),
    "email_field": (AppiumBy.ACCESSIBILITY_ID, "TODO_signup_email_field"),
    "password_field": (AppiumBy.ACCESSIBILITY_ID, "TODO_signup_password_field"),
    "confirm_password_field": (AppiumBy.ACCESSIBILITY_ID, "TODO_confirm_password_field"),
    "signup_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_signup_button"),
    "login_link": (AppiumBy.ACCESSIBILITY_ID, "TODO_signup_login_link"),
    "signup_success_indicator": (AppiumBy.ACCESSIBILITY_ID, "TODO_home_screen_root"),
    "error_message": (AppiumBy.ACCESSIBILITY_ID, "TODO_signup_error_message"),
}

# ---------------------------------------------------------------------------
# Connect Medallion widget (lives on the Home dashboard in this app, not a
# separate screen — see COURSE_SEARCH below, same story)
CONNECT_DEVICE = {
    "connect_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_connect_medallion_button"),
    "connected_indicator": (AppiumBy.ACCESSIBILITY_ID, "TODO_device_connected_label"),
}

# ---------------------------------------------------------------------------
# Course search / selection
# ---------------------------------------------------------------------------
COURSE_SEARCH = {
    "search_field": (AppiumBy.ACCESSIBILITY_ID, "TODO_course_search_field"),
    "result_row_template": (
        AppiumBy.IOS_PREDICATE,
        'label CONTAINS "{course_name}"',
    ),
    "start_round_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_start_round_button"),
}

# ---------------------------------------------------------------------------
# Golf bag / tag pairing screen ("My Golf Bag - Setup your Clubs", reached
# after confirming Start Round)
GOLF_BAG = {
    "club_slot_template": (AppiumBy.IOS_PREDICATE, 'label CONTAINS "{club_name}"'),
    "pair_tag_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_pair_tag_button"),
    "tag_row_template": (AppiumBy.IOS_PREDICATE, 'label CONTAINS "{tag_id}"'),
    "confirm_pair_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_confirm_pair_button"),
    "continue_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_golf_bag_continue_button"),
}

# ---------------------------------------------------------------------------
# Active round screen (satellite map, Live Shot Tracking + Smart Caddie)
# ---------------------------------------------------------------------------
ROUND_ACTIVE = {
    "round_screen_root": (AppiumBy.ACCESSIBILITY_ID, "TODO_round_map_root"),
    "smart_caddie_recommendation": (AppiumBy.ACCESSIBILITY_ID, "TODO_smart_caddie_club_label"),
    "menu_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_round_menu_button"),
    "end_round_option": (AppiumBy.ACCESSIBILITY_ID, "TODO_end_round_menu_item"),
    "end_round_confirm_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_end_round_confirm_button"),
}
