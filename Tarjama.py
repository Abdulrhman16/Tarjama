import sys
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFileDialog, QLabel, QTableWidget, QTableWidgetItem, QProgressBar, QInputDialog, QMessageBox, QWidget, QComboBox, QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import subprocess
import requests
from deep_translator import GoogleTranslator
from PyQt5.QtGui import QIcon
import pysrt
import ass
import openai

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

openai.api_key = 'sk-proj-pZzZVlZwF7qkz8Unl8qzT3BlbkFJvjfbifWKqj2y5zIg7sYF'  # Replace with your OpenAI API key

class TranslatorThread(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(list)
    error = pyqtSignal(str)
    stopped = pyqtSignal()

    def __init__(self, subtitles, engine, parent=None):
        super(TranslatorThread, self).__init__(parent)
        self.subtitles = subtitles
        self.engine = engine
        self._is_running = True

    def run(self):
        try:
            if self.engine == "Deep Translator":
                translated_content = self.translate_with_deep_translator(self.subtitles)
                self.result.emit(translated_content)
            elif self.engine == "ChatGPT":
                self.translate_with_chatgpt(self.subtitles)
        except requests.ConnectionError:
            self.error.emit("Network error: Failed to connect to the server.")
        except Exception as e:
            self.error.emit(f"Translation failed. Please try again. {str(e)}")

    def translate_with_deep_translator(self, subtitles):
        original_texts = [subtitle.text for subtitle in subtitles]
        translator = GoogleTranslator(source='en', target='ar')
        translated_texts = []
        for text in original_texts:
            if not self._is_running:
                break
            translated_texts.append(translator.translate(text))
        return translated_texts

    def translate_with_chatgpt(self, subtitles):
        original_texts = [(i, subtitle.text) for i, subtitle in enumerate(subtitles)]
        translated_texts = []
        batch_size = 20  # Adjust batch size as needed
        for i in range(0+1, len(original_texts), batch_size):
            batch = original_texts[i:i+batch_size]
            batch_text = "\n".join([f"{index}: {text}" for index, text in batch])
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Translate the following English subtitles to Arabic while maintaining the subtitle format , line numbers and text in same line number before translated. and translated the line literaly without take care on other context"},
                        {"role": "user", "content": batch_text}
                    ],
                    temperature=0,
                    top_p=0.0,
                )
                translated_batch = response['choices'][0]['message']['content']
                translated_lines = self.parse_translated_batch(translated_batch)
                translated_texts.extend(translated_lines)
                self.progress.emit(len(translated_texts))
            except Exception as e:
                self.error.emit(f"Translation failed. {str(e)}")
                return
        self.result.emit(translated_texts)

    def parse_translated_batch(self, translated_batch):
        # Split the response by lines and parse the index and text
        translated_lines = translated_batch.split('\n')
        parsed_lines = []
        for line in translated_lines:
            if ':' in line:
                index, text = line.split(':', 1)
                parsed_lines.append((int(index.strip()), text.strip()))
        # Sort by index to maintain the original order
        parsed_lines.sort(key=lambda x: x[0]) #test 1
        return [text for index, text in parsed_lines]

    def stop(self):
        self._is_running = False
        self.stopped.emit()

class PlayerThread(QThread):
    def __init__(self, player_command, parent=None):
        super(PlayerThread, self).__init__(parent)
        self.player_command = player_command

    def run(self):
        try:
            subprocess.run(self.player_command, check=True)
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
        self.setGeometry(100, 100, 1000, 600)
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

        self.engineSelector = QComboBox(self)
        self.engineSelector.addItems(["Deep Translator", "ChatGPT"])
        self.sidebar.addWidget(self.engineSelector)

        self.sidebar.addStretch()

        self.statusLabel = QLabel("Status: Idle", self)
        self.sidebar.addWidget(self.statusLabel)

        self.progressBar = QProgressBar(self)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.sidebar.addWidget(self.progressBar)

        self.mainLayout.addLayout(self.sidebar, 1)

        # Main window for subtitles
        self.textEditLayout = QHBoxLayout()

        self.originalTable = QTableWidget(self)
        self.originalTable.setColumnCount(2)
        self.originalTable.setHorizontalHeaderLabels(["Start", "Original Subtitle"])
        self.originalTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.textEditLayout.addWidget(self.originalTable)

        self.translatedTable = QTableWidget(self)
        self.translatedTable.setColumnCount(2)
        self.translatedTable.setHorizontalHeaderLabels(["Start", "Translated Subtitle"])
        self.translatedTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.textEditLayout.addWidget(self.translatedTable)

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
                self.subtitle_file = fileName
                if fileName.endswith('.srt'):
                    self.subtitleContent = pysrt.open(fileName, encoding='utf-8')
                elif fileName.endswith('.ass') or fileName.endswith('.ssa'):
                    with open(fileName, 'r', encoding='utf-8') as f:
                        self.subtitleContent = ass.parse(f)
                self.loadSubtitles(self.originalTable, self.subtitleContent)
            except Exception:
                QMessageBox.critical(self, "Error", "Failed to read the subtitle file.")

    def loadSubtitles(self, table, subtitles):
        if isinstance(subtitles, pysrt.SubRipFile):
            table.setRowCount(len(subtitles))
            for i, subtitle in enumerate(subtitles):
                start_item = QTableWidgetItem(str(subtitle.start))
                text_item = QTableWidgetItem(subtitle.text)
                table.setItem(i, 0, start_item)
                table.setItem(i, 1, text_item)
        elif isinstance(subtitles, ass.document.Document):
            events = [event for event in subtitles.events if event.type == 'Dialogue']
            table.setRowCount(len(events))
            for i, event in enumerate(events):
                start_item = QTableWidgetItem(str(event.start))
                text_item = QTableWidgetItem(event.text)
                table.setItem(i, 0, start_item)
                table.setItem(i, 1, text_item)

    def getSubtitlesFromTable(self, table, original_subtitles):
        if isinstance(original_subtitles, pysrt.SubRipFile):
            for row in range(table.rowCount()):
                text_item = table.item(row, 1)
                if text_item:
                    original_subtitles[row].text = text_item.text()
            return original_subtitles
        elif isinstance(original_subtitles, ass.document.Document):
            events = [event for event in original_subtitles.events if event.type == 'Dialogue']
            for row in range(table.rowCount()):
                text_item = table.item(row, 1)
                if text_item:
                    events[row].text = text_item.text()
            return original_subtitles

    def translateFile(self):
        if self.subtitle_file:
            self.statusLabel.setText("Status: In Progress...")
            self.progressBar.setValue(0)
            selected_engine = self.engineSelector.currentText()
            self.translation_thread = TranslatorThread(self.subtitleContent, selected_engine)
            self.translation_thread.result.connect(self.updateTableWithTranslation)
            self.translation_thread.error.connect(self.showTranslationError)
            self.translation_thread.stopped.connect(self.translationStopped)
            self.translation_thread.start()
        else:
            QMessageBox.warning(self, "Error", "Please upload a subtitle file first.")

    def updateTableWithTranslation(self, translated_texts):
        logging.debug(f'Updating table with translated texts: {translated_texts}')
        if isinstance(self.subtitleContent, pysrt.SubRipFile):
            for i, subtitle in enumerate(self.subtitleContent):
                if i < len(translated_texts):
                    subtitle.text = translated_texts[i]
                else:
                    logging.error(f"Missing translation for subtitle {i}: {subtitle.text}")
            self.loadSubtitles(self.translatedTable, self.subtitleContent)
        elif isinstance(self.subtitleContent, ass.document.Document):
            events = [event for event in self.subtitleContent.events if event.type == 'Dialogue']
            for i, event in enumerate(events):
                if i < len(translated_texts):
                    event.text = translated_texts[i]
                else:
                    logging.error(f"Missing translation for event {i}: {event.text}")
            self.loadSubtitles(self.translatedTable, self.subtitleContent)
        self.statusLabel.setText("Status: Done")

    def stopTranslation(self):
        if self.translation_thread and self.translation_thread.isRunning():
            self.translation_thread.stop()
            self.statusLabel.setText("Status: Stopped")

    def translationStopped(self):
        self.statusLabel.setText("Status: Stopped")

    def displayTranslatedText(self, translated_texts):
        logging.debug(f'Displaying translated texts: {translated_texts}')
        for i, translated_text in enumerate(translated_texts):
            self.translatedTable.setItem(i, 1, QTableWidgetItem(translated_text))
        self.statusLabel.setText("Status: Done")

    def saveFile(self):
        if self.subtitle_file:
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getSaveFileName(self, "Save Translated File", "",
                                                      "Subtitle Files (*.srt *.ass *.ssa);;All Files (*)",
                                                      options=options)
            if fileName:
                try:
                    edited_subtitles = self.getSubtitlesFromTable(self.translatedTable, self.subtitleContent)
                    if fileName.endswith('.srt'):
                        edited_subtitles.save(fileName, encoding='utf-8')
                    elif fileName.endswith('.ass') or fileName.endswith('.ssa'):
                        with open(fileName, 'w', encoding='utf-8') as f:
                            f.write(edited_subtitles.to_string())
                    QMessageBox.information(self, "Success", f"Translated subtitle file saved at: {fileName}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save the translated subtitle file. {str(e)}")
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
                if fileName.endswith('.srt'):
                    self.translatedContent = pysrt.open(fileName, encoding='utf-8')
                elif fileName.endswith('.ass') or fileName.endswith('.ssa'):
                    with open(fileName, 'r', encoding='utf-8') as f:
                        self.translatedContent = ass.parse(f)
                self.loadSubtitles(self.translatedTable, self.translatedContent)
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
        elif sys.platform.startswith('win'):  # Windows
            vlc_path = "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"
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
