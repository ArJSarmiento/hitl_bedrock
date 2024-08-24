import json
import re


def extract_json_from_payload(payload):
    # Access the text field in the payload
    text_content = payload['Payload']['Body']['content'][0]['text']

    # Remove Markdown code block delimiters if present
    if text_content:
        # Remove triple backticks and 'json' keyword if they exist
        json_str = re.sub(r'```json\n|```', '', text_content).strip()

        try:
            json_data = json.loads(json_str)
            return json_data
        except json.JSONDecodeError as e:
            print(f'Error decoding JSON: {e}')
            return None
    else:
        print('No JSON object found in the text field.')
        return None


def handler(event, context):
    _ = context
    print(f'Received event: {event}')
    return extract_json_from_payload(event)
