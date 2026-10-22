from dataclasses import dataclass, field
from typing import List
from models.enums import ErrorCode, FunctionType


@dataclass
class ProtocolInfo:
    """Metadados e parâmetros operacionais globais do protocolo HID++ 2.0."""
    name: str = "Logitech HID++ 2.0 Draft Specification"
    version: str = "2.0"
    doc_date: str = "2012-06-04"
    short_report_id: str = "0x10"
    long_report_id: str = "0x11"
    endianness: str = "Big-Endian"


@dataclass
class ErrorCodeDefinition:
    """Definição tabular de um código de erro."""
    code: ErrorCode
    name: str
    description: str


@dataclass
class FeatureFunction:
    """Função, evento de difusão ou ASE associado a uma feature."""
    function_id: int
    name: str
    function_type: FunctionType
    description: str
    request_params: str
    response_results: str


@dataclass
class Feature:
    """Feature HID++ 2.0 com a sua coleção de funções suportadas."""
    feature_id: str
    name: str
    description: str
    functions: List[FeatureFunction] = field(default_factory=list)


@dataclass
class SpecialControlID:
    """Control ID físico para teclas especiais e botões multimédia (Feature 0x1B00)."""
    control_id: int
    control_id_hex: str
    description: str
    hid_mapping: str
    suggested_task_id: int


@dataclass
class ControlTask:
    """Ação/tarefa atribuível a um botão ou tecla multimédia."""
    task_id: int
    name: str
    description: str


@dataclass
class HIDMessage:
    # Byte 0: 0x11 (beginning of the message)
    # Byte 1: Device Index
    # Byte 2: Feature Index
    # Byte 3: Function ID
    # Others: Params
    feature_idx: int
    function_idx: int
    parameters: bytes
