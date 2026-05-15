from dataclasses import dataclass

@dataclass
class SerialConfig:
    port: str = 'COM1'

    baudrate: int = 9600

    byte_size: int = 8

    parity: str = 'N'

    stopbits: int = 1

    timeout: float = 1.0