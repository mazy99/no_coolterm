import sys
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRegularExpression
from PyQt6.QtGui import QFont, QIntValidator, QRegularExpressionValidator

from modbus_core.modbus_controller import ModbusController 
from utils.style_loader import load_stylesheet
from gui.modbus_table import   DEVICE_MAPS



class ModbusTerminal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.syncing = False #синхронизация UI с пакетом (чтобы не было циклических обновлений)
        self.current_packet = [0] * 8 # текущий формируемый пакет (8 байт)

        self.setWindowTitle("Modbus Терминал")
        self.setMinimumSize(1200, 800)
        self.dark_mode = False
        # СОЗДАЁМ ДВИЖОК
        self.modbus_engine = ModbusController()
        self.setup_ui()
        self.apply_styles()
        self.connected = False
        
        
        self.refresh_com_ports()    
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_com_ports)
        self.timer.start(2000)

    
    def refresh_com_ports(self):
            
            ports = ModbusController.scan_serial_ports()

            current_text = self.port_combo.currentText()
            self.port_combo.clear()

            for port in ports:
                self.port_combo.addItem(port)

            if self.port_combo.count() == 0:
                self.port_combo.addItem("Нет портов")

            idx = self.port_combo.findText(current_text)
            if idx >= 0:
                self.port_combo.setCurrentIndex(idx)
    
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

        # Создаем валидатор для HEX-полей (от 1 до 4 символов: 0-9, A-F)
        hex_validator_4 = QRegularExpressionValidator(QRegularExpression("[0-9A-Fa-f]{1,4}"))
        
        # Адрес
        addr_container = QWidget()
        addr_container_layout = QHBoxLayout(addr_container)
        addr_container_layout.setContentsMargins(0, 0, 0, 0)
        addr_label = QLabel("Адрес устройства")
        addr_label.setMinimumWidth(130)
        addr_container_layout.addWidget(addr_label)
        self.device_addr = QLineEdit()
        self.device_addr.setValidator(QIntValidator(1, 247)) # Только DEC
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
        cell_label = QLabel("Начальная ячейка (hex)")
        cell_label.setMinimumWidth(130)
        cell_container_layout.addWidget(cell_label)
        self.start_addr = QLineEdit()
        self.start_addr.setValidator(QIntValidator(0, 65535)) # Только HEX
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
        self.read_count.setValidator(QIntValidator(1, 125)) # Только DEC
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
        self.write_data.setValidator(hex_validator_4) # ИСПРАВЛЕНО: было start_addr
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
        
        # Валидатор для одиночных байт (максимум 2 символа HEX)
        hex_validator_2 = QRegularExpressionValidator(QRegularExpression("[0-9A-Fa-f]{1,2}"))

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
            byte_input.setValidator(hex_validator_2) # ДОБАВЛЕНО: защита от неверного ввода
            byte_input.setPlaceholderText("00")
            byte_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            byte_input.setFixedWidth(80)
            byte_input.textChanged.connect(self.on_byte_changed)
            byte_widget_layout.addWidget(byte_input)
            
            self.byte_inputs.append(byte_input)
            bytes_layout.addWidget(byte_widget)
        
        self.byte_inputs[6].setReadOnly(True)
        self.byte_inputs[7].setReadOnly(True)
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
        log_frame = QWidget()
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
    
   
    
    def get_int(self, text, default=0):
        try:
            return int(text) 
        except:
            return default
        
    def get_hex(self, text, default=0):
        try:
            if not text:
                return default
            return int(text, 16)
        except:
            return default
        

    def update_from_ui(self):
        if self.syncing:
            return

        try:
            self.syncing = True

            # Читаем данные из UI с помощью безопасных методов
            addr = self.get_int(self.device_addr.text(), 1)
            cmd = 0x03 if self.cmd_combo.currentIndex() == 0 else 0x06
            start = self.get_hex(self.start_addr.text(), 0) # Читаем адрес как HEX

            if cmd == 0x03:
                count = self.get_int(self.read_count.text(), 8)
                if count < 1 or count > 125:  # Валидация по стандарту Modbus
                    count = 8
                val_or_count = count
            else:
                val_or_count = self.get_hex(self.write_data.text(), 0)

            # КРАСОТА: Используем твой готовый метод preview_request из контроллера!
            # Он возвращает строку вида "11 03 00 08 00 01 06 1A"
            hex_packet_str = self.modbus_engine.preview_request(addr, cmd, start, val_or_count)
            hex_bytes = hex_packet_str.split() # Получаем список ['11', '03', '00', '08', ...]

            # Обновляем 8 HEX ячеек в правой панели
            for i, byte_str in enumerate(hex_bytes):
                if i < len(self.byte_inputs):
                    self.byte_inputs[i].blockSignals(True)
                    self.byte_inputs[i].setText(byte_str.upper())
                    self.byte_inputs[i].blockSignals(False)

            # Сохраняем пакет как список чисел
            self.current_packet = [int(b, 16) for b in hex_bytes]

        except Exception as e:
            self.log(f"Ошибка UI: {e}")

        finally:
            self.syncing = False
    
    def on_byte_changed(self):
        if self.syncing:
            return
            
        try:
            self.syncing = True
            packet = []
            
            # Считываем все 8 байт из правой панели (ожидаем HEX)
            for i in range(8):
                text = self.byte_inputs[i].text().strip().upper()
                try:
                    val = int(text or "0", 16)
                    if 0 <= val <= 255:
                        packet.append(val)
                    else:
                        packet.append(0)
                except:
                    packet.append(0)
            
            # Пересчитываем CRC для первых 6 байт
            first_six = packet[:6]
            crc = self.modbus_engine.calculate_crc16(bytes(first_six))
            crc_l = crc & 0xFF
            crc_h = (crc >> 8) & 0xFF
            
            packet[6] = crc_l
            packet[7] = crc_h
            
            # Обновляем байты CRC в UI
            self.byte_inputs[6].blockSignals(True)
            self.byte_inputs[6].setText(f"{crc_l:02X}")
            self.byte_inputs[6].blockSignals(False)
            
            self.byte_inputs[7].blockSignals(True)
            self.byte_inputs[7].setText(f"{crc_h:02X}")
            self.byte_inputs[7].blockSignals(False)
            
            self.current_packet = packet
            
            # ===== Синхронизация с левой панелью =====
            if len(packet) == 8:
                addr = packet[0]
                cmd = packet[1]
                start_h = packet[2]
                start_l = packet[3]
                data_h = packet[4]
                data_l = packet[5]
                
                start = (start_h << 8) | start_l
                
                # Адрес (переводим в DEC)
                self.device_addr.blockSignals(True)
                self.device_addr.setText(str(addr))
                self.device_addr.blockSignals(False)
                
                # Начальная ячейка (оставляем в HEX)
                self.start_addr.blockSignals(True)
                self.start_addr.setText(str(start))
                self.start_addr.blockSignals(False)
                
                if cmd == 0x03:
                    # Количество байт (переводим в DEC)
                    count = (data_h << 8) | data_l
                    self.read_count.blockSignals(True)
                    self.read_count.setText(str(count))
                    self.read_count.blockSignals(False)
                else:
                    # Данные записи (оставляем в HEX)
                    val = (data_h << 8) | data_l
                    self.write_data.blockSignals(True)
                    self.write_data.setText(f"{val:04X}")
                    self.write_data.blockSignals(False)
                
                cmd_index = 0 if cmd == 0x03 else 1
                self.cmd_combo.blockSignals(True)
                self.cmd_combo.setCurrentIndex(cmd_index)
                self.cmd_combo.blockSignals(False)
                
                # Обновляем активность полей
                is_read = cmd_index == 0
                self.read_count.setEnabled(is_read)
                self.write_data.setEnabled(not is_read)
            
        except Exception as e:
            self.log(f"Ошибка UI: {e}")
        
        finally:
            self.syncing = False

    def on_connect(self):
        port = self.port_combo.currentText()
        if port == "Нет портов" or not port:
            self.log("Нет доступных портов")
            return

        baud = int(self.baud_combo.currentText())

        from serial_core.serial_config import SerialConfig

        config = SerialConfig(
            port=port,
            baudrate=baud,
            parity="N",
            stopbits=1
        )

        self.log(f"Подключение к {port} ({baud})...")

        if self.modbus_engine.connect(config):
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
    
    def format_registers_to_ascii_table(self, slave_id: int, start_address: int, registers: list) -> str:
        """Форматирует прочитанные регистры в красивую текстовую ASCII-таблицу с масштабом"""

        if slave_id not in DEVICE_MAPS:
            return ""
        lines = []
        current_map = DEVICE_MAPS.get(slave_id, {})
        # Шапка таблицы с фиксированной шириной столбцов (с учетом новой колонки Масштаб)
        lines.append("+" + "-"*8 + "+" + "-"*55 + "+" + "-"*17 + "+" + "-"*9 + "+" + "-"*10 + "+")
        lines.append(f"| {'Адрес':<6} | {'Параметр':<53} | {'Физическое знач':<15} | {'Масштаб':<7} | {'HEX':<8} |")
        lines.append("+" + "-"*8 + "+" + "-"*55 + "+" + "-"*17 + "+" + "-"*9 + "+" + "-"*10 + "+")
        
        has_data = False
        
        # Цикл идет строго по полученному массиву регистров (динамический размер: 1, 5, 10 и т.д.)
        for offset, val in enumerate(registers):
            current_addr = start_address + offset
            
            # Проверяем, описан ли этот регистр в карте МКБ4
            if current_addr in current_map:
                has_data = True
                info = current_map[current_addr]

                # Обработка знака (signed short, 16 бит)
                raw_val = val
                if info["знак"] and raw_val > 0x7FFF:
                    raw_val -= 0x10000
                
                # Ключ "Масштаб"
                scale= info["Масштаб"]
                phys_val = raw_val / scale
                phys_str = f"{phys_val:.2f}" if scale > 1 else f"{int(phys_val)}"
                scale_str = str(scale)
                
                addr_str = f"0x{current_addr:04X}"
                hex_str = f"0x{val:04X}"
                name_str = info["Параметр"]
            else:
                # Если запросили регистр, которого нет в карте параметров
                has_data = True
                addr_str = f"0x{current_addr:04X}"
                hex_str = f"0x{val:04X}"
                phys_str = f"{val}"  # выводим просто как DEC число
                scale_str = "1"
                name_str = f"Регистр {current_addr} (Вне карты параметров)"

            # Формируем строку таблицы с выравниванием (добавлена колонка scale_str)
            lines.append(f"| {addr_str:<6} | {name_str:<53} | {phys_str:>15} | {scale_str:>7} | {hex_str:<8} |")
        
        lines.append("+" + "-"*8 + "+" + "-"*55 + "+" + "-"*17 + "+" + "-"*9 + "+" + "-"*10 + "+")
        
        # Возвращаем готовую таблицу, если в ней есть хоть одна строчка данных
        return "\n".join(lines) if has_data else ""
    
    def on_send(self):
        if not self.modbus_engine.is_connected():
            self.log("Ошибка: нет подключения")
            return


        slave_id = self.get_int(self.device_addr.text(), 1)
        

        address = self.get_int(self.start_addr.text(), 0)

        if self.cmd_combo.currentIndex() == 0:  # READ
            # DEC поле (все верно)
            count = self.get_int(self.read_count.text(), 8)
            self.log(f"Чтение: {self.modbus_engine.preview_request(slave_id=slave_id, function_code=3, address=address, value_or_count=count)}")

            try:
                result = self.modbus_engine.read_holding_registers(slave_id, address, count)
                
                registers = []

                # КОРРЕКЦИЯ: Если ответ пришел в виде HEX-строки, переводим ее в байты
                if isinstance(result, str):
                    # Убираем пробелы, если они есть в строке ответа
                    clean_result = result.replace(" ", "")
                    try:
                        result = bytes.fromhex(clean_result)
                    except ValueError:
                        pass # Если это была не HEX строка, оставим как есть

                # ВАРИАНТ 1: Если это байты (или успешно преобразованная строка)
                if isinstance(result, (bytes, bytearray)):
                    self.log(f"Результат чтения: {result.hex(sep=' ').upper()}")
                    
                    if len(result) >= 5:
                        data_bytes = result[3:-2] # Отрезаем заголовок (3 байта) и CRC (2 байта)
                        
                        # Превращаем пары байт в 16-битные регистры
                        for i in range(0, len(data_bytes), 2):
                            if i + 1 < len(data_bytes):
                                reg_val = int.from_bytes(data_bytes[i:i+2], byteorder='big')
                                registers.append(reg_val)
                    else:
                        self.log("Ошибка: Слишком короткий пакет ответа")

                # ВАРИАНТ 2: Если движок вернул словарь
                elif isinstance(result, dict):
                    registers = result.get("registers", [])
                    self.log(f"Получены регистры из словаря: {registers}")
                
                else:
                    self.log(f"Неизвестный формат ответа: {result}")

                # ВЫВОД ТАБЛИЦЫ (Сработает динамически для любого количества параметров: от 1 до 28)
                if registers:
                    # Ограничиваем количество выводимых регистров тем, сколько реально запросили,
                    # чтобы не выйти за рамки массива, если устройство прислало чуть больше байт
                    registers = registers[:count]
                    
                    ascii_table = self.format_registers_to_ascii_table(slave_id, address, registers)
                    if ascii_table:
                        self.log_text.append(f"<pre style='color: #000000;'>{ascii_table}</pre>")
                        self.log_text.ensureCursorVisible()
                else:
                    self.log("Не удалось выделить регистры для отображения таблицы")

            except Exception as e:
                self.log(f"Ошибка чтения: {e}")

        else:  # WRITE
            # HEX поле (ИСПРАВЛЕНО: используем get_hex)
            value = self.get_hex(self.write_data.text(), 0)
            self.log(f"Запись: {self.modbus_engine.preview_request(slave_id=slave_id, function_code=6, address=address, value_or_count=value)}")

            try:
                response = self.modbus_engine.write_single_register(slave_id, address, value)
                self.log(f"Ответ: {response.hex(sep='')}")

            except Exception as e:
                self.log(f"Ошибка записи: {e}")
    
    def clear_log(self):
        self.log_text.clear()
        self.log("Журнал очищен")
    
    def log(self, msg):
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    def apply_styles(self):
        if not self.dark_mode:
            self.theme_btn.setText("🌙")
            self.setStyleSheet(load_stylesheet("gui/style_light_theme.qss"))
        else:
            self.theme_btn.setText("☀️")
            self.setStyleSheet(load_stylesheet("gui/style_dark_theme.qss"))

