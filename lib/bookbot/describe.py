from lib import get_logger
from lib.aws.dynamodb import Dynamodb
from lib.util.converter import Converter


class Describe:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dynamodb = Dynamodb()
        self.converter = Converter()

    def specified_entry_no(self, message, entry_no):
        items = self.dynamodb.query_specified_key_value(self.dynamodb.default_table, 'entry_no', entry_no)
        # プライマリキー指定なので必ず1件取得
        item = items[0]

        text_list = list()

        entry_no = item.get('entry_no', '-')
        book_url = item.get('book_url', '-')
        book_name = item.get('book_name', '-')
        book_type = self.converter.get_book_type_str(item.get('book_type', '本'))
        entry_date_yyyymmdd = item.get('entry_time', '99999999')[0:8]
        entry_date = self.converter.get_date_str(entry_date_yyyymmdd)
        real_name = item.get('real_name', '-')
        text_list.append(f"[{entry_no}] <{book_url}|{book_name}>{book_type} at {entry_date} by {real_name}")

        impression = item.get('impression')
        if impression is not None:
            text_list.append(f"```\n{impression}\n```")

        message.send("\n".join(text_list))
