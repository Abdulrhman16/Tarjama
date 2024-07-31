from PyQt5.QtCore import QThread
import subprocess

class PlayerThread(QThread):
    def __init__(self, command, parent=None):
        super(PlayerThread, self).__init__(parent)
        self.command = command

    def run(self):
        subprocess.run(self.command)
