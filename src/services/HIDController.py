from typing import List, Optional
from easyhid import Enumeration, HIDDevice
import time
from loguru import logger
from models.protocol import HIDMessage

# Brand
LOGITECH_VID = 0x046D

# protocol
PROTOCOL_HID_USAGE_PAGE = 0XFF00
PROTOCOL_MOUSE_INTERFACE_NUMBER = 2

# feature IDs
FEATURE_ROOT = 0x0000            # IRoot
FEATURE_FEATURE_SET = 0x0001     # IFeatureSet
FEATURE_DEVICE_NAME = 0x0005     # GetDeviceName
FEATURE_DEVICE_NAME_TYPE = 0x0005     # GetDeviceNameType
FEATURE_BATTERY = 0x1004         # Unified Battery
FEATURE_ADJUSTABLE_DPI = 0x2202  # Extended Adjustable DPI
FEATURE_REPORT_RATE = 0x8061     # Extended Adjustable Report Rate
FEATURE_ONBOARD_PROFILES = 0x8100  # Onboard Profiles Memory


class HIDController():

    @staticmethod
    def send_hidpp(device: HIDDevice, message: HIDMessage, timeout_ms: int = 1000) -> Optional[list]:
        """Send the HID messages"""

        if not device:
            logger.error("No device connected")
            return None

        cmd = [0x11, device.device_index, message.feature_idx,
               (message.function_idx << 4) & 0xF0] + [0x00] * 16
        for i, b in enumerate(message.parameters):
            cmd[4 + i] = b

        device.write(cmd)
        logger.log(f"Wrote {cmd} in {device.product_string}")
        time.sleep(0.02)
        return device.read(timeout=timeout_ms)

    @staticmethod
    def get_feature_index(device: HIDDevice, target_feature_id: int) -> Optional[int]:
        """
        Searchs for a feature index based on the id

        Returns:
            None: Mouse doesn't support the feature
            int: Index of the feature
        """
        msb = (target_feature_id >> 8) & 0xFF
        lsb = target_feature_id & 0xFF

        resp = HIDController.send_hidpp(
            device=device,
            message=HIDMessage
        )

        if not resp or len(resp) < 7:
            logger.error("Feature not supported")
            return None

        feat_index = resp[4]
        return feat_index if feat_index != 0 else None

    @staticmethod
    def get_device_type(device: HIDDevice):
        resp_type = HIDController.get_feature_index(
            device=device, target_feature_id=FEATURE_DEVICE_NAME_TYPE)

        if not resp_type:
            logger.error("Feature not supported")
            return
        return resp_type

    @staticmethod
    def get_logitech_devices() -> List[HIDDevice]:
        logitech_devices: List[HIDDevice] = Enumeration().find(
            vid=LOGITECH_VID)

        print(f"NOME\tID\n")
        for ld in logitech_devices:
            print(f"{ld.product_string}\t{ld.product_id}\n")
        return logitech_devices
