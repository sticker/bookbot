from lib import get_logger
from lib.aws.dynamodb import Dynamodb
from lib.util.converter import Converter
from lib.bookbot.list_history import ListHistory


class Delete:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dynamodb = Dynamodb()
        self.converter = Converter()
        self.list_history = ListHistory()

    def specified_entry_no(self, message, entry_no):
        # 削除対象レコードを取得
        items = self.dynamodb.query_specified_key_value(self.dynamodb.default_table, 'entry_no', entry_no)
        if len(items) == 0:
            message.send("対象の購入データが見つかりません")
            return

        text_list = list()

        # レコード削除
        key = dict()
        key['entry_no'] = entry_no
        self.dynamodb.remove(self.dynamodb.default_table, key)
        text_list.append("以下の購入データを削除しました！")

        # プライマリキー指定なので必ず1件取得
        item = items[0]
        text_list.append(self.converter.get_list_str(item))

        message.send("\n".join(text_list))
