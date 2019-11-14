from lib import get_logger
from lib.aws.dynamodb import Dynamodb
from lib.util.converter import Converter
from lib.bookbot.list_history import ListHistory


class Describe:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dynamodb = Dynamodb()
        self.converter = Converter()
        self.list_history = ListHistory()

    def specified_entry_no(self, message, entry_no):
        items = self.dynamodb.query_specified_key_value(self.dynamodb.default_table, 'entry_no', entry_no)
        if len(items) == 0:
            message.reply(f"登録番号 *[{entry_no}]* のデータが見つかりません。")
            return

        # プライマリキー指定なので必ず1件取得
        item = items[0]

        text_list = list()
        text_list.append(self.converter.get_list_str(item))

        impression = item.get('impression')
        if impression is not None or impression != '':
            text_list.append(f"```\n{impression}\n```")
        else:
            text_list.append("感想は登録されていません。")

        message.send("\n".join(text_list))
