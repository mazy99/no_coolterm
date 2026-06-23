import unittest
from unittest.mock import Mock
from modbus_core.modbus_controller import ModbusController
from serial_core.serial_config import SerialConfig

class TestModbusController(unittest.TestCase):

    def test_connect(self):
        controller = ModbusController()

        config = SerialConfig(port="COM1", baudrate=9600, parity="N", stopbits=1)

        controller.connect = Mock(return_value=True)

        result = controller.connect(config)

        self.assertTrue(result)


    def test_scan_ports(self):
        controller = ModbusController()

        controller.scan_serial_ports = Mock(return_value=["COM1", "COM2"])

        ports = controller.scan_serial_ports()

        self.assertEqual(ports, ["COM1", "COM2"])

if __name__ == "__main__":
    unittest.main()