import time
from typing import Dict, List, Optional
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

    device_index: Optional[int]
    device_name: Optional[str]
    device_handler: Optional[HIDDevice]

    def __init__(self, device_handler: Optional[HIDDevice] = None):
        self.device_handler = device_handler
        self.device_index = None
        self.device_name = None

    def send_cmd(
        self,
        feature_idx: int,
        func_idx: int,
        params: bytes = b"",
    ) -> Optional[HIDPPMessage]:
        """
        Sends a 20-byte Long Report (0x11) using easyhid's explicit report_id argument.
        """
        if self.device_index is None:
            logger.error("Cannot send command: device_index is not resolved.")
            return None

        # Pack 19 bytes payload: device_index, feature_index, func/software id, and parameters
        payload = [self.device_index, feature_idx,
                   (func_idx << 4) & 0xF0] + list(params)
        payload = payload + [0x00] * (19 - len(payload))

        try:
            self.device_handler.write(payload, report_id=0x11)
            time.sleep(0.02)
            raw = self.device_handler.read(timeout=150)
            if not raw:
                return None
            return self.parse_hidpp(raw)
        except Exception as e:
            logger.debug(f"Write/Read cycle failed: {e}")
            return None

    def get_feature_index(self, target_feature_id: int) -> Optional[int]:
        """
        Looks up a feature index by querying IRoot (0x0000, func 0).
        """
        msb = (target_feature_id >> 8) & 0xFF
        lsb = target_feature_id & 0xFF

        msg = self.send_cmd(
            feature_idx=FEATURE_ROOT,
            func_idx=0,
            params=bytes([msb, lsb]),
        )

        if not msg or msg.is_error or len(msg.parameters) < 1:
            return None

        feat_idx = msg.parameters[0]
        return feat_idx if feat_idx > 0 else None

    def get_all_features(self) -> Dict[int, int]:
        """
        Enumerates all features supported by this device through IFeatureSet (0x0001).
        Returns a dictionary mapping feature_id to feature_index.
        """
        feature_map: Dict[int, int] = {}

        feat_set_idx = self.get_feature_index(FEATURE_FEATURE_SET)
        if not feat_set_idx:
            return feature_map

        # Func 0: GetCount
        count_msg = self.send_cmd(feature_idx=feat_set_idx, func_idx=0)
        if not count_msg or count_msg.is_error or len(count_msg.parameters) < 1:
            return feature_map

        total_features = count_msg.parameters[0]

        # Func 1: GetFeatureID for each index
        for idx in range(1, total_features + 1):
            feat_msg = self.send_cmd(
                feature_idx=feat_set_idx,
                func_idx=1,
                params=bytes([idx]),
            )
            if feat_msg and not feat_msg.is_error and len(feat_msg.parameters) >= 2:
                feat_id = (feat_msg.parameters[0]
                           << 8) | feat_msg.parameters[1]
                feature_map[feat_id] = idx

        return feature_map

    def get_device_index(self) -> Optional[int]:
        """
        Finds the active device index for this instance's device_handler.
        """
        return self._detect_device_index(self.device_handler)

    def is_mouse_device(self) -> bool:
        """
        Checks if this device is actually a mouse using feature 0x0005 or DPI features.
        """
        if self.device_index is None:
            return False

        # Try device type query via Feature 0x0005 (func 2)
        name_type_idx = self.get_feature_index(FEATURE_DEVICE_NAME_TYPE)
        if name_type_idx:
            msg = self.send_cmd(
                feature_idx=name_type_idx,
                func_idx=2,
            )
            if msg and not msg.is_error and len(msg.parameters) > 0:
                if msg.parameters[0] == DEVICE_TYPE_MOUSE:
                    return True

        # Fallback: check presence of mouse-only sensor features
        has_extended_dpi = self.get_feature_index(FEATURE_EXTENDED_DPI)
        has_adjustable_dpi = self.get_feature_index(FEATURE_ADJUSTABLE_DPI)

        return bool(has_extended_dpi or has_adjustable_dpi)

    def get_device_name(self) -> str:
        """
        Fetches the marketing device name using feature 0x0005.
        """
        name_idx = self.get_feature_index(FEATURE_DEVICE_NAME_TYPE)
        if not name_idx:
            return self.device_handler.product_string or "Logitech Mouse"

        # Func 0: get string length
        len_msg = self.send_cmd(feature_idx=name_idx, func_idx=0)
        if not len_msg or len_msg.is_error or len(len_msg.parameters) < 1:
            return self.device_handler.product_string or "Logitech Mouse"

        name_len = len_msg.parameters[0]

        # Func 1: get string content starting from index 0
        str_msg = self.send_cmd(
            feature_idx=name_idx,
            func_idx=1,
            params=bytes([0]),
        )
        if not str_msg or str_msg.is_error:
            return self.device_handler.product_string or "Logitech Mouse"

        name_bytes = str_msg.parameters[:name_len]
        return name_bytes.decode("utf-8", errors="ignore").strip()

    # -------------------------------------------------------------------------
    # Internal static helpers used for device discovery before instantiation
    # -------------------------------------------------------------------------

    @staticmethod
    def _raw_send(
        device_handler: HIDDevice,
        dev_idx: int,
        feature_idx: int,
        func_idx: int,
        params: bytes = b"",
    ) -> Optional[HIDPPMessage]:
        payload = [dev_idx, feature_idx, (func_idx << 4) & 0xF0] + list(params)
        payload = payload + [0x00] * (19 - len(payload))
        try:
            device_handler.write(payload, report_id=0x11)
            time.sleep(0.02)
            raw = device_handler.read(timeout=150)
            return HIDController.parse_hidpp(raw) if raw else None
        except Exception:
            return None

    @staticmethod
    def _detect_device_index(device_handler: HIDDevice) -> Optional[int]:
        try:
            while device_handler.read(timeout=5):
                pass
        except Exception:
            pass

        # 1 is standard for wireless, 0 for direct USB cable, 2-6 for multi-paired dongles
        candidate_indices = [1, 0, 2, 3, 4, 5, 6]

        for idx in candidate_indices:
            # Query IRoot (0x00) -> GetFeature(0) -> IFeatureSet (0x0001)
            msg = HIDController._raw_send(
                device_handler,
                dev_idx=idx,
                feature_idx=FEATURE_ROOT,
                func_idx=0,
                params=bytes([0x00, 0x01]),
            )
            if msg and not msg.is_error and len(msg.parameters) > 0 and msg.parameters[0] > 0:
                return idx

        return None

    @staticmethod
    def _is_mouse(device_handler: HIDDevice, dev_idx: int) -> bool:
        # Check type via Feature 0x0005
        name_msg = HIDController._raw_send(
            device_handler,
            dev_idx,
            FEATURE_ROOT,
            0,
            bytes([0x00, 0x05]),
        )
        if name_msg and not name_msg.is_error and len(name_msg.parameters) > 0:
            name_idx = name_msg.parameters[0]
            if name_idx > 0:
                type_msg = HIDController._raw_send(
                    device_handler, dev_idx, name_idx, 2)
                if type_msg and not type_msg.is_error and len(type_msg.parameters) > 0:
                    if type_msg.parameters[0] == DEVICE_TYPE_MOUSE:
                        return True

        # Fallback: check DPI feature presence
        dpi_msg = HIDController._raw_send(
            device_handler,
            dev_idx,
            FEATURE_ROOT,
            0,
            bytes([0x22, 0x02]),
        )
        return bool(dpi_msg and not dpi_msg.is_error and len(dpi_msg.parameters) > 0 and dpi_msg.parameters[0] > 0)

    @staticmethod
    def get_logitech_mouses() -> List[HIDDevice]:
        """
        Enumerates connected devices and filters strictly for responsive Logitech mice.
        """
        all_devices: List[HIDDevice] = Enumeration().find(vid=LOGITECH_VID)
        mouse_devices: List[HIDDevice] = []

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
                dev_idx = HIDController._detect_device_index(dev)

                if dev_idx is not None and HIDController._is_mouse(dev, dev_idx):
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
