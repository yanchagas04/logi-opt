from typing import Dict, List, Optional
from easyhid import Enumeration, HIDDevice
from loguru import logger
from services.HIDController import LOGITECH_VID, PROTOCOL_HID_USAGE_PAGE, PROTOCOL_MOUSE_INTERFACE_NUMBER, HIDController


class MouseController():

    device_index: str
    device_name: str
    # feature_map: Dict[int, int]
    device: HIDDevice

    def __init__(self, device_index=1):
        self.device_index = device_index
        self.device_name = "Unknown"
        self.feature_map = {}
        self.device = None

    def get_device_features(self):
        pass

    def connect(self) -> bool:
        """Open the connection with the mouse HID controller"""

        logitech_devices: List[HIDDevice] = HIDController.get_logitech_devices(
        )

        if len(logitech_devices) == 0:
            logger.error("No logitech mouse was detected")
            return False

        device_list = [dev for dev in logitech_devices if dev.usage_page ==
                       PROTOCOL_HID_USAGE_PAGE or dev.interface_number == PROTOCOL_MOUSE_INTERFACE_NUMBER]
        for i, dev in enumerate(device_list):
            print(f"{i} - {dev.product_string}")
        chosen = int(input("Select device to connect: "))

        self.device = device_list[chosen]

        if not self.device:
            logger.error("No logitech mouse was detected")

        self.device.open()
        self.device_name = self.device.product_string

        logger.success(f"Connected to {self.device_name}")
        return True

    def disconnect(self) -> bool:
        """Close the connection with the mouse HID controller"""

        if not self.device:
            return False

        self.device.close()
        logger.success(f"Disconnected from {self.device_name}")
