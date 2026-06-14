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
        if len(response) < 8: #  что эта цифра? 
            raise ValueError("Modbus: response too short")

        data = response[:-2]
        recv_crc = response[-2:]
        calc_crc = self.crc16(data).to_bytes(2, byteorder="little")

        if recv_crc != calc_crc:
            raise ValueError("Modbus: CRC error")

    # =========================
    # PARSERS
    # =========================
    def _parse_read_holding_registers(self, response: bytes) -> dict:
        self._check_crc(response)

        byte_count = response[2]
        data = response[3:3 + byte_count]

        registers = [
            int.from_bytes(data[i:i+2], byteorder="big")
            for i in range(0, len(data), 2)
        ]

        return {
            "slave_id": response[0],
            "function": response[1],
            "registers": registers,
            "crc": response[-2:],
        }

    def _parse_write_single_register(self, response: bytes) -> dict:
        self._check_crc(response)

        return {
            "slave_id": response[0],
            "function": response[1],
            "address": int.from_bytes(response[2:4], byteorder="big"),
            "value": int.from_bytes(response[4:6], byteorder="big"),
            "crc": response[-2:],
        }

    # =========================
    # PUBLIC API
    # =========================
    def read_holding_registers(self, slave_id: int, address: int, count: int):
        payload = bytearray()
        payload += address.to_bytes(2, byteorder="big")
        payload += count.to_bytes(2, byteorder="big")

        request = self._build_request(slave_id, 0x03, payload)
        response = self._send(request)

        return self._parse_read_holding_registers(response)

    def write_single_register(self, slave_id: int, address: int, value: int):
        payload = bytearray()
        payload += address.to_bytes(2, byteorder="big")
        payload += value.to_bytes(2, byteorder="big")

        request = self._build_request(slave_id, 0x06, payload)
        response = self._send(request)

        return self._parse_write_single_register(response)