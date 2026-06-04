

class ModbusRTU:
    

    def __init__(self, serial_port):
        self.serial = serial_port

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
    
    def read_holding_registers(self, slave_id: int, address: int, count: int):

        request = bytearray()
        request.append(slave_id)
        request.append(0x03)
        request += address.to_bytes(2, byteorder="big")
        request += count.to_bytes(2, byteorder="big")

        crc = self.crc16(request)
        request += crc.to_bytes(2, byteorder="little")
        self.serial.write(request)
        response = self.serial.read(256)


        return response

    def write_single_register(
        self,
        slave_id: int,
        address: int,
        value: int
    ):

        request = bytearray()

        request.append(slave_id)
        request.append(0x06)

        request += address.to_bytes(2, byteorder="big")
        request += value.to_bytes(2, byteorder="big")

        crc = self.crc16(request)

        request += crc.to_bytes(2, byteorder="little")

        self.serial.write(request)

        response = self.serial.read(256)

        return response

    
    def parse_read_holding_registers_response(self, response: bytes):

        if len(response) < 5:
            raise ValueError("Response too short")

        data_without_crc = response[:-2]

        crc_received = response[-2:]

        crc_calculated = self.crc16(data_without_crc)

        crc_calculated_bytes = crc_calculated.to_bytes(
            2,
            byteorder="little"
        )

        if crc_received != crc_calculated_bytes:
            raise ValueError("CRC ERROR")

        slave_id = response[0]

        function_code = response[1]

        byte_count = response[2]

        data = response[3:3 + byte_count]

        registers = []

        for i in range(0, len(data), 2):

            value = int.from_bytes(
                data[i:i+2],
                byteorder="big"
            )

            registers.append(value)

        return {
            "slave_id": slave_id,
            "function": function_code,
            "registers": registers
        }