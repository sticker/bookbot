import os
from lib import get_logger
from lib.aws.dynamodb import Dynamodb
from lib.aws.s3 import S3
from lib.util.converter import Converter
from lib.util.validation import Validation
from lib.util.slack import Slack


class Amount:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dynamodb = Dynamodb()
        self.s3 = S3()
        self.converter = Converter()
        self.validation = Validation()
        self.slack = Slack()
        # 年間上限金額
        self.max_amount = int(os.getenv("MAX_AMOUNT", 10000))

    def get_total_price_in_this_year(self, slack_name: str) -> int:
        this_year_start, this_year_end = self.converter.get_this_year_from_today()

        target_entry_time_start = this_year_start.ljust(14, '0')
        target_entry_time_end = this_year_end.ljust(14, '9')
        self.logger.debug(target_entry_time_start)
        self.logger.debug(target_entry_time_end)

        items = self.dynamodb.query_entry_time(slack_name, target_entry_time_start, target_entry_time_end)

        total_price_in_this_year = sum(map(lambda x: int(x['book_price']), items))

        return total_price_in_this_year

    def check_max_amount(self, slack_name: str, book_price: str, total_price_in_this_year=None) -> bool:
        if total_price_in_this_year is None:
            total_price_in_this_year = self.get_total_price_in_this_year(slack_name)

        if total_price_in_this_year + int(book_price) > self.max_amount:
            self.logger.info(f"今年度の立替金額が{self.max_amount}円を超えてしまいます 対象ユーザ:{slack_name}, 今年度立替金額合計:{total_price_in_this_year}, 今回立替金額:{book_price}")
            return False

        self.logger.debug(f"対象ユーザ:{slack_name}, 今年度立替金額合計:{total_price_in_this_year}, 今回立替金額:{book_price}")
        return True

    def get_remain_amount(self, slack_name: str, total_price_in_this_year=None) -> int:
        if total_price_in_this_year is None:
            total_price_in_this_year = self.get_total_price_in_this_year(slack_name)

        remain_amount = self.max_amount - total_price_in_this_year

        # もしマイナスになったら0にしておく
        if remain_amount < 0:
            remain_amount = 0

        return remain_amount
