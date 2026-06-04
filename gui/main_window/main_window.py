import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QPushButton, QTextEdit, QLineEdit,
    QLabel, QComboBox, QVBoxLayout, QHBoxLayout
)


class ModbusUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Modbus CoolTerm (Prototype)")
        self.setGeometry(200, 200, 900, 600)

        self.is_connected = False

        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()

        # =======================
        # 🔵 TOP BUTTONS
        # =======================
        self.connect_btn = QPushButton("Connect")
        self.disconnect_btn = QPushButton("Disconnect")

        self.disconnect_btn.setEnabled(False)  # логика блокировки

        self.connect_btn.clicked.connect(self.on_connect)
        self.disconnect_btn.clicked.connect(self.on_disconnect)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.connect_btn)
        top_layout.addWidget(self.disconnect_btn)

        main_layout.addLayout(top_layout)

        # =======================
        # 🟡 MODBUS INPUT
        # =======================
        self.input_hex = QLineEdit()
        self.input_hex.setPlaceholderText("11 06 00 01 00 01")

        self.crc_label = QLabel("CRC: --")

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.on_send)

        main_layout.addWidget(QLabel("Modbus HEX Input:"))
        main_layout.addWidget(self.input_hex)
        main_layout.addWidget(self.crc_label)
        main_layout.addWidget(self.send_btn)

        # =======================
        # 🟢 RESPONSE WINDOW
        # =======================
        self.response_box = QTextEdit()
        self.response_box.setReadOnly(True)

        main_layout.addWidget(QLabel("Response Log:"))
        main_layout.addWidget(self.response_box)

        # =======================
        # 🔵 SETTINGS
        # =======================
        settings_layout = QHBoxLayout()

        self.port_select = QComboBox()
        self.baudrate = QComboBox()
        self.timeout = QLineEdit()

        self.baudrate.addItems(["9600", "19200", "38400", "115200"])
        self.timeout.setPlaceholderText("Timeout (ms)")

        settings_layout.addWidget(QLabel("COM:"))
        settings_layout.addWidget(self.port_select)
        settings_layout.addWidget(QLabel("Baud:"))
        settings_layout.addWidget(self.baudrate)
        settings_layout.addWidget(QLabel("Timeout:"))
        settings_layout.addWidget(self.timeout)

        main_layout.addLayout(settings_layout)

        # =======================
        # 🟣 LOG SAVE
        # =======================
        self.save_log_btn = QPushButton("Save Log")
        self.save_log_btn.clicked.connect(self.save_log)

        main_layout.addWidget(self.save_log_btn)

        central.setLayout(main_layout)

        # live input CRC update
        self.input_hex.textChanged.connect(self.update_crc)

    # ======================================================
    # 🔴 CONNECTION LOGIC (ТУТ ВСТАВИШЬ SerialManager)
    # ======================================================

    def on_connect(self):
        """
        TODO: ВСТАВЬ СЮДА:
        sm.connect(...)
        modbus = ModbusRTU(...)
        """

        # ---- MOCK ----
        self.is_connected = True

        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(True)

        self.log("Connected to device")

    def on_disconnect(self):
        """
        TODO: ВСТАВЬ СЮДА:
        sm.disconnect()
        """

        self.is_connected = False

        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)

        self.log("Disconnected")

    # ======================================================
    # 🟡 SEND LOGIC
    # ======================================================

    def on_send(self):
        msg = self.input_hex.text().strip()

        if not self.is_connected:
            self.log("ERROR: Not connected")
            return

        """
        TODO:
        response = modbus.send(msg)
        """

        # MOCK RESPONSE
        response = f"sent: {msg}"

        self.log(f"TX: {msg}")
        self.log(f"RX: {response}")

    # ======================================================
    # 🧠 CRC UPDATE (вставишь свой модуль)
    # ======================================================

    def update_crc(self):
        msg = self.input_hex.text().strip()

        if not msg:
            self.crc_label.setText("CRC: --")
            return

        """
        TODO:
        crc = your_crc_module.calculate(msg)
        """

        crc = "ABCD"  # MOCK

        self.crc_label.setText(f"CRC: {crc}")

    # ======================================================
    # 🟢 LOG SYSTEM
    # ======================================================

    def log(self, text):
        self.response_box.append(text)

    def save_log(self):
        """
        TODO: сохранить self.response_box.toPlainText()
        """
        self.log("Log saved (TODO)")

# ======================================================
# RUN
# ======================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModbusUI()
    window.show()
    sys.exit(app.exec_())