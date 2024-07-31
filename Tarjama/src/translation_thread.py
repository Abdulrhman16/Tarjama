import requests
from PyQt5.QtCore import QThread, pyqtSignal
from deep_translator import GoogleTranslator

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
            elif self.engine == "Microsoft Translator":
                self.translate_with_microsoft_translator(self.subtitles)
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

    def translate_with_microsoft_translator(self, subtitles):
        original_texts = [(i, subtitle.text) for i, subtitle in enumerate(subtitles)]
        translated_texts = []
        batch_size = 10  # Adjust batch size as needed
        endpoint = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"
        subscription_key = "1b7a6f0532ae4e4e9cc8854f504566b3"
        location = "qatarcentral"

        for i in range(0, len(original_texts), batch_size):
            batch = original_texts[i:i+batch_size]
            batch_text = [{"Text": text} for index, text in batch]
            headers = {
                'Ocp-Apim-Subscription-Key': subscription_key,
                'Ocp-Apim-Subscription-Region': location,
                'Content-type': 'application/json'
            }
            params = {
                'from': 'en',
                'to': ['ar']
            }
            response = requests.post(endpoint, params=params, headers=headers, json=batch_text)
            if response.status_code == 200:
                translated_batch = response.json()
                for j, translation in enumerate(translated_batch):
                    translated_texts.append(translation['translations'][0]['text'])
                self.progress.emit(len(translated_texts))
            else:
                self.error.emit(f"Translation failed: {response.text}")
                return
        self.result.emit(translated_texts)

    def stop(self):
        self._is_running = False
        self.stopped.emit()
