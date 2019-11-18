from lib import get_logger
from lib.util.amount import Amount
from lib.util.converter import Converter
from lib.util.slack import Slack


class Total:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.amount = Amount()
        self.converter = Converter()
        self.slack = Slack()

    def default(self, message):
        # 申請者 Slack ID
        slack_id = self.slack.get_slack_id(message)
        # 申請者名
        user_name = self.slack.get_user_name(slack_id, message)
        slack_name = user_name[0]

        total_price_in_this_year = self.amount.get_total_price_in_this_year(slack_name)
        remain_amount = self.amount.get_remain_amount(slack_name)

        text_list = list()
        text_list.append(f"今年度の立替金合計は *{total_price_in_this_year}* 円 です。")
        if remain_amount == 0:
            text_list.append(f"上限金額は *{self.amount.max_amount}* 円です。今年度はこれ以上立替できません。")
        else:
            text_list.append(f"残り *{remain_amount}* 円 までならOKです。")

        message.reply("\n".join(text_list))

    def all_total_price_in_year(self, message, target_yyyy):
        text_list = list()
        self.logger.debug(len(target_yyyy))
        if len(target_yyyy) == 4:
            all_total_price_in_year = self.amount.get_all_total_price_in_year(target_yyyy)
            text_list.append(f"{target_yyyy}年度のすべての立替金合計は *{all_total_price_in_year}* 円 です。")
        else:
            this_year_start, this_year_end = self.converter.get_this_year_from_today()
            target_yyyy = this_year_start[0:4]
            all_total_price_in_year = self.amount.get_all_total_price_in_year(target_yyyy)
            text_list.append(f"今年度のすべての立替金合計は *{all_total_price_in_year}* 円 です。")

        message.reply("\n".join(text_list))
