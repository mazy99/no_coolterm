
from serial_core.serial_config import SerialConfig
from modbus_core.modbus_controller import ModbusController



def main():

    try:
        mc = ModbusController()

        serial_port = mc.get_get_default_port()

        sc = SerialConfig(port=serial_port)
        
        connect = mc.connect(config=sc)

        slave_id = 17

        address = 0

        count = 2

        print(f"serial config: {sc}")

        print(f"Реузльтат подлкючения: {connect}")

        is_connected = mc.is_connected()

        request = mc.preview_request(slave_id=slave_id, function_code=0x03, address=address, value_or_count=count)

        print(f"Предварительный запрос: {request}")

        if is_connected:
            response = mc.read_holding_registers(slave_id,address,count)
            print(f"Результат чтения: {response}")
    
    finally:
            disconnect = mc.disconnect()
            print(f"Результат подключения после вызова функции отлкючения: {mc.is_connected()}")



if __name__ == "__main__":
    main()