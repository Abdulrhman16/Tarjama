# src/translation.py

from transformers import MarianMTModel, MarianTokenizer

def translate_text(text, target_language='ar'):
    model_name = 'Helsinki-NLP/opus-mt-en-ar'
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)

    translated = model.generate(**tokenizer(text, return_tensors="pt", padding=True))
    translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
    return translated_text
