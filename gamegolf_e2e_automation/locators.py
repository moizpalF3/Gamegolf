"""
Locators for every screen in the GameGolf app flow.

*** Android values below marked "VERIFIED" were captured live against the
staging build (org.gameyourgame.kzn.dev) on a real device on 2026-09-17.
Everything else (iOS, and anything still marked TODO_) is still a
placeholder and needs filling in from your own app/build. ***

IMPORTANT — this app's UI is built with Jetpack Compose. Compose elements
generally have NO resource-id and usually no content-desc either (a few
decorative icons do, but not the interactive controls), so uiautomator2's
usual resource-id/accessibility-id locators mostly don't apply here. The
working strategy instead is AppiumBy.ANDROID_UIAUTOMATOR with a
`textContains(...)` UiSelector matched against the (visible, non-empty)
TextView label associated with a control, and letting the tap land on the
underlying compose Modifier.clickable region. This is inherently a bit more
fragile than id-based locators (breaks if copy changes), so replace with a
resource-id/testTag-based locator if the dev team ever adds
`Modifier.testTag`/`semantics { testTagsAsResourceId = true }` to the
composables.

How to find real locators:
  Android: run the app, then `adb shell uiautomator dump` and pull the XML,
           or use the Appium Inspector app (https://github.com/appium/appium-inspector)
           connected to your running session. Android locators are usually
           resource-id (e.g. "com.gamegolf.app:id/login_button") or
           accessibility id (contentDescription) — except in Compose screens,
           see above.
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
        # Not yet captured: the live test device was already logged in
        # (persisted session, no_reset=true), so the Welcome/Login screen
        # itself was never reached this pass. Log out first to fill these in.
        "email_field": (AppiumBy.ID, "com.gamegolf.app:id/TODO_email_field"),
        "password_field": (AppiumBy.ID, "com.gamegolf.app:id/TODO_password_field"),
        "login_button": (AppiumBy.ID, "com.gamegolf.app:id/TODO_login_button"),
        "signup_link": (AppiumBy.ID, "com.gamegolf.app:id/TODO_signup_link"),
        # VERIFIED: "My Golf Bag" appears on the post-login home dashboard
        # (org.gameyourgame.kzn.presentation.main.MainActivity).
        "logged_in_indicator": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("My Golf Bag")',
        ),
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
# Connect Medallion widget (lives on the Home dashboard in this app, not a
# separate screen — see COURSE_SEARCH below, same story)
# ---------------------------------------------------------------------------
CONNECT_DEVICE = {
    "android": {
        # VERIFIED: "Connect" button next to the "GPS Tracker" label on Home.
        "connect_button": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("Connect").className("android.widget.TextView")',
        ),
        # VERIFIED: the real connect flow is 3 taps, not 1 — tapping
        # "Connect" opens an instructional screen with a "Find GPS Tracker"
        # button; tapping that runs a real BLE scan and shows a "Choose GPS
        # Tracker" dialog listing found devices (e.g. "GYG Medallion KZN");
        # tapping the device row connects it for real. Once connected, the
        # Home dashboard's "GPS Tracker / Connect" widget is replaced by an
        # "Update Tags" banner, which is what this locator checks for.
        "connected_indicator": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("Update Tags")',
        ),
        # VERIFIED: instructional screen reached after tapping "Connect".
        "find_tracker_button": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("Find GPS Tracker")',
        ),
        # VERIFIED: template for a discovered device row in the "Choose GPS
        # Tracker" dialog; format with the device's advertised name.
        "device_row_template": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("{device_name}")',
        ),
    },
    "ios": {
        "connect_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_connect_medallion_button"),
        "connected_indicator": (AppiumBy.ACCESSIBILITY_ID, "TODO_device_connected_label"),
    },
}

# ---------------------------------------------------------------------------
# Course search / selection
# ---------------------------------------------------------------------------
# Real app note: tapping "Choose your golf course" on Home opens a full-text
# Search screen. Typing alone does NOT trigger results (tried waiting up to
# ~15s with no results rendering) — you must press Enter/the IME search
# action after typing for the debounced search to actually fire and render
# a result row. Once that's done, tapping the result behaves the same as
# tapping a row in "Nearby Courses" on Home: it returns to Home with the
# course selected in the search box and the "Start Round" button revealed.
COURSE_SEARCH = {
    "android": {
        # VERIFIED to exist (generic class match — Compose gives it no id/
        # content-desc — so this could match other EditTexts if the screen
        # changes; scope it further if that becomes a problem).
        "search_field": (AppiumBy.CLASS_NAME, "android.widget.EditText"),
        # VERIFIED: opens the Search screen from Home.
        "search_trigger": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("Choose your golf course")',
        ),
        # VERIFIED: matches a course row both in "Nearby Courses" on Home
        # and (presumably) in real search results, by visible text.
        "result_row_template": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("{course_name}")',
        ),
        # VERIFIED: renders disabled/greyed out until the Medallion is
        # connected (confirmed by connecting a real one and watching this
        # turn active/red — untested whether tapping it while disabled
        # throws or no-ops). It's below the fold on the Home dashboard's
        # lazy-rendered list, so scroll it into view before tapping —
        # Compose only composes visible list items, so a find() for
        # off-screen text fails as if the element doesn't exist.
        "start_round_button": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("Start Round")',
        ),
        # VERIFIED: tapping start_round_button opens a "Start Live Round?"
        # confirmation dialog with this button.
        "start_round_confirm_button": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("Yes, Start round")',
        ),
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
# Golf bag / tag pairing screen ("My Golf Bag - Setup your Clubs", reached
# after confirming Start Round)
# ---------------------------------------------------------------------------
# Real app note: this screen is a grid of club-type chips (Driver, Wood x4,
# Iron x6, Hybrid x4, Wedge x4, Putter), each either a solid colored circle
# with the loft label (e.g. "D", "2W", "8I", "P") if a tag is already paired
# to it, or a grey circle with a "+" badge if not. club_slot_template/
# pair_tag_button/tag_row_template/confirm_pair_button below are UNVERIFIED
# placeholders — this pass only exercised an already-fully-paired bag (all 4
# tags pre-paired from a prior session), so pairing a *new* tag by tapping a
# "+" chip was never actually driven. Re-verify against a real "+" tap and a
# BLE tag scan dialog before trusting pair_club()/pair_all_clubs().
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
        # VERIFIED: "Continue" button at the bottom of the Golf Bag screen.
        "continue_button": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("Continue")',
        ),
        # VERIFIED: header text reading e.g. "4/14 Clubs Connected".
        "clubs_connected_header": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("Clubs Connected")',
        ),
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
# Active round screen (satellite map, Live Shot Tracking + Smart Caddie)
# ---------------------------------------------------------------------------
# Real app note: after Golf Bag's Continue, this screen shows a Google
# satellite map with the flag/tee/ball markers, a "Smart Caddie" widget
# (shows "Loading NN%" then presumably a club recommendation once ready —
# only the loading state was observed this pass, so
# smart_caddie_recommendation below still targets the generic widget text,
# not a specific recommended-club value), and a bottom bar with
# "Hole: N  Score: N" / "Par: N Stroke: N". Confirmed working end-to-end:
# real GPS movement (nmea fake_coordinates) and shots (storage_service_v2
# shot_add) sent over the Medallion's USB serial CLI show up live on this
# map and update the score, including auto-advancing hole-to-hole.
# menu_button/end_round_* below are VERIFIED end-to-end (a real round was
# started, played through 3 holes, and cleanly ended this way): the 3-dot
# menu button is a red circular icon with no text/resource-id/content-desc,
# so it's addressed by relative screen position (see menu_button_relative)
# rather than a normal locator. Tapping it opens a "More Options" bottom
# sheet with "Sync Shots" / "Tee Position" / "End Round" / "Satellite Maps".
# Tapping "End Round" opens an "Exit? Do you want to end your game?" dialog
# with "Cancel" / "Confirm" buttons.
ROUND_ACTIVE = {
    "android": {
        # VERIFIED: the bottom status bar always shows "Score:" while a
        # round is active.
        "round_screen_root": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("Score:")',
        ),
        # PARTIALLY VERIFIED: matches the "Smart Caddie" widget while it's
        # still loading; not confirmed against an actual loaded recommendation.
        "smart_caddie_recommendation": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("Smart Caddie")',
        ),
        # VERIFIED (from a saved page dump): the bottom bar renders "Hole:",
        # its number, "Score:" and its number as four separate sibling
        # TextViews, so each value is the label's next sibling.
        "hole_number_value": (
            AppiumBy.XPATH,
            '//android.widget.TextView[@text="Hole:"]/following-sibling::android.widget.TextView[1]',
        ),
        "score_value": (
            AppiumBy.XPATH,
            '//android.widget.TextView[@text="Score:"]/following-sibling::android.widget.TextView[1]',
        ),
        # VERIFIED but fragile: (x_pct, y_pct) of the 3-dot menu button,
        # captured on a 1080x2400 device. Use with BasePage.tap_relative();
        # not a (By, value) tuple like other locators, so don't pass this to
        # click()/find(). Re-measure if this ever stops landing on the button
        # (different aspect ratio, redesigned layout, etc.).
        "menu_button_relative": (0.8875, 0.7619),
        # VERIFIED: item in the "More Options" bottom sheet opened by the menu.
        "end_round_option": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("End Round")',
        ),
        # VERIFIED: button in the "Exit? Do you want to end your game?" dialog.
        "end_round_confirm_button": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().text("Confirm")',
        ),
    },
    "ios": {
        "round_screen_root": (AppiumBy.ACCESSIBILITY_ID, "TODO_round_map_root"),
        "smart_caddie_recommendation": (AppiumBy.ACCESSIBILITY_ID, "TODO_smart_caddie_club_label"),
        "menu_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_round_menu_button"),
        "end_round_option": (AppiumBy.ACCESSIBILITY_ID, "TODO_end_round_menu_item"),
        "end_round_confirm_button": (AppiumBy.ACCESSIBILITY_ID, "TODO_end_round_confirm_button"),
    },
}
