from dataclasses import dataclass, field
from typing import Optional, List
from models.protocol import Feature

@dataclass
class ButtonMapping:
    """Mapeamento de botões físicos para eventos do kernel Linux e códigos HID."""
    button_key: str
    description: str
    is_programmable: bool
    linux_event: str
    linux_code: int
    msc_scan: Optional[str] = None
    hid_usage: Optional[str] = None


@dataclass
class OnboardDPISlot:
    """Nível de sensibilidade (DPI) armazenado no perfil da memória onboard."""
    slot_number: int
    dpi_value: int
    is_active: bool = False


@dataclass
class ReceiverInfo:
    """Dados de hardware do receptor USB Lightspeed."""
    vendor_id: str = "0x046d"
    product_id: str = "0xC543"
    serial: str = "E8359309"
    device_index: int = 1
    default_hidraw: str = "/dev/hidraw3"


@dataclass
class LogitechDevice:
    """Entidade consolidada contendo hardware, mapeamento e perfis do rato."""
    name: str
    codename: str
    protocol: str
    serial_number: str
    model_id: str
    unit_id: str
    wpid: str
    vendor_id: str
    product_id: str
    receiver: ReceiverInfo
    buttons: List[ButtonMapping] = field(default_factory=list)
    features: List[Feature] = field(default_factory=list)
    dpi_slots: List[OnboardDPISlot] = field(default_factory=list)