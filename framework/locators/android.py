"""
Android locators, one dict per screen (used through framework/locators).

Values marked VERIFIED were captured on the staging build
(org.gameyourgame.kzn.dev) on a real device. Anything marked TODO_ or
NOT YET VERIFIED is still a placeholder.

The app's UI is Jetpack Compose: controls have no resource-id and usually no
content-desc, so most locators use AppiumBy.ANDROID_UIAUTOMATOR text matches
or XPath against the visible label. This breaks if the copy changes; switch
to resource-id locators if the app adds Modifier.testTag with
testTagsAsResourceId = true.

To find a locator: `adb shell uiautomator dump`, or Appium Inspector attached
to a running session.
"""

from appium.webdriver.common.appiumby import AppiumBy


# ---------------------------------------------------------------------------
# Login / Sign up screen
# ---------------------------------------------------------------------------
LOGIN = {
    # VERIFIED 2026-10-25. Logged out, the app opens on an entry screen
    # with two buttons: "Sign In" (opens the Log In form) and "Sign Up
    # With Email" (opens the sign-up form; see SIGNUP).
    "sign_in_entry_button": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Sign In")',
    ),
    "signup_entry_button": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Sign Up With Email")',
    ),
    # VERIFIED: Log In form fields are EditTexts holding their label
    # ("Email Address" / "Password") as a child TextView.
    "email_field": (
        AppiumBy.XPATH,
        '//android.widget.EditText[.//android.widget.TextView[@text="Email Address"]]',
    ),
    "password_field": (
        AppiumBy.XPATH,
        '//android.widget.EditText[.//android.widget.TextView[@text="Password"]]',
    ),
    # VERIFIED: the clickable container around the "Log In" button label
    # (the screen title also reads "Log In", but isn't clickable). It is
    # disabled (enabled="false") until both fields have text.
    "login_button": (
        AppiumBy.XPATH,
        '//android.view.View[@clickable="true"][./android.widget.TextView[@text="Log In"]]',
    ),
    # VERIFIED: "Login Unsuccessful" dialog shown for wrong credentials,
    # with the message "Please check your credentials and try again" and a
    # "Try again" button that closes it.
    "error_message": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("check your credentials")',
    ),
    "error_title": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Login Unsuccessful")',
    ),
    "error_dismiss_button": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Try again")',
    ),
    # VERIFIED: back arrow at the top left of the Log In and sign-up forms
    # (the first clickable element); leads to the entry screen.
    "back_button": (
        AppiumBy.XPATH,
        '(//android.view.View[@clickable="true"])[1]',
    ),
    # Same as SIGNUP's form_title; used to tell the sign-up form apart
    # from the Log In form (both have an "Email Address" field).
    "signup_form_title": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("create your")',
    ),
    # VERIFIED: signing out is My Profile tab -> "Sign Out" -> "Sign Out!
    # Are you sure?" dialog -> "Confirm". It ends on the Log In form.
    "profile_tab": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("My Profile")',
    ),
    "sign_out_button": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Sign Out")',
    ),
    "sign_out_confirm_button": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Confirm")',
    ),
    # VERIFIED: "My Golf Bag" appears on the post-login home dashboard
    # (org.gameyourgame.kzn.presentation.main.MainActivity).
    "logged_in_indicator": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("My Golf Bag")',
    ),
    # VERIFIED: bottom navigation tab that opens the Home dashboard. The
    # app reopens on whichever tab was last used (e.g. My Rounds after a
    # round is ended), so tests tap this to get back to Home.
    "home_tab": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Play Golf")',
    ),
}

# ---------------------------------------------------------------------------
# Sign up screen
# ---------------------------------------------------------------------------
SIGNUP = {
    # VERIFIED 2026-10-25: "Let's create your new account!" form, reached
    # from the entry screen's "Sign Up With Email". Fields are EditTexts
    # holding their label as a child TextView. There is no confirm-
    # password field.
    "form_title": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("create your")',
    ),
    "first_name_field": (
        AppiumBy.XPATH,
        '//android.widget.EditText[.//android.widget.TextView[@text="First Name"]]',
    ),
    "last_name_field": (
        AppiumBy.XPATH,
        '//android.widget.EditText[.//android.widget.TextView[@text="Last Name"]]',
    ),
    "email_field": (
        AppiumBy.XPATH,
        '//android.widget.EditText[.//android.widget.TextView[@text="Email Address"]]',
    ),
    "password_field": (
        AppiumBy.XPATH,
        '//android.widget.EditText[.//android.widget.TextView[@text="Password"]]',
    ),
    # VERIFIED: the checkbox is an unlabelled clickable View next to the
    # "I agree to GameGolf's Terms & Conditions" text (its following
    # sibling).
    "terms_checkbox": (
        AppiumBy.XPATH,
        '//android.widget.TextView[contains(@text, "Terms & Conditions")]'
        '/following-sibling::android.view.View[@clickable="true"][1]',
    ),
    # VERIFIED: clickable container around the "Continue" label; disabled
    # until every field is filled and the terms are accepted.
    "signup_button": (
        AppiumBy.XPATH,
        '//android.view.View[@clickable="true"][./android.widget.TextView[@text="Continue"]]',
    ),
    # VERIFIED: an already registered email shows a "Registration
    # Unsuccessful" dialog with the message "Email already exists" and a
    # "Try again" button.
    "error_message": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("already exists")',
    ),
    "error_title": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Registration Unsuccessful")',
    ),
    # VERIFIED: after a successful sign-up the new account lands on the
    # onboarding screen ("Set up your device ... Swipe to Continue").
    "onboarding_screen": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("Set up your device")',
    ),
    # VERIFIED: swiping up on the onboarding screen shows a 3-step set-up
    # guide (Charge GPS Tracker / Screw in Smart Sensors / Connect One by
    # One) with two buttons: "Start Setup" (the "I have a device" path,
    # leading to the golf bag screen with SKIP) and "Don't have a Device"
    # (written with a curly apostrophe, hence "don.t").
    "have_device_button": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Start Setup")',
    ),
    "dont_have_device_button": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textMatches("(?i)don.t have a device")',
    ),
    "skip_button": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textMatches("(?i) *skip *")',
    ),
}

# ---------------------------------------------------------------------------
# Connect Medallion widget (lives on the Home dashboard in this app, not a
# separate screen — see COURSE_SEARCH below, same story)
# ---------------------------------------------------------------------------
CONNECT_DEVICE = {
    # VERIFIED: "Connect" button next to the "GPS Tracker" label on Home.
    # Exact text: once connected the same spot reads "Connected", which
    # textContains("Connect") would also match.
    "connect_button": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Connect").className("android.widget.TextView")',
    ),
    # VERIFIED: Home's "GPS Tracker" widget reads "Connected" while the
    # Medallion is connected (e.g. still connected from a previous run).
    "connected_label": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Connected")',
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
    # VERIFIED to exist (generic class match — Compose gives it no id/
    # content-desc — so this could match other EditTexts if the screen
    # changes; scope it further if that becomes a problem).
    "search_field": (AppiumBy.CLASS_NAME, "android.widget.EditText"),
    # VERIFIED: opens the Search screen from Home. Uses the box's
    # "Search Location" label, which is always shown; the placeholder
    # "Choose your golf course" is replaced by the course name once one
    # has been selected (e.g. by a previous run).
    "search_trigger": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Search Location")',
    ),
    # VERIFIED: matches a course row both in "Nearby Courses" on Home
    # and (presumably) in real search results, by visible text. Limited
    # to TextView: the search box (an EditText) holds the same text, and
    # matching it taps the box instead of the result.
    "result_row_template": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.TextView").textContains("{course_name}")',
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
    # VERIFIED: once Smart Caddie has loaded, the map shows its
    # recommendation ("Plays Like NNN Mtr / Actual NNN Mtr / Club 2W") and
    # the bottom-left loader is replaced by a strategy selector reading
    # "Optimal". The recommendation is drawn on the map and isn't in the
    # element tree, so the strategy selector is what's checked. If Smart
    # Caddie was calculated recently it can show straight away, without
    # the loader.
    "smart_caddie_loaded": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Optimal")',
    ),
    # The Smart Caddie loader (bottom left) shows its progress as
    # "Loading NN%"; matches any text with a percentage in it.
    # VERIFIED: the arrows either side of "Hole: N Score: N" in the bottom
    # bar (content-desc "Previous Hole" / "Next Hole").
    "previous_hole_button": (AppiumBy.ACCESSIBILITY_ID, "Previous Hole"),
    "next_hole_button": (AppiumBy.ACCESSIBILITY_ID, "Next Hole"),
    # VERIFIED: dialog shown on Home when a round was left open
    # ("Unfinished Round - It seems there is an unfinished round. Would
    # you like to continue?" / "Continue Round" / "Create New Round").
    "unfinished_round_dialog": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("unfinished round")',
    ),
    "continue_round_button": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Continue Round")',
    ),
    # VERIFIED: error dialog the app sometimes shows when ending a round
    # ("Ops! An unexpected error occurred. Please certify that your device
    # is connected with internet and try again." / Cancel / Confirm).
    # Its "Confirm" retries; end_round_confirm_button matches that too.
    "end_round_error": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("unexpected error occurred")',
    ),
    "smart_caddie_progress": (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textMatches(".*[0-9]+ ?%.*")',
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
}
