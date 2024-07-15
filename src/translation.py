# src/translation.py

from google.cloud import translate_v2 as translate

def translate_text(text, target_language='ar'):
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language=target_language)
    return result['translatedText']
