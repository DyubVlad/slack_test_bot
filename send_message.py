from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from sys import argv
import json

def send_message_to_channel(token, channel, text):
    client = WebClient(token=token)

    try:
        response = client.chat_postMessage(channel=channel, text=text)
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")

try:
    script, json_file = argv
except Exception as e:
    print(f"Got an error: {e}")
    pass

with open(json_file, 'r') as json_f:
    json_from_file = json_f.read()
parsed_json = json.loads(json_from_file)

for channels in parsed_json['channels']:
    send_message_to_channel(parsed_json['bot_token'], channels['channel'], channels['text'])
print()
