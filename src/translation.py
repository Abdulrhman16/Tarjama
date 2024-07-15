# src/translation.py

import requests
import uuid

def translate_text(text, target_language='ar'):
    subscription_key = '6298b2ed-301c-4cae-849f-c03c9bb8a4ae'  # Replace with your actual subscription key
    endpoint = 'https://api.cognitive.microsofttranslator.com'
    path = '/translate?api-version=3.0'
    params = '&to=' + target_language
    constructed_url = endpoint + path + params

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{'text': text}]

    try:
        response = requests.post(constructed_url, headers=headers, json=body)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        result = response.json()
        return result[0]['translations'][0]['text']
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Other error occurred: {err}")
    except requests.exceptions.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err}")
    return "Translation failed. Please check the logs for more details."
