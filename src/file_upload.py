# src/file_upload.py

import os
import pysrt
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
        if ext in ['.srt']:
            self.processSRT(filePath)
        elif ext in ['.ass']:
            self.processASS(filePath)
        elif ext in ['.mp4', '.mkv']:
            print("Video file selected:", filePath)
            # Process video file (e.g., extract subtitles)

    def processSRT(self, filePath):
        print("Subtitle file selected:", filePath)
        subs = pysrt.open(filePath)
        translated_subs = []

        for sub in subs:
            translated_text = translate_text(sub.text)
            translated_subs.append(translated_text)
            sub.text = translated_text

        # Save translated subtitles to a new file
        translated_file_path = filePath.replace('.srt', '_translated.srt')
        subs.save(translated_file_path, encoding='utf-8')
        print(f"Translated subtitle file saved at: {translated_file_path}")

    def processASS(self, filePath):
        print("ASS subtitle processing is not yet implemented.")
        # Implement similar to SRT processing
