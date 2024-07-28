import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFileDialog, QLabel, QTextEdit, QProgressBar, QInputDialog, QMessageBox, QWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import subprocess
import requests
from deep_translator import GoogleTranslator
from PyQt5.QtGui import QIcon

class TranslatorThread(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(str)
    error = pyqtSignal(str)
    stopped = pyqtSignal()

    def __init__(self, subtitle_file, parent=None):
        super(TranslatorThread, self).__init__(parent)
        self.subtitle_file = subtitle_file
        self._is_running = True

    def run(self):
        try:
            with open(self.subtitle_file, 'rb') as f:
                response = requests.post("http://CoopTeam.pythonanywhere.com/translate", files={'file': f})
            if response.status_code == 200:
                translated_content = response.json().get("translated_content", "")
                self.result.emit(translated_content)
            else:
                self.error.emit(f"Translation failed: {response.json().get('error')}")
        except requests.ConnectionError:
            self.error.emit("Network error: Failed to connect to the server.")
        except Exception as e:
            self.error.emit(f"Translation failed. Please try again. {str(e)}")

    def stop(self):
        self._is_running = False
        self.stopped.emit()

class PlayerThread(QThread):
    def __init__(self, player_command, parent=None):
        super(PlayerThread, self).__init__(parent)
        self.player_command = player_command

    def run(self):
        try:
            subprocess.run(self.player_command)
        except FileNotFoundError:
            QMessageBox.warning(None, "Error", "Player is not installed or not found.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to play the video: {str(e)}")

class TarjamaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Tarjama")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('w.ico'))

        # Main layout
        self.centralWidget = QWidget()
        self.mainLayout = QHBoxLayout(self.centralWidget)

        # Sidebar
        self.sidebar = QVBoxLayout()

        self.sidebar_label = QLabel("Tarjama", self)
        self.sidebar_label.setAlignment(Qt.AlignCenter)
        self.sidebar.addWidget(self.sidebar_label)

        self.uploadButton = QPushButton("Upload Subtitle File", self)
        self.uploadButton.clicked.connect(self.uploadFile)
        self.sidebar.addWidget(self.uploadButton)

        self.translateButton = QPushButton("Translate File", self)
        self.translateButton.clicked.connect(self.translateFile)
        self.sidebar.addWidget(self.translateButton)

        self.stopButton = QPushButton("Stop Translating", self)
        self.stopButton.clicked.connect(self.stopTranslation)
        self.sidebar.addWidget(self.stopButton)

        self.saveButton = QPushButton("Save File", self)
        self.saveButton.clicked.connect(self.saveFile)
        self.sidebar.addWidget(self.saveButton)

        self.uploadTranslatedButton = QPushButton("Upload Translated File", self)
        self.uploadTranslatedButton.clicked.connect(self.uploadTranslatedFile)
        self.sidebar.addWidget(self.uploadTranslatedButton)

        self.sidebar.addStretch()

        self.statusLabel = QLabel("Status: Idle", self)
        self.sidebar.addWidget(self.statusLabel)

        self.progressBar = QProgressBar(self)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.sidebar.addWidget(self.progressBar)

        self.mainLayout.addLayout(self.sidebar, 1)

        # Main window for subtitles
        self.textEditLayout = QHBoxLayout()

        self.originalText = QTextEdit(self)
        self.originalText.setReadOnly(True)
        self.originalText.setPlaceholderText("Original Subtitle")
        self.textEditLayout.addWidget(self.originalText)

        self.translatedText = QTextEdit(self)
        self.translatedText.setPlaceholderText("Translated Subtitle")
        self.textEditLayout.addWidget(self.translatedText)

        self.mainLayout.addLayout(self.textEditLayout, 3)

        # Footer with video button
        self.footerLayout = QVBoxLayout()
        self.chooseVideoButton = QPushButton("Choose Video", self)
        self.chooseVideoButton.clicked.connect(self.chooseVideo)
        self.footerLayout.addWidget(self.chooseVideoButton)

        self.playButton = QPushButton("Play Video with Subtitles", self)
        self.playButton.clicked.connect(self.playVideo)
        self.footerLayout.addWidget(self.playButton)

        self.customPlayerButton = QPushButton("Set Custom Player", self)
        self.customPlayerButton.clicked.connect(self.setCustomPlayer)
        self.footerLayout.addWidget(self.customPlayerButton)

        self.videoStatusLabel = QLabel("", self)
        self.footerLayout.addWidget(self.videoStatusLabel)

        self.footerLayout.addStretch()

        self.mainLayout.addLayout(self.footerLayout)

        self.setCentralWidget(self.centralWidget)

        self.subtitle_file = None
        self.video_file = None
        self.translated_file = None
        self.translation_thread = None
        self.player_thread = None
        self.custom_player_path = None

    def uploadFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Subtitle File", "",
                                                  "Subtitle Files (*.srt *.ass *.ssa);;All Files (*)",
                                                  options=options)
        if fileName:
            try:
                with open(fileName, 'r', encoding='utf-8') as file:
                    self.subtitleContent = file.read()
                self.originalText.setPlainText(self.subtitleContent)
                self.subtitle_file = fileName
            except Exception:
                QMessageBox.critical(self, "Error", "Failed to read the subtitle file.")

    def translateFile(self):
        if self.subtitle_file:
            self.statusLabel.setText("Status: In Progress...")
            self.progressBar.setValue(0)
            self.translation_thread = TranslatorThread(self.subtitle_file)
            self.translation_thread.result.connect(self.displayTranslatedText)
            self.translation_thread.error.connect(self.showTranslationError)
            self.translation_thread.stopped.connect(self.translationStopped)
            self.translation_thread.start()
        else:
            QMessageBox.warning(self, "Error", "Please upload a subtitle file first.")

    def stopTranslation(self):
        if self.translation_thread and self.translation_thread.isRunning():
            self.translation_thread.stop()
            self.statusLabel.setText("Status: Stopped")

    def translationStopped(self):
        self.statusLabel.setText("Status: Stopped")

    def displayTranslatedText(self, translated_text):
        self.translatedContent = translated_text
        self.translatedText.setPlainText(self.translatedContent)
        self.statusLabel.setText("Status: Done")

    def saveFile(self):
        if self.subtitle_file:
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getSaveFileName(self, "Save Translated File", "",
                                                      "Subtitle Files (*.srt *.ass *.ssa);;All Files (*)",
                                                      options=options)
            if fileName:
                try:
                    editedContent = self.translatedText.toPlainText()
                    with open(fileName, 'w', encoding='utf-8') as file:
                        file.write(editedContent)
                    QMessageBox.information(self, "Success", f"Translated subtitle file saved at: {fileName}")
                except Exception:
                    QMessageBox.critical(self, "Error", "Failed to save the translated subtitle file.")
        else:
            QMessageBox.warning(self, "Error", "Please upload and translate a subtitle file first.")

    def chooseVideo(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Choose Video File", "",
                                                  "Video Files (*.mp4 *.mkv);;All Files (*)",
                                                  options=options)
        if fileName:
            self.video_file = fileName
            self.videoStatusLabel.setText("Video uploaded successfully.")

    def uploadTranslatedFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Translated Subtitle File", "",
                                                  "Subtitle Files (*.srt *.ass *.ssa);;All Files (*)",
                                                  options=options)
        if fileName:
            try:
                with open(fileName, 'r', encoding='utf-8') as file:
                    self.translatedContent = file.read()
                self.translatedText.setPlainText(self.translatedContent)
                self.translated_file = fileName
            except Exception:
                QMessageBox.critical(self, "Error", "Failed to read the translated subtitle file.")

    def playVideo(self):
        if not self.video_file or not (self.subtitle_file or self.translated_file):
            QMessageBox.warning(self, "Error", "Please upload a video and a subtitle file.")
            return

        subtitle_options = []
        if self.subtitle_file:
            subtitle_options.append("Original Subtitle")
        if self.translated_file:
            subtitle_options.append("Translated Subtitle")

        if not subtitle_options:
            QMessageBox.warning(self, "Error", "No subtitles available to play with the video.")
            return

        subtitle_choice, ok = QInputDialog.getItem(self, "Select Subtitle", "Choose a subtitle file:", subtitle_options, 0, False)
        if ok and subtitle_choice:
            if subtitle_choice == "Original Subtitle":
                subtitle_file_to_use = self.subtitle_file
            elif subtitle_choice == "Translated Subtitle":
                subtitle_file_to_use = self.translated_file

            players = ["mpv", "vlc", "custom"]
            player, ok = QInputDialog.getItem(self, "Select Player", "Choose a video player:", players, 0, False)

            if ok and player:
                if player == "mpv":
                    self.playWithMPV(subtitle_file_to_use)
                elif player == "vlc":
                    self.playWithVLC(subtitle_file_to_use)
                elif player == "custom":
                    if self.custom_player_path:
                        self.playWithCustomPlayer(subtitle_file_to_use)
                    else:
                        QMessageBox.warning(self, "Error", "No custom player path set.")

    def playWithMPV(self, subtitle_file):
        command = ["mpv", "--sub-file=" + subtitle_file, self.video_file]
        self.player_thread = PlayerThread(command)
        self.player_thread.start()

    def playWithVLC(self, subtitle_file):
        vlc_path = "vlc"
        if sys.platform.startswith('darwin'):  # macOS
            vlc_path = "/Applications/VLC.app/Contents/MacOS/VLC"
        command = [vlc_path, "--sub-file=" + subtitle_file, self.video_file]
        self.player_thread = PlayerThread(command)
        self.player_thread.start()

    def playWithCustomPlayer(self, subtitle_file):
        command = [self.custom_player_path, subtitle_file, self.video_file]
        self.player_thread = PlayerThread(command)
        self.player_thread.start()

    def setCustomPlayer(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Custom Player Executable", "",
                                                  "Executables (*.exe *.app *.sh);;All Files (*)",
                                                  options=options)
        if fileName:
            self.custom_player_path = fileName
            QMessageBox.information(self, "Success", f"Custom player set to: {fileName}")

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)

    def showTranslationError(self, message):
        self.statusLabel.setText("Status: Error")
        QMessageBox.critical(self, "Error", message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    translator_app = TarjamaApp()
    translator_app.show()
    sys.exit(app.exec_())
