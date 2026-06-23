class ModbusRTU:

    def __init__(self, serial_port):
        self.serial = serial_port

    # =========================
    # CRC
    # =========================
    @staticmethod
    def crc16(data: bytes) -> int:
        crc = 0xFFFF

        for b in data:
            crc ^= b
            for _ in range(8):
                if crc & 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1

        return crc

    # =========================
    # REQUEST BUILDING
    # =========================
    def _build_request(self, slave_id: int, function: int, payload: bytes) -> bytes:
        request = bytearray()
        request.append(slave_id)
        request.append(function)
        request += payload

        crc = self.crc16(request)
        request += crc.to_bytes(2, byteorder="little")

        return request

    # =========================
    # IO LAYER
    # =========================
    def _send(self, request: bytes) -> bytes:
        self.serial.write(request)

        response = self.serial.read(256)

        if not response:
            raise TimeoutError("Modbus: empty response (timeout)")

        return response

    # =========================
    # VALIDATION
    # =========================
    def _check_crc(self, response: bytes) -> None:
        if len(response) < 4: #  что эта цифра? 
            raise ValueError("Modbus: response too short")

        data = response[:-2]  
        recv_crc = response[-2:]
        calc_crc = self.crc16(data).to_bytes(2, byteorder="little")

        if recv_crc != calc_crc:
            raise ValueError("Modbus: CRC error")

    # =========================
    # PARSERS
    # =========================
    def _parse_read_holding_registers(self, response: bytes) -> hex:
        self._check_crc(response)

        return response.hex(sep=' ')

    def _parse_write_single_register(self, response: bytes) -> hex:
        self._check_crc(response)

        return response.hex(sep=' ')
    
    # =========================
    # PUBLIC API
    # =========================
    def read_holding_registers(self, slave_id: int, address: int, count: int) -> dict:
        payload = bytearray()
        payload += address.to_bytes(2, byteorder="big")
        payload += count.to_bytes(2, byteorder="big")

        request = self._build_request(slave_id, 0x03, payload)
        response = self._send(request)

        return self._parse_read_holding_registers(response)

    def write_single_register(self, slave_id: int, address: int, value: int) -> dict:
        payload = bytearray()
        payload += address.to_bytes(2, byteorder="big")
        payload += value.to_bytes(2, byteorder="big")

        request = self._build_request(slave_id, 0x06, payload)
        response = self._send(request)

        return self._parse_write_single_register(response)