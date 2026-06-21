from serial_core.serial_manage import SerialManager
from serial_core.serial_config import SerialConfig
from modbus_core.modbus_rtu import ModbusRTU


class ModbusController:

    def __init__(self):
        self.serial_manager = SerialManager()
        self.modbus_rtu = None

    # =========================
    # SYSTEM
    # =========================
    @staticmethod
    def scan_serial_ports() -> list:
        return SerialManager.scan_serial_ports()
    
    @staticmethod
    def get_get_default_port() -> str:
        return SerialManager.get_default_port()

    def is_connected(self) -> bool:
        return self.modbus_rtu is not None and self.serial_manager.is_connected()

    def disconnect(self) -> bool:
        ok = self.serial_manager.disconnect()
        self.modbus_rtu = None
        return ok

    # =========================
    # CONNECTION
    # =========================
    def connect(self, config: SerialConfig) -> bool:
        if not isinstance(config, SerialConfig):
            raise TypeError("config must be SerialConfig")

        if not self.serial_manager.connect(config):
            self.modbus_rtu = None
            return False

        self.modbus_rtu = ModbusRTU(self.serial_manager.serial_port)
        return True

    # =========================
    # VALIDATION
    # =========================
    def _ensure_connected(self):
        if not self.modbus_rtu:
            raise RuntimeError("ModbusController: not connected")

    def _validate_slave(self, slave_id: int):
        if not (1 <= slave_id <= 247):
            raise ValueError("Invalid slave_id (1–247)")

    def _validate_address(self, address: int):
        if address < 0 or address > 0xFFFF:
            raise ValueError("Invalid address")

    def _validate_count(self, count: int):
        if count <= 0 or count > 125:
            raise ValueError("Invalid register count")

    def _validate_value(self, value: int):
        if value < 0 or value > 0xFFFF:
            raise ValueError("Invalid register value")

    # =========================
    # API WRAPPERS
    # =========================
    def read_holding_registers(self, slave_id: int, address: int, count: int) -> dict:
        self._ensure_connected()

        self._validate_slave(slave_id)
        self._validate_address(address)
        self._validate_count(count)

        return self.modbus_rtu.read_holding_registers(
            slave_id, address, count
        )

    def write_single_register(self, slave_id: int, address: int, value: int) -> dict:
        self._ensure_connected()

        self._validate_slave(slave_id)
        self._validate_address(address)
        self._validate_value(value)

        return self.modbus_rtu.write_single_register(
            slave_id, address, value
        )

    # =========================
    # OPTIONAL UTILS
    # =========================
    def calculate_crc16(self, data: bytes) -> int:
        return ModbusRTU.crc16(data)
    
    def preview_request(self, slave_id: int, function_code: int, address: int, value_or_count: int) -> bytes:
        self._validate_slave(slave_id)
        self._validate_address(address)

        payload = bytearray()
        payload += address.to_bytes(2, byteorder="big")
        payload += value_or_count.to_bytes(2, byteorder="big")

        request = bytearray()
        request.append(slave_id)
        request.append(function_code)
        request += payload
        
        crc = ModbusRTU.crc16(request)
        request += crc.to_bytes(2, byteorder="little")

        return request.hex(sep=' ').upper()
