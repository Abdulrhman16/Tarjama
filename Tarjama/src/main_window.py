import logging
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, 
    QTableWidget, QTableWidgetItem, QProgressBar, QInputDialog, QMessageBox, 
    QWidget, QComboBox, QHeaderView, QListWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import pysrt
import ass
import src.functionality_main_window as func

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

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

<<<<<<< HEAD

=======
>>>>>>> parent of 3a8aca8 (version 2.2)
    def load_videos(self):
        func.load_videos(self)

    def load_subtitles_for_video(self, item):
        func.load_subtitles_for_video(self, item)

    def uploadFile(self):
        func.uploadFile(self)

    def loadSubtitles(self, table, subtitles):
        func.loadSubtitles(self, table, subtitles)

    def getSubtitlesFromTable(self, table, original_subtitles):
        func.getSubtitlesFromTable(self, table, original_subtitles)

    def translateFile(self):
        func.translateFile(self)

    def updateTableWithTranslation(self, translated_texts):
        func.updateTableWithTranslation(self, translated_texts)

    def stopTranslation(self):
        func.stopTranslation(self)

    def translationStopped(self):
        func.translationStopped(self)

    def displayTranslatedText(self, translated_texts):
        func.displayTranslatedText(self, translated_texts)

    def saveFile(self):
        func.saveFile(self)

    def saveOriginalFile(self):
        func.saveOriginalFile(self)

    def chooseVideo(self):
        func.chooseVideo(self)

    def uploadTranslatedFile(self):
        func.uploadTranslatedFile(self)

    def deleteVideo(self):
        func.deleteVideo(self)

    def deleteSubtitle(self):
        func.deleteSubtitle(self)

    def playVideo(self):
        func.playVideo(self)

    def playWithMPV(self, subtitle_file):
        func.playWithMPV(self, subtitle_file)

    def playWithVLC(self, subtitle_file):
        func.playWithVLC(self, subtitle_file)

    def playWithCustomPlayer(self, subtitle_file):
        func.playWithCustomPlayer(self, subtitle_file)

    def setCustomPlayer(self):
        func.setCustomPlayer(self)

    def updateProgressBar(self, value):
        func.updateProgressBar(self, value)

    def showTranslationError(self, message):
        func.showTranslationError(self, message)

    def uploadVideo(self):
        func.uploadVideo(self)

    def extract_and_translate_audio(self, audio_chunks_and_sample_rate):
        func.extract_and_translate_audio(self, audio_chunks_and_sample_rate)

    def on_audio_extracted(self, transcript_with_timestamps):
        func.on_audio_extracted(self, transcript_with_timestamps)

    def cleanup_audio_chunks(self, audio_chunks):
        func.cleanup_audio_chunks(self, audio_chunks)
<<<<<<< HEAD
=======

>>>>>>> parent of 3a8aca8 (version 2.2)
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
