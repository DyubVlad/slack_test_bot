import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from sys import argv
import json


logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler('output.log', mode='w')
ch.setLevel(logging.DEBUG)

strfmt = '[%(asctime)s] [%(funcName)s] [%(levelname)s] > %(message)s'
datefmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(fmt=strfmt, datefmt=datefmt)
ch.setFormatter(formatter)
logger.addHandler(ch)
conversations_store = {}


# Получение списка публичных каналов рабочего пространства
# требуется channels:read scope для бота
def fetch_conversations(client):
    try:
        result = client.conversations_list()
        save_conversations(result["channels"])
    except SlackApiError as e:
        logger.error("Error fetching conversations: {}".format(e))


# Полученный список каналов записывается в словарь
def save_conversations(conversations):
    for conversation in conversations:
        conversation_name = conversation["name"]
        conversations_store[conversation_name] = conversation

# Функция отправляет в Slack запрос на присоединения бота в канал
# требуется channels:join scope для бота
def try_join_to_channel(client, channel):
    try:
        response = client.conversations_join(channel=conversations_store[channel]['id'])
    except SlackApiError as e:
        if e.response['error'] == 'missing_scope':
            logger.error('if you want the bot to be able to invite, need to install scoop channels:join')
        else:
            logging.error(f"Got an join error: {e.response['error']}")
    except KeyError as e:
        logger.error('Channel with name ' + channel + ' not found in list of public channel')


# Функция отправляет в Slack запрос на отправку сообщения в канал с указанным именем
# требуется chat:write scope для бота
def send_message_to_channel(client, channel, text):
    try_join_to_channel(client, channel)
    try:
        response = client.chat_postMessage(channel=channel, text=text)
        if response.data['ok']:
            logger.info('message has been sent to channel ' + channel)
    except SlackApiError as e:
        logger.error(f"Got an postMess error: {e.response['error']}")


try:
    script, json_file = argv
except Exception as e:
    logger.error(f"Got an error: {e}")

with open(json_file, 'r') as json_f:
    json_from_file = json_f.read()
parsed_json = json.loads(json_from_file)

client = WebClient(token=parsed_json['bot_token'])
fetch_conversations(client)
for channels in parsed_json['channels']:
    send_message_to_channel(client, channels['channel'], channels['text'])
