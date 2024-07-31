import logging
from PyQt5.QtCore import QThread, pyqtSignal
from google.cloud import speech
import os

class SpeechRecognitionThread(QThread):
    result = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, audio_chunks, timestamps, sample_rate, parent=None):
        super(SpeechRecognitionThread, self).__init__(parent)
        self.audio_chunks = audio_chunks
        self.timestamps = timestamps
        self.sample_rate = sample_rate

    def run(self):
        client = speech.SpeechClient()
        results = []
        try:
            for i, chunk in enumerate(self.audio_chunks):
                start_time, end_time = self.timestamps[i]
                with open(chunk, 'rb') as audio_file:
                    audio_content = audio_file.read()

                audio = speech.RecognitionAudio(content=audio_content)
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=self.sample_rate,
                    language_code='en-US',
                    enable_word_time_offsets=True
                )

                response = client.recognize(config=config, audio=audio)
                for result in response.results:
                    for word_info in result.alternatives[0].words:
                        results.append({
                            'word': word_info.word,
                            'start_time': start_time + word_info.start_time.total_seconds() * 1000,
                            'end_time': start_time + word_info.end_time.total_seconds() * 1000
                        })
                os.remove(chunk)
            self.result.emit(results)
        except Exception as e:
            logging.error('Failed to process chunk %s: %s', chunk, e)
            self.error.emit(str(e))
