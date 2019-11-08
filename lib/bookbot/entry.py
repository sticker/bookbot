import os
import re
import pdfkit
from markdown import Markdown
from datetime import datetime
from slackbot.dispatcher import Message
from lib import get_logger, app_home
from lib.aws.dynamodb import Dynamodb
from lib.util.converter import Converter
from lib.util.validation import Validation
from lib.util.slack import Slack


class Entry:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dynamodb = Dynamodb()
        self.converter = Converter()
        self.validation = Validation()
        self.slack = Slack()
        # 年間上限金額
        self.max_amount = 25000

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
            elif '*税込金額（半角数字）*' in text:
                # book_price = re.sub('\*金額\*| |,|\n', '', text)
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
        slack_id = self.slack.get_slack_id(message.body['text'])

        # 申請者名
        user_name = self.slack.get_user_name(slack_id, message)
        slack_name = user_name[0]
        real_name = user_name[1]

        # そのユーザが年間上限金額以上買っていないか
        (result, total_price_in_this_year) = self.check_max_amount_per_user(slack_name, book_price)
        if not result:
            self.logger.debug("年間購入金額上限を超えています")
            message.send(f"<@{slack_id}> 年間購入金額上限を超えるため登録できません。", thread_ts=ts)

            return

        # 受付番号
        # entry_no = now.strftime("%Y%m%d%H%M%S%f")[:-3]
        # アトミックカウンタでシーケンス番号を発行し文字列として取得する
        entry_no = str(self.dynamodb.atomic_counter('atomic_counter', 'entry_no'))

        # 感想（空で登録）
        impression = ''

        item = {
            'entry_no': entry_no,
            'book_name': book_name,
            'book_type': book_type,
            'book_price': book_price,
            'total_price_in_this_year': total_price_in_this_year,
            'book_url': book_url,
            'purpose': purpose,
            'entry_time': entry_time,
            'slack_id': slack_id,
            'slack_name': slack_name,
            'real_name': real_name,
            'impression': impression
        }
        self.logger.info(f"item={item}")

        self.dynamodb.insert(self.dynamodb.default_table, item)

        reply_texts = [f"<@{slack_id}> 登録しました！購入番号: [{entry_no}]"]
        reply_texts.append(f"今年度購入金額合計: {total_price_in_this_year}円")
        reply_texts.append(f"残り {self.max_amount - total_price_in_this_year}円 までOKです。")
        reply_texts.append('補助対象になりますので承認PDFを作成します。')
        message.send("\n".join(reply_texts), thread_ts=ts)

        item['total_price_in_this_year'] = total_price_in_this_year
        # 承認内容のPDFを作成してSlackにアップ　バックアップでS3にアップ
        # self.upload_approved(message, item)
        # パーマリンクを取得
        item['permalink'] = self.slack.get_message_permalink(message)
        # 保存先PDFファイルパス
        save_pdf_path = f"{app_home}/file/{item['entry_no']}_{item['slack_name']}.pdf"
        # 承認PDF作成
        if not self.make_approved_pdf(item, save_pdf_path):
            self.logger.warning('承認PDFの作成に失敗しました')
            message.send(f"<@{item['slack_id']}> 承認PDFの作成に失敗しました...すいません！")
            return False

        channel_name = self.slack.get_channel_name(message)
        self.logger.debug(channel_name)

        self.slack.upload_file(message, channel_name,
                               fpath=save_pdf_path,
                               comment="このPDFと購入時の領収書を添付して立替金申請をしてください。",
                               thread_ts=ts)

        # TODO: S3にもアップロード

    def check_max_amount_per_user(self, slack_name: str, book_price: str) -> tuple:
        this_year_start, this_year_end = self.converter.get_this_year_from_today()

        target_entry_time_start = this_year_start.ljust(14, '0')
        target_entry_time_end = this_year_end.ljust(14, '9')
        self.logger.debug(target_entry_time_start)
        self.logger.debug(target_entry_time_end)

        items = self.dynamodb.query_entry_time(slack_name, target_entry_time_start, target_entry_time_end)

        total_price_in_this_year = sum(map(lambda x: int(x['book_price']), items))
        self.logger.debug(f"対象ユーザ:{slack_name}, 今年度購入金額合計:{total_price_in_this_year}, 今回購入金額:{book_price}")

        if total_price_in_this_year + int(book_price) >= self.max_amount:
            self.logger.info(f"今年度の購入金額が{self.max_amount}円を超えてしまいます 対象ユーザ:{slack_name}, 今年度購入金額合計:{total_price_in_this_year}, 今回購入金額:{book_price}")
            return (False, total_price_in_this_year)

        return (True, total_price_in_this_year + int(book_price))

    def make_approved_html(self, item: dict) -> str:
        entry_date = "%s/%s/%s %s:%s:%s" % (item['entry_time'][0:4],
                                            item['entry_time'][4:6],
                                            item['entry_time'][6:8],
                                            item['entry_time'][8:10],
                                            item['entry_time'][10:12],
                                            item['entry_time'][12:14])
        book_type = item.get('book_type', '本')
        if book_type != '本':
            book_type = f'({book_type})'
        else:
            book_type = ''

        md_text = f"""
{entry_date} {item['real_name']}(@{item['slack_name']})
<{item['permalink']}>

#### 対象書籍
- [{item['book_name']}]({item['book_url']}){book_type}

#### 購入目的
- {item['purpose']}

#### 購入金額
- {item['book_price']} 円

#### 今年度購入金額合計
- {item['total_price_in_this_year']} 円
"""
        self.logger.debug(md_text)

        md = Markdown()
        body = md.convert(md_text)
        self.logger.debug(body)

        html = '<html lang="ja"><meta charset="utf-8"><body>'
        html += '<style> body { font-size: 3em; } </style>'
        html += body + '</body></html>'

        return html

    def make_approved_pdf(self, item: dict, save_path: str):

        html = self.make_approved_html(item)

        # PDFファイルを保存
        try:
            pdfkit.from_string(html, save_path)
        except:
            import traceback
            traceback.print_exc()
            return False

        return save_path


