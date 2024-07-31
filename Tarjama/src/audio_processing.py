import logging
from PyQt5.QtCore import QThread, pyqtSignal
import os
import wave
import contextlib
import ffmpeg

class AudioProcessingThread(QThread):
    finished = pyqtSignal(tuple)
    error = pyqtSignal(str)

    def __init__(self, video_file, parent=None):
        super(AudioProcessingThread, self).__init__(parent)
        self.video_file = video_file

    def run(self):
        try:
            # Extract audio from video
            audio_file = 'temp_audio.wav'
            ffmpeg.input(self.video_file).output(audio_file).run(overwrite_output=True)
            logging.debug('Extracted audio to %s', audio_file)

            # Split audio into chunks
            audio_chunks, timestamps = self.split_audio(audio_file)
            logging.debug('Audio split into %d chunks', len(audio_chunks))

            self.finished.emit((audio_chunks, timestamps, 16000))  # Emit as a tuple
            os.remove(audio_file)
            logging.debug('Deleted temporary audio file: %s', audio_file)
        except Exception as e:
            logging.error('Error in AudioProcessingThread: %s', e)
            self.error.emit(str(e))

    def split_audio(self, audio_file):
        chunk_length_ms = 30000  # 30 seconds
        chunks = []
        timestamps = []

        with contextlib.closing(wave.open(audio_file, 'r')) as wf:
            total_length_ms = int((wf.getnframes() / wf.getframerate()) * 1000)
            num_chunks = total_length_ms // chunk_length_ms + 1

            for i in range(num_chunks):
                start = i * chunk_length_ms
                end = min((i + 1) * chunk_length_ms, total_length_ms)
                chunk_file = f'audio_chunk_{i}.wav'
                mono_chunk_file = f'mono_audio_chunk_{i}.wav'
                ffmpeg.input(audio_file, ss=start / 1000, t=(end - start) / 1000).output(chunk_file).run(overwrite_output=True)
                ffmpeg.input(chunk_file).output(mono_chunk_file, ac=1, ar=16000).run(overwrite_output=True)
                os.remove(chunk_file)
                chunks.append(mono_chunk_file)
                timestamps.append((start, end))

        return chunks, timestamps
