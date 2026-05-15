import serial


class SerialManager:

    def __init__(self) -> None:
        self.serial = None

    def connect(self, config) -> bool:
        try:
            self.serial = serial.Serial(
                port=config.port,
                baudrate=config.baudrate,
                bytesize=config.byte_size,
                parity=config.parity,
                stopbits=config.stopbits,
                timeout=config.timeout
            )
            return True

        except serial.SerialException as e:
            self.serial = None
            print(f"[ERROR] Connect failed: {e}")
            return False

        except Exception as e:
            self.serial = None
            print(f"[ERROR] Unexpected error on connect: {e}")
            return False

    def disconnect(self) -> None:
        try:
            if self.serial and self.serial.is_open:
                self.serial.close()
        except serial.SerialException as e:
            print(f"[ERROR] Disconnect failed: {e}")
        finally:
            self.serial = None

    def send(self, data: bytes) -> bool:
        try:
            if self.serial and self.serial.is_open:
                self.serial.write(data)
                return True
            return False

        except serial.SerialException as e:
            print(f"[ERROR] Send failed: {e}")
            return False

        except Exception as e:
            print(f"[ERROR] Unexpected send error: {e}")
            return False

    def read(self, size: int) -> bytes:
        try:
            if self.serial and self.serial.is_open:
                return self.serial.read(size)
            return b""

        except serial.SerialException as e:
            print(f"[ERROR] Read failed: {e}")
            return b""

    def read_all(self) -> bytes:
        try:
            if self.serial and self.serial.is_open:
                return self.serial.read_all()
            return b""

        except serial.SerialException as e:
            print(f"[ERROR] Read_all failed: {e}")
            return b""

    def is_connected(self) -> bool:
        try:
            return self.serial is not None and self.serial.is_open
        except Exception:
            return False

    def clear_buffers(self) -> None:
        try:
            if self.serial and self.serial.is_open:
                self.serial.reset_input_buffer()
                self.serial.reset_output_buffer()
        except serial.SerialException as e:
            print(f"[ERROR] Clear buffers failed: {e}")


