# src/file_upload.py

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel
from translation import translate_text

class FileUpload(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.layout = QVBoxLayout()
        
        self.label = QLabel("Upload a subtitle or video file:", self)
        self.layout.addWidget(self.label)
        
        self.uploadButton = QPushButton("Upload File", self)
        self.uploadButton.clicked.connect(self.showDialog)
        self.layout.addWidget(self.uploadButton)
        
        self.setLayout(self.layout)
        
    def showDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Select a File", "", 
                                                  "Subtitle Files (*.srt *.ass);;Video Files (*.mp4 *.mkv)", 
                                                  options=options)
        if fileName:
            self.label.setText(f"Selected file: {fileName}")
            self.processFile(fileName)
            
    def processFile(self, filePath):
        _, ext = os.path.splitext(filePath)
        if ext in ['.srt', '.ass']:
            print("Subtitle file selected:", filePath)
            with open(filePath, 'r', encoding='utf-8') as file:
                subtitle_text = file.read()
            translated_text = translate_text(subtitle_text)
            print("Translated Text:", translated_text)
        elif ext in ['.mp4', '.mkv']:
            print("Video file selected:", filePath)
            # Process video file (e.g., extract subtitles)
