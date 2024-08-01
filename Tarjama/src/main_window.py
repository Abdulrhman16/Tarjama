import logging
import os
import json
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QTableWidget, QTableWidgetItem, QProgressBar, QInputDialog, QMessageBox, QWidget, QComboBox, QHeaderView, QListWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import pysrt
import ass
from .audio_processing import AudioProcessingThread
from .speech_recognition_thread import SpeechRecognitionThread
from .translation_thread import TranslatorThread
from .player_thread import PlayerThread
import sys
# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class MainWindow(QMainWindow):
    DATA_FILE = 'data.json'

    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_data()

    def initUI(self):
        self.setWindowTitle("Tarjama")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon('w.ico'))

        # Apply dark theme
        self.apply_dark_theme()

        # Main layout
        self.centralWidget = QWidget()
        self.mainLayout = QVBoxLayout(self.centralWidget)

        # Top layout
        self.topLayout = QHBoxLayout()

        # Sidebar
        self.sidebar = QVBoxLayout()

        self.sidebar_label = QLabel("Tarjama", self)
        self.sidebar_label.setAlignment(Qt.AlignCenter)
        self.sidebar.addWidget(self.sidebar_label)

        self.uploadButton = QPushButton("Upload Subtitle File", self)
        self.uploadButton.clicked.connect(self.uploadFile)
        self.sidebar.addWidget(self.uploadButton)

        self.uploadVideoButton = QPushButton("Upload Video File", self)
        self.uploadVideoButton.clicked.connect(self.uploadVideo)
        self.sidebar.addWidget(self.uploadVideoButton)

        self.uploadTestVideoButton = QPushButton("Upload Test Video", self)
        self.uploadTestVideoButton.clicked.connect(self.chooseVideo)
        self.sidebar.addWidget(self.uploadTestVideoButton)

        self.translateButton = QPushButton("Translate File", self)
        self.translateButton.clicked.connect(self.translateFile)
        self.sidebar.addWidget(self.translateButton)

        self.playTranslatedButton = QPushButton("Play Translated Video", self)
        self.playTranslatedButton.clicked.connect(self.playTranslatedVideo)
        self.sidebar.addWidget(self.playTranslatedButton)

        self.stopButton = QPushButton("Stop Translating", self)
        self.stopButton.clicked.connect(self.stopTranslation)
        self.sidebar.addWidget(self.stopButton)

        self.saveButton = QPushButton("Save File", self)
        self.saveButton.clicked.connect(self.saveFile)
        self.sidebar.addWidget(self.saveButton)

        self.saveOriginalButton = QPushButton("Save Original Text", self)
        self.saveOriginalButton.clicked.connect(self.saveOriginalFile)
        self.sidebar.addWidget(self.saveOriginalButton)

        self.uploadTranslatedButton = QPushButton("Upload Translated File", self)
        self.uploadTranslatedButton.clicked.connect(self.uploadTranslatedFile)
        self.sidebar.addWidget(self.uploadTranslatedButton)

        self.engineSelector = QComboBox(self)
        self.engineSelector.addItems(["Deep Translator", "Microsoft Translator"])
        self.sidebar.addWidget(self.engineSelector)

        self.sidebar.addStretch()

        self.statusLabel = QLabel("Status: Idle", self)
        self.sidebar.addWidget(self.statusLabel)

        self.progressBar = QProgressBar(self)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.sidebar.addWidget(self.progressBar)

        self.topLayout.addLayout(self.sidebar, 1)

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

        self.topLayout.addLayout(self.textEditLayout, 3)

        # Bottom layout for video
        self.bottomLayout = QHBoxLayout()

        self.videoList = QListWidget(self)
        self.videoList.itemClicked.connect(self.load_subtitles_for_video)
        self.bottomLayout.addWidget(self.videoList)

        self.subtitlesList = QListWidget(self)
        self.bottomLayout.addWidget(self.subtitlesList)

        self.deleteVideoButton = QPushButton("Delete Video", self)
        self.deleteVideoButton.clicked.connect(self.deleteVideo)
        self.bottomLayout.addWidget(self.deleteVideoButton)

        self.deleteSubtitleButton = QPushButton("Delete Subtitle", self)
        self.deleteSubtitleButton.clicked.connect(self.deleteSubtitle)
        self.bottomLayout.addWidget(self.deleteSubtitleButton)

        self.playVideoButton = QPushButton("Play Video", self)
        self.playVideoButton.clicked.connect(self.playVideo)
        self.bottomLayout.addWidget(self.playVideoButton)

        self.customPlayerButton = QPushButton("Set Custom Player", self)
        self.customPlayerButton.clicked.connect(self.setCustomPlayer)
        self.bottomLayout.addWidget(self.customPlayerButton)

        self.videoStatusLabel = QLabel("", self)
        self.bottomLayout.addWidget(self.videoStatusLabel)

        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addLayout(self.bottomLayout)

        self.setCentralWidget(self.centralWidget)

        self.subtitle_file = None
        self.subtitleContent = None
        self.video_file = None
        self.translated_file = None
        self.translation_thread = None
        self.player_thread = None
        self.custom_player_path = None
        self.current_video_id = None

    def save_data(self):
        data = {
            "videos": [self.videoList.item(i).text() for i in range(self.videoList.count())],
            "subtitles": [self.subtitlesList.item(i).text() for i in range(self.subtitlesList.count())]
        }
        with open(self.DATA_FILE, 'w') as f:
            json.dump(data, f)

    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, 'r') as f:
                data = json.load(f)
                self.videoList.addItems(data.get("videos", []))
                self.subtitlesList.addItems(data.get("subtitles", []))

    def load_videos(self):
        self.videoList.clear()
        videos = [('1', 'Sample Video 1'), ('2', 'Sample Video 2')]
        for video in videos:
            self.videoList.addItem(f"{video[0]}: {video[1]}")

    def load_subtitles_for_video(self, item):
        video_path = item.text()
        self.current_video_id = video_path
        # Load subtitles from a predefined list or any other source instead of the database
        subtitles = [('1', 'Sample Subtitle 1'), ('2', 'Sample Subtitle 2')]
        self.subtitlesList.clear()
        for subtitle in subtitles:
            self.subtitlesList.addItem(f"{subtitle[0]}: {subtitle[1]}")

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
                self.subtitlesList.addItem(fileName)
                self.save_data()
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

    def saveOriginalFile(self):
        if self.subtitleContent:
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getSaveFileName(self, "Save Original Text", "",
                                                      "Subtitle Files (*.srt *.ass *.ssa);;All Files (*)",
                                                      options=options)
            if fileName:
                try:
                    if fileName.endswith('.srt'):
                        self.subtitleContent.save(fileName, encoding='utf-8')
                    elif fileName.endswith('.ass') or fileName.endswith('.ssa'):
                        with open(fileName, 'w', encoding='utf-8') as f:
                            f.write(self.subtitleContent.to_string())
                    QMessageBox.information(self, "Success", f"Original subtitle file saved at: {fileName}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save the original subtitle file. {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "No original text to save.")

    def chooseVideo(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Choose Video File", "",
                                                  "Video Files (*.mp4 *.mkv);;All Files (*)",
                                                  options=options)
        if fileName:
            self.video_file = fileName
            self.videoStatusLabel.setText("Video uploaded successfully.")
            self.videoList.addItem(fileName)
            self.save_data()

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
                self.save_data()
            except Exception:
                QMessageBox.critical(self, "Error", "Failed to read the translated subtitle file.")

    def deleteVideo(self):
        current_item = self.videoList.currentItem()
        if current_item:
            self.videoList.takeItem(self.videoList.row(current_item))
            self.save_data()

    def deleteSubtitle(self):
        current_item = self.subtitlesList.currentItem()
        if current_item:
            self.subtitlesList.takeItem(self.subtitlesList.row(current_item))
            self.save_data()

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

    def showTranslationError(self, message):
        self.statusLabel.setText("Status: Error")
        QMessageBox.critical(self, "Error", message)

    def uploadVideo(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Video File", "",
                                                  "Video Files (*.mp4 *.mkv);;All Files (*)",
                                                  options=options)
        if fileName:
            self.video_file = fileName
            self.statusLabel.setText("Status: Extracting audio...")
            self.audio_processing_thread = AudioProcessingThread(self.video_file)
            self.audio_processing_thread.finished.connect(self.extract_and_translate_audio)
            self.audio_processing_thread.error.connect(self.showTranslationError)
            self.audio_processing_thread.start()
            self.videoList.addItem(fileName)
            self.save_data()

    def extract_and_translate_audio(self, audio_chunks_and_sample_rate):
        audio_chunks, timestamps, sample_rate = audio_chunks_and_sample_rate
        self.statusLabel.setText("Status: Extracting and Transcribing Audio...")
        self.progressBar.setValue(0)

        self.speech_thread = SpeechRecognitionThread(audio_chunks, timestamps, sample_rate)
        self.speech_thread.result.connect(self.on_audio_extracted)
        self.speech_thread.error.connect(self.showTranslationError)
        self.speech_thread.finished.connect(lambda: self.cleanup_audio_chunks(audio_chunks))
        self.speech_thread.start()

    def on_audio_extracted(self, transcript_with_timestamps):
        if not transcript_with_timestamps:
            QMessageBox.critical(self, "Error", "Speech recognition failed")
            return

        # Combine words into subtitles
        subtitles = []
        current_subtitle = []
        max_words_per_subtitle = 6
        min_words_per_subtitle = 3

        for word_info in transcript_with_timestamps:
            current_subtitle.append(word_info)

            if len(current_subtitle) >= max_words_per_subtitle or \
               (len(current_subtitle) >= min_words_per_subtitle and \
                word_info['end_time'] - current_subtitle[0]['start_time'] > 2000):
                start_time = current_subtitle[0]['start_time']
                end_time = current_subtitle[-1]['end_time']
                text = ' '.join([word['word'] for word in current_subtitle])
                subtitles.append(pysrt.SubRipItem(index=len(subtitles) + 1,
                                                  start=pysrt.SubRipTime(milliseconds=start_time),
                                                  end=pysrt.SubRipTime(milliseconds=end_time),
                                                  text=text))
                current_subtitle = []

        # Handle remaining words
        if current_subtitle:
            start_time = current_subtitle[0]['start_time']
            end_time = current_subtitle[-1]['end_time']
            text = ' '.join([word['word'] for word in current_subtitle])
            subtitles.append(pysrt.SubRipItem(len(subtitles) + 1,
                                              start=pysrt.SubRipTime(milliseconds=start_time),
                                              end=pysrt.SubRipTime(milliseconds=end_time),
                                              text=text))

        # Save the extracted subtitles to an SRT file
        extracted_subtitles = pysrt.SubRipFile(items=subtitles)
        self.subtitle_file = "extracted_subtitles.srt"
        extracted_subtitles.save(self.subtitle_file, encoding='utf-8')
        self.subtitleContent = extracted_subtitles

        self.loadSubtitles(self.originalTable, self.subtitleContent)
        self.statusLabel.setText("Status: Done")
        QMessageBox.information(self, "Success", "Audio extracted and transcribed successfully")

    def cleanup_audio_chunks(self, audio_chunks):
        for chunk in audio_chunks:
            if os.path.exists(chunk):
                os.remove(chunk)
                logging.debug('Deleted chunk file: %s', chunk)

    def apply_dark_theme(self):
        dark_stylesheet = """
        QWidget {
            background-color: #2E2E2E;
            color: #FFFFFF;
        }
        QPushButton {
            background-color: #4E4E4E;
            color: #FFFFFF;
        }
        QTableWidget {
            background-color: #2E2E2E;
            color: #FFFFFF;
        }
        QHeaderView::section {
            background-color: #4E4E4E;
            color: #FFFFFF;
        }
        QListWidget {
            background-color: #2E2E2E;
            color: #FFFFFF;
        }
        """
        self.setStyleSheet(dark_stylesheet)

    def playTranslatedVideo(self):
        if not self.video_file or not self.translated_file:
            QMessageBox.warning(self, "Error", "Please upload a video and translate a subtitle file.")
            return

        self.playVideo()
