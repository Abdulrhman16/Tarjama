# src/file_upload.py

import os
import pysrt
from pysubparser import parser
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QProgressBar
from PyQt5.QtCore import Qt
from translation import batch_translate

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
        
        self.progressBar = QProgressBar(self)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.progressBar)
        
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
        original_texts = [sub.text for sub in subs]

        # Update progress bar
        total_subs = len(original_texts)
        self.progressBar.setMaximum(total_subs)
        
        translated_texts = batch_translate(original_texts, update_progress=self.updateProgressBar)

        for sub, translated_text in zip(subs, translated_texts):
            sub.text = translated_text

        # Save translated subtitles to a new file
        translated_file_path = filePath.replace('.srt', '_translated.srt')
        subs.save(translated_file_path, encoding='utf-8')
        print(f"Translated subtitle file saved at: {translated_file_path}")

    def processASS(self, filePath):
        print("ASS subtitle file selected:", filePath)
        subs = parser.parse(filePath)
        original_texts = []

        # Extract original lines from ASS file
        with open(filePath, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Collect text to translate with context
        dialogue_lines = []
        for line in lines:
            if line.startswith("Dialogue:"):
                parts = line.split(',', 9)
                if len(parts) > 9:
                    original_texts.append(parts[9])
                    dialogue_lines.append(line)
                else:
                    original_texts.append("")
                    dialogue_lines.append(line)

        # Update progress bar
        total_dialogues = len(original_texts)
        self.progressBar.setMaximum(total_dialogues)

        # Translate text in batches
        translated_texts = batch_translate(original_texts, update_progress=self.updateProgressBar)

        # Replace original text with translated text
        translated_lines = []
        for line, translated_text in zip(dialogue_lines, translated_texts):
            parts = line.split(',', 9)
            if len(parts) > 9:
                parts[9] = translated_text
                translated_lines.append(','.join(parts))
            else:
                translated_lines.append(line)

        # Combine translated dialogue lines with other lines
        translated_file_lines = []
        dialogue_index = 0
        for line in lines:
            if line.startswith("Dialogue:"):
                translated_file_lines.append(translated_lines[dialogue_index])
                dialogue_index += 1
            else:
                translated_file_lines.append(line)

        # Save translated subtitles to a new file
        translated_file_path = filePath.replace('.ass', '_translated.ass')
        with open(translated_file_path, 'w', encoding='utf-8') as file:
            file.writelines(translated_file_lines)
        print(f"Translated subtitle file saved at: {translated_file_path}")

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)
