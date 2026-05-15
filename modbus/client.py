from  pymodbus.client import ModbusSerialClient 

class ModbusClient:

    def __init__(self,  port, baudrate, parity, bytesize, stopbits, timeout):
        self.client = ModbusSerialClient (
            port=port, 
            baudrate=baudrate, 
            parity=parity,
            bytesize=bytesize,
            stopbits=stopbits,
            timeout=timeout,
        )


    def connect(self):
        return self.client.connect()
    
    def disconnect(self):
        return self.client.close()

    # Modbus functions 0x03
    def read_holding_registers(self, address, count, slave_id):

        try:
            response = self.client.read_holding_registers(
                address=address,
                count=count,
                device_id =slave_id
            )

            if response is None or response.isError():
                return None

            return response.registers
    

        except Exception as e:
            print(f"[MODBUS ERROR] {e}")
            return None

    # Modbus functions 0x04
    def read_input_registers(self, address, count, slave_id):

        try:
            response = self.client.read_input_registers(
                address=address,
                count=count,
                device_id =slave_id
            )

            if response is None:
                print("[MODBUS] No response (timeout or device offline)")
                return None

            if response.isError():
                print(f"[MODBUS] Device error: {response}")
                return None

            return response.registers

        except Exception as e:
            print(f"[MODBUS EXCEPTION] {e}")
            return None
        
    def write_register(self, address, value, slave_id):
        return self.client.write_register(address, value, device_id=slave_id)