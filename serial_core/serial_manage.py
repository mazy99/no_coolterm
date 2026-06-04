import serial
import serial.tools.list_ports

class SerialManager:

    def __init__(self) -> None:
        self.serial_port = None



    @staticmethod
    def scan_serial_ports() -> list:

        '''Получение списка доступных COM-портов на компьютере'''

        ports: list = serial.tools.list_ports.comports()

        return [port.device for port in ports]
    
    @staticmethod
    def get_default_port() -> str | None:

        '''Получение первого доступного COM-порта, если он есть'''

        ports = SerialManager.scan_serial_ports()

        return ports[0] if ports else None
    

    def connect(self, config) -> bool:

        '''Установка соединения с COM-портом на основе переданных параметров конфигурации'''

        try:
            self.serial_port = serial.Serial(
                port=config.port,
                baudrate=config.baudrate,
                bytesize=config.byte_size,
                parity=config.parity,
                stopbits=config.stopbits,
                timeout=config.timeout
            )
            return True

        except serial.SerialException as e:
            self.serial_port = None
            print(f"[ERROR] Connect failed: {e}")
            return False

        except Exception as e:
            self.serial_port = None
            print(f"[ERROR] Unexpected error on connect: {e}")
            return False

    def disconnect(self) -> bool:

        '''Закрытие соединения с COM-портом, если оно установлено'''

        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            
            self.serial_port = None
            return True
        
        except serial.SerialException as e:
            print(f"[ERROR] Disconnect failed: {e}")

    def is_connected(self) -> bool:

        '''Проверка, установлено ли соединение с COM-портом'''
        
        return  self.serial_port  is not None and self.serial_port.is_open




