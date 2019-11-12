import re
import os
from slackbot.dispatcher import Message
from lib import get_logger, app_home

class Slack:
    def __init__(self):
        self.logger = get_logger(__name__)

    def get_slack_id(self, text: str) -> str:
        slack_id = re.findall('<@(.*)>さん', text)
        return slack_id[0]

    def get_user_name(self, slack_id: str, message: Message) -> tuple:
        user = message._client.get_user(slack_id)
        slack_name = user['name']
        real_name = user['real_name']

        return (slack_name, real_name)

    def get_channel_name(self, message: Message, channel_id=None) -> str:
        if channel_id is None:
            channel_id = message.body['channel']
        res = message._client.webapi.channels.info(channel=channel_id)

        return res.body['channel']['name']

    def get_message_permalink(self, message: Message) -> str:
        res = message._client.webapi.chat.get_permalink(channel=message.body['channel'], message_ts=message.body['ts'])

        return res.body['permalink']

    def upload_file(self, message: Message, channel_name: str, fpath: str, comment: str, thread_ts: str ) -> bool:
        message._client.webapi.files.upload(fpath,
                                            channels=channel_name,
                                            filename=os.path.basename(fpath),
                                            initial_comment=comment,
                                            thread_ts=thread_ts)
        return True
