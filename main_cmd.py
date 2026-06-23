from serial_core.serial_manage import SerialManager
from serial_core.serial_config import SerialConfig
from modbus_core.modbus_rtu import ModbusRTU




def main():
    
        sm = SerialManager()
        serial_config = SerialConfig()

        try:
            active_ports = sm.scan_serial_ports()
            default_port = sm.get_default_port()

            serial_config.port = default_port

            connect_to_port = sm.connect(serial_config)
            is_connected = sm.is_connected()

            print(f"Список активных портов: {active_ports}")
            print(f"Выбор первого порта из списка {default_port}")
            print(f"Подключение порта: {connect_to_port}")
            print(f"Проверка подключения: {is_connected}")

            if is_connected:
                modbus = ModbusRTU(sm.serial_port)

                response = modbus.write_single_register(
                    slave_id=17,
                    address=8,
                    value=1
                )

                print(f"Отправка сообщения: {response}")

                read = modbus.read_holding_registers(
                    slave_id=17,
                    address=8,
                    count=1
                )


                # print(read)
                print(f"Считывание ответа: {read}")

        finally:
            print("Отключение от порта...")
            sm.disconnect()
            print("Отключение завершено.")

if __name__ == "__main__":

    main()