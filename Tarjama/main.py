import os
from PyQt5.QtWidgets import QApplication
from src.main_window import MainWindow
import sys
import logging

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/abdulrhmanfahd/Documents/GitHub/Tarjama/Tarjama/credentials/ab16hul-59296cd58c00.json'

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()