from dataclasses import dataclass, field
from serial_core.serial_manage import SerialManager


@dataclass
class SerialConfig:
    sm: SerialManager = field(default_factory=SerialManager)

    port: str | None = field(default=None)

    baudrate: int = 9600

    byte_size: int = 8

    parity: str = "N"

    stopbits: int = 1

    timeout: float = 1.0
