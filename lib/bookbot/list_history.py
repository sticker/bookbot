from lib import get_logger
from lib.aws.dynamodb import Dynamodb


class ListHistory:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dynamodb = Dynamodb()

    def default(self, message):
        items = self.dynamodb.find('bookbot-entry')
        self.logger.info(items)
        # 申請日でソート TODO: セカンダリインデックスをqueryで検索してソート
        items.sort(key=lambda x: x['entry_time'], reverse=True)

        text_list = list()
        for item in items:
            book_url = item.get('book_url', '-')
            book_name = item.get('book_name', '-')
            book_type = item.get('book_type', '本')
            if book_type != '本':
                book_type = f'({book_type})'
            else:
                book_type = ''
            entry_date = item.get('entry_time', '99999999')[0:8]
            real_name = item.get('real_name', '-')

            text_list.append(f"<{book_url}|{book_name}>{book_type} at {entry_date} by {real_name}")

        message.send("\n".join(text_list))
