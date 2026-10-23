from pages.base_page import BasePage
from locators import CONNECT_DEVICE


class ConnectDevicePage(BasePage):
    def __init__(self, driver, platform):
        super().__init__(driver, platform, CONNECT_DEVICE)

    def connect(self, device_name="GYG Medallion", scan_timeout=20, timeout=30):
        """
        Real flow is 3 taps: "Connect" (Home) -> instructional screen ->
        "Find GPS Tracker" triggers a real BLE scan -> "Choose GPS Tracker"
        dialog lists found devices -> tapping the device row connects it.
        The medallion must be powered on and in range for the scan to find
        it. This drives the UI side; the actual BLE connection happens for
        real against the physical device.
        """
        if self.is_visible("connected_label", timeout=5):
            print("[ConnectDevice] Medallion already connected - skipping connect")
            return
        print("[ConnectDevice] Tapping connect...")
        self.click("connect_button")
        self.click("find_tracker_button")
        print(f"[ConnectDevice] Scanning for '{device_name}'...")
        self.click_templated("device_row_template", timeout=scan_timeout, device_name=device_name)
        self.find("connected_indicator", timeout=timeout)
        print("[ConnectDevice] Medallion connected")
