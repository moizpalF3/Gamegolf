from pages.base_page import BasePage
from locators import COURSE_SEARCH


class CourseSearchPage(BasePage):
    def __init__(self, driver, platform):
        super().__init__(driver, platform, COURSE_SEARCH)

    def search_and_select_course(self, course_name):
        """
        Opens the Search screen, types the course name, and presses Enter to
        trigger the (debounced) search - typing alone does not render
        results. Then taps the matching result, which returns to Home with
        the course selected and "Start Round" revealed.
        """
        print(f"[CourseSearch] Searching for '{course_name}'")
        self.click("search_trigger")
        self.type_text("search_field", course_name)
        self.driver.press_keycode(66)  # ENTER, triggers the debounced search
        self.click_templated("result_row_template", timeout=20, course_name=course_name)
        print(f"[CourseSearch] Selected course '{course_name}'")

    def start_round(self, max_scrolls=4):
        print("[CourseSearch] Scrolling to Start Round")
        # Start Round sits below the fold in a lazily-composed list; Compose
        # doesn't render off-screen items, so scroll it into view first. Home
        # re-renders after a course is picked, which can undo a single early
        # scroll, so keep scrolling until the button is actually there.
        for _ in range(max_scrolls):
            if self.is_visible("start_round_button", timeout=3):
                break
            self.driver.execute_script("mobile: scrollGesture", {
                "left": 100, "top": 500, "width": 800, "height": 1500,
                "direction": "down", "percent": 3.0,
            })
        print("[CourseSearch] Tapping Start Round")
        self.click("start_round_button")
        self.click("start_round_confirm_button")
        print("[CourseSearch] Confirmed Start Round")
