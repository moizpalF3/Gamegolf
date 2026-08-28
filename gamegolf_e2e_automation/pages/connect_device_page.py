from pages.base_page import BasePage
from locators import CONNECT_DEVICE


class ConnectDevicePage(BasePage):
    def __init__(self, driver, platform):
        super().__init__(driver, platform, CONNECT_DEVICE)

    def connect(self, timeout=30):
        """
        Taps the Connect button and waits for the app to report the medallion
        as connected. Note: the actual Bluetooth pairing/connection happens
        for real between the phone and the physical Medallion device - this
        just drives the UI side and waits for confirmation. The medallion
        must be powered on and in range.
        """
        print("[ConnectDevice] Tapping connect...")
        self.click("connect_button")
        self.find("connected_indicator", timeout=timeout)
        print("[ConnectDevice] Medallion connected")
