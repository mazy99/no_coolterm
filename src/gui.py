import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIntValidator

from modbus_core import ModbusEngine

try:
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("Warning: pyserial not installed. Run: pip install pyserial")

class ModbusTerminal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modbus Терминал")
        self.setMinimumSize(1200, 800)
        self.dark_mode = False
        self.setup_ui()
        self.apply_styles()
        self.connected = False
        
        # СОЗДАЁМ ДВИЖОК
        self.modbus_engine = ModbusEngine()
        
        self.refresh_com_ports()
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_com_ports)
        self.timer.start(2000)
    
    def refresh_com_ports(self):
        if SERIAL_AVAILABLE:
            ports = serial.tools.list_ports.comports()
            current_text = self.port_combo.currentText()
            self.port_combo.clear()
            for port in ports:
                self.port_combo.addItem(port.device)
            if self.port_combo.count() == 0:
                self.port_combo.addItem("Нет портов")
            idx = self.port_combo.findText(current_text)
            if idx >= 0:
                self.port_combo.setCurrentIndex(idx)
        else:
            self.port_combo.clear()
            self.port_combo.addItem("pyserial не установлен")
    
    def animate_button(self, button):
        """Плавная анимация при нажатии на кнопку"""
        anim = QPropertyAnimation(button, b"geometry")
        anim.setDuration(80)
        geo = button.geometry()
        anim.setStartValue(geo)
        anim.setEndValue(geo.adjusted(1, 1, -1, -1))
        anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        anim.start()
        QTimer.singleShot(80, lambda: button.setGeometry(geo))
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_styles()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # Панель подключения
        conn_frame = QFrame()
        conn_frame.setObjectName("connFrame")
        conn_layout = QHBoxLayout(conn_frame)
        conn_layout.setContentsMargins(20, 12, 20, 12)
        conn_layout.setSpacing(15)
        
        # Индикатор подключения
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(12, 12)
        self.status_indicator.setObjectName("statusIndicator")
        self.status_indicator.setStyleSheet("border-radius: 6px; background-color: #9CA3AF;")
        conn_layout.addWidget(self.status_indicator)
        
        conn_layout.addWidget(QLabel("COM порт:"))
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(100)
        conn_layout.addWidget(self.port_combo)
        
        conn_layout.addWidget(QLabel("Скорость:"))
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "19200", "38400", "115200", "230400"])
        self.baud_combo.setMinimumWidth(90)
        conn_layout.addWidget(self.baud_combo)
        
        conn_layout.addStretch()
        
        # Кнопка переключения темы
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setObjectName("themeBtn")
        self.theme_btn.clicked.connect(self.toggle_theme)
        conn_layout.addWidget(self.theme_btn)
        
        self.connect_btn = QPushButton("Подключиться")
        self.connect_btn.setObjectName("connectBtn")
        self.disconnect_btn = QPushButton("Отключиться")
        self.disconnect_btn.setObjectName("disconnectBtn")
        self.disconnect_btn.setEnabled(False)
        
        conn_layout.addWidget(self.connect_btn)
        conn_layout.addWidget(self.disconnect_btn)
        
        main_layout.addWidget(conn_frame)
        
        # ========== ЛЕВАЯ ПАНЕЛЬ - НАСТРОЙКИ ==========
        left_panel = QWidget()
        left_panel.setObjectName("card")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        left_layout.addWidget(QLabel("НАСТРОЙКИ ЗАПРОСА"))
        
        # Адрес
        addr_container = QWidget()
        addr_container_layout = QHBoxLayout(addr_container)
        addr_container_layout.setContentsMargins(0, 0, 0, 0)
        addr_label = QLabel("Адрес устройства")
        addr_label.setMinimumWidth(130)
        addr_container_layout.addWidget(addr_label)
        self.device_addr = QLineEdit()
        addr_container_layout.addWidget(self.device_addr)
        left_layout.addWidget(addr_container)
        
        # Команда
        cmd_container = QWidget()
        cmd_container_layout = QHBoxLayout(cmd_container)
        cmd_container_layout.setContentsMargins(0, 0, 0, 0)
        cmd_label = QLabel("Команда")
        cmd_label.setMinimumWidth(130)
        cmd_container_layout.addWidget(cmd_label)
        self.cmd_combo = QComboBox()
        self.cmd_combo.addItems(["03 Чтение", "06 Запись"])
        cmd_container_layout.addWidget(self.cmd_combo)
        left_layout.addWidget(cmd_container)
        
        # Ячейка
        cell_container = QWidget()
        cell_container_layout = QHBoxLayout(cell_container)
        cell_container_layout.setContentsMargins(0, 0, 0, 0)
        cell_label = QLabel("Начальная ячейка")
        cell_label.setMinimumWidth(130)
        cell_container_layout.addWidget(cell_label)
        self.start_addr = QLineEdit()
        cell_container_layout.addWidget(self.start_addr)
        left_layout.addWidget(cell_container)
        
        # Кол-во байт
        count_container = QWidget()
        count_container_layout = QHBoxLayout(count_container)
        count_container_layout.setContentsMargins(0, 0, 0, 0)
        count_label = QLabel("Кол-во байт (чтение)")
        count_label.setMinimumWidth(130)
        count_container_layout.addWidget(count_label)
        self.read_count = QLineEdit()
        count_container_layout.addWidget(self.read_count)
        left_layout.addWidget(count_container)
        
        # Данные записи
        write_container = QWidget()
        write_container_layout = QHBoxLayout(write_container)
        write_container_layout.setContentsMargins(0, 0, 0, 0)
        write_label = QLabel("Данные записи (hex)")
        write_label.setMinimumWidth(130)
        write_container_layout.addWidget(write_label)
        self.write_data = QLineEdit()
        self.write_data.setEnabled(False)
        write_container_layout.addWidget(self.write_data)
        left_layout.addWidget(write_container)
        
        left_layout.addStretch()
        
        # ========== ПРАВАЯ ПАНЕЛЬ - ФОРМИРУЕМЫЙ ЗАПРОС ==========
        right_panel = QWidget()
        right_panel.setObjectName("card")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок по центру
        header_widget = QWidget()
        header_widget.setObjectName("headerWidget")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addStretch()
        
        header_label = QLabel("ФОРМИРУЕМЫЙ ЗАПРОС (8 БАЙТ)")
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        right_layout.addWidget(header_widget)
        right_layout.addSpacing(5)
        
        # Создаем 8 отдельных полей ввода для байт
        bytes_container = QWidget()
        bytes_layout = QHBoxLayout(bytes_container)
        bytes_layout.setSpacing(10)
        bytes_layout.setContentsMargins(0, 0, 0, 0)
        
        self.byte_inputs = []
        byte_labels = ["Байт 1\nАдрес", "Байт 2\nКоманда", "Байт 3\nАдр.H", "Байт 4\nАдр.L", 
                       "Байт 5\nДанные H", "Байт 6\nДанные L", "Байт 7\nCRC L", "Байт 8\nCRC H"]
        
        for i in range(8):
            byte_widget = QWidget()
            byte_widget_layout = QVBoxLayout(byte_widget)
            byte_widget_layout.setSpacing(6)
            byte_widget_layout.setContentsMargins(0, 0, 0, 0)
            
            label = QLabel(byte_labels[i])
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setObjectName("byteLabel")
            byte_widget_layout.addWidget(label)
            
            byte_input = QLineEdit()
            byte_input.setMaxLength(2)
            byte_input.setPlaceholderText("00")
            byte_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            byte_input.setFixedWidth(80)
            byte_input.textChanged.connect(self.on_byte_changed)
            byte_widget_layout.addWidget(byte_input)
            
            self.byte_inputs.append(byte_input)
            bytes_layout.addWidget(byte_widget)
        
        right_layout.addWidget(bytes_container)
        
        # Объединяем левую и правую панели в горизонтальный слой
        top_layout = QHBoxLayout()
        top_layout.addWidget(left_panel, 1)
        top_layout.addWidget(right_panel, 2)
        main_layout.addLayout(top_layout)
        
        # Кнопка отправки
        self.send_btn = QPushButton("Отправить запрос")
        self.send_btn.setObjectName("sendBtn")
        self.send_btn.setMinimumHeight(50)
        self.send_btn.setEnabled(False)
        main_layout.addWidget(self.send_btn)
        
        # Журнал событий
        log_frame = QFrame()
        log_frame.setObjectName("logFrame")
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(20, 15, 20, 15)
        
        log_header = QHBoxLayout()
        log_header.addWidget(QLabel("ЖУРНАЛ СОБЫТИЙ"))
        log_header.addStretch()
        clear_btn = QPushButton("Очистить")
        clear_btn.setObjectName("clearBtn")
        clear_btn.clicked.connect(self.clear_log)
        log_header.addWidget(clear_btn)
        log_layout.addLayout(log_header)
        log_layout.addSpacing(5)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 12))
        self.log_text.setMinimumHeight(280)
        log_layout.addWidget(self.log_text)
        
        main_layout.addWidget(log_frame)
        
        # Сигналы
        self.connect_btn.clicked.connect(lambda: [self.animate_button(self.connect_btn), self.on_connect()])
        self.disconnect_btn.clicked.connect(lambda: [self.animate_button(self.disconnect_btn), self.on_disconnect()])
        self.send_btn.clicked.connect(lambda: [self.animate_button(self.send_btn), self.on_send()])
        self.cmd_combo.currentIndexChanged.connect(self.on_command_changed)
        self.device_addr.textChanged.connect(self.update_from_ui)
        self.start_addr.textChanged.connect(self.update_from_ui)
        self.read_count.textChanged.connect(self.update_from_ui)
        self.write_data.textChanged.connect(self.update_from_ui)
        
        self.update_from_ui()
    
    def on_command_changed(self):
        is_read = self.cmd_combo.currentIndex() == 0
        self.read_count.setEnabled(is_read)
        self.write_data.setEnabled(not is_read)
        self.update_from_ui()
    
    def calculate_crc16(self, data):
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc
    
    def parse_hex(self, text):
        if not text:
            return 0
        t = text.strip().replace('0x', '').replace('0X', '').replace(',', ' ')
        parts = t.split()
        if parts:
            try:
                return int(parts[0], 16) & 0xFFFF
            except:
                return 0
        return 0
    
    def get_int(self, text, default=0):
        try:
            return int(text)
        except:
            return default
    
    def update_from_ui(self):
        try:
            addr = self.get_int(self.device_addr.text(), 1)
            if addr < 1 or addr > 247:
                addr = 1
            
            cmd = 0x03 if self.cmd_combo.currentIndex() == 0 else 0x06
            start = self.get_int(self.start_addr.text(), 0)
            
            start_h = (start >> 8) & 0xFF
            start_l = start & 0xFF
            
            if cmd == 0x03:
                count = self.get_int(self.read_count.text(), 8)
                if count < 1 or count > 252:
                    count = 8
                data_h = (count >> 8) & 0xFF
                data_l = count & 0xFF
            else:
                val = self.parse_hex(self.write_data.text())
                data_h = (val >> 8) & 0xFF
                data_l = val & 0xFF
            
            packet = [addr, cmd, start_h, start_l, data_h, data_l]
            crc = self.calculate_crc16(packet)
            crc_l = crc & 0xFF
            crc_h = (crc >> 8) & 0xFF
            
            full = packet + [crc_l, crc_h]
            
            for i, val in enumerate(full):
                self.byte_inputs[i].blockSignals(True)
                if i == 0:
                    self.byte_inputs[i].setText(str(val))
                else:
                    self.byte_inputs[i].setText(f"{val:02X}")
                self.byte_inputs[i].blockSignals(False)
            
            self.current_packet = full
            
        except Exception as e:
            pass
    
    def on_byte_changed(self):
        try:
            packet = []
            for i in range(8):
                text = self.byte_inputs[i].text().strip().upper()
                if i == 0:
                    try:
                        val = int(text, 10)
                        if 0 <= val <= 255:
                            packet.append(val)
                        else:
                            packet.append(0)
                    except:
                        packet.append(0)
                else:
                    if len(text) == 2:
                        try:
                            val = int(text, 16)
                            if 0 <= val <= 255:
                                packet.append(val)
                            else:
                                packet.append(0)
                        except:
                            packet.append(0)
                    elif len(text) == 1:
                        try:
                            val = int(text, 16)
                            packet.append(val)
                        except:
                            packet.append(0)
                    else:
                        packet.append(0)
            
            first_six = packet[:6]
            crc = self.calculate_crc16(first_six)
            crc_l = crc & 0xFF
            crc_h = (crc >> 8) & 0xFF
            
            packet[6] = crc_l
            packet[7] = crc_h
            
            for i, val in enumerate(packet):
                self.byte_inputs[i].blockSignals(True)
                if i == 0:
                    self.byte_inputs[i].setText(str(val))
                else:
                    self.byte_inputs[i].setText(f"{val:02X}")
                self.byte_inputs[i].blockSignals(False)
            
            self.current_packet = packet
            
            if len(packet) >= 6:
                addr = packet[0]
                cmd = packet[1]
                start_h = packet[2]
                start_l = packet[3]
                data_h = packet[4]
                data_l = packet[5]
                
                start = (start_h << 8) | start_l
                
                self.device_addr.blockSignals(True)
                self.device_addr.setText(str(addr))
                self.device_addr.blockSignals(False)
                
                self.start_addr.blockSignals(True)
                self.start_addr.setText(str(start))
                self.start_addr.blockSignals(False)
                
                if cmd == 0x03:
                    count = (data_h << 8) | data_l
                    self.read_count.blockSignals(True)
                    self.read_count.setText(str(count))
                    self.read_count.blockSignals(False)
                else:
                    val = (data_h << 8) | data_l
                    self.write_data.blockSignals(True)
                    self.write_data.setText(f"{val:04X}")
                    self.write_data.blockSignals(False)
                
                cmd_index = 0 if cmd == 0x03 else 1
                self.cmd_combo.blockSignals(True)
                self.cmd_combo.setCurrentIndex(cmd_index)
                self.cmd_combo.blockSignals(False)
                
                self.on_command_changed()
            
        except Exception as e:
            pass
    
    def on_connect(self):
        port = self.port_combo.currentText()
        if port == "Нет портов" or not port:
            self.log("Нет доступных портов")
            return
        
        baud = int(self.baud_combo.currentText())
        self.log(f"Подключение к {port} ({baud} бод)...")
        
        if self.modbus_engine.connect(port, baud):
            self.connected = True
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.send_btn.setEnabled(True)
            self.status_indicator.setStyleSheet("border-radius: 6px; background-color: #10B981;")
            self.log(f"Подключено к {port}")
        else:
            self.log("Ошибка подключения")
    
    def on_disconnect(self):
        self.log("Отключение...")
        self.modbus_engine.disconnect()
        self.connected = False
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.status_indicator.setStyleSheet("border-radius: 6px; background-color: #9CA3AF;")
        self.log("Отключено")
    
    def on_send(self):
        if not self.modbus_engine.is_connected():
            self.log("Ошибка: нет подключения")
            return
        if not hasattr(self, 'current_packet'):
            self.log("Ошибка: пакет не сформирован")
            return
        
        slave_id = self.get_int(self.device_addr.text(), 1)
        address = self.get_int(self.start_addr.text(), 0)
        
        if self.cmd_combo.currentIndex() == 0:  # Чтение (03)
            count = self.get_int(self.read_count.text(), 8)
            self.log(f"Чтение: slave_id={slave_id}, address={address}, count={count}")
            try:
                result = self.modbus_engine.read_registers(slave_id, address, count)
                registers = result.get("registers", [])
                self.log(f"Получены регистры: {registers}")
                
                # Формируем ответ для отображения в логе как hex
                response_data = bytearray()
                for val in registers:
                    response_data += val.to_bytes(2, byteorder="big")
                self.log(f"Ответ (hex): {response_data.hex().upper()}")
                
            except Exception as e:
                self.log(f"Ошибка чтения: {e}")
        
        else:  # Запись (06)
            value = self.parse_hex(self.write_data.text())
            self.log(f"Запись: slave_id={slave_id}, address={address}, value={value}")
            try:
                response = self.modbus_engine.write_register(slave_id, address, value)
                self.log(f"Ответ: {response.hex().upper()}")
                self.log("Запись выполнена")
            except Exception as e:
                self.log(f"Ошибка записи: {e}")
    
    def clear_log(self):
        self.log_text.clear()
        self.log("Журнал очищен")
    
    def log(self, msg):
        from datetime import datetime
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    def apply_styles(self):
        if not self.dark_mode:
            # СВЕТЛАЯ ТЕМА
            self.theme_btn.setText("🌙")
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #F2F4F7;
                }
                
                QFrame#connFrame {
                    background-color: white;
                    border-radius: 12px;
                    border: 1px solid #E4E7EC;
                }
                
                QFrame#card {
                    background-color: white;
                    border-radius: 12px;
                    border: 1px solid #E4E7EC;
                }
                
                QFrame#logFrame {
                    background-color: white;
                    border-radius: 12px;
                    border: 1px solid #D1D5DB;
                }
                
                QLabel {
                    color: #1A2C3E;
                    font-weight: 500;
                    font-size: 12px;
                    background-color: transparent;
                }
                
                QWidget#headerWidget {
                    background-color: transparent;
                }
                
                QLabel#headerLabel {
                    color: #1A2C3E;
                    font-weight: 600;
                    font-size: 14px;
                    background-color: transparent;
                    padding: 6px 20px;
                    border-bottom: 2px solid #3B82F6;
                }
                
                QLabel#byteLabel {
                    font-size: 11px;
                    color: #6B7280;
                    font-weight: 500;
                    background-color: transparent;
                }
                
                QComboBox, QLineEdit {
                    background-color: white;
                    color: #1A2C3E;
                    border: 1px solid #D0D5DD;
                    border-radius: 8px;
                    padding: 7px 10px;
                    font-size: 12px;
                    font-family: 'Consolas', monospace;
                }
                
                QComboBox:hover, QLineEdit:hover {
                    border-color: #9AA4B2;
                    background-color: #F9FAFB;
                }
                
                QComboBox:focus, QLineEdit:focus {
                    border-color: #3B82F6;
                    outline: none;
                }
                
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                
                QComboBox QAbstractItemView {
                    background-color: white;
                    color: #1A2C3E;
                    border: 1px solid #D0D5DD;
                    border-radius: 8px;
                    selection-background-color: #EFF6FF;
                    selection-color: #1A2C3E;
                }
                
                QComboBox QAbstractItemView::item {
                    padding: 6px;
                }
                
                QPushButton:pressed {
                    padding-top: 2px;
                    padding-bottom: 2px;
                }
                
                QPushButton#themeBtn {
                    background-color: #F3F4F6;
                    color: #374151;
                    border: 1px solid #D1D5DB;
                    border-radius: 8px;
                    padding: 7px 16px;
                    font-weight: 500;
                    font-size: 12px;
                }
                QPushButton#themeBtn:hover {
                    background-color: #E5E7EB;
                }
                
                QPushButton#connectBtn {
                    background-color: #10B981;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 7px 20px;
                    font-weight: 600;
                    font-size: 12px;
                }
                QPushButton#connectBtn:hover {
                    background-color: #059669;
                }
                QPushButton#connectBtn:disabled {
                    background-color: #9CA3AF;
                }
                
                QPushButton#disconnectBtn {
                    background-color: #EF4444;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 7px 20px;
                    font-weight: 600;
                    font-size: 12px;
                }
                QPushButton#disconnectBtn:hover {
                    background-color: #DC2626;
                }
                QPushButton#disconnectBtn:disabled {
                    background-color: #9CA3AF;
                }
                
                QPushButton#sendBtn {
                    background-color: #3B82F6;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 13px;
                    font-weight: 600;
                }
                QPushButton#sendBtn:hover {
                    background-color: #2563EB;
                }
                QPushButton#sendBtn:disabled {
                    background-color: #9CA3AF;
                }
                
                QPushButton#clearBtn {
                    background-color: #F3F4F6;
                    color: #374151;
                    border: 1px solid #D1D5DB;
                    border-radius: 6px;
                    padding: 5px 14px;
                    font-size: 11px;
                }
                QPushButton#clearBtn:hover {
                    background-color: #E5E7EB;
                }
                
                QTextEdit {
                    background-color: #F9FAFB;
                    color: #1A2C3E;
                    border: 1px solid #E5E7EB;
                    border-radius: 12px;
                    font-family: 'Consolas', monospace;
                    font-size: 13px;
                }
                
                QScrollBar:vertical {
                    background-color: #F9FAFB;
                    width: 8px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background-color: #D1D5DB;
                    border-radius: 4px;
                    min-height: 30px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #9CA3AF;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)
        else:
            # ТЁМНАЯ ТЕМА (СТИЛЬ ЯНДЕКС МУЗЫКИ)
            self.theme_btn.setText("☀️")
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #1A1B1E;
                }
                
                QFrame#connFrame {
                    background-color: #232428;
                    border-radius: 12px;
                    border: 1px solid #2C2D32;
                }
                
                QFrame#card {
                    background-color: #232428;
                    border-radius: 12px;
                    border: 1px solid #2C2D32;
                }
                
                QFrame#logFrame {
                    background-color: #232428;
                    border-radius: 12px;
                    border: 1px solid #2C2D32;
                }
                
                QLabel {
                    color: #E8E8F0;
                    font-weight: 500;
                    font-size: 12px;
                    background-color: transparent;
                }
                
                QWidget#headerWidget {
                    background-color: transparent;
                }
                
                QLabel#headerLabel {
                    color: #FFFFFF;
                    font-weight: 600;
                    font-size: 14px;
                    background-color: transparent;
                    padding: 6px 20px;
                    border-bottom: 2px solid #FF3B30;
                }
                
                QLabel#byteLabel {
                    font-size: 11px;
                    color: #8A8B91;
                    font-weight: 500;
                    background-color: transparent;
                }
                
                QComboBox, QLineEdit {
                    background-color: #2C2D32;
                    color: #E8E8F0;
                    border: 1px solid #3D3E44;
                    border-radius: 8px;
                    padding: 7px 10px;
                    font-size: 12px;
                    font-family: 'Consolas', monospace;
                }
                
                QComboBox:hover, QLineEdit:hover {
                    background-color: #3A3B40;
                    border-color: #4D4E54;
                }
                
                QComboBox:focus, QLineEdit:focus {
                    background-color: #3A3B40;
                    border: 1px solid #FF3B30;
                    outline: none;
                }
                
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                
                QComboBox QAbstractItemView {
                    background-color: #2C2D32;
                    color: #E8E8F0;
                    border: 1px solid #3D3E44;
                    border-radius: 8px;
                    selection-background-color: #FF3B30;
                    selection-color: white;
                }
                
                QComboBox QAbstractItemView::item {
                    padding: 8px;
                }
                
                QPushButton:pressed {
                    padding-top: 2px;
                    padding-bottom: 2px;
                }
                
                QPushButton#themeBtn {
                    background-color: #2C2D32;
                    color: #E8E8F0;
                    border: 1px solid #3D3E44;
                    border-radius: 8px;
                    padding: 7px 16px;
                    font-weight: 500;
                    font-size: 12px;
                }
                QPushButton#themeBtn:hover {
                    background-color: #3A3B40;
                }
                
                QPushButton#connectBtn {
                    background-color: #00A88F;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 7px 20px;
                    font-weight: 600;
                    font-size: 12px;
                }
                QPushButton#connectBtn:hover {
                    background-color: #00C4A8;
                }
                QPushButton#connectBtn:disabled {
                    background-color: #3A3B40;
                    color: #6A6B70;
                }
                
                QPushButton#disconnectBtn {
                    background-color: #FF3B30;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 7px 20px;
                    font-weight: 600;
                    font-size: 12px;
                }
                QPushButton#disconnectBtn:hover {
                    background-color: #FF5E55;
                }
                QPushButton#disconnectBtn:disabled {
                    background-color: #3A3B40;
                    color: #6A6B70;
                }
                
                QPushButton#sendBtn {
                    background-color: #3B82F6;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 13px;
                    font-weight: 600;
                }
                QPushButton#sendBtn:hover {
                    background-color: #2563EB;
                }
                QPushButton#sendBtn:disabled {
                    background-color: #3A3B40;
                    color: #6A6B70;
                }
                
                QPushButton#clearBtn {
                    background-color: #2C2D32;
                    color: #E8E8F0;
                    border: 1px solid #3D3E44;
                    border-radius: 6px;
                    padding: 5px 14px;
                    font-size: 11px;
                }
                QPushButton#clearBtn:hover {
                    background-color: #3A3B40;
                }
                
                QTextEdit {
                    background-color: #1A1B1E;
                    color: #E8E8F0;
                    border: 1px solid #2C2D32;
                    border-radius: 12px;
                    font-family: 'Consolas', monospace;
                    font-size: 13px;
                }
                
                QScrollBar:vertical {
                    background-color: #1A1B1E;
                    width: 8px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background-color: #3A3B40;
                    border-radius: 4px;
                    min-height: 30px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #4A4B50;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)

def main():
    app = QApplication(sys.argv)
    window = ModbusTerminal()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()