from enum import Enum, IntEnum

class ErrorCode(IntEnum):
    """Códigos de erro padronizados do protocolo HID++ 2.0."""
    NO_ERROR = 0
    UNKNOWN = 1
    INVALID_ARGUMENT = 2
    OUT_OF_RANGE = 3
    HW_ERROR = 4
    LOGITECH_INTERNAL = 5
    INVALID_FEATURE_INDEX = 6
    INVALID_FUNCTION_ID = 7
    BUSY = 8
    UNSUPPORTED = 9


class DeviceType(IntEnum):
    """Classificação de tipos de dispositivos."""
    KEYBOARD = 0
    REMOTE_CONTROL = 1
    NUMPAD = 2
    MOUSE = 3
    TOUCHPAD = 4
    TRACKBALL = 5
    PRESENTER = 6
    RECEIVER = 7


class FirmwareType(IntEnum):
    """Entidades de firmware e hardware suportadas."""
    MAIN_APPLICATION = 0
    BOOTLOADER = 1
    HARDWARE = 2
    OTHER = 3


class BatteryStatus(IntEnum):
    """Estados de descarga e carregamento da bateria."""
    DISCHARGING = 0
    RECHARGING = 1
    CHARGE_IN_FINAL_STAGE = 2
    CHARGE_COMPLETE = 3
    RECHARGING_BELOW_OPTIMAL_SPEED = 4
    INVALID_BATTERY_TYPE = 5
    THERMAL_ERROR = 6
    OTHER_CHARGING_ERROR = 7


class FunctionType(str, Enum):
    """Tipos de mensagens/chamadas no protocolo."""
    FUNCTION = "Function"
    BROADCAST_EVENT = "BroadcastEvent"
    APPLICATION_SPECIFIC_EVENT = "ASE"