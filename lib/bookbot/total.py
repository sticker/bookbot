from lib import get_logger
from lib.util.amount import Amount
from lib.util.slack import Slack


class Total:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.amount = Amount()
        self.slack = Slack()

    def default(self, message):
        # 申請者 Slack ID
        slack_id = self.slack.get_slack_id(message.body['text'])
        # 申請者名
        user_name = self.slack.get_user_name(slack_id, message)
        slack_name = user_name[0]

        total_price_in_this_year = self.amount.get_total_price_in_this_year(slack_name)
        remain_amount = self.amount.get_remain_amount(slack_name)

        text_list = list()
        text_list.append(f"<@{slack_id}> 今年度の立替金合計は *{total_price_in_this_year}* 円 です。")
        text_list.append(f"残り *{remain_amount}* 円 までならOKです。")

        message.send("\n".join(text_list))
