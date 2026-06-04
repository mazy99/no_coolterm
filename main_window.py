import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QTextEdit, QLineEdit,
    QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QDialog, QMessageBox
)

from serial_core.serial_manage import SerialManager
from serial_core.serial_config import SerialConfig
from modbus_core.modbus_rtu import ModbusRTU

# =====================================================
# 🟦 ОКНО НАСТРОЕК (Ваше)
# =====================================================
class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки подключения")
        self.setFixedSize(300, 300)
        layout = QVBoxLayout()

        self.port_box = QComboBox()
        self.port_box.addItems(SerialManager.scan_serial_ports())

        self.baud_box = QComboBox()
        self.baud_box.addItems(["9600", "19200", "38400", "115200"])

        self.data_bits = QComboBox()
        self.data_bits.addItems(["7", "8"])

        self.stop_bits = QComboBox()
        self.stop_bits.addItems(["1", "2"])

        self.timeout = QLineEdit("1.0")

        layout.addWidget(QLabel("COM порт")); layout.addWidget(self.port_box)
        layout.addWidget(QLabel("Скорость")); layout.addWidget(self.baud_box)
        layout.addWidget(QLabel("Data bits")); layout.addWidget(self.data_bits)
        layout.addWidget(QLabel("Stop bits")); layout.addWidget(self.stop_bits)
        layout.addWidget(QLabel("Timeout")); layout.addWidget(self.timeout)
        self.setLayout(layout)

# =====================================================
# 🟩 ГЛАВНОЕ ОКНО
# =====================================================
class ModbusUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modbus CoolTerm (PyQt6)")
        self.setGeometry(200, 200, 900, 600)
        
        self.serial_manager = SerialManager()
        self.modbus = None
        self.settings_window = SettingsWindow()
        
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        # Кнопки
        self.connect_btn = QPushButton("Подключиться")
        self.disconnect_btn = QPushButton("Отключиться")
        self.disconnect_btn.setEnabled(False)
        self.connect_btn.clicked.connect(self.connect)
        self.disconnect_btn.clicked.connect(self.disconnect)

        top = QHBoxLayout()
        top.addWidget(self.connect_btn); top.addWidget(self.disconnect_btn)
        layout.addLayout(top)

        self.settings_btn = QPushButton("Настройки")
        self.settings_btn.clicked.connect(lambda: self.settings_window.show())
        layout.addWidget(self.settings_btn)

        # HEX
        layout.addWidget(QLabel("Modbus HEX сообщение"))
        self.hex_input = QLineEdit("11 03 00 00 00 01")
        layout.addWidget(self.hex_input)
        
        self.crc_label = QLabel("CRC: ----")
        layout.addWidget(self.crc_label)

        self.send_btn = QPushButton("Отправить")
        self.send_btn.setEnabled(False)
        self.send_btn.clicked.connect(self.send_command)
        layout.addWidget(self.send_btn)

        # Журнал
        layout.addWidget(QLabel("Журнал"))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        self.save_btn = QPushButton("Сохранить лог")
        layout.addWidget(self.save_btn)
        central.setLayout(layout)

    # --- ЛОГИКА ---
    def connect(self):
        config = SerialConfig()
        config.port = self.settings_window.port_box.currentText()
        config.baudrate = int(self.settings_window.baud_box.currentText())
        config.byte_size = int(self.settings_window.data_bits.currentText())
        config.stopbits = int(self.settings_window.stop_bits.currentText())
        config.timeout = float(self.settings_window.timeout.text())

        if self.serial_manager.connect(config):
            self.modbus = ModbusRTU(self.serial_manager.serial_port)
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.send_btn.setEnabled(True)
            self.log("Подключено")
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться")

    def disconnect(self):
        self.serial_manager.disconnect()
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.log("Отключено")

    def send_command(self):
        if not self.modbus:
            return

        try:
            # 1. Получаем данные из поля ввода
            raw_hex = self.hex_input.text().replace(" ", "")
            # Преобразуем строку в байты
            data = bytes.fromhex(raw_hex)
            
            # 2. Рассчитываем CRC для введенных байт
            # Используем ваш метод crc16 из ModbusRTU
            crc_val = self.modbus.crc16(data)
            
            # 3. Формируем полное сообщение (данные + CRC)
            # В Modbus CRC передается как little-endian (младший байт вперед)
            full_packet = data + crc_val.to_bytes(2, byteorder='little')
            
            # 4. Отправляем в порт
            self.serial_manager.serial_port.write(full_packet)
            
            # Логируем то, что ушло (включая рассчитанный CRC)
            self.log(f"TX: {full_packet.hex(' ').upper()}")
            
            # 5. Читаем ответ
            # ВНИМАНИЕ: serial.read(256) может вернуть меньше данных, 
            # так как порт может быть медленным. 
            response = self.serial_manager.serial_port.read(256)
            
            if response:
                self.log(f"RX: {response.hex(' ').upper()}")
                
                # Попробуем распарсить, если ответ выглядит как Modbus ответ
                try:
                    parsed = self.modbus.parse_read_holding_registers_response(response)
                    self.log(f"Parsed: {parsed}")
                except ValueError as ve:
                    self.log(f"Ошибка парсинга: {ve}")
            else:
                self.log("RX: Таймаут (устройство не ответило)")
                
        except ValueError:
            self.log("Ошибка: Неверный HEX формат")
        except Exception as e:
            self.log(f"Ошибка при отправке: {e}")

    def log(self, text):
        self.log_box.append(f"[{datetime.now().strftime('%H:%M:%S')}] {text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModbusUI()
    window.show()
    sys.exit(app.exec())