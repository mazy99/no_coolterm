import sys
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIntValidator, QTextCursor, QIcon

from modbus_core import ModbusEngine
from modbus_core.modbus_parser import parse_module_17_registers

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
        self.setWindowIcon(QIcon("icon.ico"))
        self.setMinimumSize(1200, 850)
        self.dark_mode = False
        self.setup_ui()
        self.apply_styles()
        self.connected = False
        
        # Таймер для времени подключения
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.update_connection_time)
        self.connection_start_time = None
        
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
    
    def start_connection_timer(self):
        """Запуск таймера подключения"""
        self.connection_start_time = datetime.now()
        self.connection_timer.start(500)
        self.update_connection_time()
    
    def stop_connection_timer(self):
        """Остановка таймера подключения"""
        self.connection_timer.stop()
        self.connection_start_time = None
        self.connection_time_label.setText("")
    
    def update_connection_time(self):
        """Обновление отображения времени подключения"""
        if self.connection_start_time:
            elapsed = datetime.now() - self.connection_start_time
            hours = elapsed.seconds // 3600
            minutes = (elapsed.seconds % 3600) // 60
            seconds = elapsed.seconds % 60
            self.connection_time_label.setText(f"Подключено: {hours:02d}:{minutes:02d}:{seconds:02d}")
    
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
        
        # Метка времени подключения
        self.connection_time_label = QLabel("")
        self.connection_time_label.setStyleSheet("color: #6B7280; font-size: 12px;")
        conn_layout.addWidget(self.connection_time_label)
        
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
        
        self.connect_btn = QPushButton("Подключиться")
        self.connect_btn.setObjectName("connectBtn")
        self.disconnect_btn = QPushButton("Отключиться")
        self.disconnect_btn.setObjectName("disconnectBtn")
        self.disconnect_btn.setEnabled(False)
        
        conn_layout.addWidget(self.connect_btn)
        conn_layout.addWidget(self.disconnect_btn)
        
        main_layout.addWidget(conn_frame)
        
        # ========== ОСНОВНАЯ ГОРИЗОНТАЛЬНАЯ ОБЛАСТЬ ==========
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # ========== ЛЕВАЯ ПАНЕЛЬ - НАСТРОЙКИ ==========
        left_panel = QWidget()
        left_panel.setObjectName("card")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        left_layout.addWidget(QLabel("НАСТРОЙКИ ЗАПРОСА"))
        
        # Адрес (HEX)
        addr_container = QWidget()
        addr_container_layout = QHBoxLayout(addr_container)
        addr_container_layout.setContentsMargins(0, 0, 0, 0)
        addr_label = QLabel("Адрес устройства (HEX)")
        addr_label.setMinimumWidth(150)
        addr_container_layout.addWidget(addr_label)
        self.device_addr = QLineEdit()
        self.device_addr.setPlaceholderText("11")
        self.device_addr.setToolTip("HEX адрес (например: 11 для 17)")
        addr_container_layout.addWidget(self.device_addr)
        left_layout.addWidget(addr_container)
        
        # Команда
        cmd_container = QWidget()
        cmd_container_layout = QHBoxLayout(cmd_container)
        cmd_container_layout.setContentsMargins(0, 0, 0, 0)
        cmd_label = QLabel("Команда")
        cmd_label.setMinimumWidth(150)
        cmd_container_layout.addWidget(cmd_label)
        self.cmd_combo = QComboBox()
        self.cmd_combo.addItems(["03 Чтение", "06 Запись"])
        cmd_container_layout.addWidget(self.cmd_combo)
        left_layout.addWidget(cmd_container)
        
        # Ячейка (HEX)
        cell_container = QWidget()
        cell_container_layout = QHBoxLayout(cell_container)
        cell_container_layout.setContentsMargins(0, 0, 0, 0)
        cell_label = QLabel("Начальная ячейка (HEX)")
        cell_label.setMinimumWidth(150)
        cell_container_layout.addWidget(cell_label)
        self.start_addr = QLineEdit()
        self.start_addr.setPlaceholderText("0")
        self.start_addr.setToolTip("HEX адрес ячейки (например: 0, A, 10)")
        cell_container_layout.addWidget(self.start_addr)
        left_layout.addWidget(cell_container)
        
        # Кол-во байт
        count_container = QWidget()
        count_container_layout = QHBoxLayout(count_container)
        count_container_layout.setContentsMargins(0, 0, 0, 0)
        count_label = QLabel("Кол-во байт (чтение)")
        count_label.setMinimumWidth(150)
        count_container_layout.addWidget(count_label)
        self.read_count = QLineEdit()
        self.read_count.setPlaceholderText("8")
        count_container_layout.addWidget(self.read_count)
        left_layout.addWidget(count_container)
        
        # Данные записи
        write_container = QWidget()
        write_container_layout = QHBoxLayout(write_container)
        write_container_layout.setContentsMargins(0, 0, 0, 0)
        write_label = QLabel("Данные записи (hex)")
        write_label.setMinimumWidth(150)
        write_container_layout.addWidget(write_label)
        self.write_data = QLineEdit()
        self.write_data.setEnabled(False)
        self.write_data.setPlaceholderText("0010")
        write_container_layout.addWidget(self.write_data)
        left_layout.addWidget(write_container)
        
        left_layout.addStretch()
        
        # ========== ПРАВАЯ ПАНЕЛЬ - ФОРМИРУЕМЫЙ ЗАПРОС ==========
        right_panel = QWidget()
        right_panel.setObjectName("card")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)
        right_layout.setContentsMargins(30, 70, 30, 30)
        
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
        right_layout.addSpacing(10)
        
        # Создаем 8 отдельных полей ввода для байт (HEX) - без валидатора
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
        right_layout.addSpacing(15)
        
        # Кнопка отправки - теперь здесь, под ячейками
        self.send_btn = QPushButton("Отправить запрос")
        self.send_btn.setObjectName("sendBtn")
        self.send_btn.setMinimumHeight(45)
        self.send_btn.setEnabled(False)
        right_layout.addWidget(self.send_btn)
        
        top_splitter.addWidget(left_panel)
        top_splitter.addWidget(right_panel)
        top_splitter.setSizes([350, 850])
        main_layout.addWidget(top_splitter)
        
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
        self.log_text.setFont(QFont("Consolas", 11))
        self.log_text.setMinimumHeight(100)
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
        """Парсит HEX строку в число (без 0x)"""
        if not text:
            return 0
        text = text.strip().upper()
        if text.startswith("0X"):
            text = text[2:]
        try:
            return int(text, 16) & 0xFFFF
        except:
            return 0
    
    def format_hex(self, value, digits=4):
        """Форматирует число в HEX строку (без 0x)"""
        return f"{value:0{digits}X}"
    
    def get_int_from_hex(self, text, default=0):
        """Получает число из HEX строки"""
        try:
            if text.startswith("0x") or text.startswith("0X"):
                return int(text, 16)
            return int(text, 16)
        except:
            return default
    
    def get_int(self, text, default=0):
        """Получает число из десятичной строки"""
        try:
            return int(text)
        except:
            return default
    
    def update_from_ui(self):
        try:
            addr = self.get_int_from_hex(self.device_addr.text(), 1)
            if addr < 1 or addr > 247:
                addr = 1
            
            cmd = 0x03 if self.cmd_combo.currentIndex() == 0 else 0x06
            start = self.get_int_from_hex(self.start_addr.text(), 0)
            
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
                self.byte_inputs[i].setText(f"{val:02X}")
                self.byte_inputs[i].blockSignals(False)
            
            self.current_packet = full
            
        except Exception as e:
            pass
    
    def on_byte_changed(self):
        """Обработка изменения байтов в ручном режиме"""
        try:
            # Сначала просто собираем то, что ввели (без авто-исправления)
            packet = []
            for i in range(8):
                text = self.byte_inputs[i].text().strip().upper()
                if len(text) == 0:
                    # Пустое поле - не трогаем, оставляем как есть
                    packet.append(None)
                elif len(text) == 1:
                    # Один символ - пробуем как hex
                    try:
                        val = int(text, 16)
                        if 0 <= val <= 15:
                            packet.append(val)
                        else:
                            packet.append(None)
                    except:
                        packet.append(None)
                elif len(text) == 2:
                    # Два символа - пробуем как hex
                    try:
                        val = int(text, 16)
                        if 0 <= val <= 255:
                            packet.append(val)
                        else:
                            packet.append(None)
                    except:
                        packet.append(None)
                else:
                    packet.append(None)
            
            # Проверяем, все ли байты валидны (кроме CRC, их можно пересчитать)
            all_valid = all(p is not None for p in packet[:6])
            
            if all_valid:
                # Пересчитываем CRC для первых 6 байт
                first_six = [p for p in packet[:6] if p is not None]
                crc = self.calculate_crc16(first_six)
                crc_l = crc & 0xFF
                crc_h = (crc >> 8) & 0xFF
                
                # Обновляем CRC поля без вызова сигнала
                self.byte_inputs[6].blockSignals(True)
                self.byte_inputs[7].blockSignals(True)
                self.byte_inputs[6].setText(f"{crc_l:02X}")
                self.byte_inputs[7].setText(f"{crc_h:02X}")
                self.byte_inputs[6].blockSignals(False)
                self.byte_inputs[7].blockSignals(False)
                
                packet[6] = crc_l
                packet[7] = crc_h
                
                # Сохраняем текущий пакет
                self.current_packet = packet
                
                # Обновляем поля настроек из первых 6 байт
                addr = packet[0]
                cmd = packet[1]
                start_h = packet[2]
                start_l = packet[3]
                data_h = packet[4]
                data_l = packet[5]
                
                start = (start_h << 8) | start_l
                
                self.device_addr.blockSignals(True)
                self.device_addr.setText(f"{addr:02X}")
                self.device_addr.blockSignals(False)
                
                self.start_addr.blockSignals(True)
                self.start_addr.setText(f"{start:04X}")
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
            else:
                # Если не все байты валидны, CRC не обновляем
                # Собираем только валидные для временного расчёта
                temp_packet = []
                for i in range(6):
                    if packet[i] is not None:
                        temp_packet.append(packet[i])
                    else:
                        temp_packet.append(0)
                
                # Временный CRC для отображения
                if len(temp_packet) == 6:
                    crc = self.calculate_crc16(temp_packet)
                    crc_l = crc & 0xFF
                    crc_h = (crc >> 8) & 0xFF
                    
                    self.byte_inputs[6].blockSignals(True)
                    self.byte_inputs[7].blockSignals(True)
                    self.byte_inputs[6].setText(f"{crc_l:02X}")
                    self.byte_inputs[7].setText(f"{crc_h:02X}")
                    self.byte_inputs[6].blockSignals(False)
                    self.byte_inputs[7].blockSignals(False)
            
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
            self.start_connection_timer()
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
        self.stop_connection_timer()
        self.log("Отключено")
    
    def on_send(self):
        if not self.modbus_engine.is_connected():
            self.log("Ошибка: нет подключения")
            return
        if not hasattr(self, 'current_packet'):
            self.log("Ошибка: пакет не сформирован")
            return
        
        slave_id = self.get_int_from_hex(self.device_addr.text(), 1)
        address = self.get_int_from_hex(self.start_addr.text(), 0)
        
        if self.cmd_combo.currentIndex() == 0:  # Чтение (03)
            count = self.get_int(self.read_count.text(), 8)
            self.log(f"Чтение: адрес устройства: 0x{slave_id:02X}, начальный адрес ячейки: 0x{address:04X}, количество слов: {count}")
            try:
                result = self.modbus_engine.read_registers(slave_id, address, count)
                registers = result.get("registers", [])
                
                # Специальный формат для модуля 17 (0x11) - для ЛЮБОГО начального адреса
                if slave_id == 0x11:
                    parsed_data = parse_module_17_registers(registers, address)
                    for item in parsed_data:
                        self.log(f"{item['address']}: {item['name']}: {item['formatted_value']} (масштаб: {item['scale']})")
                else:
                    # Обычный вывод для других модулей
                    self.log(f"Получены регистры ({len(registers)} шт.):")
                    for i, reg in enumerate(registers):
                        addr_hex = f"0x{(address + i):04X}"
                        self.log(f"  {addr_hex}: 0x{reg:04X} ({reg})")
                
                # HEX вывод ответа с пробелами
                response_data = bytearray()
                for val in registers:
                    response_data += val.to_bytes(2, byteorder="big")
                hex_str = " ".join([f"{b:02X}" for b in response_data])
                self.log(f"Ответ (hex): {hex_str}")
                
            except Exception as e:
                self.log(f"Ошибка чтения: {e}")
        
        else:  # Запись (06)
            value = self.parse_hex(self.write_data.text())
            self.log(f"Запись: адрес устройства: 0x{slave_id:02X}, адрес ячейки: 0x{address:04X}, значение: 0x{value:04X}")
            try:
                response = self.modbus_engine.write_register(slave_id, address, value)
                hex_str = " ".join([f"{b:02X}" for b in response])
                self.log(f"Ответ: {hex_str}")
                self.log("Запись выполнена")
            except Exception as e:
                self.log(f"Ошибка записи: {e}")
    
    def clear_log(self):
        self.log_text.clear()
        self.log("Журнал очищен")
    
    def log(self, msg):
        from datetime import datetime
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
        # Автопрокрутка вниз
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)
    
    def apply_styles(self):
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
                    font-size: 14px;
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
                    font-size: 14px;
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

def main():
    app = QApplication(sys.argv)
    window = ModbusTerminal()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()