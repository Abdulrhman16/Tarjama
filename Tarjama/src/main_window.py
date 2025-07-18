import logging
import os
import shutil
import json
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QTableWidget, QTableWidgetItem, QProgressBar, QInputDialog, QMessageBox, QWidget, QComboBox, QHeaderView, QListWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
import pysrt
import ass,sys
from .audio_processing import AudioProcessingThread
from .speech_recognition_thread import SpeechRecognitionThread
from .translation_thread import TranslatorThread
from .player_thread import PlayerThread

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class MainWindow(QMainWindow):
    DATA_FILE = 'data.json'
    DATA_DIR = 'data'
    
    PRIMARY_COLOR = "#4E4E4E"
    SECONDARY_COLOR = "#2E2E2E"
    BACKGROUND_COLOR = "#1E1E1E"
    BUTTON_COLOR = "#5E5E5E"
    TEXT_COLOR = "#FFFFFF"
    FONT_FAMILY = "Arial"
    BUTTON_FONT_SIZE = 10

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

        # Top layout for subtitle editing and translation
        self.topLayout = QHBoxLayout()

        # Sidebar
        self.sidebar = QVBoxLayout()

        self.sidebar_label = QLabel("Tarjama", self)
        self.sidebar_label.setAlignment(Qt.AlignCenter)
        self.sidebar_label.setFont(QFont(self.FONT_FAMILY, 16, QFont.Bold))
        self.sidebar.addWidget(self.sidebar_label)

        self.projectLabel = QLabel("Select Project")
        self.sidebar.addWidget(self.projectLabel)
        self.projectComboBox = QComboBox(self)
        self.projectComboBox.currentIndexChanged.connect(self.load_project_data)
        self.sidebar.addWidget(self.projectComboBox)

        self.newProjectButton = QPushButton("New Project", self)
        self.newProjectButton.clicked.connect(self.create_new_project)
        self.style_button(self.newProjectButton)
        self.sidebar.addWidget(self.newProjectButton)

        self.uploadButton = QPushButton("Upload Subtitle File", self)
        self.uploadButton.clicked.connect(self.uploadFile)
        self.style_button(self.uploadButton)
        self.sidebar.addWidget(self.uploadButton)

        self.uploadVideoButton = QPushButton("Upload Video File", self)
        self.uploadVideoButton.clicked.connect(self.uploadVideo)
        self.style_button(self.uploadVideoButton)
        self.sidebar.addWidget(self.uploadVideoButton)

        self.translateButton = QPushButton("Translate File", self)
        self.translateButton.clicked.connect(self.translateFile)
        self.style_button(self.translateButton)
        self.sidebar.addWidget(self.translateButton)

        self.stopButton = QPushButton("Stop Translating", self)
        self.stopButton.clicked.connect(self.stopTranslation)
        self.style_button(self.stopButton)
        self.sidebar.addWidget(self.stopButton)

        self.saveButton = QPushButton("Save File", self)
        self.saveButton.clicked.connect(self.saveFile)
        self.style_button(self.saveButton)
        self.sidebar.addWidget(self.saveButton)

        self.saveOriginalButton = QPushButton("Save Original Text", self)
        self.saveOriginalButton.clicked.connect(self.saveOriginalFile)
        self.style_button(self.saveOriginalButton)
        self.sidebar.addWidget(self.saveOriginalButton)

        self.uploadTranslatedButton = QPushButton("Upload Translated File", self)
        self.uploadTranslatedButton.clicked.connect(self.uploadTranslatedFile)
        self.style_button(self.uploadTranslatedButton)
        self.sidebar.addWidget(self.uploadTranslatedButton)

        self.addExternalSubtitleButton = QPushButton("Add External Subtitle", self)
        self.addExternalSubtitleButton.clicked.connect(self.addExternalSubtitle)
        self.style_button(self.addExternalSubtitleButton)
        self.sidebar.addWidget(self.addExternalSubtitleButton)

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
        self.textEditLayout = QVBoxLayout()

        self.originalTableLabel = QLabel("Original Subtitles")
        self.textEditLayout.addWidget(self.originalTableLabel)
        self.originalTable = QTableWidget(self)
        self.originalTable.setColumnCount(2)
        self.originalTable.setHorizontalHeaderLabels(["Start", "Original Subtitle"])
        self.originalTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.textEditLayout.addWidget(self.originalTable)

        self.translatedTableLabel = QLabel("Translated Subtitles")
        self.textEditLayout.addWidget(self.translatedTableLabel)
        self.translatedTable = QTableWidget(self)
        self.translatedTable.setColumnCount(2)
        self.translatedTable.setHorizontalHeaderLabels(["Start", "Translated Subtitle"])
        self.translatedTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.textEditLayout.addWidget(self.translatedTable)

        self.topLayout.addLayout(self.textEditLayout, 3)

        # Bottom layout for video and subtitle lists and controls
        self.bottomLayout = QVBoxLayout()

        self.managementLabel = QLabel("Testing and Managing Database")
        self.managementLabel.setAlignment(Qt.AlignCenter)
        self.bottomLayout.addWidget(self.managementLabel)

        listsLayout = QHBoxLayout()

        videoLayout = QVBoxLayout()
        self.videoListLabel = QLabel("Videos")
        videoLayout.addWidget(self.videoListLabel)
        self.videoList = QListWidget(self)
        self.videoList.setMaximumWidth(300)
        self.videoList.itemClicked.connect(self.load_subtitles_for_video)
        videoLayout.addWidget(self.videoList)
        listsLayout.addLayout(videoLayout)

        subtitleLayout = QVBoxLayout()
        self.subtitlesListLabel = QLabel("Subtitles")
        subtitleLayout.addWidget(self.subtitlesListLabel)
        self.subtitlesList = QListWidget(self)
        self.subtitlesList.setMaximumWidth(300)
        self.subtitlesList.itemClicked.connect(self.display_subtitle)
        subtitleLayout.addWidget(self.subtitlesList)
        listsLayout.addLayout(subtitleLayout)

        self.bottomLayout.addLayout(listsLayout)

        buttonLayout = QHBoxLayout()
        self.deleteVideoButton = QPushButton("Delete Video", self)
        self.deleteVideoButton.clicked.connect(self.deleteVideo)
        self.style_button(self.deleteVideoButton)
        buttonLayout.addWidget(self.deleteVideoButton)

        self.deleteSubtitleButton = QPushButton("Delete Subtitle", self)
        self.deleteSubtitleButton.clicked.connect(self.deleteSubtitle)
        self.style_button(self.deleteSubtitleButton)
        buttonLayout.addWidget(self.deleteSubtitleButton)

        self.playVideoButton = QPushButton("Play Video", self)
        self.playVideoButton.clicked.connect(self.playVideo)
        self.style_button(self.playVideoButton)
        buttonLayout.addWidget(self.playVideoButton)

        self.customPlayerButton = QPushButton("Set Custom Player", self)
        self.customPlayerButton.clicked.connect(self.setCustomPlayer)
        self.style_button(self.customPlayerButton)
        buttonLayout.addWidget(self.customPlayerButton)

        self.bottomLayout.addLayout(buttonLayout)

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

        # Create data directory if it doesn't exist
        if not os.path.exists(self.DATA_DIR):
            os.makedirs(self.DATA_DIR)

    def save_data(self):
        data = {
            "projects": {}
        }
        for i in range(self.projectComboBox.count()):
            project_name = self.projectComboBox.itemText(i)
            if project_name == self.projectComboBox.currentText():
                videos = [self.videoList.item(j).text() for j in range(self.videoList.count())]
                subtitles = [self.subtitlesList.item(j).text() for j in range(self.subtitlesList.count())]
                data["projects"][project_name] = {
                    "videos": videos,
                    "subtitles": subtitles
                }
            else:
                data["projects"][project_name] = self.load_project_data_from_file(project_name)
        with open(self.DATA_FILE, 'w') as f:
            json.dump(data, f)

    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, 'r') as f:
                data = json.load(f)
                for project_name in data.get("projects", {}).keys():
                    self.projectComboBox.addItem(project_name)
                self.load_project_data()

    def load_project_data_from_file(self, project_name):
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, 'r') as f:
                data = json.load(f)
                return data.get("projects", {}).get(project_name, {"videos": [], "subtitles": []})
        return {"videos": [], "subtitles": []}

    def load_project_data(self):
        project_name = self.projectComboBox.currentText()
        self.clear_tables()
        self.videoList.clear()
        self.subtitlesList.clear()
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, 'r') as f:
                data = json.load(f)
                project_data = data["projects"].get(project_name, {})
                self.videoList.addItems(project_data.get("videos", []))
                self.subtitlesList.addItems(project_data.get("subtitles", []))

    def clear_tables(self):
        self.originalTable.setRowCount(0)
        self.translatedTable.setRowCount(0)

    def create_new_project(self):
        project_name, ok = QInputDialog.getText(self, "New Project", "Enter project name:")
        if ok and project_name:
            self.projectComboBox.addItem(project_name)
            self.projectComboBox.setCurrentText(project_name)
            self.save_data()

    def load_videos(self):
        self.videoList.clear()
        videos = [f for f in os.listdir(self.DATA_DIR) if f.endswith(('.mp4', '.mkv'))]
        for video in videos:
            self.videoList.addItem(video)

    def load_subtitles_for_video(self, item):
        project_name = self.projectComboBox.currentText()
        video_path = os.path.join(self.DATA_DIR, project_name, item.text())
        self.current_video_id = video_path
        # Load associated subtitles
        subtitle_files = [f for f in os.listdir(os.path.join(self.DATA_DIR, project_name)) if f.startswith(os.path.splitext(item.text())[0])]
        self.subtitlesList.clear()
        for subtitle in subtitle_files:
            self.subtitlesList.addItem(subtitle)

    def uploadFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Subtitle File", "",
                                                  "Subtitle Files (*.srt *.ass *.ssa);;All Files (*)",
                                                  options=options)
        if fileName:
            try:
                project_name = self.projectComboBox.currentText()
                dest_dir = os.path.join(self.DATA_DIR, project_name)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                dest_path = os.path.join(dest_dir, os.path.basename(fileName))
                self.prompt_save_file(fileName, dest_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read the subtitle file: {str(e)}")

    def prompt_save_file(self, src_path, dest_path):
        reply = QMessageBox.question(self, 'Save File', 'Do you want to save the file in the data directory?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            shutil.copy(src_path, dest_path)
            self.subtitle_file = dest_path
            self.process_subtitle_file(dest_path)
            if os.path.basename(dest_path) not in [self.subtitlesList.item(i).text() for i in range(self.subtitlesList.count())]:
                self.subtitlesList.addItem(os.path.basename(dest_path))
            self.save_data()
        else:
            self.process_subtitle_file(src_path)
            self.add_save_button(dest_path)

    def process_subtitle_file(self, file_path):
        if file_path.endswith('.srt'):
            self.subtitleContent = pysrt.open(file_path, encoding='utf-8')
        elif file_path.endswith('.ass') or file_path.endswith('.ssa'):
            with open(file_path, 'r', encoding='utf-8') as f:
                self.subtitleContent = ass.parse(f)
        self.loadSubtitles(self.originalTable, self.subtitleContent)

    def add_save_button(self, dest_path):
        save_button = QPushButton("Save to Data Directory", self)
        save_button.clicked.connect(lambda: self.save_to_data_directory(dest_path))
        self.style_button(save_button)
        self.sidebar.addWidget(save_button)

    def save_to_data_directory(self, dest_path):
        shutil.copy(self.subtitle_file, dest_path)
        if os.path.basename(dest_path) not in [self.subtitlesList.item(i).text() for i in range(self.subtitlesList.count())]:
            self.subtitlesList.addItem(os.path.basename(dest_path))
        self.save_data()
        QMessageBox.information(self, "Success", f"File saved at: {dest_path}")

    def loadSubtitles(self, table, subtitles):
        table.setRowCount(len(subtitles))
        if isinstance(subtitles, pysrt.SubRipFile):
            for i, subtitle in enumerate(subtitles):
                start_item = QTableWidgetItem(str(subtitle.start))
                text_item = QTableWidgetItem(subtitle.text)
                table.setItem(i, 0, start_item)
                table.setItem(i, 1, text_item)
        elif isinstance(subtitles, ass.document.Document):
            events = [event for event in subtitles.events if event.type == 'Dialogue']
            for i, event in enumerate(events):
                start_item = QTableWidgetItem(str(event.start))
                text_item = QTableWidgetItem(event.text)
                table.setItem(i, 0, start_item)
                table.setItem(i, 1, text_item)

    def translateFile(self):
        if self.subtitle_file and self.originalTable.rowCount() > 0:
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
        self.save_translated_subtitles()

    def save_translated_subtitles(self):
        if self.subtitle_file and self.originalTable.rowCount() > 0:
            project_name = self.projectComboBox.currentText()
            dest_dir = os.path.join(self.DATA_DIR, project_name)
            dest_path = os.path.join(dest_dir, os.path.basename(self.subtitle_file).replace(".srt", "_translated.srt"))
            self.getSubtitlesFromTable(self.translatedTable, self.subtitleContent).save(dest_path, encoding='utf-8')
            if os.path.basename(dest_path) not in [self.subtitlesList.item(i).text() for i in range(self.subtitlesList.count())]:
                self.subtitlesList.addItem(os.path.basename(dest_path))
            self.save_data()

    def stopTranslation(self):
        if self.translation_thread and self.translation_thread.isRunning():
            self.translation_thread.stop()
            self.statusLabel.setText("Status: Stopped")

    def translationStopped(self):
        self.statusLabel.setText("Status: Stopped")

    def saveFile(self):
        if self.subtitle_file and self.originalTable.rowCount() > 0:
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getSaveFileName(self, "Save Translated File", "",
                                                      "Subtitle Files (*.srt *.ass *.ssa);;All Files (*)",
                                                      options=options)
            if fileName:
                try:
                    edited_subtitles = self.getSubtitlesFromTable(self.translatedTable, self.subtitleContent)
                    dest_path = os.path.join(self.DATA_DIR, self.projectComboBox.currentText(), os.path.basename(fileName))
                    self.prompt_save_file(fileName, dest_path)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save the translated subtitle file: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Please upload and translate a subtitle file first.")

    def saveOriginalFile(self):
        if self.subtitleContent and self.originalTable.rowCount() > 0:
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getSaveFileName(self, "Save Original Text", "",
                                                      "Subtitle Files (*.srt *.ass *.ssa);;All Files (*)",
                                                      options=options)
            if fileName:
                try:
                    dest_path = os.path.join(self.DATA_DIR, self.projectComboBox.currentText(), os.path.basename(fileName))
                    self.prompt_save_file(fileName, dest_path)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save the original subtitle file: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "No original text to save.")

    def chooseVideo(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Choose Video File", "",
                                                  "Video Files (*.mp4 *.mkv);;All Files (*)",
                                                  options=options)
        if fileName:
            project_name = self.projectComboBox.currentText()
            dest_dir = os.path.join(self.DATA_DIR, project_name)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            dest_path = os.path.join(dest_dir, os.path.basename(fileName))
            shutil.copy(fileName, dest_path)
            self.video_file = dest_path
            self.videoStatusLabel.setText("Video uploaded successfully.")
            if os.path.basename(dest_path) not in [self.videoList.item(i).text() for i in range(self.videoList.count())]:
                self.videoList.addItem(os.path.basename(dest_path))
            self.save_data()

    def uploadTranslatedFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Translated Subtitle File", "",
                                                  "Subtitle Files (*.srt *.ass *.ssa);;All Files (*)",
                                                  options=options)
        if fileName:
            try:
                project_name = self.projectComboBox.currentText()
                dest_dir = os.path.join(self.DATA_DIR, project_name)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                dest_path = os.path.join(dest_dir, os.path.basename(fileName))
                self.prompt_save_file(fileName, dest_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read the translated subtitle file: {str(e)}")

    def deleteVideo(self):
        current_item = self.videoList.currentItem()
        if current_item:
            project_name = self.projectComboBox.currentText()
            video_path = os.path.join(self.DATA_DIR, project_name, current_item.text())
            if os.path.exists(video_path):
                os.remove(video_path)
            self.videoList.takeItem(self.videoList.row(current_item))
            self.save_data()

    def deleteSubtitle(self):
        current_item = self.subtitlesList.currentItem()
        if current_item:
            project_name = self.projectComboBox.currentText()
            subtitle_path = os.path.join(self.DATA_DIR, project_name, current_item.text())
            if os.path.exists(subtitle_path):
                os.remove(subtitle_path)
            self.subtitlesList.takeItem(self.subtitlesList.row(current_item))
            self.save_data()

    def playVideo(self):
        if not self.video_file or not (self.subtitle_file or self.translated_file):
            QMessageBox.warning(self, "Error", "Please upload a video and a subtitle file.")
            return

        project_choice, ok = QInputDialog.getItem(self, "Select Project", "Choose a project:", [self.projectComboBox.currentText()], 0, False)
        if not ok or not project_choice:
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
            project_name = self.projectComboBox.currentText()
            dest_dir = os.path.join(self.DATA_DIR, project_name)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            dest_path = os.path.join(dest_dir, os.path.basename(fileName))
            shutil.copy(fileName, dest_path)
            self.video_file = dest_path
            self.statusLabel.setText("Status: Extracting audio...")
            self.audio_processing_thread = AudioProcessingThread(self.video_file)
            self.audio_processing_thread.finished.connect(self.extract_and_translate_audio)
            self.audio_processing_thread.error.connect(self.showTranslationError)
            self.audio_processing_thread.start()
            if os.path.basename(dest_path) not in [self.videoList.item(i).text() for i in range(self.videoList.count())]:
                self.videoList.addItem(os.path.basename(dest_path))
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
            subtitles.append(pysrt.SubRipItem(index=len(subtitles) + 1,
                                              start=pysrt.SubRipTime(milliseconds=start_time),
                                              end=pysrt.SubRipTime(milliseconds=end_time),
                                              text=text))

        # Save the extracted subtitles to an SRT file
        project_name = self.projectComboBox.currentText()
        dest_dir = os.path.join(self.DATA_DIR, project_name)
        self.subtitle_file = os.path.join(dest_dir, "extracted_subtitles.srt")
        extracted_subtitles = pysrt.SubRipFile(items=subtitles)
        extracted_subtitles.save(self.subtitle_file, encoding='utf-8')
        self.subtitleContent = extracted_subtitles

        self.loadSubtitles(self.originalTable, self.subtitleContent)
        if os.path.basename(self.subtitle_file) not in [self.subtitlesList.item(i).text() for i in range(self.subtitlesList.count())]:
            self.subtitlesList.addItem(os.path.basename(self.subtitle_file))
        self.save_data()
        self.statusLabel.setText("Status: Done")
        QMessageBox.information(self, "Success", "Audio extracted and transcribed successfully")

    def cleanup_audio_chunks(self, audio_chunks):
        for chunk in audio_chunks:
            if os.path.exists(chunk):
                os.remove(chunk)
                logging.debug('Deleted chunk file: %s', chunk)

    def addExternalSubtitle(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open External Subtitle File", "",
                                                  "Subtitle Files (*.srt *.ass *.ssa);;All Files (*)",
                                                  options=options)
        if fileName:
            try:
                project_name = self.projectComboBox.currentText()
                dest_dir = os.path.join(self.DATA_DIR, project_name)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                dest_path = os.path.join(dest_dir, os.path.basename(fileName))
                shutil.copy(fileName, dest_path)
                if fileName.endswith('.srt'):
                    external_subtitle = pysrt.open(dest_path, encoding='utf-8')
                elif fileName.endswith('.ass') or fileName.endswith('.ssa'):
                    with open(dest_path, 'r', encoding='utf-8') as f:
                        external_subtitle = ass.parse(f)
                self.loadSubtitles(self.translatedTable, external_subtitle)
                self.translated_file = dest_path
                if os.path.basename(dest_path) not in [self.subtitlesList.item(i).text() for i in range(self.subtitlesList.count())]:
                    self.subtitlesList.addItem(os.path.basename(dest_path))
                self.save_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read the external subtitle file: {str(e)}")

    def apply_dark_theme(self):
        dark_stylesheet = f"""
        QWidget {{
            background-color: {self.BACKGROUND_COLOR};
            color: {self.TEXT_COLOR};
        }}
        QPushButton {{
            background-color: {self.BUTTON_COLOR};
            color: {self.TEXT_COLOR};
            border-radius: 10px;
            padding: 5px;
            font-size: {self.BUTTON_FONT_SIZE}px;
            font-family: {self.FONT_FAMILY};
        }}
        QPushButton:hover {{
            background-color: {self.PRIMARY_COLOR};
        }}
        QTableWidget {{
            background-color: {self.SECONDARY_COLOR};
            color: {self.TEXT_COLOR};
        }}
        QHeaderView::section {{
            background-color: {self.SECONDARY_COLOR};
            color: {self.TEXT_COLOR};
        }}
        QListWidget {{
            background-color: {self.SECONDARY_COLOR};
            color: {self.TEXT_COLOR};
        }}
        QLabel {{
            font-family: {self.FONT_FAMILY};
        }}
        """
        self.setStyleSheet(dark_stylesheet)

    def style_button(self, button):
        button.setFont(QFont(self.FONT_FAMILY, self.BUTTON_FONT_SIZE))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.BUTTON_COLOR};
                color: {self.TEXT_COLOR};
                border-radius: 10px;
                padding: 5px;
                font-size: {self.BUTTON_FONT_SIZE}px;
                font-family: {self.FONT_FAMILY};
            }}
            QPushButton:hover {{
                background-color: {self.PRIMARY_COLOR};
            }}
        """)

    def playTranslatedVideo(self):
        if not self.video_file or not self.translated_file:
            QMessageBox.warning(self, "Error", "Please upload a video and translate a subtitle file.")
            return

        self.playVideo()

    def is_video_file(self, filename):
        return filename.endswith(('.mp4', '.mkv'))

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

    def display_subtitle(self, item):
        subtitle_path = os.path.join(self.DATA_DIR, self.projectComboBox.currentText(), item.text())
        self.process_subtitle_file(subtitle_path)
