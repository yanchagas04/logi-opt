import time
from typing import List, Optional
from easyhid import Enumeration, HIDDevice
from loguru import logger
from models.protocol import HIDPPErrorCode, HIDPPMessage

# Brand
LOGITECH_VID = 0x046D

# Protocol & interface IDs
PROTOCOL_HID_USAGE_PAGE = 0xFF00
PROTOCOL_MOUSE_INTERFACE_NUMBER = 2

# Core HID++ Features
FEATURE_ROOT = 0x0000
FEATURE_FEATURE_SET = 0x0001
FEATURE_DEVICE_NAME_TYPE = 0x0005
FEATURE_ADJUSTABLE_DPI = 0x2201
FEATURE_EXTENDED_DPI = 0x2202

DEVICE_TYPE_MOUSE = 3


class HIDController:

    @staticmethod
    def send_cmd(
        device_handler: HIDDevice,
        feature_idx: int,
        func_idx: int,
        dev_idx: int = 1,
        params: bytes = b"",
    ) -> Optional[HIDPPMessage]:
        """
        Sends a 20-byte Long Report (0x11) using easyhid's explicit report_id argument[cite: 2].
        """
        # Pack 19 bytes payload: dev_index, feature_index, func/software id, and parameters[cite: 2]
        payload = [dev_idx, feature_idx, (func_idx << 4) & 0xF0] + list(params)
        payload = payload + [0x00] * (19 - len(payload))

        try:
            device_handler.write(payload, report_id=0x11)
            time.sleep(0.02)
            raw = device_handler.read(timeout=150)
            if not raw:
                return None
            return HIDController.parse_hidpp(raw)
        except Exception as e:
            logger.debug(f"Write/Read cycle failed: {e}")
            return None

    @staticmethod
    def get_feature_index(device_handler: HIDDevice, dev_idx: int, target_feature_id: int) -> Optional[int]:
        """
        Looks up a feature index by querying IRoot (0x0000, func 0).
        """
        msb = (target_feature_id >> 8) & 0xFF
        lsb = target_feature_id & 0xFF

        msg = HIDController.send_cmd(
            device_handler=device_handler,
            feature_idx=0x00,
            func_idx=0,
            dev_idx=dev_idx,
            params=bytes([msb, lsb]),
        )

        if not msg or msg.is_error or len(msg.parameters) < 1:
            return None

        # Feature index is placed at the first parameter byte
        feat_idx = msg.parameters[0]
        return feat_idx if feat_idx > 0 else None

    @staticmethod
    def get_device_index(device_handler: HIDDevice) -> Optional[int]:
        """
        Finds the active device index by querying IFeatureSet (0x0001) through IRoot.
        """
        try:
            while device_handler.read(timeout=5):
                pass
        except Exception:
            pass

        # 1 is standard for wireless, 0 for direct USB cable, 2-6 for multi-paired dongles[cite: 2]
        candidate_indices = [1, 0, 2, 3, 4, 5, 6]

        for idx in candidate_indices:
            feat_set_idx = HIDController.get_feature_index(
                device_handler, idx, FEATURE_FEATURE_SET)
            if feat_set_idx is not None:
                return idx

        return None

    @staticmethod
    def is_mouse_device(device_handler: HIDDevice, dev_idx: int) -> bool:
        """
        Checks if the device at dev_idx is actually a mouse using feature 0x0005 or DPI features.
        """
        # Try device type query via Feature 0x0005 (func 2)
        name_type_idx = HIDController.get_feature_index(
            device_handler, dev_idx, FEATURE_DEVICE_NAME_TYPE)
        if name_type_idx:
            msg = HIDController.send_cmd(
                device_handler=device_handler,
                feature_idx=name_type_idx,
                func_idx=2,
                dev_idx=dev_idx,
            )
            if msg and not msg.is_error and len(msg.parameters) > 0:
                if msg.parameters[0] == DEVICE_TYPE_MOUSE:
                    return True

        # Fallback: check presence of mouse-only sensor features
        has_extended_dpi = HIDController.get_feature_index(
            device_handler, dev_idx, FEATURE_EXTENDED_DPI)
        has_adjustable_dpi = HIDController.get_feature_index(
            device_handler, dev_idx, FEATURE_ADJUSTABLE_DPI)

        return bool(has_extended_dpi or has_adjustable_dpi)

    @staticmethod
    def get_device_name(device_handler: HIDDevice, dev_idx: int) -> str:
        """
        Fetches the marketing device name using feature 0x0005.
        """
        name_idx = HIDController.get_feature_index(
            device_handler, dev_idx, FEATURE_DEVICE_NAME_TYPE)
        if not name_idx:
            return device_handler.product_string or "Logitech Mouse"

        # Func 0: get string length
        len_msg = HIDController.send_cmd(
            device_handler, feature_idx=name_idx, func_idx=0, dev_idx=dev_idx)
        if not len_msg or len_msg.is_error or len(len_msg.parameters) < 1:
            return device_handler.product_string or "Logitech Mouse"

        name_len = len_msg.parameters[0]

        # Func 1: get string content starting from index 0
        str_msg = HIDController.send_cmd(
            device_handler,
            feature_idx=name_idx,
            func_idx=1,
            dev_idx=dev_idx,
            params=bytes([0]),
        )
        if not str_msg or str_msg.is_error:
            return device_handler.product_string or "Logitech Mouse"

        name_bytes = str_msg.parameters[:name_len]
        return name_bytes.decode("utf-8", errors="ignore").strip()

    @staticmethod
    def get_logitech_devices() -> List[HIDDevice]:
        """
        Enumerates connected devices and filters strictly for responsive Logitech mice.
        """
        all_devices: List[HIDDevice] = Enumeration().find(vid=LOGITECH_VID)
        mouse_devices: List[HIDDevice] = []

        # Filter nodes bound to control interface (Vendor Specific or Interface 2)
        candidates = [
            dev for dev in all_devices
            if dev.usage_page == PROTOCOL_HID_USAGE_PAGE or dev.interface_number == PROTOCOL_MOUSE_INTERFACE_NUMBER
        ]

        seen_paths = set()

        for dev in candidates:
            if dev.path in seen_paths:
                continue

            try:
                dev.open()
                dev_idx = HIDController.get_device_index(dev)

                if dev_idx is not None and HIDController.is_mouse_device(dev, dev_idx):
                    mouse_devices.append(dev)
                    seen_paths.add(dev.path)
            except Exception:
                pass
            finally:
                dev.close()

        return mouse_devices

    @staticmethod
    def parse_hidpp(resp: List[int]) -> Optional[HIDPPMessage]:
        """
        Parses raw bytes into a structured HIDPPMessage model.
        """
        if not resp or len(resp) < 4:
            return None

        report_id = resp[0]
        dev_idx = resp[1]
        feature_idx = resp[2]

        # Handle formal HID++ error response (0x8F)
        if feature_idx == 0x8F:
            failed_feature = resp[3]
            func_and_sw = resp[4] if len(resp) > 4 else 0
            err_byte = resp[5] if len(resp) > 5 else 0x01

            try:
                err_enum = HIDPPErrorCode(err_byte)
            except ValueError:
                err_enum = HIDPPErrorCode.UNKNOWN

            return HIDPPMessage(
                report_id=report_id,
                device_index=dev_idx,
                feature_index=failed_feature,
                function_id=(func_and_sw >> 4) & 0x0F,
                software_id=func_and_sw & 0x0F,
                parameters=bytes(resp[5:]),
                is_error=True,
                error_code=err_enum,
                raw=bytes(resp),
            )

        # Standard message parsing
        func_and_sw = resp[3]
        func_id = (func_and_sw >> 4) & 0x0F
        software_id = func_and_sw & 0x0F

        if report_id == 0x10:
            params = resp[4:7]
        elif report_id == 0x11:
            params = resp[4:20]
        else:
            params = resp[4:]

        return HIDPPMessage(
            report_id=report_id,
            device_index=dev_idx,
            feature_index=feature_idx,
            function_id=func_id,
            software_id=software_id,
            parameters=bytes(params),
            is_error=False,
            error_code=None,
            raw=bytes(resp),
        )
