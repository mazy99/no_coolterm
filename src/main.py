"""Точка входа в приложение"""

import sys
from PyQt6.QtWidgets import QApplication
from gui import ModbusTerminal

def main():
    app = QApplication(sys.argv)
    window = ModbusTerminal()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()