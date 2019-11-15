from slackbot import settings
from lib import get_logger
from lib.aws.dynamodb import Dynamodb
from lib.util.converter import Converter
from lib.util.slack import Slack


class Reminder:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dynamodb = Dynamodb()
        self.converter = Converter()
        self.slack = Slack()

    def remind_impression(self, elapsed_days=60):
        self.logger.info(f"感想登録されずに{elapsed_days}日経過したのでリマインドをします")
        target_entry_time_yyyymmdd = self.converter.get_yyyymmdd_specified_days_ago(days_ago=elapsed_days)
        self.logger.debug(f"target_entry_time_yyyymmdd={target_entry_time_yyyymmdd}")
        items = self.dynamodb.query_impression_flag_and_entry_time("0", target_entry_time_yyyymmdd)

        if len(items) == 0:
            self.logger.info(f"リマインド対象者はいませんでした")
            return

        mention_set = set()
        book_list = list()
        for item in items:
            mention_set.add(f"<@{item['slack_id']}>")
            book_list.append(self.converter.get_list_str(item))

        text_list = list()
        text_list.append(" ".join(mention_set) + " そろそろ読み終わりましたか？読み終わったら感想登録お願いします！")
        text_list.extend(book_list)
        channel_name = self.slack.get_channel_name_by_slacker(settings.DEFAULT_CHANNEL_ID)
        self.slack.send_message_by_slacker(channel=channel_name, text="\n".join(text_list))

        return True

    def remind_impression_minutes(self):
        self.logger.info("remind minutes!")
