import re
from datetime import datetime
from slackbot.dispatcher import Message
from lib import get_logger
from lib.aws.dynamodb import Dynamodb
from lib.util.converter import Converter
from lib.util.slack import Slack


class Impression:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dynamodb = Dynamodb()
        self.converter = Converter()
        self.slack = Slack()

    def save(self, message: Message):
        now = datetime.now()

        entry_no = ''
        impression = ''
        for block in message.body['blocks']:
            if not ('text' in block and 'text' in block['text']):
                continue

            text = block['text']['text']
            if '*登録番号*' in text:
                entry_no = re.sub('\\D', '', self.converter.to_hankaku(text))
            elif '*感想*' in text:
                impression = re.sub('\*感想\*\n', '', text).strip()

        self.logger.debug(f"impression={impression}")
        # 感想登録日
        impression_time = now.strftime("%Y%m%d%H%M%S")
        self.logger.debug(f"impression_time={impression_time}")

        # 申請者 Slack ID
        slack_id = self.slack.get_slack_id_from_workflow(message.body['text'])

        # 申請者名
        user_name = self.slack.get_user_name(slack_id, message)
        slack_name = user_name[0]
        real_name = user_name[1]

        # 投稿タイムスタンプ（スレッド投稿のため）
        ts = message.body['ts']

        # 更新対象レコードを取得
        items = self.dynamodb.query_specified_key_value(self.dynamodb.default_table, 'entry_no', entry_no)
        # プライマリキー指定なので必ず1件取得
        item = items[0]

        if item['slack_id'] != slack_id:
            message.send(f"<@{slack_id}> 購入者本人以外は感想登録できません！", thread_ts=ts)
            return False

        self.logger.debug(f"entry_no={entry_no}, impression={impression}, impression_time={impression_time}")
        response = self.dynamodb.update_bookbot_entry_impression(entry_no, impression, impression_time)
        self.logger.debug(response)
        if response is None:
            self.logger.error(f"感想の登録に失敗しました")
            message.send(f"<@{slack_id}> 感想の登録に失敗しました...すいません！", thread_ts=ts)
            return False

        item['impression'] = impression
        reply_texts = [f"<!here> 以下の感想が登録されました！"]
        reply_texts.append(self.converter.get_list_str(item))

        message.send("\n".join(reply_texts), thread_ts=ts)
