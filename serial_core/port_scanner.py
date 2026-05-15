import serial.tools.list_ports

def scan_serial_ports() -> list:

    ports: list = serial.tools.list_ports.comports()
    available_ports: list = []
    for port in ports:
        available_ports.append(port.device)

    return available_ports




