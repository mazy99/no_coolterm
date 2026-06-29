"""Точка входа в приложение"""

import sys
import ctypes
from PyQt6.QtWidgets import QApplication
from gui.gui import ModbusTerminal


def main():

    try:
        myappid = "mycompany.modbusterminal.nocoolterm.1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        print(f"Не удалось установить AppUserModelID: {e}")
    app = QApplication(sys.argv)
    window = ModbusTerminal()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
