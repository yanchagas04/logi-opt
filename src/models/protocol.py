from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional

class HIDPPReportType(IntEnum):
    SHORT = 0x10
    LONG = 0x11
    VERY_LONG = 0x12


class HIDPPErrorCode(IntEnum):
    SUCCESS = 0x00
    UNKNOWN = 0x01
    INVALID_ARGUMENT = 0x02
    OUT_OF_RANGE = 0x03
    HW_ERROR = 0x04
    BUSY = 0x05
    INVALID_FEATURE_INDEX = 0x06
    INVALID_FUNCTION_ID = 0x07
    RESOURCE_ERROR = 0x08
    UNAVAILABLE = 0x09


@dataclass(frozen=True)
class HIDPPMessage:
    report_id: int
    device_index: int
    feature_index: int
    function_id: int
    software_id: int
    parameters: bytes
    is_error: bool = False
    error_code: Optional[HIDPPErrorCode] = None
    raw: bytes = field(default=b"", repr=False)
