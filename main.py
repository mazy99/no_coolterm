from serial_core.port_scanner import scan_serial_ports
from modbus.client import ModbusClient


if __name__ == "__main__":
    active_ports = scan_serial_ports()
    print("Ports:", active_ports)
    if not active_ports:
        print("No COM ports found")
        exit()

    modbus_client = ModbusClient(
            port=active_ports[0],
            baudrate=9600,
            parity = 'N',
            bytesize = 8,
            stopbits = 1,

            timeout=1,
        )
    
    connected = modbus_client.connect()
    print("Connected:", connected)

  
    # data_write = modbus_client.write_register(address=1, value=255,  slave_id=161)
    data_read = modbus_client.read_holding_registers(address=1, count=8, slave_id=161)
    print("Data:", data_read)