from pages.base_page import BasePage
from locators import COURSE_SEARCH


class CourseSearchPage(BasePage):
    def __init__(self, driver, platform):
        super().__init__(driver, platform, COURSE_SEARCH)

    def search_and_select_course(self, course_name):
        print(f"[CourseSearch] Searching for '{course_name}'")
        self.type_text("search_field", course_name)
        self.click_templated("result_row_template", course_name=course_name)
        print(f"[CourseSearch] Selected course '{course_name}'")

    def start_round(self):
        print("[CourseSearch] Tapping Start Round")
        self.click("start_round_button")
