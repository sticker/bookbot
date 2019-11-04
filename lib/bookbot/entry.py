import os
import re
import mojimoji
import pdfkit
from markdown import Markdown
from datetime import datetime
from slackbot.dispatcher import Message
from lib import get_logger
from lib.aws.dynamodb import Dynamodb


class Entry:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dynamodb = Dynamodb()

    def save(self, message: Message):

        now = datetime.now()

        book_name = ''
        book_type = ''
        book_price = ''
        book_url = ''
        for block in message.body['blocks']:
            if not ('text' in block and 'text' in block['text']):
                continue

            text = block['text']['text']
            if '*書籍名*' in text:
                book_name = re.sub('\*書籍名\*|\n', '', text)
            elif '*形式*' in text:
                book_type = re.sub('\*形式\*|\n', '', text)
            elif '*金額（半角数字）*' in text:
                # book_price = re.sub('\*金額\*| |,|\n', '', text)
                book_price = re.sub('\\D', '', mojimoji.zen_to_han(text))
            elif '*詳細リンク（Amazonなど）*' in text:
                book_url = re.sub('\*詳細リンク（Amazonなど）\*|<|>|\n', '', text)

        # パラメータチェック
        if not self.__validate(book_name=book_name, book_price=book_price, book_url=book_url, message=message):
            self.logger.debug("パラメータチェックNG")
            return

        # 申請日
        entry_time = now.strftime("%Y%m%d%H%M%S")

        # 申請者 Slack ID
        slack_id = self.get_slack_id(message.body['text'])

        # 申請者名
        user_name = self.get_user_name(slack_id, message)
        slack_name = user_name[0]
        real_name = user_name[1]

        # そのユーザが年間25000円以上買っていないか
        if not self.check_money_limit_per_user(slack_name):
            self.logger.debug("年間購入金額上限を超えています")
            return

        # 受付番号
        # TODO: アトミックカウンタでシーケンス番号にしたほうがいいか
        entry_no = now.strftime("%Y%m%d%H%M%S%f")[:-3]

        item = {
            'entry_no': entry_no,
            'book_name': book_name,
            'book_type': book_type,
            'book_price': book_price,
            'book_url': book_url,
            'entry_time': entry_time,
            'slack_id': slack_id,
            'slack_name': slack_name,
            'real_name': real_name
        }
        self.logger.info(f"item={item}")

        self.dynamodb.insert('bookbot-entry', item)

        reply_texts = [f"<@{slack_id}> 登録しました！補助対象になりますので承認PDFを作成します。"]
        message.send("\n".join(reply_texts))

        # 承認内容のPDFを作成してSlackにアップ　バックアップでS3にアップ
        self.upload_approved(message, item)


    def __validate(self, **kwargs):
        check_ok = True
        # 各パラメータのバリデーションを呼び出す
        if not self.__validate_book_name(kwargs['book_name'], kwargs['message']):
            check_ok = False
        if not self.__validate_book_price(kwargs['book_price'], kwargs['message']):
            check_ok = False
        if not self.__validate_book_url(kwargs['book_url'], kwargs['message']):
            check_ok = False

        return check_ok

    def __validate_book_name(self, book_name: str, message: Message) -> bool:
        """
        書籍名のバリデーション
        :param book_name: 書籍名
        :return:
        """
        # 何チェックする？
        return True

    def __validate_book_price(self, book_price: str, message: Message) -> bool:
        """
        金額のバリデーション
        :param book_price: 金額
        :return:
        """
        if not book_price.isdecimal():
            message.reply("金額は数字で入力してください")
            return False

        return True

    def __validate_book_url(self, book_url: str, message: Message) -> bool:
        """
        詳細URLのバリデーション
        :param book_url: 詳細URL
        :param message:
        :return:
        """
        return True

    def get_slack_id(self, text: str) -> str:
        slack_id = re.findall('<@(.*)>さん', text)
        return slack_id[0]

    def get_user_name(self, slack_id: str, message: Message) -> tuple:
        user = message._client.get_user(slack_id)
        self.logger.debug(user)
        slack_name = user['name']
        real_name = user['real_name']

        return (slack_name, real_name)

    def check_money_limit_per_user(self, slack_name: str) -> bool:
        # ユーザと期間でフィルタして取得
        return True

    def upload_approved(self, message: Message, item: dict):
        # パーマリンクを取得
        item['permalink'] = self.get_message_permalink(message)
        # 保存先PDFファイルパス
        save_pdf_path = f"file/{item['entry_no']}.pdf"
        # 承認PDF作成
        if not self.make_approved_pdf(item, save_pdf_path):
            self.logger.warning('承認PDFの作成に失敗しました')
            message.send(f"<@{item['slack_id']}> 承認PDFの作成に失敗しました...すいません！")
            return False

        channel_name = self.get_channel_name(message)
        self.logger.debug(channel_name)

        message._client.upload_file(channel=channel_name, fname=None, fpath=save_pdf_path,
                                    comment="このファイルと購入時の領収書を添付して立替金申請をしてください。")

        # TODO: S3にもアップロード

        return True

    def get_channel_name(self, message: Message) -> str:
        res = message._client.webapi.channels.info(channel=message.body['channel'])
        self.logger.debug(res)
        self.logger.debug(res.body)

        return res.body['channel']['name']

    def make_approved_html(self, item: dict) -> str:
        # entry_date = f"{item['entry_time'][0:4]}-{item['entry_time'][4:6]}-{item['entry_time'][6:8]} {item['entry_time'][8:10]}:{item['entry_time'][10:12]}:{item['entry_time'][12:14]}"
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
- <{item['book_url']}|{item['book_name']}>{item['book_type']}

#### 申請金額
- {item['book_price']}
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
        pdfkit.from_string(html, save_path)

        return save_path

    def get_message_permalink(self, message: Message) -> str:
        res = message._client.webapi.chat.get_permalink(channel=message.body['channel'], message_ts=message.body['ts'])
        self.logger.debug(res)
        self.logger.debug(res.body)

        return res.body['permalink']
