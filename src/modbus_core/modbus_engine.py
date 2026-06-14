"""Адаптер между GUI и ModbusRTU/SerialManager"""

from .serial_manager import SerialManager, ModbusConfig
from .modbus_rtu import ModbusRTU


class ModbusEngine:
    """Упрощённый интерфейс для GUI"""
    
    def __init__(self):
        self.serial_manager = SerialManager()
        self.modbus_rtu = None
        self._connected = False
    
    def connect(self, port: str, baudrate: int) -> bool:
        """Подключение к COM-порту"""
        config = ModbusConfig(port=port, baudrate=baudrate)
        
        if self.serial_manager.connect(config):
            self.modbus_rtu = ModbusRTU(self.serial_manager.serial_port)
            self._connected = True
            return True
        return False
    
    def disconnect(self):
        """Отключение от COM-порта"""
        self.serial_manager.disconnect()
        self.modbus_rtu = None
        self._connected = False
    
    def is_connected(self) -> bool:
        """Проверка подключения"""
        return self._connected and self.serial_manager.is_connected()
    
    def read_registers(self, slave_id: int, address: int, count: int) -> dict:
        """Чтение регистров (команда 03)"""
        if not self.is_connected():
            raise Exception("Нет подключения")
        
        response = self.modbus_rtu.read_holding_registers(slave_id, address, count)
        
        if not response:
            raise Exception("Нет ответа от устройства")
        
        return self.modbus_rtu.parse_read_holding_registers_response(response)
    
    def write_register(self, slave_id: int, address: int, value: int) -> bytes:
        """Запись одного регистра (команда 06)"""
        if not self.is_connected():
            raise Exception("Нет подключения")
        
        return self.modbus_rtu.write_single_register(slave_id, address, value)
    
    def send_raw_packet(self, packet: bytes) -> bytes:
        """Отправка сырого пакета"""
        if not self.is_connected():
            raise Exception("Нет подключения")
        
        self.serial_manager.serial_port.write(packet)
        response = self.serial_manager.serial_port.read(256)
        return response