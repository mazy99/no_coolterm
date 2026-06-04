

from gui.main_window.ui_gen.main_window_design import Ui_MainWindow
from PySide6.QtWidgets import QMainWindow, QApplication
from utils.style_loader import load_stylesheet


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setStyleSheet(load_stylesheet())
         


if __name__ == "__main__":

    app = QApplication([])
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    
    app.exec()