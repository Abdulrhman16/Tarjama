# src/translation.py

import requests
import uuid
import json

# Add your key and endpoint
key = '1b7a6f0532ae4e4e9cc8854f504566b3'  # Replace with your actual subscription key
endpoint = 'https://api.cognitive.microsofttranslator.com'

# Location, also known as region.
location = 'QatarCentral'  # Replace with your actual resource location

path = '/translate'
constructed_url = endpoint + path

headers = {
    'Ocp-Apim-Subscription-Key': key,
    'Ocp-Apim-Subscription-Region': location,  # Required if using a multi-service or regional resource
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

def translate_text_batch(texts, target_language='ar'):
    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': [target_language]
    }

    body = [{'text': text} for text in texts]

    print("Request body:", json.dumps(body, indent=2))  # Log the request body for debugging

    try:
        request = requests.post(constructed_url, params=params, headers=headers, json=body)
        request.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        response = request.json()
        return [translation['translations'][0]['text'] for translation in response]
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print("Response content:", request.text)  # Log the response content for debugging
    except requests.exceptions.RequestException as err:
        print(f"Other error occurred: {err}")
    except requests.exceptions.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err}")
    return ["Translation failed. Please check the logs for more details."] * len(texts)

def batch_translate(texts, batch_size=10, update_progress=None):
    translated_texts = []
    total_batches = (len(texts) + batch_size - 1) // batch_size  # Calculate total number of batches
    current_batch = 0

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        translated_batch = translate_text_batch(batch)
        translated_texts.extend(translated_batch)
        current_batch += 1
        if update_progress:
            update_progress(current_batch * batch_size)  # Update the progress bar

    return translated_texts