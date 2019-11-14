import re
from datetime import datetime
from slackbot.dispatcher import Message
from lib import get_logger, app_home
from lib.aws.dynamodb import Dynamodb
from lib.aws.s3 import S3
from lib.util.amount import Amount
from lib.util.converter import Converter
from lib.util.validation import Validation
from lib.util.slack import Slack
from lib.util.pdf import Pdf


class Entry:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dynamodb = Dynamodb()
        self.s3 = S3()
        self.amount = Amount()
        self.converter = Converter()
        self.validation = Validation()
        self.slack = Slack()
        self.pdf = Pdf()

    def save(self, message: Message):

        now = datetime.now()

        book_name = ''
        book_type = ''
        book_price = ''
        book_url = ''
        purpose = ''
        for block in message.body['blocks']:
            if not ('text' in block and 'text' in block['text']):
                continue

            text = block['text']['text']
            if '*題名*' in text:
                book_name = re.sub('\*題名\*|\n', '', text)
            elif '*形式*' in text:
                book_type = re.sub('\*形式\*|\n', '', text)
            elif '*立替金額（税込）*' in text:
                book_price = re.sub('\\D', '', self.converter.to_hankaku(text))
            elif '*詳細リンク（Amazonなど）*' in text:
                book_url = re.sub('\*詳細リンク（Amazonなど）\*|<|>|\n', '', text)
            elif '*購入目的*' in text:
                purpose = re.sub('\*購入目的\*|<|>|\n', '', text)

        # 投稿タイムスタンプ（スレッド投稿のため）
        ts = message.body['ts']

        # パラメータチェック
        # if not self.validation.validate_entry(book_name=book_name, book_price=book_price, book_url=book_url, message=message):
        #     self.logger.debug("パラメータチェックNG")
        #     return

        # 申請日
        entry_time = now.strftime("%Y%m%d%H%M%S")

        # 申請者 Slack ID
        slack_id = self.slack.get_slack_id_from_workflow(message.body['text'])

        # 申請者名
        user_name = self.slack.get_user_name(slack_id, message)
        slack_name = user_name[0]
        real_name = user_name[1]

        # 今年度の合計立替金額を取得
        total_price_in_this_year = self.amount.get_total_price_in_this_year(slack_name)
        # そのユーザが年間上限金額以上立替していないか
        result = self.amount.check_max_amount(slack_name, book_price, total_price_in_this_year)
        # 今回申請分を登録する前の 残り金額
        remain_amount = self.amount.get_remain_amount(slack_name, total_price_in_this_year)
        if not result:
            self.logger.debug("年間立替金額上限を超えています")
            message.send(f"<@{slack_id}> 年間立替金額上限を超えるため登録できません。残り *{remain_amount}* 円 までならOKです。", thread_ts=ts)
            return

        # 受付番号
        # アトミックカウンタでシーケンス番号を発行し文字列として取得する
        entry_no = str(self.dynamodb.atomic_counter('atomic-counter', 'entry_no'))

        # 今年度の合計立替金額に今回申請分を足す
        total_price_in_this_year += int(book_price)
        # 今回申請分を登録した後の 残り金額
        remain_amount = self.amount.get_remain_amount(slack_name, total_price_in_this_year)

        # パーマリンクを取得
        permalink = self.slack.get_message_permalink(message)

        # 感想（空で登録）
        impression = ''

        item = {
            'entry_no': entry_no,
            'book_name': book_name,
            'book_type': book_type,
            'book_price': book_price,
            'total_price_in_this_year': total_price_in_this_year,
            'remain_amount': remain_amount,
            'book_url': book_url,
            'purpose': purpose,
            'entry_time': entry_time,
            'slack_id': slack_id,
            'slack_name': slack_name,
            'real_name': real_name,
            'permalink': permalink,
            'impression': impression
        }
        self.logger.info(f"item={item}")

        self.dynamodb.insert(self.dynamodb.default_table, item)

        reply_texts = [f"<@{slack_id}> 登録しました！"]
        reply_texts.append(f"登録番号: *[{entry_no}]*")
        reply_texts.append(f"今年度の立替金額合計が *{total_price_in_this_year}* 円になりました。")
        if remain_amount == 0:
            reply_texts.append(f"上限金額は *{self.amount.max_amount}* 円です。今年度はこれが最後の立替になります。")
        else:
            reply_texts.append(f"残り *{remain_amount}* 円 までならOKです。")

        if book_price == '0':
            self.logger.info("0円のため承認PDFは作成しません")
            message.send("\n".join(reply_texts), thread_ts=ts)
            return

        reply_texts.append('補助対象になりますので承認PDFを作成します。')
        message.send("\n".join(reply_texts), thread_ts=ts)

        # 承認内容のPDFを作成してSlackにアップ　バックアップでS3にアップ
        # 保存先PDFファイルパス
        save_pdf_fname = f"{entry_no}_{entry_time}_{slack_name}.pdf"
        save_pdf_path = f"{app_home}/output_pdf/{save_pdf_fname}"
        # 承認PDF作成
        if not self.pdf.make_approved_pdf(item, save_pdf_path):
            self.logger.warning('承認PDFの作成に失敗しました')
            message.send(f"<@{item['slack_id']}> 承認PDFの作成に失敗しました...すいません！")
            return False

        channel_name = self.slack.get_channel_name(message)
        self.logger.debug(channel_name)

        self.slack.upload_file(message, channel_name,
                               fpath=save_pdf_path,
                               comment="このPDFと購入時の領収書を添付して立替金申請をしてください。",
                               thread_ts=ts)

        # S3にもアップロード
        this_year = self.converter.get_this_year_from_today()[0][0:4]  # 今年度のYYYY
        self.s3.upload_to_pdf(save_pdf_path, process_ym=this_year)

