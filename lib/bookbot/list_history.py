from lib import get_logger
from lib.aws.dynamodb import Dynamodb
from lib.util.converter import Converter


class ListHistory:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dynamodb = Dynamodb()
        self.converter = Converter()
        self.default_record_num = 20

    def default(self, message):
        items = self.dynamodb.find(self.dynamodb.default_table, self.default_record_num)
        self.logger.info(items)

        if len(items) == 0:
            message.send('見つかりませんでした！')
            return

        # 申請日でソート
        items.sort(key=lambda x: x['entry_time'], reverse=True)

        text_list = list()
        for item in items:
            text_list.append(self.converter.get_list_str(item))

        message.send("\n".join(text_list))

    def search(self, message, search_words):
        items = self.dynamodb.scan_contains_search_words(search_words)

        if len(items) == 0:
            message.send('見つかりませんでした！')
            return

        # 申請日でソート
        items.sort(key=lambda x: x['entry_time'], reverse=True)

        text_list = list()
        for item in items:
            text_list.append(self.converter.get_list_str(item))

        message.send("\n".join(text_list))
