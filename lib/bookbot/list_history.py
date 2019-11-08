from lib import get_logger
from lib.aws.dynamodb import Dynamodb
from lib.util.converter import Converter


class ListHistory:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dynamodb = Dynamodb()
        self.converter = Converter()

    def default(self, message):
        items = self.dynamodb.find(self.dynamodb.default_table)
        self.logger.info(items)
        # 申請日でソート TODO: セカンダリインデックスをqueryで検索してソート
        items.sort(key=lambda x: x['entry_time'], reverse=True)

        text_list = list()
        for item in items:
            entry_no = item.get('entry_no', '-')
            book_url = item.get('book_url', '-')
            book_name = item.get('book_name', '-')
            book_type = self.converter.get_book_type_str(item.get('book_type', '本'))
            entry_date_yyyymmdd = item.get('entry_time', '99999999')[0:8]
            entry_date = self.converter.get_date_str(entry_date_yyyymmdd)
            real_name = item.get('real_name', '-')

            text_list.append(f"[{entry_no}] <{book_url}|{book_name}>{book_type} at {entry_date} by {real_name}")

        message.send("\n".join(text_list))
