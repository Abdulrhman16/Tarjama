# src/main.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from file_upload import FileUpload

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Tarjama - Translation Application")
        self.setGeometry(100, 100, 600, 400)
        
        self.fileUpload = FileUpload()
        self.setCentralWidget(self.fileUpload)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
